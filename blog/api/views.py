from rest_framework import generics

from blango_auth.models import User
from blog.api.serializers import PostSerializer, UserSerializer
from blog.models import Post
#from blog.api.permissions import AuthorModifyOrReadOnly
from blog.api.permissions import AuthorModifyOrReadOnly, IsAdminUserForObject

import logging
logger = logging.getLogger(__name__)

class PostList(generics.ListCreateAPIView):
    logger.debug("in blog.api.views.PostList")
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    #permission_classes = [AuthorModifyOrReadOnly]
    logger.debug("in blog.api.views.PostDetail")
    permission_classes = [AuthorModifyOrReadOnly | IsAdminUserForObject]
    queryset = Post.objects.all()
    serializer_class = PostSerializer

class UserDetail(generics.RetrieveAPIView):
    lookup_field = "email"
    queryset = User.objects.all()
    logger.debug("In blog.api.views.UserDetail and")
    logger.debug("queryset[0] and queryset[1] are")
    logger.debug(queryset[0])
    logger.debug(queryset[1])
    serializer_class = UserSerializer