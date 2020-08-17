from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
from django.shortcuts import redirect
from django.urls import reverse
from .models import Listing, Bid, Watchlist


def form_valid_bid(self, form):
    """
    In this method, the form is being validated against:
    1) whether bid user trying to place is greater than an existing one
    2) whether the user that is trying to place a bid is the listing owner
    3) whether the user already has bid on this listing, then trying to update his existing bid
    if the form was validated, new bid is being created
    """
    instance = form.save(commit=False)

    if 'bid_amount' in form.cleaned_data:
        starting_bid = self.object.starting_bid

        if instance.bid_amount <= starting_bid:
            messages.error(self.request, 'Bid amount must be greater than starting bid')
            return redirect(reverse('listing_detail', kwargs={'pk': self.object.pk}))
        elif self.request.user == self.object.user:
            messages.error(self.request, 'Owner cannot place bids')
            return redirect(self.get_success_url())
        elif self.object.bids_number > 0:
            try:
                existing_bid = Bid.objects.get(listing=self.object.pk, user=self.request.user)
                if existing_bid.bid_amount >= instance.bid_amount:
                    messages.error(self.request, 'The bid you are trying to place is lower than existing one')
                    return redirect(self.get_success_url())
                existing_bid.bid_amount = instance.bid_amount
                existing_bid.save()
                messages.success(self.request, 'Bid was updated')
                return redirect(self.get_success_url())
            except ObjectDoesNotExist:
                pass

        Listing.objects.filter(id=self.object.pk).update(bids_number=F('bids_number') + 1)
        instance.listing = self.object
        instance.user = self.request.user
        instance.save()
        messages.success(self.request, 'Bid was registered successfully')
        return redirect(self.get_success_url())


def form_valid_watchlist(self, form):
    instance = form.save(commit=False)
    if len(Watchlist.objects.filter(listing=self.object, user=self.request.user)) != 0:
        messages.info(self.request, 'Already in watchlist')
        return redirect(self.get_success_url())
    instance.user = self.request.user
    instance.listing = self.object
    instance.save()
    messages.success(self.request, 'Added to watchlist')
    return redirect(self.get_success_url())


def form_valid_comment(self, form):
    instance = form.save(commit=False)
    instance.user = self.request.user
    instance.listing = self.object
    instance.save()
    messages.success(self.request, 'Comment posted!')
    return redirect(self.get_success_url())


def form_valid_closing(self, form):
    try:
        Listing.objects.filter(id=self.object.pk).update(
            winner=Bid.objects.filter(listing=self.object).first().user,
            closed=True
        )
    except AttributeError:
        messages.error(self.request, 'Cannot close auction: 0 bids')
        return redirect(self.get_success_url())
    messages.success(self.request, 'Auction closed')
    return redirect(self.get_success_url())
