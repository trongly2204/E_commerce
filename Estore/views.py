from django.shortcuts import render, get_object_or_404, redirect
from .models import Customer, Product, Order, Cart, Shipment, OrdereachTransaction, CarteachProduct, Logging
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .api.weather import weather_api
from decimal import Decimal
from .api.payment import payment_check, create_paypal_order
from .api.tracking_number import tracking_number_api
from .api.change_password import change_customer_password
from datetime import timedelta

def product_page(request):
    list_product = Product.objects.all()
    category = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    name_search = request.GET.get('name_search')

    filters = Q()
    customer_id = request.session.get('customer_id')
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    customer = None
    weather = None
    cart_count = 0

    if lat and lon:
        try:
            lat = float(lat)
            lon = float(lon)
            weather = weather_api(lat, lon)
        except ValueError:
            weather = weather_api()
    else:
        weather = weather_api()

    if name_search:
        filters &= Q(product_name__icontains=name_search) | Q(product_description__icontains=name_search)
    if category:
        filters &= Q(product_category__iexact=category)
    if min_price:
        filters &= Q(product_price__gte=min_price)
    if max_price:
        filters &= Q(product_price__lte=max_price)

    list_product = list_product.filter(filters)

    if customer_id:
        try:
            customer = Customer.objects.get(id=customer_id)
            cart = Cart.objects.filter(cart_customer_id=customer).first()
            if cart:
                cart_count = cart.total_quantity()
        except Customer.DoesNotExist:
            customer = None

    context = {
        'list_product': list_product,
        'customer': customer,
        'cart_count': cart_count,
        'weather': weather,
    }
    return render(request, 'product_page.html', context)


def login_page(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = Customer.objects.filter(username=username).first()

        if user and check_password(password, user.password):
            Logging.objects.create(username_logging=user, logged_at=timezone.now())
            request.session['customer_id'] = user.id
            next_page = request.POST.get('next')
            return redirect(next_page) if next_page else redirect('product_page')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login_page.html')


def logout_page(request):
    request.session.flush()
    return redirect('product_page')


def signup_page(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        re_password = request.POST.get('re_password')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        if Customer.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
        elif Customer.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists!')
        elif password != re_password:
            messages.error(request, 'Passwords do not match!')
        else:
            Customer.objects.create(
                username=username,
                password=make_password(password),
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            messages.success(request, 'Account created successfully!')
            return redirect('login_page')
    return render(request, 'signup_page.html')


@csrf_exempt
def add_to_cart(request, product_id):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('login_page')

    customer = get_object_or_404(Customer, id=customer_id)
    cart, _ = Cart.objects.get_or_create(cart_customer_id=customer)
    product = get_object_or_404(Product, id=product_id)

    item, created = CarteachProduct.objects.get_or_create(
        cart_id=cart,
        product=product,
        defaults={'cart_quantity': 1, 'cart_price': product.product_price}
    )
    next_page = request.POST.get('next') or request.GET.get('next')

    
    if not created:
        if item.cart_quantity + 1 > product.product_quantity:
            messages.error(request, f"Only {product.product_quantity} left in stock!")
        else:
            item.cart_quantity += 1
            item.save()
    
    # If created, redirect similarly
    if next_page:
        return redirect(next_page)
    else:
        return redirect(reverse('cart_page', kwargs={'customer_id': customer_id}))

@csrf_exempt
def remove_from_cart(request, product_id):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('login_page')

    customer = get_object_or_404(Customer, id=customer_id)
    cart, _ = Cart.objects.get_or_create(cart_customer_id=customer)
    product = get_object_or_404(Product, id=product_id)

    item, created = CarteachProduct.objects.get_or_create(
        cart_id=cart,
        product=product,
        defaults={'cart_quantity': 1, 'cart_price': product.product_price}
    )

    next_page = request.POST.get('next')

    if not created:
        if item.cart_quantity - 1 > product.product_quantity:
            messages.error(request, f"Only {product.product_quantity} left in stock!")
        else:
            item.cart_quantity -= 1
            item.save()

    if next_page:
        return redirect(next_page)
    else:
        return redirect(reverse('cart_page', kwargs={'customer_id': customer_id}))
@csrf_exempt
def clear_cart(request, customer_id):
    cart = get_object_or_404(Cart, cart_customer_id = customer_id)
    cart.items.all().delete()
    return redirect('cart_page', customer_id=customer_id )
def cart_page(request, customer_id):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect(f"{reverse('login_page')}?next={request.path}")
    customer = get_object_or_404(Customer, id=customer_id)
    cart, _ = Cart.objects.get_or_create(cart_customer_id=customer)
    if timezone.now() - cart.cart_created > timedelta(minutes=20):
        cart.items.all().delete()
        cart.delete()
        messages.info(request, "Your cart was cleared due to inactivity.")
        return redirect('product_page')
    out_of_stock = {item.product.id: True for item in cart.items.all() if item.cart_quantity > item.product.product_quantity}
    return render(request, 'cart_page.html', {
        'cart': cart,
        'out_of_stock': out_of_stock,
        'customer_id': customer_id
    })

@csrf_exempt
def check_out_page(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    cart = get_object_or_404(Cart, cart_customer_id=customer)

    if not cart.items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('cart_page', customer_id=customer_id)

    items_total = sum(item.cart_price * item.cart_quantity for item in cart.items.all())
    shipping_cost = 0
    total_with_shipping = items_total + shipping_cost  # default for GET

    if request.method == 'POST':
        # Get form data
        customer_name = request.POST.get('customer_name')
        customer_email = request.POST.get('customer_email')
        customer_phonenumber = request.POST.get('customer_phonenumber')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        method = request.POST.get('method')

        # Validate form input
        if not all([customer_name, customer_email, customer_phonenumber, address, city, state, zip_code, method]):
            messages.error(request, "All fields are required.")
            return redirect('check_out_page', customer_id=customer_id)

        # Shipping cost logic
        if method == 'standard':
            shipping_cost = 5
        elif method == 'express':
            shipping_cost = 10
        else:
            messages.error(request, "Invalid shipping method.")
            return redirect('check_out_page', customer_id=customer_id)

        total_with_shipping = items_total + shipping_cost

        access_token = payment_check()
        if not access_token:
            messages.error(request, "Payment failed: couldn't authenticate with PayPal.")
            return redirect('check_out_page', customer_id=customer_id)

        tracking_number = tracking_number_api()
        order = Order.objects.create(order_customer_id=cart.cart_customer_id, order_total=total_with_shipping)
        for item in cart.items.all():
            OrdereachTransaction.objects.create(
                order_id=order,
                product=item.product,
                order_price=item.cart_price,
                order_quantity=item.cart_quantity
            )
        Shipment.objects.create(
            customer=customer,
            order=order,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phonenumber=customer_phonenumber,
            address=address,
            city=city,
            state=state,
            zip_code=zip_code,
            method=method,
            tracking_number=tracking_number,
            payment_id=create_paypal_order(access_token, total_with_shipping)
        )

        messages.success(request, "Checkout complete!")
        cart.items.all().delete()
        return render(request, 'waiting_redirect.html', {'order_id': order.id})

    # Show form on GET
    return render(request, 'check_out_page.html', {
        'cart': cart,
        'customer': customer,
        'shipping_cost': shipping_cost,
        'total': total_with_shipping  # make sure this matches your template
    })


def order_summary_page(request, order_id):
    order = get_object_or_404(Order, id = order_id)
    shipment = Shipment.objects.filter(customer=order.order_customer_id).last()  # lastest shipment info in shipment database
    return render(request, 'order_summary_page.html', {
        'order': order,
        'order_items': order.items.all(),
        'shipment': shipment
    })


def user_order_page(request, customer_id):
    customer = get_object_or_404(Customer, id = customer_id)
    orders = Order.objects.filter(order_customer_id = customer).order_by('-order_created')
    return render(request, 'user_order_page.html', 
                  {'orders': orders,
                   'customer': customer})

def profile_page(request, customer_id):
    customer = get_object_or_404(Customer, id= customer_id)
    orders = Order.objects.filter(order_customer_id=customer)
    if request.method == "POST":
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        success, message = change_customer_password(customer_id, old_password, new_password, confirm_password)
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
    return render(request, 'profile_page.html', {'customer': customer,
                                                 'orders': orders})
    