# Create your views here.
from models import Post,Comment,CommentForm
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext

def index(req):
    posts = Post.objects.all()
    return render_to_response('index.html',{'posts':posts},RequestContext(req))

def post(req,post_id):
    
    
    is_ajax = req.GET.has_key('xhr')
    
    post = Post.objects.get(pk=post_id)

    if req.method == 'POST':
        comment_form = CommentForm(req.POST)
        comment = comment_form.save(commit=False)
        comment.post = post
        comment.save()
        
    payload = {'post':post,
               'comments':Comment.objects.filter(post__id=post_id),
               'comment_form':CommentForm()}
                              
    return render_to_response('post.html',payload, RequestContext(req))    

    