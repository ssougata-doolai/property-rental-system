# from django.db import models
from django.contrib.gis.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class Blog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    text = models.TextField()
    published = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    published_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        if 'published_date':
            ordering = ('-published_date', )
        else:
            ordering = ('-created_date', )

    def __str__(self):
        return self.slug
