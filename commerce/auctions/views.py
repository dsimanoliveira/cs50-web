from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from decimal import Decimal

from .models import User, AuctionListing, UserWatchlist, Bid, Comment, AuctionCategorie


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


def categories_view(request):
    categories = AuctionCategorie.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": categories
    })


def listings_from_categorie_view(request, category_id):
    category = AuctionCategorie.objects.get(id=category_id)
    listings = AuctionListing.objects.filter(category=category)
    return render(request, "auctions/listings_from_category.html", {
        "listings": listings,
        "category": category
    })


def user_watchlist_view(request):
    if request.user.is_authenticated:
        user = request.user 
        watchlist = AuctionListing.objects.filter(watchlisted_by__user=user)
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
    

def bid_view(request, listing_id):
    if request.method == "POST" and request.user.is_authenticated:
        user = request.user 
        listing = AuctionListing.objects.get(id=listing_id)
        bid_amount = Decimal(request.POST.get("bid_amount"))
        
        bid = Bid(bidder=user, listing=listing, amount=bid_amount)

        try:
            bid.full_clean()  # Validate the bid
            bid.save()
            return HttpResponseRedirect(reverse("listing", args=[listing_id]))
        except Exception as e:
            bid_error = str(e)
            return render(request, "auctions/listing_page.html", {
                "listing": listing,
                "bid_error": bid_error,
                "is_watchlisted": True if user.watchlist.filter(listing_id=listing_id).first() else False
            })
        

def close_auction_view(request, listing_id):
    if request.method == "POST" and request.user.is_authenticated:
        user = request.user
        listing = AuctionListing.objects.get(id=listing_id)

        if user == listing.owner:
            listing.is_active = False 
            listing.save() 
            return HttpResponseRedirect(reverse("listing", args=[listing_id]))


def add_comment_view(request, listing_id):
    if request.method == "POST" and request.user.is_authenticated:
        user = request.user 
        listing = AuctionListing.objects.get(id=listing_id)
        comment_text = request.POST.get("comment_text")

        comment = Comment(commenter=user, listing=listing, text=comment_text)
        comment.save()
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
