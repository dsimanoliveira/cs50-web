from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Max
from django.core.exceptions import ValidationError


class User(AbstractUser):
    pass

class AuctionListing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True, null=True, max_length=400)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    category = models.ForeignKey("AuctionCategorie", on_delete=models.SET_NULL, null=True, blank=True, related_name="listings")

    def get_current_price(self):
        bids = self.bids.all()
        if bids:
            return bids.aggregate(Max('amount'))['amount__max']
        return self.starting_bid

    def __str__(self):
        return f"{self.title} - ${self.get_current_price()}"
    
class AuctionCategorie(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name
    
class UserWatchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="watchlisted_by")

    def __str__(self):
        return f"{self.user.username} is watching {self.listing.title}"
    
class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        errors = {}
        if self.bidder == self.listing.owner:
            errors['bidder'] = "Owner cannot bid on their own listing."
        if self.amount < self.listing.starting_bid:
            errors['amount'] = "Bid amount must be at least the starting bid."
        else:
            if self.amount <= self.listing.get_current_price():
                    errors['amount'] = 'Bid amount must be greater than any other bids'

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.bidder.username} bid {self.amount} on {self.listing.title}"
