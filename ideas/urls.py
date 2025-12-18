from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('ideas/submit/', views.submit_idea, name='submit_idea'),
    path('ideas/<int:pk>/', views.idea_detail, name='idea_detail'),
    path('ideas/<int:pk>/edit/', views.edit_idea, name='edit_idea'),
    path('ideas/<int:pk>/status/', views.update_idea_status, name='update_idea_status'),
    path('ideas/<int:pk>/vote/', views.vote, name='vote'),
    path('ideas/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('my-ideas/', views.my_ideas, name='my_ideas'),
    path('review-dashboard/', views.review_dashboard, name='review_dashboard'),
    path('register/', views.register, name='register'),
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='ideas/login.html'),
        name='login',
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(),
        name='logout',
    ),
]

