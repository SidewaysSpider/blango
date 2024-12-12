from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from blog.models import Post
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from blog.forms import CommentForm
from django.views.decorators.cache import cache_page
import logging

from django.urls import reverse

logger = logging.getLogger(__name__)

# Create your views here.

@cache_page(300)
def index(request):
    #return render(request, "blog/index.html")
    #Below return HttpResponseRedirect("/ip/") was temporary to enable
    #access to get_ip to get new view to return the IP address that’s 
    #connected to Django in codio.  This is so we can add the 
    #INTERNAL_IPS setting to settings.py in order to get the Django
    #Debug Toolbar (DjDT) to work.  See Module3 Database Optimization 
    #Installing & Configuring Django Debug Toolbar for more on this. 
    #return HttpResponseRedirect("/ip/")
    #posts = Post.objects.filter(published_at__lte=timezone.now())
    posts = Post.objects.filter(published_at__lte=timezone.now()).select_related("author")
    logger.debug("Got %d posts", len(posts))
    return render(request, "blog/index.html", {"posts": posts})


def get_ip(request):
  from django.http import HttpResponse
  return HttpResponse(request.META['REMOTE_ADDR'])

def post_table(request):
    #the logger.debug output should indicate that
    #reverse("post-list") is the string /api/v1/posts/
    logger.debug("reverse of post-list is %s",reverse("post-list") )
    #return render(request, "blog/post-table.html")
    return render(
        request, "blog/post-table.html", {"post_list_url": reverse("post-list")}
    )

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    logger.debug("request user is_active is %r", request.user.is_active)
    if request.user.is_active or not request.user.is_active:
        logger.debug("request.method %s", request.method)
        if request.method == "POST":
            comment_form = CommentForm(request.POST)

            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                logger.debug("comment from comment_form.save is %s", comment)
                comment.content_object = post
                comment.creator = request.user
                comment.save()
                return redirect(request.path_info)
        else:
            comment_form = CommentForm()
    else:
        comment_form = None
    #return render(request, "blog/post-detail.html", {"post": post})
    return render(
        request, "blog/post-detail.html", {"post": post, "comment_form": comment_form}
    )
