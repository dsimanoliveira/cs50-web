from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, AuctionListing, UserWatchlist, Bid


def index(request):
    active_listings = AuctionListing.objects.filter(is_active=True)
    return render(request, "auctions/index.html", {
        "listings": active_listings
    })


def listing_view(request, listing_id):
    # Check if listing_id is in user's watchlist
    if request.user.is_authenticated:
        user = request.user
        is_watchlisted = True if user.watchlist.filter(listing_id=listing_id).first() else False
    else:
        is_watchlisted = False
    
    listing = AuctionListing.objects.get(id=listing_id)
    return render(request, "auctions/listing_page.html", {
        "listing": listing,
        "is_watchlisted": is_watchlisted
    })


def user_watchlist_view(request):
    if request.user.is_authenticated:
        user = request.user 
        watchlist = user.watchlist.all()
        return render(request, "auctions/watchlist.html", {
            "watchlist": watchlist
        })
    

def add_to_watchlist(request, listing_id):
    if request.method == "POST":
        user = request.user
        listing = AuctionListing.objects.get(id=listing_id)
        watchlist_item = UserWatchlist(user=user, listing=listing)
        watchlist_item.save() 
        return HttpResponseRedirect(reverse("listing", args=[listing_id]))


def remove_from_watchlist(request, listing_id):
    if request.method == "POST":
        user = request.user
        listing = AuctionListing.objects.get(id=listing_id)
        watchlist_item = UserWatchlist.objects.filter(user=user, listing=listing).first()
        if watchlist_item:
            watchlist_item.delete()
        return HttpResponseRedirect(reverse("listing", args=[listing_id]))


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
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
