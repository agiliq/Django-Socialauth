from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.comments.forms import CommentDetailsForm

class CommentForm(CommentDetailsForm):
    name          = forms.CharField(widget=forms.HiddenInput, required=False)
    email         = forms.EmailField(widget=forms.HiddenInput, required=False)
    url           = forms.URLField(widget=forms.HiddenInput, required=False)


def get_form():
    return CommentForm
