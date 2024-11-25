from rest_framework import generics, viewsets
from django.db.models import Q
from django.utils import timezone

from datetime import timedelta
from django.http import Http404

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

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers, vary_on_cookie

from rest_framework.exceptions import PermissionDenied

from blog.api.filters import PostFilterSet

from django.urls import resolve

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

    @method_decorator(cache_page(300))
    def get(self, *args, **kwargs):
        return super(UserDetail, self).get(*args, *kwargs)

"""
For TagViewSet and PostViewSet the urls are established by virture of the following lines in
../blog/api/urls.py

from rest_framework.routers import DefaultRouter
...
router = DefaultRouter()
router.register("tags", TagViewSet)
router.register("posts", PostViewSet)
"""

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    @action(methods=["get"], detail=True, name="Posts with the Tag")
    def posts(self, request, pk=None):
        path = self.request.path
        resolved = resolve(path)
        url_name = resolved.url_name
        logger.debug("in blog.api.views.TagViewSet.posts and url_name is")
        logger.debug(url_name)
        logger.debug("Inside TagView.posts and pk and self.request are")
        logger.debug(pk)
        logger.debug(self.request)
        tag = self.get_object()
        """
        page = self.paginate_queryset(tag.posts)
        if page is not None:
            post_serializer = PostSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(post_serializer.data)
        """

        post_serializer = PostSerializer(
            tag.posts, many=True, context={"request": request}
        )
        return Response(post_serializer.data)

    @method_decorator(cache_page(300))
    def list(self, *args, **kwargs):
        path = self.request.path
        resolved = resolve(path)
        url_name = resolved.url_name
        logger.debug("in blog.api.views.TagViewSet.list and url_name is")
        logger.debug(url_name)
        return super(TagViewSet, self).list(*args, **kwargs)

    @method_decorator(cache_page(300))
    def retrieve(self, *args, **kwargs):
        path = self.request.path
        resolved = resolve(path)
        url_name = resolved.url_name
        logger.debug("in blog.api.views.TagViewSet.retrieve and url_name is")
        logger.debug(url_name)
        return super(TagViewSet, self).retrieve(*args, **kwargs)

class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [AuthorModifyOrReadOnly | IsAdminUserForObject]
    queryset = Post.objects.all()
    #filterset_fields = ["author", "tags"] commented out as now using PostFilterSet for customization
    filterset_class = PostFilterSet
    ordering_fields = ["published_at", "author", "title", "slug"]

    def get_queryset(self):
        path = self.request.path
        resolved = resolve(path)
        url_name = resolved.url_name
        logger.debug("in blog.api.views.PostViewSet.get_queryset and url_name is")
        logger.debug(url_name)
        if self.request.user.is_anonymous:
            # published only
            #return self.queryset.filter(published_at__lte=timezone.now())
            queryset = self.queryset.filter(published_at__lte=timezone.now())
        elif self.request.user.is_staff:
            # allow all
            #return self.queryset
            queryset = self.queryset

        # filter for own or
        else:
          """
          an example of filtering using Q is:
          queryset = User.objects.filter(Q(first_name__startswith='R')|Q(last_name__startswith='D'))
          for comparison purposes, an alternative verbose way to do the same filtering is:
          queryset = User.objects.filter(
             first_name__startswith='R'
           ) | User.objects.filter(last_name__startswith='D')
          see https://books.agiliq.com/projects/django-orm-cookbook/en/latest/query_relatedtool.html
          """
          queryset = self.queryset.filter(
            Q(published_at__lte=timezone.now()) | Q(author=self.request.user)
          )

        time_period_name = self.kwargs.get("period_name")

        if not time_period_name:
            # no further filtering required
            return queryset

        if time_period_name == "new":
            return queryset.filter(
                published_at__gte=timezone.now() - timedelta(hours=1)
            )
        elif time_period_name == "today":
            return queryset.filter(
                published_at__date=timezone.now().date(),
            )
        elif time_period_name == "week":
            return queryset.filter(published_at__gte=timezone.now() - timedelta(days=7))
        else:
            raise Http404(
                f"Time period {time_period_name} is not valid, should be "
                f"'new', 'today' or 'week'"
            )

    def get_serializer_class(self):
        if self.action in ("list", "create"):
            return PostSerializer
        return PostDetailSerializer

    @method_decorator(cache_page(300))
    @method_decorator(vary_on_headers("Authorization"))
    @method_decorator(vary_on_cookie)
    @action(methods=["get"], detail=False, name="Posts by the logged in user")
    def mine(self, request):
        if request.user.is_anonymous:
            raise PermissionDenied("You must be logged in to see which Posts are yours")
        posts = self.get_queryset().filter(author=request.user)

        page = self.paginate_queryset(posts)

        if page is not None:
            serializer = PostSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)

        serializer = PostSerializer(posts, many=True, context={"request": request})
        return Response(serializer.data)

    """
    @method_decorator(cache_page(120))
    def list(self, *args, **kwargs):
        return super(PostViewSet, self).list(*args, **kwargs)
    """

    @method_decorator(cache_page(120))
    @method_decorator(vary_on_headers("Authorization", "Cookie"))
    def list(self, *args, **kwargs):
        return super(PostViewSet, self).list(*args, **kwargs) #super is viewsets.ModelViewSet which has a 
                                                              #list method.  See def list(...) under Methods at
                                                              #https://www.cdrf.co/3.1/rest_framework.viewsets/ModelViewSet.html
