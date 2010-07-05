from django.db import models

class Comment(models.Model):
    comment = models.TextField()
