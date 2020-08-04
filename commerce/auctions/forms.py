from django import forms
from .models import Listing


class CreateListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ('title', 'description', 'starting_bid', 'img_url', 'category')
