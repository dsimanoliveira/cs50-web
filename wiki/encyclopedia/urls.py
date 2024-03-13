from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>/", views.entry, name="entry"),
    path("search-results/", views.search, name="search-results"),
    path("new-page/", views.new_page, name="new"),
    path("<str:title>/edit/", views.edit_page, name="edit"),
    path("random/", views.random_page, name="random")
]
