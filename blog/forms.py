from django import forms
from .models import Blog
from django_summernote.widgets import SummernoteWidget

class BlogForm(forms.ModelForm):
    text = forms.CharField(widget=SummernoteWidget())

    class Meta:
        model = Blog
        fields = ['title', 'text', ]
