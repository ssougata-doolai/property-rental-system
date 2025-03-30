from django.urls import path
from crud.api.views import *
app_name = 'crud_api'

urlpatterns = [
    path('list/', api_post_list_view, name='list'),
    # path('create/', api_post_create_view, name='create'),
    path('create/', PostCreateView.as_view(), name='create'),
    path('details/<int:id>/', api_post_details_view, name='details'),
    # path('update/<int:id>/', api_post_update_view, name='update'),
    path('update/<int:id>/', PostUpdateView.as_view(), name='update'),
    path('delete/<int:id>/', api_post_delete_view, name='delete'),
]
