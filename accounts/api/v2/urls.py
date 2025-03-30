from django.urls import path
from accounts.api.v2.views import *
app_name = 'accounts-api-v2'

urlpatterns = [
    path('verify-phone/', VerifyPhoneView.as_view(), name='verify-phone'),
    path('verify-phone-otp/', VerifyPhoneOtpView.as_view(), name='verify-phone-otp'),
    path('set-password/', SetPasswordView.as_view(), name='set-password'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('edit-profile/', EditProfileView.as_view(), name='edit-profile'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('verify-email-otp/', VerifyEmailOtpView.as_view(), name='verify-email-otp'),
]
