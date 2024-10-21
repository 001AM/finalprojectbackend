from . import views
from django.views.generic import TemplateView
from django.urls import path

app_name = 'UserProfile'

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('update-user-profile/', views.update_user_profile, name='update-user-profile'),

    path('follow/', views.follow_user, name='follow_user'),
    path('unfollow/', views.unfollow_user, name='unfollow_user'),
    path('follower_list/', views.follower_list, name='follower_list'),
    path('create_post/', views.create_post, name='create_post'),
    path('get_user_posts/', views.get_user_posts, name='get_user_posts'),
]
