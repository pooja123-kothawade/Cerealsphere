from django.shortcuts import render, redirect
from store.models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login as django_login
from django.contrib.auth.decorators import login_required
from cart.cart import Cart
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def home(request):
    cat_items = CatagoryItems.objects.all()
    products = Product.objects.all()
    categories = Category.objects.all()
    context = {
        "items" : cat_items,
        "products":products,
        "categories" :categories
    }
    return render(request, "index.html", context)

def base(request):
    return render(request, "base.html")

def features(request):
    return render(request, "features.html")

def featureFresh(request):
    return render(request, "freshAndOrg.html")

def freeDel(request):
    return render(request, "free.html")

def easyPay(request):
    return render(request, "easyPayment.html")

def categories(request):
    cat_items = CatagoryItems.objects.all()
    context = {
        "items" : cat_items
    }
    return render(request, "categories.html", context)

def product(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    context = {
        "products":products,
        "categories" :categories
    }
    return render(request, "product.html", context)
    
def Search(request):
    query = request.GET.get("query")
    products = Product.objects.filter(name__icontains = query)
    context = {
        "products":products,
    }
    return render(request, "search.html", context)

def register(request):
    if request.method =="POST":
        username = request.POST.get("username")
        firstName = request.POST.get("firstName")
        lastName = request.POST.get("lastName")
        email = request.POST.get("email")
        username = request.POST.get("username")
        pass1 = request.POST.get("pass1")
        pass2 = request.POST.get("pass2")

        customer = User.objects.create_user(username, email, pass1)
        customer.first_name = firstName
        customer.last_name = lastName
        customer.save()
        return redirect("login")
    return render(request, "register.html")

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            django_login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error_message': 'Invalid login credentials'})
    else:
        return render(request, 'login.html')
    
def logout(request):
    auth_logout(request)
    return redirect("home")

@login_required(login_url="/login/")
def cart_add(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.add(product=product)
    return redirect("home")


@login_required(login_url="/login/")
def item_clear(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.remove(product)
    return redirect("cart_detail")


@login_required(login_url="/login/")
def item_increment(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.add(product=product)
    return redirect("cart_detail")


@login_required(login_url="/login/")
def item_decrement(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.decrement(product=product)
    return redirect("cart_detail")


@login_required(login_url="/login/")
def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect("cart_detail")


@login_required(login_url="/login/")
def cart_detail(request):
    return render(request, 'cart/cart_detail.html')


def Checkout(request):
    amount_str = request.POST.get("amount")
    amount_flo = float(amount_str)
    amount_dec = Decimal(amount_flo).quantize(Decimal('1'))
    amount = int(amount_dec)
    payment = client.order.create({
        "amount": amount * 100,  
        "currency": "INR",
        "payment_capture": "1"
    })
    order_id = payment["id"]
    context = {
        "order_id": order_id,
        "payment": payment
    }
    return render(request, "checkout.html", context)

def placeorder(request):
    if request.method == "POST":
        cart = request.session.get('cart')
        uid = request.session.get('_auth_user_id')
        user = User.objects.get(id = uid)
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        country = request.POST.get("country")
        address = request.POST.get("address")
        date = request.POST.get("date")
        state = request.POST.get("state")
        city = request.POST.get("city")
        zipcode = request.POST.get("zipcode")
        total_amount = request.POST.get("total_amount")
        # payment_method = request.POST.get("payment_method")
        order_id = request.POST.get("order_id")
        payment = request.POST.get("payment")
        context = {
            "order_id":order_id
        }

        order = Order(
            user = user,
            first_name = first_name,
            last_name = last_name,
            phone = phone,
            email = email,
            country = country,
            address = address,
            state = state,
            city = city,
            zipcode = zipcode,
            total_amount = total_amount,
            # payment_method = payment_method,
            date = date
        )
        order.save()
        total = 0
        for i in cart:
            a = float(cart[i]['price'])
            b = int(cart[i]['quantity'])
            total = a * b
            item = OrderItem(
                order = order,
                product = cart[i]['name'],
                image = cart[i]['image'],
                price = cart[i]['price'],
                quantity = cart[i]['quantity'],
                total = total,
            )
            item.save()

    return render(request, "place_order.html", context)

@csrf_exempt
def thankYou(request):
    if request.method == "POST":
        a = request.POST
        order_id = ""
        for key, value in a.items():
            if key == "razorpay_order_id":
                order_id = value
                break

        user = Order.objects.filter(payment_id = order_id).first()
        # user.paid = True
        # user.save()
    

    return render(request, "thankyou.html")