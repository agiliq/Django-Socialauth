# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.comments.models import Comment
from models import Post
from django.template import RequestContext

def comment_posted(request):
    comment_id = request.GET['c']
    post_id = Comment.objects.get(id=comment_id).content_object.id
    return HttpResponseRedirect('/blog/'+str(post_id))

def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    return render_to_response('example/post_detail.html', {'post': post}, context_instance=RequestContext(request))
