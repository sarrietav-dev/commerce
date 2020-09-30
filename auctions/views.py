from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import ObjectDoesNotExist
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
import datetime as dt
import re

from auctions.forms import BidForm, CommentForm, ListingForm
from auctions.models import Bid, Comment, Listing, User, Watchlist
from auctions.helpers import ensure_user


def error_view(request, code=403, error_message="You shall not pass"):
    def escape(message):
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            message = message.replace(old, new)
        return message

    return render(request, "auctions/error.html", {
        "code": code,
        "error_message": escape(error_message),
        "is_403": code == 403
    })


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all()[::-1]
    })


def listing_view(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    bids = Bid.objects.filter(listing=listing)[::-1]

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comment_form": CommentForm(),
        "comments": Comment.objects.filter(listing=listing)[::-1],
        "bid_form": BidForm(),
        "bids": bids if len(bids) != 0 else False,
        "winner": bids[0] if len(bids) != 0 else None,
        "has_in_watchlist": has_in_watchlist(request.user, listing),
        "is_user_owner": listing.owner == request.user
    })


def has_in_watchlist(user, listing):
    if user.is_anonymous:
        return False
    try:
        Watchlist.objects.get(user=user, listings=listing)
    except ObjectDoesNotExist:
        return False
    return True


@login_required
def watchlist_view(request):
    watchlist = request.user.watchlist
    return render(request, "auctions/watchlist.html", {
        "listings": watchlist.listings.all()[::-1]
    })

@login_required
def watchlist_add(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    watchlist = request.user.watchlist

    watchlist.listings.add(listing)
    return HttpResponseRedirect(reverse("listing", args=(listing.id, )))


@login_required
def watchlist_del(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    watchlist = request.user.watchlist

    watchlist.listings.remove(listing)
    return HttpResponseRedirect(reverse("listing", args=(listing.id, )))


@login_required
def bid_view(request, listing_id):
    listing = Listing.objects.get(id=listing_id)

    if request.method == "POST":

        form = BidForm(request.POST, listing=listing)

        if form.is_valid():
            bid = form.save(commit=False)

            bid.bidder = request.user
            bid.listing = listing

            bid.save()
            return HttpResponseRedirect(reverse("listing", args=(listing.id, )))
        else:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "comment_form": CommentForm(),
                "comments": Comment.objects.filter(listing=listing)[::-1],
                "bid_form": form,
                "bids": Bid.objects.filter(listing=listing)[::-1],
                "has_in_watchlist": has_in_watchlist(request.user, listing)
            })
    return HttpResponseRedirect(reverse("listing", args=(listing.id, )))


@login_required
def comment_view(request, listing_id):
    listing = Listing.objects.get(id=listing_id)

    if request.method == "POST":

        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)

            comment.user = request.user
            comment.listing = listing

            comment.save()
            return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
    return HttpResponseRedirect(reverse("listing", args=(listing.id, )))


@ensure_user
def close_confirm(request, listing_id):
    listing = Listing.objects.get(id=listing_id)

    return render(request, "auctions/close_confirm.html", {
        "listing": listing,
        "time_active": listing.get_time_active,
        "lastest_bid": Bid.objects.filter(listing=listing)[::-1][0]
    })


@ensure_user
def close_listing(request, listing_id):
    listing = Listing.objects.get(id=listing_id)

    listing.active = False
    listing.save()
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))


def create_listing(request):
    if request.method == "POST":

        form = ListingForm(request.POST, request.FILES)

        if form.is_valid():
            listing = form.save(commit=False)

            listing.owner = request.user

            listing.save()

            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/make_listing.html", {
                "form": form,
                "message": "Write only one category and only letters"
            })

    return render(request, "auctions/make_listing.html", {
        "form": ListingForm()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            watchlist = Watchlist(user=user)
            watchlist.save()
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
