from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    def __str__(self):
        return f'{self.username} ({self.email})'


class Listing(models.Model):
    """ Auction listings"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usr_listings")
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=160)
    starting_bid = models.IntegerField()
    img_url = models.URLField("Image URL", max_length=200, blank=True)
    category = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return f'{self.title} starts with {self.starting_bid}(category{self.category})'


class Bid(models.Model):
    """ Bids made on auction listings"""
    pass


class Comment(models.Model):
    """Comments made on auction listings"""
    pass

