from django.db import models
from django.forms import ModelForm

from djangoratings.fields import RatingField

class Post(models.Model):
    title = models.CharField(max_length=100)
    text = models.TextField()
    datetime = models.DateTimeField()

    rating = RatingField(range=5) # 5 possible rating values, 1-5
    
    class Meta():
        ordering = ('-datetime',)

    def __unicode__(self):
        return self.title
        
class Comment(models.Model):
    post = models.ForeignKey(Post)
    text = models.TextField()
    
    def __unicode__(self):
        return self.text
    
class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
