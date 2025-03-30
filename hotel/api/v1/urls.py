from django.urls import path
from hotel.api.v1 import views
app_name = 'hotel_api'

urlpatterns = [
    path('create/', views.CreateHotel.as_view(), name="create"),

]