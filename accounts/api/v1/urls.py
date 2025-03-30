from django.urls import path
from accounts.api.views import *
app_name = 'crud_api'

urlpatterns = [
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('verify-otp/', VerifyOtpView.as_view(), name='verify-otp'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('set-password/', SetPasswordView.as_view(), name='set-password'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
]
