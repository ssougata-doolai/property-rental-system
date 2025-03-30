from django.urls import path
from mess.api import views
app_name = 'mess_api'

urlpatterns = [
    path('details/<str:mess_id>/', views.GetMess.as_view(), name='get-mess'),
    path('publish/<str:mess_id>/', views.PublishMess.as_view(), name='publish-mess'),
    path('delete/<str:mess_id>/', views.DeleteMess.as_view(), name='delete-mess'),
    path('list/', views.MessList.as_view(), name='list'),
    path('visible-list/', views.MessVisibleList.as_view(), name='visible-list'),
    path('filter-view/', views.FilterMessView.as_view(), name='filter'),
    # path('list/', views.filter_mess, name='filter'),
    path('create/', views.CreateMess.as_view(), name='create'),
    path('create/room/<str:mess_id>/', views.CreateMessRoom.as_view(), name='room'),
    path('create/address/<str:mess_id>/', views.CreateMessAddress.as_view(), name='address'),
    path('create/details/<str:mess_id>/', views.CreateMessDetails.as_view(), name='details'),
    path('create/amenites/<str:mess_id>/', views.CreateMessAmenities.as_view(), name='amenites'),
    path('create/image/<str:mess_id>/', views.CreateMessImage.as_view(), name='image'),
    path('create/image/<str:mess_id>/<str:img_id>/', views.CreateMessImage.as_view(), name='image'),
    path('create/wishlist/', views.CreateMessWishList.as_view(), name='wishlist'),
    path('create/wishlist/<str:mess_id>/', views.CreateMessWishList.as_view(), name='wishlist'),
    path('user-mess-list/<int:type>/', views.UserMessListView.as_view(), name='user-mess-list'),
    path('request-for-mess/', views.RequestForMess.as_view(), name='request-for-mess'),
    # path('user-mess-list/', views.UserMessListView.as_view(), name='user-mess-list'),
    # path('user-mess-list/', views.UserMessListView.as_view(), name='user-mess-list'),
    # path('user-mess-list/', views.UserMessListView.as_view(), name='user-mess-list'),
]
