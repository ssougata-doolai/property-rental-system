from django.urls import path
from . import views

app_name = 'blog-api-v1'

urlpatterns = [
    path('publish/', views.BlogPublishView.as_view(), name='publish'),
    path('update-publish/<slug:slug>/', views.BlogPublishView.as_view(), name='update'),
    path('details/<slug:slug>/', views.BlogDetailsView.as_view(), name="details"),
    # path('list/', views.BlogListView.as_view(), name='list'),
    path('list/', views.BlogList.as_view(), name='blog-list'),
]
