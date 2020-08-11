from django import forms
from .models import Listing, Bid


class CreateListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ('title', 'description', 'starting_bid', 'img_url', 'category')


class CreateBidForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bid_amount'].widget.attrs.update({'placeholder': 'Bid'})

    bid_amount = forms.IntegerField(label="")

    class Meta:
        model = Bid
        fields = ('bid_amount',)

