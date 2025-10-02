from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.db import models

def home(request):
    categories = [
        {
            'name': 'Diapers & Pampers',
            'image': 'shop/images/Home/Feature1.png',
            'url': '/products/diaper/',
        },
        {
            'name': 'Baby Dress',
            'image': 'shop/images/Home/Feature2.png',
            'url': '/products/girls-fashion/',
        },
        {
            'name': 'Baby Soap',
            'image': 'shop/images/Home/Feature3.png',
            'url': '/products/soap/',
        },
        {
            'name': 'Baby Stroller & Prams',
            'image': 'shop/images/Home/Feature4.jpg',
            'url': '/products/stroller/',
        },
    ]
    bestsellers = [
        {
            'name': 'Wipes',
            'image': 'shop/images/Home/best1.jpg',
            'is_new': True,
            'rating': "⭐⭐⭐⭐⭐",
            'old_price': 1444,
            'price': 1299,
            'url': '/products/diaper/',
        },
        {
            'name': 'Mama Miel Baby',
            'image': 'shop/images/Home/best2.jpg',
            'is_new': True,
            'rating': "⭐⭐⭐⭐⭐",
            'old_price': 1444,
            'price': 1299,
            'url': '/products/boys-fashion/',
        },
        {
            'name': 'Zibuyu',
            'image': 'shop/images/Home/best3.png',
            'is_new': True,
            'rating': "⭐⭐⭐⭐⭐",
            'old_price': 1444,
            'price': 1299,
            'url': '/products/girls-fashion/',
        },
    ]
    return render(request, 'shop/home.html', {'categories': categories, 'bestsellers': bestsellers})

def about_view(request):
    return render(request, 'shop/about.html')


def product_search(request):
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        from .models import Product
        results = Product.objects.filter(is_active=True).filter(
            models.Q(title__icontains=query) | models.Q(description__icontains=query)
        )
    return render(request, 'shop/search_results.html', {'query': query, 'results': results})

from django.http import JsonResponse

def product_name_suggestions(request):
    q = request.GET.get('q', '').strip()
    suggestions = []
    if q:
        from .models import Product
        suggestions = list(
            Product.objects.filter(is_active=True, title__icontains=q)
            .order_by('title')
            .values_list('title', flat=True)[:8]
        )
    return JsonResponse({'suggestions': suggestions})





from django.shortcuts import render

from .models import Product, Category, Offer
from django.shortcuts import get_object_or_404

def products_by_category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category, is_active=True)
    return render(request, f'shop/products_{category_slug}.html', {'products': products, 'category': category})

from django.shortcuts import redirect, get_object_or_404

# Session-based cart helpers

from django.contrib.auth.decorators import login_required

from django.http import JsonResponse

# Legacy add_to_cart removed (was Offer-based)

# Legacy remove_from_cart removed (was Offer-based)

def cart_view(request):
    cart = request.session.get('cart', {})
    user = request.user
    alert_message = None
    disable_checkout = False
    if not user.is_authenticated:
        alert_message = 'Login required to access cart.'
        disable_checkout = True
    # Handle quantity update on any POST (only if logged in)
    if user.is_authenticated and request.method == 'POST':
        for offer_id, qty in request.POST.items():
            if offer_id.startswith('qty_'):
                oid = offer_id.replace('qty_', '')
                if oid in cart:
                    try:
                        cart[oid]['quantity'] = max(1, int(qty))
                    except Exception:
                        pass
        request.session['cart'] = cart
    # Handle coupon code (demo: static discount)
    coupon = request.POST.get('coupon', '') if user.is_authenticated else ''
    discount = 0
    subtotal = sum(item['price'] * item['quantity'] for item in cart.values())
    if coupon == 'SAVE250':
        discount = 250
    elif coupon.lower() == 'baby10':
        discount = round(subtotal * 0.10)
    for item in cart.values():
        item['subtotal'] = item['price'] * item['quantity']
    total = subtotal - discount
    shipping = 0 if total > 0 else 0
    context = {
        'cart_items': cart,
        'subtotal': subtotal,
        'discount': discount,
        'shipping': shipping,
        'total': total,
        'coupon': coupon,
        'alert_message': alert_message,
        'disable_checkout': disable_checkout,
    }
    return render(request, 'shop/cart.html', context)

from django.core.paginator import Paginator

@require_POST
@login_required
def ajax_add_offer_to_cart(request, offer_id):
    cart = request.session.get('cart', {})
    offer = get_object_or_404(Offer, pk=offer_id)
    item = cart.get(f"offer_{offer_id}", {
        'title': offer.title,
        'price': float(offer.price or 0),
        'mrp': float(offer.mrp or 0),
        'image': offer.image.url if offer.image else '',
        'quantity': 0,
        'is_offer': True,
    })
    item['quantity'] += 1
    cart[f"offer_{offer_id}"] = item
    request.session['cart'] = cart
    return JsonResponse({'success': True, 'message': 'Offer added to cart!', 'cart_count': len(cart)})

@login_required
def remove_from_cart(request, product_key):
    cart = request.session.get('cart', {})
    if product_key in cart:
        del cart[product_key]
        request.session['cart'] = cart
    return redirect('cart')

@login_required
def remove_offer_from_cart(request, offer_key):
    cart = request.session.get('cart', {})
    if offer_key in cart:
        del cart[offer_key]
        request.session['cart'] = cart
    return redirect('cart')

from django.views.decorators.csrf import ensure_csrf_cookie

@ensure_csrf_cookie
def cart_count_api(request):
    cart = request.session.get('cart', {})
    return JsonResponse({'cart_count': len(cart)})

def offer_view(request):
    from .models import Offer
    from django.core.paginator import Paginator
    offers_qs = Offer.objects.filter(is_active=True)
    paginator = Paginator(offers_qs, 6)  # 6 offers per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'shop/offer.html', {'offers': page_obj})

from .forms import ContactForm, UserAddressForm
from .models import Contact, UserAddress

@login_required
def checkout_view(request):
    cart = request.session.get('cart', {})
    subtotal = sum(item['price'] * item['quantity'] for item in cart.values())
    discount = 0
    coupon = request.POST.get('coupon', '')
    if coupon == 'SAVE250':
        discount = 250
    elif coupon.lower() == 'baby10':
        discount = round(subtotal * 0.10)
    total = subtotal - discount
    shipping = 0 if total > 0 else 0
    saved_addresses = UserAddress.objects.filter(user=request.user).order_by('-created_at')
    selected_address = None
    form = UserAddressForm()
    save_success = False
    if request.method == 'POST' and ('place_order' in request.POST or 'save_address' in request.POST):
        selected_id = request.POST.get('address_select')
        if 'place_order' in request.POST:
            if selected_id and selected_id != 'new':
                try:
                    selected_address = saved_addresses.get(id=selected_id)
                    request.session['last_address_id'] = selected_address.id  # Store last used
                    # --- Create Order and OrderItems ---
                    from .models import Order, OrderItem, Product
                    cart = request.session.get('cart', {})
                    if not cart:
                        return render(request, 'shop/checkout.html', {'form': form, 'cart_items': cart, 'subtotal': subtotal, 'discount': discount, 'shipping': shipping, 'total': total, 'coupon': coupon, 'saved_addresses': saved_addresses, 'alert_message': 'Your cart is empty.'})
                    order = Order.objects.create(
                        user=request.user,
                        address=selected_address,
                        subtotal=subtotal,
                        discount=discount,
                        total=total,
                        status='pending',
                    )
                    for item_key, item in cart.items():
                        try:
                            if str(item_key).startswith("offer_"):
                                offer_id = int(str(item_key).replace("offer_", ""))
                                offer = Offer.objects.get(id=offer_id)
                                OrderItem.objects.create(
                                    order=order,
                                    offer=offer,
                                    price=item['price'],
                                    quantity=item['quantity'],
                                    subtotal=item['price'] * item['quantity'],
                                )
                            elif str(item_key).isdigit():
                                product = Product.objects.get(id=int(item_key))
                                OrderItem.objects.create(
                                    order=order,
                                    product=product,
                                    price=item['price'],
                                    quantity=item['quantity'],
                                    subtotal=item['price'] * item['quantity'],
                                )
                            else:
                                continue  # skip unknown key format
                        except Exception as e:
                            print(f"Skipping cart item {item_key}: {e}")
                            continue
                    request.session['cart'] = {}  # Clear the cart
                    return render(request, 'shop/checkout_success.html', {'address': selected_address, 'order': order})
                except UserAddress.DoesNotExist:
                    pass
        form = UserAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            request.session['last_address_id'] = address.id  # Store last used
            if 'place_order' in request.POST:
                # --- Create Order and OrderItems for new address ---
                from .models import Order, OrderItem, Product
                cart = request.session.get('cart', {})
                if not cart:
                    return render(request, 'shop/checkout.html', {'form': form, 'cart_items': cart, 'subtotal': subtotal, 'discount': discount, 'shipping': shipping, 'total': total, 'coupon': coupon, 'saved_addresses': saved_addresses, 'alert_message': 'Your cart is empty.'})
                order = Order.objects.create(
                    user=request.user,
                    address=address,
                    subtotal=subtotal,
                    discount=discount,
                    total=total,
                    status='pending',
                )
                for item_key, item in cart.items():
                    try:
                        if str(item_key).startswith("offer_"):
                            offer_id = int(str(item_key).replace("offer_", ""))
                            offer = Offer.objects.get(id=offer_id)
                            OrderItem.objects.create(
                                order=order,
                                offer=offer,
                                price=item['price'],
                                quantity=item['quantity'],
                                subtotal=item['price'] * item['quantity'],
                            )
                        elif str(item_key).isdigit():
                            product = Product.objects.get(id=int(item_key))
                            OrderItem.objects.create(
                                order=order,
                                product=product,
                                price=item['price'],
                                quantity=item['quantity'],
                                subtotal=item['price'] * item['quantity'],
                            )
                        else:
                            continue  # skip unknown key format
                    except Exception as e:
                        print(f"Skipping cart item {item_key}: {e}")
                        continue
                request.session['cart'] = {}  # Clear the cart
                return render(request, 'shop/checkout_success.html', {'address': address, 'order': order})
            elif 'save_address' in request.POST:
                save_success = True
    return render(request, 'shop/checkout.html', {
        'form': form,
        'cart_items': cart,
        'subtotal': subtotal,
        'discount': discount,
        'shipping': shipping,
        'total': total,
        'coupon': coupon,
        'saved_addresses': saved_addresses,
        'save_success': save_success,
    })

def edit_address(request, address_id):
    address = UserAddress.objects.get(id=address_id, user=request.user)
    if request.method == 'POST':
        form = UserAddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect('checkout')
    else:
        form = UserAddressForm(instance=address)
    return render(request, 'shop/edit_address.html', {'form': form, 'address': address})

def delete_address(request, address_id):
    address = UserAddress.objects.get(id=address_id, user=request.user)
    if request.method == 'POST':
        address.delete()
        return redirect('checkout')
    return render(request, 'shop/delete_address.html', {'address': address})

def contact_view(request):
    success = False
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            Contact.objects.create(
                first_name=cd['first_name'],
                last_name=cd['last_name'],
                email=cd['email'],
                phone_number=cd['phone_number'],
                message=cd['message']
            )
            success = True
            form = ContactForm()  # Reset form after success
    else:
        form = ContactForm()
    return render(request, 'shop/contact.html', {'form': form, 'success': success})

from django.contrib import messages

from django.contrib.auth import authenticate, login

def login_view(request):
    errors = []
    if request.method == 'POST':
        user_input = request.POST.get('username')
        password = request.POST.get('password')
        if not user_input or not password:
            errors.append('Both username/email and password are required.')
        else:
            from django.contrib.auth.models import User
            user = None
            # Try username first
            user_obj = User.objects.filter(username=user_input).first()
            if user_obj:
                user = authenticate(request, username=user_obj.username, password=password)
            else:
                # Try email
                user_obj = User.objects.filter(email=user_input).first()
                if user_obj:
                    user = authenticate(request, username=user_obj.username, password=password)
            if user is not None:
                login(request, user)
                return render(request, 'shop/login.html', {'login_success': True})
            else:
                errors.append('Invalid username/email or password.')
    return render(request, 'shop/login.html', {'errors': errors})

from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import logout

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return render(request, 'shop/login.html', {'logout_success': True})
    return render(request, 'shop/logout_confirm.html')


def forgot_password_view(request):
    errors = []
    success = False
    if request.method == 'POST':
        email = request.POST.get('email')
        new_password = request.POST.get('new_password')
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            success = True
        except User.DoesNotExist:
            errors.append('No user found with that email address.')
    return render(request, 'shop/forgot_password.html', {'errors': errors, 'success': success})

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password1')
        errors = []
        if not username or not email or not password:
            errors.append('All fields are required.')
        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            errors.append('User already registered.')
            return render(request, 'shop/signup.html', {'errors': errors, 'username': username, 'email': email})
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        return render(request, 'shop/signup.html', {'registration_success': True})
    return render(request, 'shop/signup.html')

from django.http import JsonResponse
from django.views.decorators.http import require_POST

@require_POST
def ajax_add_to_cart(request, product_id):


    cart = request.session.get('cart', {})
    from .models import Product
    product = Product.objects.get(pk=product_id)
    item = cart.get(str(product_id), {
        'title': product.title,
        'price': float(product.price),
        'quantity': 0,
        'image': product.image.url if product.image else '',
    })
    item['quantity'] += 1
    cart[str(product_id)] = item
    request.session['cart'] = cart
    return JsonResponse({'success': True})
