# Create your views here.

from django.contrib.auth.decorators import login_required
from django.contrib.comments.views.comments import post_comment as old_post_comment

@login_required
def post_comment(request):
        return old_post_comment(request)
