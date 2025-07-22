from django.urls import path, include
from django.urls import path, re_path 
from . import views

app_name = "orders"

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_request, name="login"),
    path("register/", views.register, name="register"),
    path("logout", views.logout_request, name="logout"),
    path("Pizza", views.pizza, name="pizza"),
    path("Pasta", views.pasta, name="pasta"),
    path("Biryani", views.biryani, name="biryani"),
    path("reviews/", views.reviews_page, name="reviews"),
    path("Salad", views.salad, name="salad"),
    path("Rolls", views.rolls, name="rolls"),
    path('North-Indian/', views.north_indian, name='north_indian'),
    path("Subs", views.subs, name="subs"),
    path("Rice", views.rice, name="rice"),
    path("hours", views.hours, name="hours"),
    path("contact", views.contact, name="contact"),
    path("cart", views.cart, name="cart"),
    path("view-orders", views.view_orders, name="view_orders"),
    path("mark_order_as_delivered", views.mark_order_as_delivered, name="mark_order_as_delivered"),
    path("save_cart", views.save_cart, name="save_cart"),
    path("retrieve_saved_cart", views.retrieve_saved_cart, name="retrieve_saved_cart"),
    path("check_superuser", views.check_superuser, name="check_superuser"),
    path('tinymce/', include('tinymce.urls')),
    path('pay/', views.payment_page, name='payment_page'),
    path('save-address/', views.save_address, name='save_address'),
    path('pay/', views.payment_page, name='payment_page'),
    path('stripe-checkout/', views.stripe_checkout, name='stripe_checkout'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('store-cart-session/', views.store_cart_session, name='store_cart_session'),
    path('track-order/', views.track_order, name='track_order'),
    path('reviews/', views.reviews_page, name='reviews_page'),
    path('submit-review/', views.submit_review, name='submit_review'),
    path('get-order-status/', views.get_order_status, name='get_order_status'),
   
]
