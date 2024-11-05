from rest_framework import generics, viewsets

from blango_auth.models import User
#from blog.api.serializers import PostSerializer, UserSerializer, PostDetailSerializer
from blog.api.serializers import (
    PostSerializer,
    UserSerializer,
    PostDetailSerializer,
    TagSerializer,
)
from blog.models import Post, Tag
#from blog.api.permissions import AuthorModifyOrReadOnly
from blog.api.permissions import AuthorModifyOrReadOnly, IsAdminUserForObject

from rest_framework.decorators import action
from rest_framework.response import Response

import logging
logger = logging.getLogger(__name__)

"""
class PostList below extends generics.ListCreateAPIView which in turn 
extends generics.GenericAPIView as well as mixins.ListModelMixin and 
mixins.CreateModelMixin.  See https://testdriven.io/blog/drf-views-part-2/

ListModelMixin provides a list(self, request, *args, **kwargs) method that ListCreateAPIView 
uses in its get() method.

CreateModelMixin provides a create(self, request, *args, **kwargs) method that handles the
logic for creating a new object. ListCreateAPIView uses this create() method in its post()
method.

See https://www.django-rest-framework.org/api-guide/generic-views/ 
for documentation on GenericAPIView, ListModelMixin, and CreateModelMixin.

Note that the following lines from urls.py and blog.api.urls.py cause routing to
blog.api.view.PostList.as_view():
from urls.py we have:
path("api/v1/", include("blog.api.urls"))
from blog.api.urls.py we have:
path("posts/", PostList.as_view(), name="api_post_list"

When extending generics.GenericAPIView, generics.ListCreateAPIView does not set 
queryset and serializer_class. So these must set within any given subclass of it. 
Alternatively, you can overwrite get_queryset()/get_serializer_class() in that
subclass. Below we see that two of the attribute settings inside 
class PostList(generics.ListCreateAPIView) are:
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer

"""
class PostList(generics.ListCreateAPIView):
    logger.debug("in blog.api.views.PostList")
    queryset = Post.objects.all()
    serializer_class = PostSerializer


"""
class PostDetail below extends generics.RetrieveUpdateDestroyAPIView which in turn 
extends generics.GenericAPIView as well as mixins.RetrieveModelMixin, mixins.UpdateModelMixin
and mixins.DestroyModelMixinModelMixin.

RetrieveUpdateDestroyAPIView is one of several subclasses of rest_framework.generics.GenericAPIView 
that contains request handlers.  These provide functionality for handling requests to retrieve, 
update, and delete a single model instance.

Key points:
Methods: It supports get, put, patch, and detlete methods.
Mixins: It combines the following mixins:

RetrieveModelMixin: provides a retrieve(self, request, *args, **kwargs) method for retrieving
a single object. RetrieveUpdateDestroyAPIView uses this retrieve method in its get() method.
https://www.google.com/search?q=django+rest+framework+RetrieveModelMixin&rlz=1C1VDKB_enUS1092US1092&oq=django+rest+framework+RetrieveModelMixin&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIKCAEQABiABBiiBDIKCAIQABiABBiiBDIKCAMQABiABBiiBDIKCAQQABiABBiiBDIKCAUQABiABBiiBDIGCAYQRRg80gEIOTM3M2owajeoAgCwAgA&sourceid=chrome&ie=UTF-8

UpdateModelMixin provides an update(self, request, *args, **kwargs) method, that implements
updating and saving an existing model record instance. It also provides a 
partial_update(self, request, *args, **kwargs) method, that is similar to the update method, 
except that all fields for the update will be optional. RetrieveUpdateDestroyAPIView uses
the update method in its put() method and the partial_update method in its patch() method.

DestroyModelMixin provides a destroy(self, request, *args, **kwargs) metod for deleting an object.
RetrieveUpdateDestroyAPIView uses this method in is delete() method. 

You can customize the behavior of generics.RetrieveUpdateDestroyAPIView by overriding methods or 
setting attributes.

Note that generics.RetrieveUpdateDestroyAPIView does not include the Mixin CreateModelMixin. Thus,
it does not provide a post() method and so does not support HTTP POST.

When extending generics.GenericAPIView, generics.RetrieveUpdateDestroyAPIView does not set queryset and 
serializer_class. So these must set within any given subclass of it. Alternatively, you can overwrite
get_queryset()/get_serializer_class() in that subclass. 
Below we see that two of the attribute settings inside class PostDetail(generics.RetrieveUpdateDestroyAPIView) 
are:
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer

See https://www.django-rest-framework.org/api-guide/generic-views/ 
for documentation on GenericAPIView, RetrieveModelMixin, UpdateModelMixin, and DestroyModelMixin.

A basic example:
Python
from rest_framework import generics
from .models import Product
from .serializers import ProductSerializer

class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

Explanation:
queryset: Specifies the queryset to use for retrieving the object.
serializer_class: Specifies the serializer class to use for serializing the object and validating 
incoming data. With this setup, you can perform the following:
GET /products/{id}/: Retrieve a specific product.
PUT /products/{id}/: Update a product with a full payload.
PATCH /products/{id}/: Partially update a product.
DELETE /products/{id}/: Delete a product.

The as_view() method in generics.RetrieveUpdateDestroyAPIView, that is the parent of 
class PostDetail (see below), is invoked based on the following paths:

in blango.urls.py we have:
    path("api/v1/", include("blog.api.urls"))

in blango.blog.api.urls.py we see PostDetail.as_view() as the 2nd element in the urlpatterns list 
seen below:
....
from blog.api.views import PostList, PostDetail, UserDetail
urlpatterns = [
    path("posts/", PostList.as_view(), name="api_post_list"),
    path("posts/<int:pk>", PostDetail.as_view(), name="api_post_detail"),
    path("users/<str:email>", UserDetail.as_view(), name="api_user_detail"),
    path("auth/", include("rest_framework.urls")),
    path("token-auth/", views.obtain_auth_token),
]
"""
class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    #permission_classes = [AuthorModifyOrReadOnly]
    logger.debug("in blog.api.views.PostDetail")
    permission_classes = [AuthorModifyOrReadOnly | IsAdminUserForObject]
    queryset = Post.objects.all()
    #serializer_class = PostSerializer
    serializer_class = PostDetailSerializer

"""
class UserDetail below extends generics.RetrieveAPIView which in turn 
extends generics.GenericAPIView as well as mixins.RetrieveModelMixin.

RetrieveModelMixin: provides a retrieve(self, request, *args, **kwargs) method for retrieving
a single object. RetrieveAPIView uses this retrieve method in its get() method.

The as_view() method in generics.RetrieveAPIView, that is the parent of class UserDetail (see below),
is invoked based on the following paths:

in blango.urls.py we have:
    path("api/v1/", include("blog.api.urls"))

in blango.blog.api.urls.py we see UserDetail.as_view() as the 3rd element in the urlpatterns list 
seen below:
....
from blog.api.views import PostList, PostDetail, UserDetail
urlpatterns = [
    path("posts/", PostList.as_view(), name="api_post_list"),
    path("posts/<int:pk>", PostDetail.as_view(), name="api_post_detail"),
    path("users/<str:email>", UserDetail.as_view(), name="api_user_detail"),
    path("auth/", include("rest_framework.urls")),
    path("token-auth/", views.obtain_auth_token),

See https://www.django-rest-framework.org/api-guide/generic-views/ 
for documentation on RetrieveModelMixin.

"""
class UserDetail(generics.RetrieveAPIView):
    """
    By default, lookup_field is set to 'pk' in RetrieveAPIView which means
    it uses the primary key to find the desired record.  Below we set lookup_field
    to "email" which means it uses the email field to find the desired record.  
    An example url would be:
    .../api/v1/users/Rengie899@gmail.com
    """
    lookup_field = "email"
    queryset = User.objects.all()
    logger.debug("In blog.api.views.UserDetail and")
    #logger.debug("queryset[0] and queryset[1] are")
    #logger.debug(queryset[0])
    #logger.debug(queryset[1])
    serializer_class = UserSerializer

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    @action(methods=["get"], detail=True, name="Posts with the Tag")
    def posts(self, request, pk=None):
        tag = self.get_object()
        post_serializer = PostSerializer(
            tag.posts, many=True, context={"request": request}
        )
        return Response(post_serializer.data)

class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [AuthorModifyOrReadOnly | IsAdminUserForObject]
    queryset = Post.objects.all()

    def get_serializer_class(self):
        if self.action in ("list", "create"):
            return PostSerializer
        return PostDetailSerializer
