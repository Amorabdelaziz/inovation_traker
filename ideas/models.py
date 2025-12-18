from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Idea(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('implemented', 'Implemented'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='ideas')
    submitter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_ideas')
    submission_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        ordering = ['-submission_date']

    def __str__(self):
        return self.title

    def upvote_count(self):
        return self.votes.filter(vote_type='upvote').count()

    def downvote_count(self):
        return self.votes.filter(vote_type='downvote').count()

    def vote_score(self):
        return self.upvote_count() - self.downvote_count()

    def comment_count(self):
        return self.comments.count()


class Vote(models.Model):
    VOTE_CHOICES = [
        ('upvote', 'Upvote'),
        ('downvote', 'Downvote'),
    ]

    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    vote_type = models.CharField(max_length=10, choices=VOTE_CHOICES)
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('idea', 'user')  # One vote per user per idea
        ordering = ['-voted_at']

    def __str__(self):
        return f"{self.user.username} - {self.vote_type} on {self.idea.title}"


class Comment(models.Model):
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.idea.title}"

    def is_reply(self):
        return self.parent_comment is not None


class UserProfile(models.Model):
    ROLE_SUBMITTER = 'submitter'
    ROLE_REVIEWER = 'reviewer'
    ROLE_ADMIN = 'admin'
    ROLE_CHOICES = [
        (ROLE_SUBMITTER, 'Submitter'),
        (ROLE_REVIEWER, 'Reviewer'),
        (ROLE_ADMIN, 'Administrator'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_SUBMITTER)

    class Meta:
        ordering = ['user__username']

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def can_review(self):
        return self.role in {self.ROLE_REVIEWER, self.ROLE_ADMIN} or self.user.is_staff