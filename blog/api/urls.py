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
We see that per the 1st of the two router.register commands below, perfix would be received by def register as "tags"
and viewset would be received as TagViewSet.  For the 2nd of the two router.register commands below, prefix would
be received by def register as "posts" and viewset would be received as PostViewSet.
"""
router = DefaultRouter()
router.register("tags", TagViewSet)
router.register("posts", PostViewSet) #per this router register, for HTTP Method=GET, url='/posts/'	Action=list  URL Name=post-list
                                      #and for HTTP Method=POST, url=/posts/  Action=create  URL Name=post-list
                                      #and the Viewset that is identifed to be accessed is PostViewSet which per the
                                      #above import is in blog.api.views.
                                      #reverse of post-list is /api/v1/posts/ because in blango/urls.py
                                      #one of the paths is path("api/v1/", include("blog.api.urls")),
                                      #and below we have urlpatterns += [path("", include(router.urls)),] which causes 
                                      #the ending of the url for accessing PostViewSet to be /api/v1/posts/ 
                                      #For example, the codio url produced by router.register("posts", PostViewSet) would 
                                      #something like the following:
                                      #https://bondobros-meetwithfox-8000.codio.io/api/v1/posts/
                                      #and this would cause invocation of PostViewSet in blog/api/views.py.
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

