from rest_framework import serializers
from blog.models import Post, Tag
from blango_auth.models import User
import logging
logger = logging.getLogger(__name__)

class PostSerializer(serializers.ModelSerializer):
    #tags and author are defined so that when the blog.api.views.PostList.as_view()  
    #and blog.api.views.PostDetail.as_view() methods are exectuted what is returned is
    #are meaningful values rather than just the primary keys.  For example, if tags
    #wasn't defined as below, the tags field in the output permission_classes
    #per https://blah-8000.codio.io/api/v1/posts/1
    #would be:
    #"tags": [1]
    #rather than 
    #"tags": ["Bondos"]

    tags = serializers.SlugRelatedField(
        slug_field="value", many=True, queryset=Tag.objects.all()
    )
    
    author = serializers.HyperlinkedRelatedField(
        queryset=User.objects.all(), view_name="api_user_detail", lookup_field="email"
    )
    logger.debug("type of tags is %s",type(tags))
    logger.debug(dir(tags))
    logger.debug("type of author is %s",type(author))
    logger.debug(dir(author))
    class Meta:
        model = Post
        fields = "__all__"
        readonly = ["modified_at", "created_at"]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

