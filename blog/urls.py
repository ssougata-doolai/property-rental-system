from django.urls import path
from .import views

app_name = 'blog'

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create, name='create'),
    path('update/<slug:slug>/', views.update, name='update'),
    path('confirm-publish/<slug:slug>/', views.confirm_publish, name="confirm-publish"),
    path('publish/', views.publish_blog, name='publish'),
    path('publish/<slug:slug>/', views.publish_blog, name='publish'),
    path('details/<slug:slug>/', views.blog_details, name="details"),
    path('all-list/', views.blog_list, name="list"),
    path('draft-list/', views.blog_draft_list, name="draft-list"),
    path('published-list/', views.blog_published_list, name="published-list"),
]
