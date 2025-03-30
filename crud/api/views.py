from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from crud.models import Post
from crud.api.serializers import PostSerializer
# import coreapi
# from rest_framework.schemas import AutoSchema
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.http import QueryDict
#
# class PostListViewSchema(AutoSchema):
#     def get_manual_fields(self, path, method):
#         extra_fields = []
#         if method.lower() in ['post']:
#             extra_fields = [
#                 coreapi.Field(
#                     name = 'title',
#                     required = True,
#                     description='Name of title',
#                 ),
#                 coreapi.Field(
#                     name = 'body',
#                     required = True,
#                     description='body here'
#                 ),
#             ]
#         manual_fields = super().get_manual_fields(path, method)
#         return manual_fields + extra_fields

class PostCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    # schema = PostListViewSchema()
    def post(self, request):
        post = PostSerializer(data = request.data)
        if post.is_valid():
            post.save(author=request.user)
            return Response(post.data, status=status.HTTP_201_CREATED)
        else:
            return Response(post.errors, status=status.HTTP_400_BAD_REQUEST)

class PostUpdateView(APIView):
    # schema = PostListViewSchema()
    def post(self, id):
        try:
            post = Post.objects.get(id = id)
        except Post.DoesNotExist:
            return Response(status = status.HTTP_404_NOT_FOUND)

        if request.method == 'POST':
            serialized = PostSerializer(post, data=request.data)
            if serialized.is_valid():
                serialized.save()
                return Response(serialized.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', ])
def api_post_list_view(request):
    posts = Post.objects.all()
    serialize = PostSerializer(posts, many = True)
    return Response(serialize.data)

@api_view(['GET', ])
def api_post_details_view(request, id):
    try:
        post = Post.objects.get(id = id)
    except Post.DoesNotExist:
        return Response(status = status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serialized = PostSerializer(post)
        return Response(serialized.data)

@api_view(['DELETE', ])
def api_post_delete_view(request, id):
    try:
        post = Post.objects.get(id = id)
    except Post.DoesNotExist:
        return Response(status = status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# @api_view(['POST', ])
# def api_post_create_view(request):
#     post = PostSerializer(data = request.data)
#     if post.is_valid():
#         post.save()
#         return Response(post.data, status=status.HTTP_201_CREATED)
#     else:
#         return Response(post.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['POST', ])
# def api_post_update_view(request, id):
#     try:
#         post = Post.objects.get(id = id)
#     except Post.DoesNotExist:
#         return Response(status = status.HTTP_404_NOT_FOUND)
#
#     if request.method == 'POST':
#         serialized = PostSerializer(post, data=request.data)
#         if serialized.is_valid():
#             serialized.save()
#             return Response(serialized.data, status=status.HTTP_201_CREATED)
#         else:
#             return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
