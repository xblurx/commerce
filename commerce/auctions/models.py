from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone


class User(AbstractUser):
    def __str__(self):
        return self.username


class Listing(models.Model):
    """Auction listing"""
    user = models.ForeignKey(User, verbose_name='user owner', on_delete=models.CASCADE, related_name="usr_listings")
    winner = models.ForeignKey(User, verbose_name='listing_winner', blank=True, null=True, on_delete=models.CASCADE, related_name='winner')
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=160)
    starting_bid = models.PositiveIntegerField()
    bids_number = models.PositiveIntegerField(default=0)
    img_url = models.URLField("Image URL", max_length=200, blank=True)
    category = models.CharField(max_length=64, blank=True)
    date_listed = models.DateTimeField(default=timezone.now)
    closed = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'auction listing'
        ordering = ['-date_listed']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        print('loading... get_absolute_url')
        return reverse('listing_detail', kwargs={'pk': self.pk})


class Bid(models.Model):
    """Bids made on auction listing"""
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_bidder")
    bid_amount = models.PositiveIntegerField(default=None)

    class Meta:
        verbose_name = 'Bid'
        ordering = ['-bid_amount']

    def __str__(self):
        return f'{self.bid_amount} by {self.user} on {self.listing}'


class Comment(models.Model):
    """Comments made on auction listing"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comments')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='listing_comments')
    text = models.TextField(max_length=160)
    date_posted = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date_posted']

    def __str__(self):
        return f'by {self.user} on {self.listing}'


class Watchlist(models.Model):
    """Items on user's watchlist"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_wanted")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watchlist_items")

    class Meta:
        verbose_name = 'watchlist'

    def __str__(self):
        return f'{self.user}, {self.listing}'
