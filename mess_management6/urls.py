"""mess_management6 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework_swagger.views import get_swagger_view
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from accounts.api.v2.views import ObtainTokenPairWithPhoneView
schema_view = get_swagger_view(title = 'Mess Management')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', include('blog.urls', 'blog')),
    path('login/',auth_views.LoginView.as_view(template_name='blog/login.html'),name='login'),
    path('logout/',auth_views.LogoutView.as_view(template_name='blog/logout.html'),name='logout'),
    # path('admin/defender/', include('defender.urls')),
    path('api/crud/', include('crud.api.urls', 'crud_api')),
    # path('api/accounts/', include('accounts.api.urls', 'accounts_api')),
    path('api/accounts/v2/', include('accounts.api.v2.urls', 'accounts-api-v2')),
    path('api/mess/', include('mess.api.urls', 'mess_api')),
    path('api/hotel/', include('hotel.api.v1.urls', 'hotel_api')),
    path('api/blog/v1/', include('blog.api.v1.urls', 'blog-api-v1')),
    path('', schema_view),
    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/', ObtainTokenPairWithPhoneView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('summernote/', include('django_summernote.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
