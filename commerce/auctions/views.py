from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import F
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, CreateView, DetailView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormMixin
from django.urls import reverse

from .models import User, Listing, Bid
from .forms import CreateBidForm


class ListingAllView(ListView):
    """Index page"""
    model = Listing


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            # return HttpResponseRedirect(reverse("index"))
            return redirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    # return HttpResponseRedirect(reverse("index"))
    return redirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords don't match"
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


class ListingCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Handle new listings creation"""
    model = Listing
    fields = ['title', 'description', 'starting_bid', 'img_url', 'category']
    success_message = 'Listing was created successfully'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ListingDetail(FormMixin, SuccessMessageMixin, DetailView):
    """
    Handles listing view by get request
    Handles Bid processing & validation on post request
    """
    model = Listing
    form_class = CreateBidForm
    initial = {'bid_amount': 'Bid'}

    def get_success_url(self):
        return reverse('listing_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super(ListingDetail, self).get_context_data(**kwargs)
        context['form'] = CreateBidForm()
        try:
            context['bid_amount'] = Bid.objects.filter(listing=self.object.pk)[0].bid_amount
        except IndexError:
            context['bid_amount'] = 0
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        """
        In this method, form is being validated against:
        1) whether bid user trying to place is greater than an existing one
        2) whether user that is trying to place a bid is the listing owner
        3) whether user already has bids on this listing, then trying to update his existing bid
        if form was validated, new bid is being created
        """
        instance = form.save(commit=False)
        starting_bid = self.object.starting_bid

        if instance.bid_amount <= starting_bid:
            messages.error(self.request, 'Bid amount must be greater than starting bid')
            return redirect(reverse('listing_detail', kwargs={'pk': self.object.pk}))
        elif self.request.user == self.object.user:
            messages.error(self.request, 'Owner cannot place bids')
            return redirect(reverse('listing_detail', kwargs={'pk': self.object.pk}))
        elif self.object.bids_number > 0:
            try:
                existing_bid = Bid.objects.get(listing=self.object.pk, user=self.request.user)
                if existing_bid.bid_amount > instance.bid_amount:
                    messages.error(self.request, 'The bid you are trying to place is lower than existing one')
                    return redirect(reverse('listing_detail', kwargs={'pk': self.object.pk}))
                existing_bid.bid_amount = instance.bid_amount
                existing_bid.save()
                messages.success(self.request, 'Your bid was updated')
                return redirect(reverse('listing_detail', kwargs={'pk': self.object.pk}))
            except ObjectDoesNotExist:
                pass

        Listing.objects.filter(id=self.object.pk).update(bids_number=F('bids_number') + 1)
        instance.listing = self.object
        instance.user = self.request.user
        form.save()
        messages.success(self.request, 'Bid was registered successfully')
        return redirect(self.get_success_url())
