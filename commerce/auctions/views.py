from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.views.generic import View
from django.views.generic import ListView, CreateView, DetailView
from django.views.generic.edit import FormMixin
from django.urls import reverse

from .models import User, Listing, Bid, Watchlist, Comment
from .forms import PlaceBidForm, AddToWatchlistForm, CommentForm, CloseAuctionForm
from .form_validation import form_valid_bid, form_valid_watchlist, form_valid_comment, form_valid_closing


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
    form_class = PlaceBidForm
    form_class_2 = AddToWatchlistForm
    form_class_3 = CommentForm
    form_class_4 = CloseAuctionForm

    def get_success_url(self):
        return reverse('listing_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super(ListingDetail, self).get_context_data(**kwargs)
        # print(f'context: {context}\n')
        context['bid_form'] = PlaceBidForm()
        context['watchlist_form'] = AddToWatchlistForm(initial={
            'user': self.request.user,
            'listing': self.object
        })
        context['close_auction'] = CloseAuctionForm(initial={
            'closed': True
        })
        context['comment_form'] = CommentForm(initial={
            'user': self.request.user,
            'listing': self.object
        })
        try:
            context['comments'] = Comment.objects.filter(listing=self.object)
        except:
            print('\nviews.py line 119 exception\n')
            pass

        try:
            Watchlist.objects.get(
                user=self.request.user,
                listing=self.object)
            context['watchlist'] = True
        except:
            pass

        try:
            context['bid_amount'] = Bid.objects.filter(listing=self.object.pk)[0].bid_amount
        except IndexError:
            context['bid_amount'] = 0
        return context

    def post(self, request, *args, **kwargs):
        print(f'\nrequest.POST: {request.POST}\n\n')
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        self.object = self.get_object()

        if 'bid_form' in request.POST:
            form_class = self.get_form_class()
        elif 'watchlist_form' in request.POST:
            form_class = self.form_class_2
        elif 'close_auction' in request.POST:
            form_class = self.form_class_4
        else:
            form_class = self.form_class_3

        form = self.get_form(form_class)
        if form.is_valid():
            print('\nForm is valid.\n')
            return self.form_valid(form)
        else:
            print(f'Form is invalid. {form.errors}')
            return self.form_invalid(form)

    def form_valid(self, form):
        print(f'\ncleaned data: {form.cleaned_data}\n')
        if 'bid_amount' in form.cleaned_data:
            return form_valid_bid(self, form)
        elif 'text' in form.cleaned_data:
            return form_valid_comment(self, form)
        elif 'closed' in form.cleaned_data:
            return form_valid_closing(self, form)
        else:
            return form_valid_watchlist(self, form)


class WatchlistView(ListView):
    model = Watchlist

    def get_context_data(self, **kwargs):
        context = super(WatchlistView, self).get_context_data(**kwargs)
        context['object_list'] = Watchlist.objects.filter(user=self.request.user)
        return context


class CategoriesView(ListView):
    """Shows all auction categories"""
    model = Listing

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'GET':
            return render(request, 'auctions/categories_list.html', context={
                'object_list': [v for x in Listing.objects.order_by().values('category').distinct() for v in x.values()]
            })

    def get_context_data(self, **kwargs):
        context = super(CategoriesView, self).get_context_data(**kwargs)
        context['object_list'] = [v for x in Listing.objects.order_by().values('category').distinct() for v in x.values()]
        return context


class CategoryItemsView(ListView):
    model = Listing
    template_name = 'auctions/categories_items.html'

    def get_context_data(self, **kwargs):
        category = self.kwargs['category']
        context = super(CategoryItemsView, self).get_context_data(**kwargs)
        context['object_list'] = Listing.objects.filter(category=category)
        context['category'] = category
        return context

