from django import forms
from .models import Listing, Bid


class CreateListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ('title', 'description', 'starting_bid', 'img_url', 'category')


class CreateBidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ('bid_amount',)
