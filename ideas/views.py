from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CommentForm, IdeaForm, IdeaStatusForm, RegistrationForm
from .models import Category, Comment, Idea, UserProfile, Vote


def user_can_review(user):
    if not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        return False
    return profile.can_review


def home(request):
    ideas = (
        Idea.objects.select_related('category', 'submitter')
        .prefetch_related('votes', 'comments')
        .annotate(
            upvotes=Count('votes', filter=Q(votes__vote_type='upvote')),
            downvotes=Count('votes', filter=Q(votes__vote_type='downvote')),
            comment_total=Count('comments', distinct=True),
        )
    )

    category_filter = request.GET.get('category')
    status_filter = request.GET.get('status')
    search_query = request.GET.get('q')

    if category_filter:
        ideas = ideas.filter(category__id=category_filter)
    if status_filter:
        ideas = ideas.filter(status=status_filter)
    if search_query:
        ideas = ideas.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )

    context = {
        'ideas': ideas,
        'categories': Category.objects.all(),
        'selected_category': category_filter,
        'selected_status': status_filter,
        'search_query': search_query or '',
    }
    return render(request, 'ideas/home.html', context)


def idea_detail(request, pk):
    idea = get_object_or_404(
        Idea.objects.select_related('category', 'submitter')
        .prefetch_related('comments__user', 'comments__replies__user', 'votes'),
        pk=pk,
    )
    comment_form = CommentForm()
    user_vote = None
    if request.user.is_authenticated:
        user_vote = idea.votes.filter(user=request.user).first()
    comments = (
        idea.comments.filter(parent_comment__isnull=True)
        .select_related('user')
        .prefetch_related('replies__user')
    )
    return render(
        request,
        'ideas/idea_detail.html',
        {
            'idea': idea,
            'comment_form': comment_form,
            'comments': comments,
            'user_vote': user_vote,
        },
    )


@login_required
def submit_idea(request):
    if request.method == 'POST':
        form = IdeaForm(request.POST)
        if form.is_valid():
            idea = form.save(commit=False)
            idea.submitter = request.user
            idea.save()
            messages.success(request, 'Idea submitted successfully.')
            return redirect('idea_detail', pk=idea.pk)
    else:
        form = IdeaForm()
    return render(request, 'ideas/idea_form.html', {'form': form})


@login_required
def edit_idea(request, pk):
    idea = get_object_or_404(Idea, pk=pk, submitter=request.user)
    if request.method == 'POST':
        form = IdeaForm(request.POST, instance=idea)
        if form.is_valid():
            form.save()
            messages.success(request, 'Idea updated successfully.')
            return redirect('idea_detail', pk=idea.pk)
    else:
        form = IdeaForm(instance=idea)
    return render(request, 'ideas/idea_form.html', {'form': form, 'idea': idea})


@login_required
def my_ideas(request):
    ideas = Idea.objects.filter(submitter=request.user).select_related('category')
    return render(request, 'ideas/my_ideas.html', {'ideas': ideas})


@login_required
def review_dashboard(request):
    if not user_can_review(request.user):
        messages.error(request, 'You do not have permission to review ideas.')
        return redirect('home')

    status_filter = request.GET.get('status') or 'pending'
    ideas = Idea.objects.select_related('category', 'submitter')
    if status_filter:
        ideas = ideas.filter(status=status_filter)

    context = {
        'ideas': ideas,
        'status_filter': status_filter,
        'status_choices': Idea.STATUS_CHOICES,
        'status_form': IdeaStatusForm(),
    }
    return render(request, 'ideas/review_dashboard.html', context)


@login_required
@require_POST
def vote(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    vote_type = request.POST.get('vote_type')

    if vote_type not in dict(Vote.VOTE_CHOICES):
        messages.error(request, 'Invalid vote type.')
        return redirect('idea_detail', pk=pk)

    vote, created = Vote.objects.get_or_create(
        idea=idea,
        user=request.user,
        defaults={'vote_type': vote_type},
    )

    if not created and vote.vote_type == vote_type:
        vote.delete()
        messages.info(request, 'Your vote has been removed.')
    else:
        vote.vote_type = vote_type
        vote.save()
        messages.success(request, 'Your vote has been recorded.')

    return redirect('idea_detail', pk=pk)


@login_required
@require_POST
def add_comment(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.idea = idea
        comment.user = request.user
        parent_id = request.POST.get('parent_id')
        if parent_id:
            comment.parent_comment = get_object_or_404(Comment, pk=parent_id, idea=idea)
        comment.save()
        messages.success(request, 'Comment added.')
    else:
        messages.error(request, 'Could not add comment. Please check the form.')
    return redirect('idea_detail', pk=pk)


def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully.')
            return redirect('home')
    else:
        form = RegistrationForm()
    return render(request, 'ideas/register.html', {'form': form})


@login_required
@require_POST
def update_idea_status(request, pk):
    if not user_can_review(request.user):
        messages.error(request, 'You do not have permission to update idea status.')
        return redirect('home')

    idea = get_object_or_404(Idea, pk=pk)
    form = IdeaStatusForm(request.POST, instance=idea)
    if form.is_valid():
        form.save()
        messages.success(request, f'Idea status updated to {idea.get_status_display()}.')
    else:
        messages.error(request, 'Could not update status. Please try again.')
    next_url = request.POST.get('next') or 'review_dashboard'
    return redirect(next_url)
