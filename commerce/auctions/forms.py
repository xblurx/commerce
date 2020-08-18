from django import forms

from .models import Listing, Bid, Watchlist, Comment


class CreateListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ('title', 'description', 'starting_bid', 'img_url', 'category')


class PlaceBidForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bid_amount'].widget.attrs.update({'placeholder': 'Bid'})

    bid_amount = forms.IntegerField(label="")

    class Meta:
        model = Bid
        fields = ('bid_amount',)


class AddToWatchlistForm(forms.ModelForm):
    class Meta:
        model = Watchlist
        fields = ('user', 'listing')
        widgets = {'user': forms.HiddenInput(), 'listing': forms.HiddenInput()}

    def __str__(self):
        return f'{self.user.username}, {self.listing.title}'


class CommentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs.update({'placeholder': 'Your comment'})

    class Meta:
        model = Comment
        fields = ('text', 'user', 'listing',)
        widgets = {'user': forms.HiddenInput(), 'listing': forms.HiddenInput()}
        labels = {'text': 'Write a comment'}

    def __str__(self):
        return f'{self.user} on {self.listing}'


class CloseAuctionForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ('closed',)
        widget = {'closed': forms.HiddenInput()}

    def __str__(self):
        return f'{self.title} is closed({self.closed})'
