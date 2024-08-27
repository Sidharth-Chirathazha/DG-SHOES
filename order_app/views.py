from django.shortcuts import render,redirect,get_object_or_404
from category_app.models import Category
from account_app.models import Address
from cart_app.models import Cart, CartItem
from django.contrib import messages
from django.utils import timezone
from .models import Order,OrderItem
from wallet_app.models import Wallet,WalletTransaction
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
# from django.template.loader import render_to_string
from coupon_app.models import Coupons
from django.views.decorators.http import require_POST
from decimal import Decimal
import razorpay
# from django.db import transaction
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json
from django.urls import reverse


# Create your views here.

#=========================CHECKOUT SECTION==============================#
@login_required
def checkout_view(request):

    categories = Category.objects.all().prefetch_related('subcategories')
    user = request.user
    user_addresses = Address.objects.filter(user=user,is_listed=True)
    active_coupons = Coupons.objects.filter(is_active=True)
    payment_method_choices = Order.PAYMENT_METHOD_CHOICES
    

    try:
        user_wallet = Wallet.objects.get(user=user)
    except Wallet.DoesNotExist:
        user_wallet = None

    try:
        cart = Cart.objects.get(user=user)
        cart_items = CartItem.objects.filter(cart=cart)
        cart_total = sum(item.get_total_price() for item in cart_items)
        cart_total_without_discount = sum((item.product.price * item.quantity) for item in cart_items)
        offer_total = cart_total_without_discount - cart_total

        #Apply coupon if one is already associated with cart
        coupon = cart.applied_coupon
        discount = 0
        if coupon and cart_total >= coupon.min_limit:
            if coupon.discount_amount:
                discount = min(coupon.discount_amount,cart_total)
            else:
                discount = (cart_total * Decimal(coupon.discount_percentage) / 100).quantize(Decimal('0.01'))
        
    except Cart.DoesNotExist:
        cart_items = []
        cart_total = 0
        coupon = None
        discount = 0
    

    if request.method == 'POST':
        selected_address_id = request.POST.get('selected_address')
        payment_method = request.POST.get('payment_method')
    

        if not selected_address_id:
            messages.error(request,'Please select a delivery address.')
        elif not payment_method:
            messages.error(request,'Please select a payment method.')
        else:
            selected_address = Address.objects.get(id=selected_address_id)


            # Calculate refund percent
            refund_percent = (discount/cart_total)*100 if discount != 0 else 0
            razorpay_order_id = None
            # final_amount = (cart_total - discount).quantize(Decimal('0.01'))

            
            # Check payment method and handle accordingly
            # Check payment method and handle accordingly
            if payment_method == 'Wallet':

                try:
                    user_wallet = user.wallet  
                except Wallet.DoesNotExist:
                    user_wallet = Wallet.objects.create(user=user)
                
                if user_wallet.balance >= (cart_total - discount):
                    # Create wallet transaction
                    WalletTransaction.objects.create(
                        wallet = user_wallet,
                        transaction_type = 'debit',
                        amount = (cart_total-discount),
                        description = 'purchase'
                    )
                    order,should_redirect = create_order(user, selected_address, payment_method, coupon, cart_total, discount,refund_percent, razorpay_order_id,offer_total)
                    if order:
                        return JsonResponse({
                            'success': True,
                            'message': 'Order placed successfully',
                            'redirect': reverse('order_success', args=[order.id])
                        })
                    if should_redirect:
                        return JsonResponse({
                            'success' : False,
                            'message' : "Some items in your cart are out of stock. Please review your cart.",
                            'redirect' : reverse('home')
                        })
                        # messages.error(request, "Some items in your cart are out of stock. Please review your cart.")
                        # return redirect('shop_list')
                    if not order:
                        return JsonResponse({
                            'success': False,
                            'message': "An error occurred while creating your order. Please try again.",
                            'redirect': reverse('home')  # Replace 'home' with your home page URL name
                        })
                else:
                    messages.error(request, 'Insufficient wallet balance.')
                    return redirect('checkout')
                
            elif payment_method == 'RazorPay':
                try:
                    # Create a Razorpay order
                    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                    amount = int((cart_total - discount) * 100)  # Amount in paise
                    razorpay_order = client.order.create({
                        'amount': amount,
                        'currency': 'INR',
                        'payment_capture': '1'
                    })

                    # Create a pending order in your database
                    razorpay_order_id = razorpay_order['id']
                    order,should_redirect = create_order(user, selected_address, payment_method, coupon, cart_total, discount, refund_percent, razorpay_order_id, offer_total)

                    # Return the Razorpay order details to the frontend
                    if order:
                        return JsonResponse({
                            'id': razorpay_order_id,
                            'amount': amount,
                            'currency': 'INR',
                            'key': settings.RAZORPAY_KEY_ID,
                            'order_id': order.id,
                        })
                    if should_redirect:
                        return JsonResponse({
                            'success' : False,
                            'message' : "Some items in your cart are out of stock. Please review your cart.",
                            'redirect' : reverse('home')
                        })
                        # messages.error(request, "Some items in your cart are out of stock. Please review your cart.")
                        # return redirect('shop_list')
                    if not order:
                        return JsonResponse({
                            'success': False,
                            'message': "An error occurred while creating your order. Please try again.",
                            'redirect': reverse('home')  # Replace 'home' with your home page URL name
                        })
                except Exception as e:
                    # print(f"Error creating Razorpay order: {str(e)}")
                    return JsonResponse({'error': 'Failed to create Razorpay order'}, status=500)
            
            else:
                # Handle other payment methods as before
                order,should_redirect = create_order(user, selected_address, payment_method, coupon, cart_total, discount, refund_percent, razorpay_order_id, offer_total)
                if order:
                    return JsonResponse({
                        'success': True,
                        'message': 'Order placed successfully',
                        'redirect': reverse('order_success', args=[order.id])
                    })
                if should_redirect:
                        return JsonResponse({
                            'success' : False,
                            'message' : "Some items in your cart are out of stock. Please review your cart.",
                            'redirect' : reverse('home')
                        })
                        # messages.error(request, "Some items in your cart are out of stock. Please review your cart.")
                        # return redirect('shop_list')
                if not order:
                    return JsonResponse({
                        'success': False,
                        'message': "An error occurred while creating your order. Please try again.",
                        'redirect': reverse('home')  # Replace 'home' with your home page URL name
                    })


    context = {

        'categories' : categories,
        'user' : user,
        'user_addresses' : user_addresses,
        'cart_items' : cart_items,
        'cart_total' : cart_total,
        'active_coupons' : active_coupons,
        'payment_method_choices' : payment_method_choices,
        'user_wallet' : user_wallet,
        'applied_coupon': coupon,
        'discount': discount,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
    }

    return render(request,'checkout.html',context)


def create_order(user,address,payment_method,coupon,cart_total,discount,refund_percent,razorpay_order_id,offer_total):

    # Create OrderItems and update product quantities
    cart = Cart.objects.get(user=user)
    cart_items = CartItem.objects.filter(cart=cart)
    for cart_item in cart_items:
        if cart_item.product_size.quantity < cart_item.quantity:
            messages.error(user.request, f"{cart_item.product.product_name} is out of stock.")
            return None, True  # Return None for order and True for redirect flag


    payment_status = 'Pending'
    if payment_method == 'Wallet':
        payment_status = 'Paid'
    order = Order.objects.create(

        ordered_user = user,
        payment_method = payment_method,
        coupon = coupon,
        total_amount = cart_total - discount,
        discount_amount = discount,
        order_date = timezone.now(),
        razorpay_order_id=razorpay_order_id,
        offer_discount_total = offer_total,
        payment_status = payment_status

    )
    order.set_delivery_address(address)
    order.save()
    for cart_item in cart_items:
        if cart_item.product.is_offer_applied:
           refund_amount =  (cart_item.product.discounted_price * ( Decimal(refund_percent)/ Decimal(100))).quantize(Decimal('0.01'))
           discounted_price = (cart_item.product.discounted_price - refund_amount).quantize(Decimal('0.01')) if refund_amount else cart_item.product.discounted_price
        else:
           refund_amount =  (cart_item.product.price * ( Decimal(refund_percent)/ Decimal(100))).quantize(Decimal('0.01'))
           discounted_price = (cart_item.product.price - refund_amount).quantize(Decimal('0.01')) if refund_amount else cart_item.product.price


        OrderItem.objects.create(

            order=order,
            product_size=cart_item.product_size,
            quantity=cart_item.quantity,
            price=discounted_price,
            status='Pending'
        )
        # Decrease product quantity
        cart_item.product_size.quantity -= cart_item.quantity
        cart_item.product_size.save()

    # Clear the cart
    cart_items.delete()
    cart.applied_coupon = None
    cart.save()

    return order,False
#=========================CHECKOUT SECTION END==============================#


#=========================RAZOR PAY PAYMENT VERIFICATION==============================#
@login_required
@csrf_exempt
def verify_payment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            params_dict = {
                'razorpay_payment_id': data['razorpay_payment_id'],
                'razorpay_order_id': data['razorpay_order_id'],
                'razorpay_signature': data['razorpay_signature']
            }
            client.utility.verify_payment_signature(params_dict)
            
            # Update the order status
            order = Order.objects.get(id=data['order_id'])
            order.payment_status = 'Paid'
            order.save()


            # Clear the cart
            cart = Cart.objects.get(user=order.ordered_user)
            cart.items.all().delete()

            # Return the URL for the order success page
            return JsonResponse({
                'success': True,
                'redirect_url': reverse('order_success', args=[order.id])
            })
        except Exception as e:
            # print(f"Payment verification failed: {str(e)}")
            order = Order.objects.get(id=data['order_id'])
            order.payment_status = 'Pending'
            order.save()
            return JsonResponse({
                'success': False, 
                'error': 'Payment verification failed',
                'redirect_url': reverse('order_details', args=[order.id])
            }, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

#=========================RAZOR PAY PAYMENT VERIFICATION END==============================#

#=========================ORDER SUCCESS VIEW==============================#
@login_required
def order_success_view(request,order_id):

    order = get_object_or_404(Order, id = order_id)
    order_items = OrderItem.objects.filter(order=order)
    categories = Category.objects.all().prefetch_related('subcategories')
    user = request.user

    context = {
        'order': order,
        'order_items': order_items,
        'categories': categories,
        'user' : user,
    }

    return render(request, 'order_success.html', context)

#=========================ORDER SUCCESS VIEW END==============================#

#=========================COUPON APPLY REMOVE SECTION==============================#
@login_required
@require_POST
def apply_coupon(request):
    coupon_code = request.POST.get('coupon_code')
    try:
        coupon = Coupons.objects.get(code=coupon_code, is_active=True)
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        cart_total = sum(item.get_total_price() for item in cart_items)

        if cart_total < coupon.min_limit:
            return JsonResponse({'status': 'error', 'message': f'Minimum purchase amount of Rs.{coupon.min_limit} required.'})

        if coupon.discount_amount:
            discount = min(coupon.discount_amount, cart_total)
        else:
            discount = (cart_total * Decimal(coupon.discount_percentage) / 100).quantize(Decimal('0.01'))

        new_total = cart_total - discount

        #Save the applied coupon to the cart
        cart.applied_coupon = coupon
        cart.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Coupon applied successfully!',
            'discount': str(discount),
            'new_total': str(new_total),
            'cart_total': str(cart_total)
        })

    except Coupons.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Invalid coupon code.'})
    except Cart.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Cart not found.'})
    


@login_required
@require_POST
def remove_coupon(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart.applied_coupon = None
        cart.save()

        cart_items = CartItem.objects.filter(cart=cart)
        cart_total = sum(item.get_total_price() for item in cart_items)

        return JsonResponse({
            'status': 'success',
            'message': 'Coupon removed successfully.',
            'cart_total': str(cart_total)
        })
    except Cart.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Cart not found.'})
    
#=========================COUPON APPLY REMOVE SECTION END==============================#

