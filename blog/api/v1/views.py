from rest_framework import status, serializers, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import BlogSerializer
from blog.models import Blog
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

User = get_user_model()

class BlogPublishView(APIView):
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [IsAuthenticated, ]
    def post(self, request, slug=None):
        if slug == None:
            obj = Blog(user=request.user, published=True, published_date=timezone.now())
            blog = BlogSerializer(obj, data=request.data)
            blog.is_valid(raise_exception=True)
            blog.save()
            return Response(blog.data, status=status.HTTP_201_CREATED)
        else:
            try:
                obj = Blog.objects.get(slug=slug, user=request.user)
                if obj.published == False:
                    obj.published = True
                    obj.published_date = timezone.now()
            except Blog.DoesNotExist:
                return Response(status = status.HTTP_404_NOT_FOUND)
            s=status.HTTP_201_CREATED
        blog = BlogSerializer(obj, data=request.data)
        blog.is_valid(raise_exception=True)
        blog.save()
        return Response(blog.data, status=s)


class BlogSaveToDraftView(APIView):
    def post(self, request):
        user = User.objects.all().first()
        obj = Blog(user=user)
        blog = BlogSerializer(obj, data=request.data)
        blog.is_valid(raise_exception=True)
        blog.save()
        return Response(blog.data, status=status.HTTP_201_CREATED)

class BlogDetailsView(APIView):
    def get(self, request, slug):
        try:
            if request.user.is_authenticated:
                blog = Blog.objects.get(slug = slug, user=request.user)
                serializer = BlogSerializer(blog)
                return Response(serializer.data)
            else:
                raise Blog.DoesNotExist
        except Blog.DoesNotExist:
            try:
                blog = Blog.objects.get(slug = slug, published=True)
                serializer = BlogSerializer(blog)
                return Response(serializer.data)
            except Blog.DoesNotExist:
                return Response(status = status.HTTP_404_NOT_FOUND)

class BlogListView(APIView):
    def get(self, request):
        blogs = Blog.objects.filter(published=True)
        serializer = BlogSerializer(blogs, many=True)
        return Response(serializer.data)

class BlogList(generics.ListAPIView):
    paginate_by = 10
    serializer_class = BlogSerializer

    def get_queryset(self):
        blogs = Blog.objects.filter(published=True)
        return blogs