from django.db import models

# Create your models here.

class Poll(models.Model):
    name = models.CharField(max_length=256)
    votes = models.IntegerField(default=0)

class Choice(models.Model):
    poll = models.ForeignKey(Poll)
    date = models.DateTimeField()


