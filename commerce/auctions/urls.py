from django.urls import path
from . import views

urlpatterns = [
    path("", views.ListingAllView.as_view(), name="index"),
    path("listing/<int:pk>", views.ListingDetail.as_view(), name="listing_detail"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_listing", views.ListingCreateView.as_view(), name="new_listing"),
    path("watchlist/<int:pk>", views.WatchlistView.as_view(), name="watchlist"),
    path("category", views.CategoriesView.as_view(), name="category"),
    path("category/<str:category>", views.CategoryItemsView.as_view(), name="category_items"),
]
