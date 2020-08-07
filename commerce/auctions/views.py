from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db import IntegrityError
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
    """Index"""
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
    model = Listing
    form_class = CreateBidForm
    initial = {'bid_amount': 'Bid'}
    success_url = 'auctions/listing_detail'
    success_message = 'Your bid was placed successfully'

    def get_success_url(self):
        return reverse('listing_detail', kwargs={'pk': self.object.pk})

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()

        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(ListingDetail, self).get_context_data(**kwargs)
        context['bid'] = Bid.objects.filter(listing=self.object).order_by('bid_amount')
        context['form'] = CreateBidForm()
        return context

    def form_valid(self, form):
        # starting_bid = Listing.objects.get(id=self.pk).starting_bid
        # number_of_bids = Listing.objects.get(id=self.pk).bids_number
        form.instance.listing = self.object
        form.instance.user = self.request.user
        form.save()
        return redirect(self.get_success_url())



"""
Another (alternative better solution) for ListingView to handle get and post
"""

# class ListingDisplay(DetailView):
#     model = Listing
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['form'] = CreateBidForm()
#         return context
#
#
# class ListingInterest(SingleObjectMixin, FormView):
#     template_name = 'auctions/listing_detail.html'
#     form_class = CreateBidForm
#     model = Bid
#     success_message = 'Your bid was placed successfully'
#
#     def post(self, request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return HttpResponseForbidden()
#         self.object = self.get_object()
#         return super().post(request, *args, **kwargs)
#
#     def get_success_url(self):
#         return reverse('listing-detail', kwargs={'pk': self.object.pk})
#
#
# class ListingDetail(View):
#
#     def get(self, request, *args, **kwargs):
#         view = ListingDisplay.as_view()
#         return view(request, *args, **kwargs)
#
#     def post(self, request, *args, **kwargs):
#         view = ListingInterest.as_view()
#         return view(request, *args, **kwargs)
