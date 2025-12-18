from django.contrib import admin

from .models import Category, Comment, Idea, UserProfile, Vote


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)


@admin.register(Idea)
class IdeaAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'submitter', 'status', 'submission_date')
    list_filter = ('status', 'category')
    search_fields = ('title', 'description', 'submitter__username')
    autocomplete_fields = ('category', 'submitter')


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('idea', 'user', 'vote_type', 'voted_at')
    list_filter = ('vote_type',)
    search_fields = ('idea__title', 'user__username')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('idea', 'user', 'timestamp', 'parent_comment')
    search_fields = ('idea__title', 'user__username', 'content')
    autocomplete_fields = ('idea', 'user', 'parent_comment')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email')
