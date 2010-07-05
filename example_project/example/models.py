from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Post(models.Model):
    author = models.ForeignKey(User)
    date = models.DateTimeField()
    title = models.CharField(max_length=100)
    post = models.TextField()

    def __unicode__(self):
        return  self.title
