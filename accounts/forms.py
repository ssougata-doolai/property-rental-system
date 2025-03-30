from django import forms
from django.contrib.auth.models import Group, Permission

class PermissionChangeListForm(forms.ModelForm):
    group = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(), required=False)
    permission = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(), required=False)

# from django.contrib.auth.forms import UserCreationForm, UserChangeForm
# from django.contrib.auth import get_user_model
# User = get_user_model()
#
#
# class UserCreationForm(UserCreationForm):
#
#     class Meta(UserCreationForm):
#         model = User
#         fields = ('email',)
#
#
# class UserChangeForm(UserChangeForm):
#
#     class Meta:
#         model = User
#         fields = ('email',)

# class UserAdminChangeForm(forms.ModelForm):
#     passowrd1 = forms.CharField(label='Password', widget=forms.PasswordInput)
#     passowrd2 = forms.CharField(label='Password confirm', widget=forms.PasswordInput)
#
#     class Meta:
#         model = User
#         fields = ('phone_number',)
#
#     def clean_password2(self):
#         password1 = self.cleaned_data.get("password1")
#         password2 = self.cleaned_data.get("password2")
#         if len(password1) > 7:
#             if password1 and password2 and password1 != password2:
#                 raise forms.ValidationError(
#                         "Password and Confirm Password didn't match"
#                     )
#         else:
#             raise forms.ValidationError(
#                 "Password must have atleast 8 characters"
#             )
#
#     def save(self, commit=True):
#         user = super(UserCreationForm, self).save(commit=False)
#         user.set_password(self.cleaned_data["passowrd1"])
#         if commit:
#             user.save()
#         return user
#
# class UserAdminChangeForm(forms.ModelForm):
#     pass
