from django.urls import path
from .views import home, login_view, signup_view, logout_view, forgot_password_view, about_view, contact_view, offer_view, cart_view, checkout_view, edit_address, delete_address, products_by_category, ajax_add_to_cart, remove_from_cart, remove_offer_from_cart, ajax_add_offer_to_cart, cart_count_api

urlpatterns = [
    path('', home, name='home'),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', logout_view, name='logout'),
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('about/', about_view, name='about'),
    path('contact/', contact_view, name='contact'),
    path('contacts/', contact_view, name='contact_plural'),
    path('offers/', offer_view, name='offer'),
    path('cart/', cart_view, name='cart'),
    path('checkout/', checkout_view, name='checkout'),
    path('edit-address/<int:address_id>/', edit_address, name='edit_address'),
    path('delete-address/<int:address_id>/', delete_address, name='delete_address'),
    path('products/<slug:category_slug>/', products_by_category, name='products_by_category'),
    path('cart/ajax_add/<int:product_id>/', ajax_add_to_cart, name='ajax_add_to_cart'),
    path('cart/remove/<str:product_key>/', remove_from_cart, name='remove_from_cart'),
    path('cart/remove_offer/<str:offer_key>/', remove_offer_from_cart, name='remove_offer_from_cart'),
    path('cart/ajax_add_offer/<int:offer_id>/', ajax_add_offer_to_cart, name='ajax_add_offer_to_cart'),
    path('cart/count/', cart_count_api, name='cart_count_api'),
]
