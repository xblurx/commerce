from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils import timezone


class User(AbstractUser):
    def __str__(self):
        return f'{self.username} ({self.email})'


class Listing(models.Model):
    """Auction listing"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usr_listings")
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=160)
    starting_bid = models.PositiveIntegerField()
    bids_number = models.PositiveIntegerField(default=1)
    img_url = models.URLField("Image URL", max_length=200, blank=True)
    category = models.CharField(max_length=64, blank=True)
    date_listed = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'auction_listing'
        ordering = ['-date_listed']

    def __str__(self):
        return f'{self.title} starts with {self.starting_bid} (category{self.category})'

    def get_absolute_url(self):
        print('loading... get_absolute_url')
        return reverse('listing_detail', kwargs={'pk': self.pk})


class Bid(models.Model):
    """Bids made on auction listing"""
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_bids")
    bid_amount = models.PositiveIntegerField(default=None)

    class Meta:
        verbose_name = 'Bid'

    def __str__(self):
        return f'Bid {self.bid_amount} by {self.user} on {self.listing}'


class Comment(models.Model):
    """Comments made on auction listing"""
    pass
