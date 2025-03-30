from rest_framework import serializers
from crud.models import Post

class PostSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(read_only=True, slug_field='email')
    class Meta:
        model = Post
        fields = ('id', 'author', 'title', 'body')
        extra_kwargs = {
            'author': {'required': False}
        }
