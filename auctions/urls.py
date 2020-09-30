from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("list/create", views.create_listing, name="create_listing"),
    path("list/<int:listing_id>", views.listing_view, name="listing"),
    path("list/<int:listing_id>/bid", views.bid_view, name="bid"),
    path("list/<int:listing_id>/comment", views.comment_view, name="comment"),
    path("list/<int:listing_id>/close_confirm", views.close_confirm, name="close_confirm"),
    path("list/<int:listing_id>/close", views.close_listing, name="close_listing"),
    path("watchlist", views.watchlist_view, name="watchlist"),
    path("watchlist/add/<int:listing_id>", views.watchlist_add, name="watchlist_add"),
    path("watchlist/del/<int:listing_id>", views.watchlist_del, name="watchlist_del"),
    path("error/<int:code>_<str:error_message>", views.error_view, name="error"),
]
