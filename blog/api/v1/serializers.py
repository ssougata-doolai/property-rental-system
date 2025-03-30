from rest_framework import serializers
from django.contrib.auth import get_user_model
from blog.models import Blog

User = get_user_model()

class BlogSerializer(serializers.ModelSerializer):

    class Meta:
        model = Blog
        exclude = ['id', ]
        extra_kwargs = {
            'slug': {'read_only': True},
            'user': {'read_only': True},
            'published': {'read_only': True},
            'published_date': {'read_only': True},
        }
        # fields = ['title', 'text']
