from pyexpat.errors import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Category, Pizza, Review, Sub, Pasta, Salad, Rice, UserOrder, SavedCarts, Biryani, Rolls, Ni
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import logout, authenticate, login
from django import forms 
from django.views.decorators.http import require_POST
import json, requests, stripe
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from orders import models

stripe.api_key = settings.STRIPE_SECRET_KEY


# Create your views here.
def index(request):
    return render(request, "orders/home.html", {
        "categories": Category.objects.all(),
        "user_authenticated": request.user.is_authenticated  
    }) 

def login_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)

                return redirect('/')

    form = AuthenticationForm()
    return render(request = request,
                    template_name = "orders/login.html",
                    context={"form":form})

def logout_request(request):
    logout(request)
    return redirect("orders:login")

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            login(request, user)
            return redirect("orders:index")

        return render(request = request,
                          template_name = "orders/register.html",
                          context={"form":form})

    return render(request = request,
                  template_name = "orders/register.html",
                  context={"form":UserCreationForm})

def pizza(request):
    return render(request, "orders/pizza.html", context={"dishes": Pizza.objects.all})

def pasta(request):
    return render(request, "orders/pasta.html", context={"dishes": Pasta.objects.all})

def salad(request):
    return render(request, "orders/salad.html", context={"dishes": Salad.objects.all})

def biryani(request):
    return render(request, "orders/biryani.html", context={"dishes": Biryani.objects.all})

def rolls(request):
    return render(request, "orders/rolls.html", context={"dishes": Rolls.objects.all})

def north_indian(request):
    return render(request, 'orders/ni.html', context={"dishes": Ni.objects.all})

def subs(request):
    return render(request, "orders/sub.html", context={"dishes": Sub.objects.all})

def rice(request):
    return render(request, "orders/rice.html", context={"dishes": Rice.objects.all})

def cart(request):
    if request.user.is_authenticated:
        return render(request, "orders/cart.html")
    else:
        return redirect("orders:login")




def directions(request):
    return render(request, "orders/directions.html")

def hours(request):
    return render(request, "orders/hours.html")

def contact(request):
    return render(request, "orders/contact.html")


@login_required
def view_orders(request):
    data = UserOrder.objects.filter(username=request.user.username).order_by('-created_at')

    for row in data:
        row.items_list = row.order.split(",")

    return render(request, 'orders/orders.html', {'data': data})

def mark_order_as_delivered(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        UserOrder.objects.filter(pk=id).update(delivered=True)
        return HttpResponse(
            json.dumps({"good":"boy"}),
            content_type="application/json"
        )
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )



@csrf_exempt
def save_cart(request):
    if request.method == 'POST':
        cart_data = request.POST.get("cart")
        if not cart_data:
            return JsonResponse({"status": "failed", "error": "No cart data"})

        request.session['cart'] = cart_data

        return JsonResponse({"status": "success"})
    else:
        return JsonResponse({"status": "failed", "error": "Invalid request method"})

def retrieve_saved_cart(request):
    saved_cart = SavedCarts.objects.get(username = request.user.username)
    return HttpResponse(saved_cart.cart)

def check_superuser(request):
    print(f"User super??? {request.user.is_superuser}")
    return HttpResponse(request.user.is_superuser)

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

def register(request):
    if request.method == "POST":
        print("Form submitted!")
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            print("Form is valid!")
            user = form.save()
            username = form.cleaned_data.get('username')
            login(request, user)
            print("Redirecting to index...") 
            return redirect("orders:index")
        else:
            print("Form errors:", form.errors) 
            return render(request, "orders/register.html", {"form": form})
    else:
        form = CustomUserCreationForm()
        return render(request, "orders/register.html", {"form": form})
def home(request):
    return render(request, "orders/home.html")

def reviews_page(request):
    if request.method == "POST":
        review_text = request.POST.get("review_text")
        review_rating = request.POST.get("review_rating")

        if review_text and review_rating:
            Review.objects.create(content=review_text, rating=int(review_rating))

        return redirect("reviews")

    reviews = Review.objects.all().order_by('-created_at')
    return render(request, "orders/reviews.html", {"reviews": reviews})


@login_required
def payment_page(request):
    cart = request.session.get('cart', [])
    print("Cart contents:", cart)
    
    if not cart:
        return render(request, 'orders/cart_empty.html')

    
    total_amount = sum(item['price'] * item['qty'] for item in cart)
    total_in_paise = int(total_amount * 100)  
    
    request.session['cart_data'] = cart
    request.session['total_amount'] = total_amount

    context = {
        'cart_items': cart,
        'total_amount': total_amount,
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY
    }
    return render(request, 'orders/payment.html', context)

@login_required
def stripe_checkout(request):
    if request.method == 'POST':
        cart = request.session.get('cart_data', [])
        if not cart:
            return redirect('orders:cart')
            
        total_amount = request.session.get('total_amount', 0)
        total_in_paise = int(total_amount * 100)  
        
        try:
            line_items = []
            for item in cart:
                line_items.append({
                    'price_data': {
                        'currency': 'inr',
                        'product_data': {
                            'name': item.get('item_description', 'Food Item'),
                        },
                        'unit_amount': int(item['price'] * 100),
                    },
                    'quantity': item.get('qty', 1),
                })

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=request.build_absolute_uri(reverse('orders:payment_success')),
                metadata={
                    'user_id': request.user.id,
                    'username': request.user.username
                }
            )
            return redirect(session.url, code=303)
            
        except Exception as e:
            messages.error(request, f"Payment error: {str(e)}")
            return redirect('orders:cart')

@login_required
def payment_success(request):
    # Process the order after successful payment
    cart_data = request.session.get("cart_data", [])
    if not cart_data:
        return redirect('orders:cart')
    
    total_amount = request.session.get("total_amount", 0)
    username = request.user.username

    list_of_items = [f"{item.get('qty', 1)} x {item.get('item_description', 'Unknown')}" for item in cart_data]

    address = request.session.get("delivery_address", "")
    latitude = request.session.get("latitude")
    longitude = request.session.get("longitude")

    if not latitude or not longitude:
        latitude, longitude = geocode_address(address)
    
    # Create the order
    order = UserOrder.objects.create(
        username=username,
        order=", ".join(list_of_items),
        price=total_amount,
        delivered=False,
        delivery_address=address,
        latitude=latitude if latitude else None,
        longitude=longitude if longitude else None,
     
    )

    # Clear session data
    SavedCarts.objects.filter(username=username).delete()
    for key in ['cart_data', 'total_amount', 'delivery_address', 'latitude', 'longitude']:
        request.session.pop(key, None)

    context = {
        "items": list_of_items,
        "total": total_amount,
        "address": address,
        "latitude": latitude,
        "longitude": longitude
    }

    return render(request, "orders/payment_success.html", context)


@login_required
@csrf_exempt
@require_POST
def save_address(request):
    data = json.loads(request.body)
    address = data.get("address")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    request.session['delivery_address'] = address
    request.session['latitude'] = latitude
    request.session['longitude'] = longitude

    return JsonResponse({"status": "saved"})

    
    
def store_cart_session(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        request.session['cart'] = data.get('cart', [])
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)


    
def track_order(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        try:
            order = UserOrder.objects.get(id=order_id)
            context = {
                'order': order,
                'status': order.status, 
                'latitude': order.latitude,
                'longitude': order.longitude, 
            }
            return render(request, 'orders/order_tracking.html', context)
        except UserOrder.DoesNotExist:
            return render(request, 'orders/order_tracking.html', {'error': 'Order not found'})
    return render(request, 'orders/order_tracking.html')




def submit_review(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        rating = int(request.POST.get('rating'))
        review_text = request.POST.get('review_text')

        if name and rating and review_text:
            Review.objects.create(
                name=name,
                rating=rating,
                review_text=review_text,
                created_at=timezone.now()
            )
        return redirect('orders:reviews')  
    
@csrf_exempt
def get_order_status(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')

        try:
            order = UserOrder.objects.get(id=order_id)

            items_list = order.order.split(",") if order.order else []
            
            data = {
                "status": order.get_status_display(),  
                "items": items_list,
                "total": float(order.price),
                "address": order.delivery_address,
                "latitude": float(order.latitude) if order.latitude else None,
                "longitude": float(order.longitude) if order.longitude else None,
                "order_time": order.time_of_order.strftime("%Y-%m-%d %H:%M:%S"),
                "delivered": order.delivered
            }
            return JsonResponse(data)

        except UserOrder.DoesNotExist:
            return JsonResponse({"error": "Order not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
def geocode_address(address):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": address,
            "format": "json",
            "limit": 1
        }
        headers = {
            'User-Agent': 'FoodieExpressApp/1.0 (anujthakur2004@gmail.com)' 
        }
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
    except Exception as e:
        print(f"Geocoding failed: {e}")
    return None, None

