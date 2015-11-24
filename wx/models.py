from django.db import models

# Create your models here.

class Poll(models.Model):
    name = models.CharField(max_length=256)
    votes = models.IntegerField(default=0)

class Choice(models.Model):
    user_id = models.CharField(max_length=256)
    poll = models.ForeignKey(Poll)
    date = models.DateTimeField()
