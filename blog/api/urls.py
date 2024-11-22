from django.urls import path, include, re_path
import rest_framework
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
import os

#from blog.api.views import PostList, PostDetail, UserDetail
from blog.api.views import PostList, PostDetail, UserDetail, TagViewSet
from blog.api.views import PostViewSet
"""
A DRF Router will inspect a viewset and determine what endpoints it has available,
then create the right URL patterns automatically. Usually you will want to use the
rest_framework.routers.DefaultRouter class.  This class inherits from the SimpleRouter class 
which in turn inherits from the BaseRouter class. The register method is a BaseRouter method.
The code for this method is:
    def register(self, prefix, viewset, basename=None):
        if basename is None:
            basename = self.get_default_basename(viewset)
        self.registry.append((prefix, viewset, basename))

        # invalidate the urls cache
        if hasattr(self, '_urls'):
            del self._urls
We see that per the 1st of the two router.register calls below, prefix would be received as "tags" and
viewset would be received as TagViewSet.  For the 2nd of the two router.register commands below, prefix would be received
as "posts" and viewset would be received as PostViewSet.  basename is is not specified in either of the below two
router.register calls so it is by default determined in the method get_default_basename(self, viewset) which is in class
SimpleRouter(BaseRouter) in rest_framework.routers.py.  The DefaultRouter class (also in rest_framework.routers.py) inherits
form class SimpleRouter.  In get_default_basename(self, viewset) we see basename = queryset.model._meta.object_name.lower()
which means it is set equal to the value _meta.object_name for the identified in queryset object.  In the case of
viewset = PostViewSet, we see queryset=Post.objects.all() in class PostViewSet (found in ../blog/api/veiws.py); this queryset object
includes the object named model which enables model._meta.object._name.lower() to be executed.  We can surmise that this
results in basename being set to post.  So, for router.register("posts", PostViewSet), we see that 
self.registry.append((prefix, viewset, basename) would result in the list ("posts",PostViewSet,"post").  We can further
surmise that the URL Name is set to "post" + "-" + str(Action). So for example, for /api/v1/posts/ URL Name would be set 
to "post-list".   The value for Action for any request going to blog.api.views.PostViewSet is output by logger.debug in
the PostViewSet get_queryset method. 
"""
router = DefaultRouter()
router.register("tags", TagViewSet)
router.register("posts", PostViewSet) #per this router register, 
                                      #for HTTP GET /api/v1/posts/, url='/posts/' Action=list  URL Name=post-list
                                      #for HTTP GET /api/v1/posts/1/ url='/posts/1/' Action=Retrieve  URL Name=post-detail
                                      #where 1 is an example of a pk value.
                                      #for HTTP POST /api/v1/posts/, url='/posts/' Action=create  URL Name=post-list
                                      #For HTTP PUT /api/v1/posts/1/, url='/posts/1/' Action=update URL Name=post-detail
                                      #mine is a special method in PostViewSet.  The relevant HTTP request is
                                      #GET /api/v1/posts/mine/ with url='posts/mine/'  Action=list  URL Name=post-mine
                                      #and the Viewset that is identifed to be accessed is PostViewSet which per the
                                      #above import is in blog.api.views.
                                      #So, for example, reverse of post-list is /api/v1/posts/ because in blango/urls.py
                                      #one of the paths is path("api/v1/", include("blog.api.urls")),
                                      #and below we have urlpatterns += [path("", include(router.urls)),] which causes 
                                      #the ending of the url for accessing PostViewSet to be /api/v1/posts/ 
                                      #Thus, the codio url produced by router.register("posts", PostViewSet) would be
                                      #something like the following:
                                      #https://bondobros-meetwithfox-8000.codio.io/api/v1/posts/
                                      #For HTTP GET /api/v1/posts/, the list method in PostViewSet would be invoked.
                                      #For HTTP POST /api/v1/posts/, the default create method in viewsets.ModelViewSet
                                      #would be invoked as viewsets.ModelViewSet is inherited by PostViewSet.
                                      #For HTTP PUT /api/v1/posts/1/, the default update method in viewsets.ModelViewSet would be invoked.
                                      #
                                      #Likewise, the codio url produced by router.register("posts", TagViewSet) would be
                                      #https://bondobros-meetwithfox-8000.codio.io/api/v1/tages/
                                      #for HTTP GET /api/v1/tags/, url='/tags/' Action=list  URL Name=tag-list
                                      #for HTTP GET /api/v1/tagss/1/ url='/tags/1/' Action=Retrieve  URL Name=tag-list
                                      #for HTTP POST /api/v1/posts/, url='/posts/' Action=create  URL Name=tag-list
                                      #For HTTP PUT /api/v1/posts/1/, url='/posts/1/' Action=update URL Name=tag-list
                                      #
                                      #For more on this topic, see https://www.django-rest-framework.org/api-guide/routers/#defaultrouter
                                      #In particular scroll down to 'Using Routers', where it states that
                                      #"Because we're using ViewSet classes rather than View classes, we actually don't need to
                                      #design the URL conf ourselves. The conventions for wiring up resources into views and urls 
                                      #can be handled automatically, using a Router class (such as above DefaultRoute()). All we  
                                      #need to do is register the appropriate view sets with a router, and let it do the rest. ..."

schema_view = get_schema_view(
    openapi.Info(
        title="Blango API",
        default_version="v1",
        description="API for Blango Blog",
    ),
    url=f"https://{os.environ.get('CODIO_HOSTNAME')}-8000.codio.io/api/v1/",
    public=True,
)

urlpatterns = [
    #path("posts/", PostList.as_view(), name="api_post_list"),
    #path("posts/<int:pk>", PostDetail.as_view(), name="api_post_detail"),
    path("users/<str:email>", UserDetail.as_view(), name="api_user_detail"),
]

urlpatterns = format_suffix_patterns(urlpatterns)

urlpatterns += [
    path("auth/", include("rest_framework.urls")),
    path("token-auth/", views.obtain_auth_token),
    path("jwt/", TokenObtainPairView.as_view(), name="jwt_obtain_pair"),
    path("jwt/refresh/", TokenRefreshView.as_view(), name="jwt_refresh"),
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
]

urlpatterns += [
    path("", include(router.urls)),
]

urlpatterns += [    
    path(
       "posts/by-time/<str:period_name>/",
        PostViewSet.as_view({"get": "list"}),
        name="posts-by-time",
    ),
 ]

