from django.db import models
from django.utils import timezone

from datetime import datetime
# Create your models here.

class Master(models.Model):
    def __str__(self):
        return self.title
    manufucturer = models.CharField(max_length=256)
    jan = models.CharField(max_length=256)
    mpn = models.CharField(max_length=256)
    title = models.CharField(max_length=256)
    category = models.CharField(max_length=256)
    subcategory = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Pos(models.Model):
    def __str__(self):
        return self.jan
    jan = models.CharField(max_length=256)
    datetime = models.DateTimeField(auto_now_add=True)
    price = models.IntegerField(default=0)
    sales = models.IntegerField(default=0)
    amount = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class SeasonalTrend(models.Model):
    def __str__(self):
        return self.subcategory
    subcategory = models.CharField(max_length=256)
    datetime = models.DateTimeField(auto_now_add=True)
    sales = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
