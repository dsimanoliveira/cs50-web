from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listing/<int:listing_id>", views.listing_view, name="listing"),
    path("watchlist", views.user_watchlist_view, name="user_watchlist"),
    path("listing/<int:listing_id>/watchlist/add", views.add_to_watchlist, name="add_to_watchlist"),
    path("listing/<int:listing_id>/watchlist/remove", views.remove_from_watchlist, name="remove_from_watchlist"),
    path("listing/<int:listing_id>/bid", views.bid_view, name="bid"),
    path("listing/<int:listing_id>/closeauction", views.close_auction_view, name="close_auction"),
    path("listing/<int:listing_id>/comment", views.add_comment_view, name="add_comment"),
    path("categories", views.categories_view, name="categories"),
    path("category/<int:category_id>", views.listings_from_categorie_view, name="listings_from_category"),
    path("listing/create", views.create_listing_view, name="create_listing"),
]
