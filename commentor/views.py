from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from commentor.models import Comment
from django.template import RequestContext
from django import forms
from django.shortcuts import render_to_response

@login_required
def leave_comment(request):
    form = CommentForm()
    if request.POST:
        form = CommentForm(data = request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('.')
        
    payload = {'form':form, 'comments':Comment.objects.all()}
    return render_to_response('commentor/index.html', payload, RequestContext(request))
    
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment