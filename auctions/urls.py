from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("newlisting", views.new_listing, name="newlisting"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("categories/<int:id>", views.category, name="category"),
    path("addtowatchlist/<int:watchlist_id>", views.add_to_watchlist, name="add_to_watchlist"),
    path("removefromwatchlist/<int:watchlist_id>", views.remove_from_watchlist, name="remove_from_watchlist"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("comment/<int:listing_id>", views.comment, name="comment"),
    path("bid/<int:listing_id>", views.bid, name="bid"),
    path("closeAuction/<int:listing_id>", views.closeAuction, name="closeAuction")

]
