from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.utils import timezone
from django.core.mail import send_mail,BadHeaderError
from .models import CustomUser
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
import random
import datetime
from .validators import validate_username,validate_email,validate_password,phone_validate,validate_first_name,validate_last_name
from category_app.models import Category,SubCategory
from product_app.models import Product,ProductColorImage,ProductSize
from django.core.paginator import Paginator
from django.db.models import Prefetch,Sum
from offer_app.models import Offer
from wallet_app.models import Wallet,WalletTransaction
from decimal import Decimal
from order_app.models import OrderItem
from django.db.models import Q


# Create your views here.

User = get_user_model()

#===============FUNTIONS TO GENERATE OTP and SEND MAIL====================#


def generateOtp():

    return str(random.randint(100000, 999999))

def send_email_otp(email,otp):
    try:
        subject = 'OTP Verification'
        message = f'Your OTP for registraion is : {otp}'
        sender = settings.EMAIL_HOST_USER
        receiver = [email]
        send_mail(
            subject,
            message,
            sender,
            receiver,
            fail_silently=False,

        )
        return True
    
    except BadHeaderError:

        print("BadHeaderError: Invalid header found in email.")
    
    except Exception as e:

        print(f"Error sending OTP via email: {e}")



#===============END====================#



#===============VIEW TO REGISTER USER====================#
@never_cache
def registerPage(request):

    if request.method == 'POST':

        gender = request.POST.get('gender')
        first_name = request.POST.get('f_name')
        last_name = request.POST.get('l_name')
        date_of_birth = request.POST.get('dob')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        referral_code = request.POST.get('referral_code')
        password = request.POST.get('password')
        password_cnf = request.POST.get('password_cnf')
        
        errors_message ={}

        first_name_error = validate_first_name(first_name)
        last_name_error = validate_last_name(last_name)

        if User.objects.filter(username = username).exists():
            username_error = 'Username already exist'
        else:
            username_error = validate_username(username)

        if User.objects.filter(email = email).exists():
            email_error = 'Email already exist'
        else:    
            email_error = validate_email(email)

        if User.objects.filter(phone_number = phone).exists():
            phone_error = 'Phone number already exist'
        else:
            phone_error = phone_validate(phone)

        if referral_code :
            if not User.objects.filter(referral_code = referral_code).exists():
                referral_code_error = 'Referral code does not match'
            else:
                referral_code_error = None
        else:
            referral_code_error = None

        if password != password_cnf:
            password_error = "Password doesn't match "
        else:
            password_error = validate_password(password)

        context = {
            'gender' : gender,
            'first_name' : first_name,
            'last_name' : last_name,
            'date_of_birth' : date_of_birth,
            'username' : username,
            'email' : email,
            'phone' : phone,
            'referral_code' : referral_code if referral_code else '',
            'password':password,
            'password_cnf':password_cnf
        }
        if not username or not email or not phone or not password or not password_cnf:
            messages.error(request, 'All fields are required')
            return render(request, 'register.html', context)
        
        if first_name_error:
            errors_message['f_name'] = first_name_error
        if last_name_error:
            errors_message['l_name'] = last_name_error
        if username_error:
            errors_message['username'] = username_error
        if email_error:
            errors_message['email'] = email_error
        if phone_error:
            errors_message['phone'] = phone_error
        if referral_code_error:
            errors_message['referral_code'] = referral_code_error
        if password_error:
            errors_message['password'] = password_error
        if not errors_message:
            # user = User.objects.create_user(username=username,email=email,phone_number=phone,password=password1)
            # my_user.save()
            otp = generateOtp()

            request.session['gender'] = gender
            request.session['first_name'] = first_name
            request.session['last_name'] = last_name
            request.session['date_of_birth'] = date_of_birth
            request.session['username'] = username
            request.session['email'] = email
            request.session['phone'] = phone
            request.session['referral_code'] = referral_code if referral_code else None
            request.session['password'] = password
            request.session['otp_value'] = otp
            otp_expiration = timezone.now() + datetime.timedelta(minutes=3)
            request.session['otp_expiration'] = otp_expiration.isoformat()

            send_email_otp(email,otp)
            messages.success(request,'An OTP has been sent to your email')
            return redirect('otp_verification')
        
        context['errors_message'] = errors_message
        return render(request,'register.html',context)
    
  
    return render(request,'register.html')

#===============END====================#


#===============VIEW FOR OTP VERIFICATION====================#
@never_cache
def otpVerification(request):

    if request.method == 'POST':
        gender = request.session.get('gender')
        first_name = request.session.get('first_name')
        last_name = request.session.get('last_name')
        date_of_birth = request.session.get('date_of_birth')
        username = request.session.get('username')
        email = request.session.get('email')
        phone = request.session.get('phone')
        referral_code = request.session.get('referral_code')
        password = request.session.get('password')
        otp_stored  = request.session.get('otp_value')
        otp_expiration_str = request.session.get('otp_expiration')
        otp_expiration = datetime.datetime.fromisoformat(otp_expiration_str)

        otp_entered = request.POST.get('otp')

        if otp_stored == otp_entered:

            if timezone.now() < otp_expiration:

                user = User.objects.create(username=username,email=email,phone_number=phone,
                                           password=password,first_name=first_name,last_name=last_name,gender=gender,date_of_birth=date_of_birth)
                user.set_password(password)
                user.save()

                # Create a wallet for the new user
                wallet = Wallet.objects.create(user=user)

                if referral_code:
                    try:
                        referred_by_user = User.objects.get(referral_code=referral_code)
                        user.referred_by = referred_by_user
                        user.save()
                        referred_by_user_wallet = Wallet.objects.get(user=referred_by_user)

                        referral_bonus = Decimal(settings.REFERRAL_BONUS_AMOUNT)
                        wallet_transaction = WalletTransaction(
                            wallet = referred_by_user_wallet,
                            transaction_type = 'credit',
                            amount = referral_bonus,
                            description = 'referral'
                        )
                        wallet_transaction.save()
                    except User.DoesNotExist:
                        pass  # Invalid referral code, do nothing

                request.session.flush()


                messages.success(request,"Account created successfully, Login into your account")
                return redirect('login')
            
            #For expired token
            else:
                messages.error(request,"The OTP has expired ! Resend OTP")
                return redirect('otp_verification')
            
        #For invalid token
        else:
            messages.error(request,"Invalid OTP! Enter valid OTP")
            return redirect('otp_verification')


    return render(request,'otp_verification.html',{'otp_expiration':request.session.get('otp_expiration')})

@never_cache
def resendOtp(request):

    email = request.session.get('email')

    if not email:
        return redirect('register')
    
    new_otp = generateOtp()

    request.session['otp_value'] = new_otp
    otp_expiration = timezone.now() + timezone.timedelta(minutes=3)
    request.session['otp_expiration'] = otp_expiration.isoformat()

    send_email_otp(email,new_otp)
    messages.success(request,'A new OTP has been send to your email')

    return redirect('otp_verification')

#===============END====================#


#===============VIEW TO USER LOGIN====================#
@never_cache
def loginPage(request):

    if request.method == 'POST':

        username_or_email = request.POST.get('username_or_email')
        password_check = request.POST.get('password')

        user = None


        try:
            user_by_email = User.objects.get(email = username_or_email)
            user = authenticate(request,username = user_by_email.username, password = password_check)
        except User.DoesNotExist:
            user = authenticate(request, username=username_or_email, password=password_check)

        if user is not None and user is not False :
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'Invalid Login Credentials')

    return render(request, 'login.html')

#===============END====================#


#===============VIEWS TO FORGOT PASSWORD AND VERIFY PASSWORD====================#
@never_cache
def forgotPassword(request):

    if request.method == 'POST':

        user_email = request.POST.get('pass_reset_email')

        if User.objects.filter(email =user_email).exists():

            user = User.objects.get(email = user_email)
            request.session['current_user_email'] = user.email
            
            reset_url = request.build_absolute_uri(reverse('verify_password'))
            subject = 'Reset Password'
            message = f"Hi {user.username}, Click on the link to reset password {reset_url}"

            sender = 'sidharthchirathazha@gmail.com'
            receiver = [user.email,]

            send_mail(
                subject,
                message,
                sender,
                receiver,
                fail_silently=False,
            )
            messages.success(request,'A password reset link has been send to your email')
    return render(request,'forgot_password.html')


@never_cache
def verifyPassword(request):

    if request.method == 'POST':
        current_email = request.session.get('current_user_email')
        password_check1 = request.POST.get('password_reset1')
        password_check2 = request.POST.get('password_reset2')

        if password_check1 == password_check2:

            current_user = User.objects.get(email = current_email)
            current_user.set_password(password_check1)
            current_user.save()
            messages.success(request,'Password has been changed successfully')
            request.session.flush()

            return redirect('login')
        
        else:
            messages.error(request,"Passwords doesn't match")
            return redirect('verify_password')


    return render(request,'verify_password.html')

#=========================END==============================#


#=========================INDEX , HOME PAGE VIEWS==============================#
@never_cache
@login_required
def homePage(request):

    categories = Category.objects.filter(is_listed = True).prefetch_related('subcategories').filter(subcategories__is_listed =True).distinct()
    first_name = request.user.first_name
    latest_products = Product.objects.filter(is_listed = True).order_by('-created_at')[:6]
    featured_products = Product.objects.filter(
            featured=True, 
            is_listed=True
        ).prefetch_related(
            Prefetch('productcolorimage_set', queryset=ProductColorImage.objects.filter(is_listed=True))
        )

    latest_product_colors = {}

    for product in latest_products:

        latest_color_image = ProductColorImage.objects.filter(product_id=product,is_listed=True).order_by('-created_at').first()
        if latest_color_image:
            latest_product_colors[product.id] = latest_color_image

    context = {

        'first_name' : first_name,
        'categories' : categories,
        'latest_product_colors' : latest_product_colors.values(),
        'featured_products' : featured_products,
    }
    return render(request,'home.html',context)


@never_cache
def indexPage(request):

    categories = Category.objects.filter(is_listed = True).prefetch_related('subcategories').filter(subcategories__is_listed =True).distinct()
    latest_products = Product.objects.filter(is_listed = True).order_by('-created_at')[:6]
    featured_products = Product.objects.filter(
            featured=True, 
            is_listed=True
        ).prefetch_related(
            Prefetch('productcolorimage_set', queryset=ProductColorImage.objects.filter(is_listed=True))
        )

    latest_product_colors = {}

    for product in latest_products:

        latest_color_image = ProductColorImage.objects.filter(product_id=product,is_listed=True).order_by('-created_at').first()
        if latest_color_image:
            latest_product_colors[product.id] = latest_color_image

    context = {

        'categories': categories,
        'latest_product_colors' : latest_product_colors.values(),
        'featured_products' : featured_products,
    }

    return render(request,'index.html',context)

#=========================END==============================#



#=========================LOGOUT VIEW==============================#

@login_required
def logoutView(request):

    if request.user.is_authenticated:
        logout(request)
    return redirect('login')

#=========================END==============================#



#=========================SHOP LIST AND PRODUCT DETAIL VIEWS==============================#
def shopList(request):
    
    category_name = request.GET.get('category')
    subcategory_name = request.GET.get('subcategory')
    query = request.GET.get('q','')
    sort_by = request.GET.get('sort', 'position')  # Default sort by position
     # Filter by color
    selected_colors = request.GET.getlist('color')  # Use getlist to get multiple colors
    selected_price_ranges = request.GET.getlist('price_ranges[]')

    categories = Category.objects.filter(is_listed = True).prefetch_related('subcategories').filter(subcategories__is_listed =True).distinct()
    products = Product.objects.filter(is_listed = True).prefetch_related('productcolorimage_set__product_size')

    if category_name:
        products = products.filter(category_id__category_name = category_name,is_listed=True)
        if subcategory_name:
            products = products.filter(subcategory_id__subcategory_name=subcategory_name,is_listed=True)
        
    if query:

        products = products.filter(product_name__icontains=query,is_listed=True)

    
    # Handle price range filtering
    if selected_price_ranges:
        price_filter = Q()
        for price_range in selected_price_ranges:
            if '-' in price_range:
                min_price, max_price = map(int, price_range.split('-'))
                price_filter |= Q(price__gte=min_price, price__lte=max_price)
            else:
                # Handle the "Above ₹6000" case
                min_price = int(price_range.rstrip('+'))
                price_filter |= Q(price__gte=min_price)
        
        products = products.filter(price_filter).distinct()

    
    color_images = []
    for product in products:
        color_images_for_product = product.productcolorimage_set.filter(is_listed=True)
        if selected_colors:
            color_images_for_product = color_images_for_product.filter(color_name__in=[color.capitalize() for color in selected_colors])


        for color_image in color_images_for_product:
            color_image.total_quantity = color_image.product_size.aggregate(
                total_quantity=Sum('quantity')
            )['total_quantity'] or 0
            color_images.append((product, color_image))

    # If no colors are selected and no color images were found, include all products
    if not selected_colors and not color_images:
        for product in products:
            for color_image in product.productcolorimage_set.filter(is_listed=True):
                color_image.total_quantity = color_image.product_size.aggregate(
                    total_quantity=Sum('quantity')
                )['total_quantity'] or 0
                color_images.append((product, color_image))


    if sort_by == 'price_asc':
        color_images.sort(key=lambda x: x[0].price)
    elif sort_by == 'price_desc':
        color_images.sort(key=lambda x: x[0].price, reverse=True)
    elif sort_by == 'name_asc':
        color_images.sort(key=lambda x: x[0].product_name)
    elif sort_by == 'name_desc':
        color_images.sort(key=lambda x: x[0].product_name, reverse=True)
    elif sort_by == 'latest':
        color_images.sort(key=lambda x: x[0].created_at, reverse=True)
    else:
        color_images.sort(key=lambda x: x[0].created_at, reverse=True) # Default ordering by latest


    paginator = Paginator(color_images,9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)



    context = {

        'categories': categories,
        'products' : products,
        # 'product_color_map': product_color_map,
        'selected_category': category_name,
        'selected_subcategory': subcategory_name,
        'page_obj' : page_obj,
        'sort_by' : sort_by,
        'selected_colors' : selected_colors,
        'selected_price_ranges': selected_price_ranges,
    }

    return render(request,'shop_list.html',context)




def product_detail_view(request,pk):

    categories = Category.objects.filter(is_listed = True).prefetch_related('subcategories').filter(subcategories__is_listed =True).distinct()
    product = get_object_or_404(Product, pk=pk, is_listed = True)
    color_variants = product.productcolorimage_set.filter(is_listed=True).prefetch_related('product_size')

    related_products = Product.objects.filter(
        category_id=product.category_id,
        subcategory_id=product.subcategory_id,
        is_listed=True,
        productcolorimage__is_listed=True
    ).exclude(id=product.id).distinct()[:3]


    selected_variant_id = request.GET.get('variant')
    selected_size_id = request.GET.get('size')
    max_quantity = 5

    if selected_variant_id:
        try:
            selected_variant = color_variants.get(id = selected_variant_id, product_id = product)
        except ProductColorImage.DoesNotExist:
            selected_variant = color_variants.first()
    else:
        selected_variant = color_variants.first()
    
    if selected_size_id and selected_variant:
        try:
            selected_size = selected_variant.product_size.get(id=selected_size_id)
            max_quantity = min(selected_size.quantity, 5)
        except ProductSize.DoesNotExist:
            selected_size = None
    else:
        selected_size = None

    context ={

        'categories' : categories,
        'product' : product,
        'color_variants' : color_variants,
        'selected_variant' : selected_variant,
        'selected_size' : selected_size,
        'max_quantity' : max_quantity,
        'related_products' : related_products,
     }

    return render(request,'product_detail.html',context)

#=========================END==============================#


#=========================CONTACT AND CUSTOM ERROR PAGE VIEWS==============================#
def contactUs(request):

    categories = Category.objects.filter(is_listed = True).prefetch_related('subcategories').filter(subcategories__is_listed =True).distinct()

    context = {

        'categories': categories,
    }

    return render(request,'contact-us.html',context)


def custom_404_view(request, exception):

    return render(request, '404.html', status=404)

#=========================END==============================#