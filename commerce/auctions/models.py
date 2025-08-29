from django.contrib.auth.models import AbstractUser
from django.db import models


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

    def __str__(self):
        return f"{self.title} - {self.starting_bid}"
    
class AuctionCategorie(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name
    
class UserWatchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="watchlisted_by")

    def __str__(self):
        return f"{self.user.username} is watching {self.listing.title}"
