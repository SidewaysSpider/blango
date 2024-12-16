from rest_framework import serializers
from blog.models import Post, Tag, Comment
from blango_auth.models import User
from versatileimagefield.serializers import VersatileImageFieldSerializer
import datetime
import logging
logger = logging.getLogger(__name__)

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

class CommentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    creator = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "creator", "content", "modified_at", "created_at"]
        readonly = ["modified_at", "created_at"]

class TagField(serializers.SlugRelatedField):
    def to_internal_value(self, data):
        try:
            return self.get_queryset().get_or_create(value=data.lower())[0]
        except (TypeError, ValueError):
            self.fail(f"Tag value {data} is invalid")

class PostSerializer(serializers.ModelSerializer):
    #tags and author are defined so that when the blog.api.views.PostList.as_view()  
    #and blog.api.views.PostDetail.as_view() methods are exectuted what is returned 
    #are meaningful values rather than just the primary keys.  For example, if tags
    #wasn't defined as below, the tags field in the output permission_classes
    #per https://blah-8000.codio.io/api/v1/posts/1
    #would be:
    #"tags": [1]
    #rather than 
    #"tags": ["Bondos"]

    """
    from an earlier version
    tags = serializers.SlugRelatedField(
        slug_field="value", many=True, queryset=Tag.objects.all()
    )
    """
    
    tags = TagField(
        slug_field="value", many=True,
        queryset=Tag.objects.all()
   )

    hero_image = VersatileImageFieldSerializer(
        sizes=[
            ("full_size", "url"),
            ("thumbnail", "thumbnail__100x100"),
        ],
        read_only=True,
    )

    author = serializers.HyperlinkedRelatedField(
        queryset=User.objects.all(), view_name="api_user_detail", lookup_field="email"
    )
    logger.debug("in serializers.py class PostSerializer and type of tags is %s",type(tags))
    #logger.debug(dir(tags))
    logger.debug("in serializers.py class PostSerializer and author is %s",author)
    #logger.debug(dir(author))
    class Meta:
        model = Post
        #fields = "__all__"
        #The following line causes exclusion only of the ppoi field in the 
        #serialization
        exclude = ["ppoi"]
        readonly = ["modified_at", "created_at"]

"""
class TagField(serializers.SlugRelatedField):
    def to_internal_value(self, data):
        try:
            return self.get_queryset().get_or_create(value=data.lower())[0]
        except (TypeError, ValueError):
            self.fail(f"Tag value {data} is invalid")
"""

class PostDetailSerializer(PostSerializer):
    comments = CommentSerializer(many=True)
    hero_image = VersatileImageFieldSerializer(
        sizes=[
            ("full_size", "url"),
            ("thumbnail", "thumbnail__100x100"),
            ("square_crop", "crop__200x200"),
        ],
        read_only=True,
    )
    
    def update(self, instance, validated_data):
        logger.debug("in serializers.PostDetailSerializer.update validated_data is")
        logger.debug(validated_data)
        comments = validated_data.pop("comments")
        logger.debug("in serializers.PostDetailSerializer.update comments is")
        logger.debug(comments)
        logger.debug("instance is %s",instance)
        logger.debug("instance.comments is %s",instance.comments)    
        #logger.debug("dir of instance.comments is %s",dir(instance.comments))   
        #logger.debug("instance.comments.get(created_at) is %s",instance.comments.get("created_at"))  
        #The following updates the post    
        instance = super(PostDetailSerializer, self).update(instance, validated_data)
        logger.debug("in serializers.PostDetailSerializer.update self.context['requests'].user is")
        logger.debug(self.context["request"].user)
        #The following updates the comments
        for comment_data in comments:
            logging.debug("comment_data.get id")
            logging.debug(comment_data.get("id"))
            logger.debug("comment_data.get(content) is %s",comment_data.get("content"))
            logger.debug("comment_data.get(created_at) is %s",comment_data.get("created_at"))
            
            #comment = Comment.objects.get(id=comment_data.get("id"))
            #logger.debug("comment.created_at is %s",comment.created_at)
            
            #This if block has to be commented out in order to be able to update a comment.
            if comment_data.get("id"):
                # comment has an ID so was pre-existing
                # so only allow editing and only if comment.creator = self.context["request"].user
                comment = Comment.objects.get(id=comment_data.get("id"))
                logger.debug("comment.creator is %s",comment.creator)
                logger.debug("user is %s",self.context["request"].user)
                if comment.creator == self.context["request"].user:
                  comment.content = comment_data.get("content")
                  logger.debug("comment.content is %s",comment.content)
                comment.save()
                continue
            
            logger.debug("Ongoing")
            #comment_data only has validated data which is just the id and content fields
            #so we need to use comment as per comment = Comment.objects.get(id=comment_data.get("id"))
            #above otherwise comment.save() below will fail because comment.created_at would be Null
            comment = Comment(**comment_data)  
            comment.creator = self.context["request"].user
            #comment.creator = self.request.user  won't work
            logger.debug("comment.content is %s",comment.content)
            logger.debug("Here comes Broker")
            comment.content_object = instance
            logger.debug("Broker is a skunk not a stock broker")
            logger.debug("comment.content_object is %s",comment.content_object)
            comment.save()

        return instance