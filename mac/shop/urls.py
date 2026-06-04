from django.contrib import admin
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include

urlpatterns = [
    path("", views.index, name="ShopHome"),
    path("about/", views.about, name="AboutUs"),
    path("contact/", views.contact, name="ContactUs"),
    path("tracker/", views.tracker, name="TrackingStatus"),
    path("search/", views.search, name="Search"),
    path("productview/<int:myid>", views.productview, name="Product"),
    path("checkout/", views.checkout, name="Checkout"),
    path("cart",views.cart, name="MyCart"),
    path("order-history",views.order_history, name="OrderHistory"),
    path("profile",views.profile, name="Profile"),
   path("handlerequest/", views.handlerequest, name="handlerequest"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

