from django.contrib import admin
from .models import User, AuctionListing, AuctionCategorie, UserWatchlist, Bid, Comment

# Register your models here.
admin.site.register(User)
admin.site.register(AuctionListing)
admin.site.register(AuctionCategorie)
admin.site.register(UserWatchlist)
admin.site.register(Bid)
admin.site.register(Comment)