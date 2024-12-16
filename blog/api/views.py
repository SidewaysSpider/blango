from rest_framework import generics, viewsets
from django.db.models import Q
from django.utils import timezone

from datetime import timedelta
from django.http import Http404
from django.utils.decorators import classonlymethod

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

    def args_checker(self,request,*args,**kwargs):
        #The only purpose of args_checker is to log to the console the type and values for request and args.
        #futher down in def get() we have:
        #new_element = "NYJets are losers!"
        #new_args = args + (new_element,)
        #x = self.args_checker(*new_args,**kwargs)
        #For above def args_checker(self,request,*args,**kwargs) request pops out
        #args[0] from the args tuple which is request. This causes args[0] to = new_args[1] 
        #Because new_args[1] = "NYJets are losers" args[0] becomes "NYJets are losers"
        logger.debug("at top of blog.api.views.UserDetail.args_checker and")
        logger.debug("type of request = %s",type(request))
        logger.debug("request =%s",request) #This logs request = <rest_framework.request.Request: GET '/api/v1/users/Rengie899@gmail.com'> 
        #logger.debug("dir of request = s%",dir(request))
        #logger.debug("request.__str__ = s%",request.__str__)
        #logger.debug("request.data = %s",request.data)
        #logger.debug("request.query_params = %s",request.query_params)
        #logger.debug("request.content_type = %s",request.content_type)
        logger.debug("request.method = %s",request.method)
        logger.debug("args =%s",args)
        logger.debug("args[0] = %s",args[0]) #This logs args[0]="NYJets are losers"
        logger.debug("type of args = %s",type(args))
        #logger.debug(type(args[0]))
        #logger.debug(request)
        return "args_checker has completed"

    """
    By default, lookup_field is set to 'pk' in RetrieveAPIView which means
    it uses the primary key to find the desired record.  Below we set lookup_field
    to "email" which means it uses the email field to find the desired record.  
    An example url would be:
    .../api/v1/users/Rengie899@gmail.com

    The following describes the process that leads to the below get method being called.
    Django picks up the following url from blog.api.urls.py
    urlpatterns = [
    path("users/<str:email>", UserDetail.as_view(), name="api_user_detail"),
    ]
    So as an example 
    This causes execution of UserDetail.as_view().  UserDetail inherits from
    class rest_framework.generics.RetrieveAPIView which inherits from 
    rest_framework.generics.GenericsAPIView which inherits from class
    rest_framework.views.APIView,  In this class we see:
    class APIView(View):
    and inside this class we see the classmethod as_view. as_view is a factory
    method that produces a view object via view = super().as_view(**initkwargs).
    super in this case is View and taking note of the statement
    from django.views.generic import View
    we find in class django.view.generic.base.View the following 

    class View:

        #Intentionally simple parent class for all views. Only implements
        #dispatch-by-method and simple sanity checking.


        http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']

        def __init__(self, **kwargs):
            
            #Constructor. Called in the URLconf; can contain helpful extra
            #keyword arguments, and other things.
            
            # Go through keyword arguments, and either save their values to our
            # instance, or raise an error.
            for key, value in kwargs.items():
                setattr(self, key, value)

        @classonlymethod
        def as_view(cls, **initkwargs):
            #Main entry point for a request-response process.
            for key in initkwargs:
                if key in cls.http_method_names:
                    raise TypeError(
                        'The method name %s is not accepted as a keyword argument '
                        'to %s().' % (key, cls.__name__)
                    )
                if not hasattr(cls, key):
                    raise TypeError("%s() received an invalid keyword %r. as_view "
                                    "only accepts arguments that are already "
                                    "attributes of the class." % (cls.__name__, key))

            def view(request, *args, **kwargs):
                self = cls(**initkwargs)
                self.setup(request, *args, **kwargs)
                if not hasattr(self, 'request'):
                    raise AttributeError(
                        "%s instance has no 'request' attribute. Did you override "
                        "setup() and forget to call super()?" % cls.__name__
                    )
                return self.dispatch(request, *args, **kwargs)
            view.view_class = cls
            view.view_initkwargs = initkwargs

            # take name and docstring from class
            update_wrapper(view, cls, updated=())

            # and possible attributes set by decorators
            # like csrf_exempt from dispatch
            update_wrapper(view, cls.dispatch, assigned=())
            return view

        def setup(self, request, *args, **kwargs):
            #Initialize attributes shared by all view methods.
            if hasattr(self, 'get') and not hasattr(self, 'head'):
                self.head = self.get
            self.request = request
            self.args = args
            self.kwargs = kwargs

        def dispatch(self, request, *args, **kwargs):
            # Try to dispatch to the right method; if a method doesn't exist,
            # defer to the error handler. Also defer to the error handler if the
            # request method isn't on the approved list.
            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed
            return handler(request, *args, **kwargs)

        etc
    
    So, in conclusion, Django's execution of the as_view() method gets back a view object
    that is an instance of class django.view.generic.base.View.  We see from the above
    code that this view object has a view method that when called exeutes the setup method
    and in its return executes the dispatch method.  The dispatch method returns the request 
    method in lower case which will be either get, post, etc.  Django then calls get or post or 
    whatever based on what is returned from the distpatch method. In the case of UserDetail, 
    the get method is get because of what's in the request object pass to the dispatch method.
    Thus, the get method that gets called by Django is the get method that is seen below.
    """

    lookup_field = "email"
    queryset = User.objects.all()
    logger.debug("In blog.api.views.UserDetail berore def get")
    #logger.debug("queryset[0] and queryset[1] are")
    #logger.debug(queryset[0])
    #logger.debug(queryset[1])
    serializer_class = UserSerializer
    @method_decorator(cache_page(300))
    def get(self, *args, **kwargs):
        logger.debug("Iowa State got beat dir(self) =%s",dir(self))
        logger.debug("self.request =%s",self.request)
        logger.debug("Texas got beat again by Georgia")
        logger.debug("args =%s",args)
        logger.debug("type of args = %s",type(args))
        logger.debug("type of args[0] = %s",type(args[0]))
        logger.debug("Here are kwargs key value pairs")
        for key,value in kwargs.items():
            logger.debug("key=%s value=%s",key,value)
            logger.debug("type of value is %s",type(value))

        """
        UserDetail inherits from class generics.RetrieveAPIView
        and the get method being call on in the below return super(...)
        is in class rest_framework.generics.RetreiveAPIView
        The code for this class is as follows:
        class RetrieveAPIView(mixins.RetrieveModelMixin,
                      GenericAPIView):
            #Concrete view for retrieving a model instance.
            def get(self, request, *args, **kwargs):
                return self.retrieve(request, *args, **kwargs)
        Note that for super in return super(UserDetail, self).get(*args, **kwargs)
        as seen in the last statement of this get method, the request object is passed to 
        super's get method via the args values revealed by logger.debug output produced 
        by the above logger.debug("args =%s",args)
        When the url is https://decidegarbo-quicknina-8000.codio.io/api/v1/users/Rengie899@gmail.com
        is used by Django the output from logger.debug("args =%s",args) is
        arg =(<rest_framework.request.Request: GET '/api/v1/users/Rengie899@gmail.com'>,)
        """
        new_element = "NYJets are losers!"
        new_args = args + (new_element,)
        logger.debug("new_args = %s",new_args)
        x = self.args_checker(*new_args,**kwargs)
        logger.debug("x = %s",x)
        #The user of super below means that we execute the parent's get method 
        return super(UserDetail, self).get(*args, **kwargs)

"""
For TagViewSet and PostViewSet the urls are established by virture of the following lines in
../blog/api/urls.py

from rest_framework.routers import DefaultRouter
...
router = DefaultRouter()
router.register("tags", TagViewSet)
router.register("posts", PostViewSet)
"""
class ExprmntViewSet(viewsets.ModelViewSet):  
    #This does not work, runserver produces the errors:
    #File "/home/codio/workspace/blango/blog/api/urls.py", line 167, in <module>
    #path("", include(router.urls)),
    #File "/home/codio/.local/lib/python3.6/site-packages/rest_framework/routers.py", line 77, in urls
    #self._urls = self.get_urls()
    #File "/home/codio/.local/lib/python3.6/site-packages/rest_framework/routers.py", line 338, in get_urls
    #urls = super().get_urls()
    #File "/home/codio/.local/lib/python3.6/site-packages/rest_framework/routers.py", line 265, in get_urls
    #view = viewset.as_view(mapping, **initkwargs)
    #TypeError: as_view() takes 1 positional argument but 2 were given
    #I was unable to determine why this error occurs; therefore, to keep this error from occuring 
    #in blog.api.urls.py I commented out router.register("exprm", ExprmntViewSet)
    logger.debug("At top of class ExprmntViewSet")
    lookup_field = "email"
    queryset = User.objects.all()
    serializer_class = UserSerializer
    @classonlymethod
    def as_view(cls, **initkwargs):
        logger.debug("in ExprmntViewSet as_view and initkwargs =",initkwargs)
        self = cls(**initkwargs)
        logger.debug("in ExprmntViewSet as_view and self =",self)
        #logger.debug("In blog.api.views.ExprmntViewSet")
        #logger.debug("queryset[0] and queryset[1] are")
        #logger.debug(queryset[0])
        #logger.debug(queryset[1])
        view = super(ExprmntViewSet, cls).as_view(**initkwargs)
        logger.debug("At end of ExprmetViewSet and view =%s",view)


class TagViewSet(viewsets.ModelViewSet):
    # For any ViewSet you must either set queryset and serializer_class,
    # or override `get_queryset()`/`get_serializer_class()`. 
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    
    def dispatch(self, request, *args, **kwargs):
        logger.debug("In blog.api.views.TagViewSet.dispatch")
        logger.debug("This is called by Django using view function returned by django.view.generics.base.View.as_view")
        #For more on view returned by as_view, see sec 2.2 of the google doc "Django and the request object"
        logger.debug("self.__class___.name = %s",self.__class__.__name__ )
        logger.debug("dispatch args = %s",args)
        logger.debug("dispatch kwargs = %s",kwargs)
        resolver_match = request.resolver_match
        logger.debug("resolver_match.view_name = %s",resolver_match.view_name)
        logger.debug("resolver_match.func = %s",resolver_match.func)
        logger.debug("resolver_match.func.actions = %s",resolver_match.func.actions)
        logger.debug("dir of resolver_match.func = %s",dir(resolver_match.func))
        logger.debug("about to execute return super().dispatch(request, *args, **kwargs)")
        return super().dispatch(request, *args, **kwargs)

    @action(methods=["get"], detail=True, name="Posts with the Tag")
    def posts(self, request, pk=None):
        logger.debug("in blog.api.views.TagViewSet.posts and request.META is")
        logger.debug(request.META)
        path = self.request.path
        logger.debug("in blog.api.views.TagViewSet.posts and path is")
        logger.debug(path)
        """
        Here is an example of a url that causes this method to be executed:
        https://decidegarbo-quicknina-8000.codio.io/api/v1/tags/4/posts/
        """
        resolved = resolve(path)
        logger.debug("in blog.api.views.TagViewSet.posts and dir(resolved) is")
        logger.debug(dir(resolved))
        logger.debug("in blog.api.views.TagViewSet.posts and resolved.func =%s",resolved.func)
        logger.debug("in blog.api.views.TagViewSet.posts and resolved.view_name =%s",resolved.view_name)
        logger.debug("in blog.api.views.TagViewSet.posts and dir(resolved.view_name) =%s",dir(resolved.view_name))
        logger.debug("in blog.api.views.TagViewSet.posts and resolved.route =%s",resolved.route)
        url_name = resolved.url_name
        logger.debug("in blog.api.views.TagViewSet.posts and url_name is")
        logger.debug(url_name)
        logger.debug("Inside TagView.posts and pk request and self.request are")
        logger.debug(pk)
        logger.debug(request)
        logger.debug(self.request)
        """ 
        We have access to the pk from the URL, so we could fetch the Tag object
        from the database ourselves. However, the ModelViewSet class provides a
        helper method that will do that for us, get_object(), so we use that
        instead.
        get_object(queryset=None)    
            returns an object or objects that this view will display. 
            If queryset is provided (as is the case above), that queryset will be used as the source of objects; 
            otherwise, get_queryset() will be used.  
        get_queryset()
            Returns the queryset that will be used to retrieve the object that this view will 
            display. By default, get_queryset() returns the value of the queryset attribute 
            if it is set, otherwise it constructs a QuerySet by calling the all() method on 
            the model attributes default manager.  
        Both get_object() and get_queryset() are found in the class generics.GenericAPIView.
        Either or both can be overridden in your viewset if there is a reson to do so.

        The inheritence that reaches class generics.GenericAPIView starts with 
        TagViewSet inheriting from viewsets.ModelViewSet. Here is the inheritence
        path:
        -class TagViewSet inherits from the class viewsets.ModelViewSet
        -in viewsets we see the following code block for ModelViewSet
        class ModelViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):
        -class GenericViewSet inherits from ViewSetMixin and generics.GenericAPIView
         For this discussion generics.GenericAPIView is the relevent class as it contains
         the method get_object.
        -the code for generics.GenericAPIView.get_object() is as follows:

        def get_object(self):
        
            #Returns the object the view is displaying.

            #You may want to override this if you need to provide non-standard
            #queryset lookups.  Eg if objects are referenced using multiple
            #keyword arguments in the url conf.
            queryset = self.filter_queryset(self.get_queryset())

            # Perform the lookup filtering.
            lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

            assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
            )

            filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
            obj = get_object_or_404(queryset, **filter_kwargs)

            # May raise a permission denied
            self.check_object_permissions(self.request, obj)

            return obj 

        Further up in class generics.GenericAPIView there is the method get_queryset.  The
        code for this method is as follows:
          def get_queryset(self):
            #Get the list of items for this view.
            #This must be an iterable, and may be a queryset.
            #Defaults to using `self.queryset`.

            #This method should always be used rather than accessing `self.queryset`
            #directly, as `self.queryset` gets evaluated only once, and those results
            #are cached for all subsequent requests.

            #You may want to override this if you need to provide different
            #querysets depending on the incoming request.

            #(Eg. return a list of items that is specific to the user)

            ###JB comment - further up in class generics.GenericAPIView we see 
            ###queryset = None
            ###serializer_class = None
            ###This is why you will need to either set these attributes in your viewset 
            ###class or in that class override `get_queryset()`and/or`get_serializer_class()`.
            ###For example, in the viewset PostViewSet further down in this python file, we see
            ###that there are overrides for both get_queryset() and get_serializer_class().
            assert self.queryset is not None, (
                "'%s' should either include a `queryset` attribute, "
                "or override the `get_queryset()` method."
                % self.__class__.__name__
            )

            queryset = self.queryset
            if isinstance(queryset, QuerySet):
                # Ensure queryset is re-evaluated on each request.
                queryset = queryset.all()
            return queryset

        """

        tag = self.get_object() 
        logger.debug("type of tag and tag are")
        logger.debug(type(tag))
        logger.debug(tag)
        
        """
        From Discussion Forum for Course 3 Module 1
        'Notice that we have the many to many relationship between Tag and Post model. 
            Jeff B insert comment: this many to many relationship means there can be many
            tags for a given post and many posts for a given tag.
        So in the TagViewSet, inside the posts method at the:
        page =self.paginate_queryset(tag.posts)
        We have to change it to:
        page = self.paginate_queryset(tag.posts.all( ))
        Since tag.posts is not the queryset, it's the manager of a Model which provides
        query operations.

        I hope this experience can help you guys out there. And hopefully the staff is 
        going to alter the code.'
        """
        page = self.paginate_queryset(tag.posts.all())
        #page = self.paginate_queryset(tag.posts) bad code from Course 3 Module1 Guide

        #See JB Note below in class PostViewSet def mine() that describes why it
        #it is necessary to include context={"request": request} in the below
        #instatiations of PostSerializer.
        if page is not None:
            post_serializer = PostSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(post_serializer.data) 
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
        logger.debug("Inside views.TagViewSet.list and request and self.request are")
        try:
            logger.debug(request)
        except:
            logger.debug("request not set; can only use self.request")
        logger.debug(self.request)
        return super(TagViewSet, self).list(*args, **kwargs)

    #@method_decorator(cache_page(300))
    def retrieve(self, *args, **kwargs):
        path = self.request.path
        resolved = resolve(path)
        url_name = resolved.url_name
        logger.debug("in blog.api.views.TagViewSet.retrieve and path=%s and url_name=%s",path,url_name)
        logger.debug("Here are args")
        for arg in args:
            logger.debug("arg = %s",arg)   
        request = arg
        logger.debug("request.path=%s and request.method=%s",request.path,request.method)        
        logger.debug("Here are kwargs")
        for key, value in kwargs.items():
            logger.debug("%s == %s",key, value)
        return super(TagViewSet, self).retrieve(*args, **kwargs)

class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [AuthorModifyOrReadOnly | IsAdminUserForObject]
    """
    permission_classes is used via inheritence.  In  
    rest_framework.generics.GenericAPIView.get_object we see:  
    # May raise a permission denied
    self.check_object_permissions(self.request, obj)
    return obj

    rest_framework.generics.GenericAPIView inherits from 
    rest_framework.views.APIView where the two methods of interest are:

    def get_permissions(self):
      return [permission() for permission in self.permission_classes]

    def check_object_permissions(self,request,obj)
      for permission in self.get_permissions():
        if not permission.has_object_permission(request, self, obj):
          self.permission_denied(
            request, message=getattr(permission, 'message', None)
          )
    Notably it is seen that get_permissions accesses self.permission_classes 
    which is as defined below.  
    AuthorModifyOrReadOnly and IsAdminUserForObject are imported from blog.api.permissions 
    where that contains the following code:

    from rest_framework import permissions

      class AuthorModifyOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
          def has_object_permission(self, request, view, obj):
              if request.method in permissions.SAFE_METHODS:
                  return True

              return request.user == obj.author

      class IsAdminUserForObject(permissions.IsAdminUser):
          def has_object_permission(self, request, view, obj):
              return bool(request.user and request.user.is_staff)

    """
    queryset = Post.objects.all()
    logger.debug("At top of blog.api.views.PostViewSet and queryset is %s",queryset)
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
        logger.debug("at top of blog.api.views.get_serializer_class and self.action is %s",self.action)
        if self.action in ("list", "create"):
            return PostSerializer
        return PostDetailSerializer

    @method_decorator(cache_page(300))
    @method_decorator(vary_on_headers("Authorization"))
    @method_decorator(vary_on_cookie)
    @action(methods=["get"], detail=False, name="Posts by the logged in user")
    #The above @action decorator enables users to enter ../api/v1/posts/mine without the need for
    #there to be a separate viewset, eg: PostMineViewSet, added to this views.py module. 
    #By setting methods=["get"] Django knows that if request.method = GET it should call the 
    #PostViewSet.mine method directly and when it does the serialization is taken care of by
    #mine and it returns a Response object.  This is in contrast to what happens say when 
    #../api/v1/posts or ../api/v1/posts/2/ is entered; when that happens Django executes
    #PostViewSet.as_view and based on the classes inherited by PostViewSet the end result is
    #one the methods in rest_framework.mixins.py gets exectuted unless overriden in in PostViewSet
    #in which case that override metfod gets exectuted.
    #
    def mine(self, request):
        if request.user.is_anonymous:
            raise PermissionDenied("You must be logged in to see which Posts are yours")
        posts = self.get_queryset().filter(author=request.user)

        page = self.paginate_queryset(posts)

        """
        JB Note
        leaving out context={"request": request} in the PostSerializer 
        instatiation below causes the follwoing assertion error. 
        AssertionError: `HyperlinkedRelatedField` requires the request
        in the serializer context. Add `context={'request': request}` 
        when instantiating the serializer.  Its not clear why request
        needs to be provided this way because PostSerializer inherits 
        request via a long inheritence chain.  According to a stackoverflow
        response from Dec, 2015, 'You're getting this error as the
        HyperlinkedIdentityField expects to receive request in context of 
        the serializer so it can build absolute URLs'.  I think this relates
        to the fact that in serializers.PostSerializer there is the following
        statement:
        author = serializers.HyperlinkedRelatedField(
        queryset=User.objects.all(), view_name="api_user_detail", lookup_field="email")
        """

        if page is not None:
            serializer = PostSerializer(page, many=True, context={"request": request})
            #serializer = PostSerializer(page, many=True) 
            return self.get_paginated_response(serializer.data)

        serializer = PostSerializer(posts, many=True, context={"request": request})
        #serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    """
    @method_decorator(cache_page(120))
    def list(self, *args, **kwargs):
        return super(PostViewSet, self).list(*args, **kwargs)
    """

    @method_decorator(cache_page(120))
    @method_decorator(vary_on_headers("Authorization", "Cookie"))
    def list(self, *args, **kwargs):
        logger.debug("in views.PostViewSet.list about to call super(PostViewSet,self).list")
        logger.debug("super(PostViewSet,self) is viewsets.ModelViewSet")
        return super(PostViewSet, self).list(*args, **kwargs) #super is viewsets.ModelViewSet which for the list method relies                                                              #relies on the list method in class rest_framework.mixins.ListModelMixin
                                                              #on the list method in class rest_framework.mixins.ListModelMixin.
                                                              #See the code for class rest_framework.mixins.ModelViewSet.
                                                              #A usefuel doc is:
                                                              #https://www.cdrf.co/3.1/rest_framework.viewsets/ModelViewSet.html
                                                              #