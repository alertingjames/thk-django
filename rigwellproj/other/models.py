from django.db import models

# Create your models here.

class Member(models.Model):
    name=models.CharField(max_length=50)
    email=models.CharField(max_length=200)
    password=models.CharField(max_length=100)

class Bid(models.Model):
    user_id = models.CharField(max_length=11)
    folder_id = models.CharField(max_length=11)
    caption = models.CharField(max_length=100)
    text = models.CharField(max_length=5000)

class BidFolder(models.Model):
    user_id = models.CharField(max_length=11)
    name = models.CharField(max_length=50)

class Folder(models.Model):
    user_id = models.CharField(max_length=11)
    name = models.CharField(max_length=50)
    files = models.CharField(max_length=11)

class File(models.Model):
    folder_id = models.CharField(max_length=11)
    name = models.CharField(max_length=50)
    link = models.CharField(max_length=1000)

class Note(models.Model):
    user_id = models.CharField(max_length=11)
    caption = models.CharField(max_length=100)
    text = models.CharField(max_length=5000)

class NowBid(models.Model):
    user_id = models.CharField(max_length=11)
    text = models.CharField(max_length=5000)













































