from django.shortcuts import render,redirect,get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from category_app.models import Category
from django.contrib.auth.decorators import login_required
from user.models import CustomUser
from user.validators import validate_password
from .models import Address
from .validators import validate_address_data
from order_app.models import Order,OrderItem
from django.views.decorators.http import require_POST
from product_app.models import ProductSize
from django.utils import timezone
from django.contrib import messages
from wallet_app.models import Wallet,WalletTransaction
from django.core.paginator import Paginator

# Create your views here.


@login_required
def user_account_view(request):

    categories = Category.objects.all().prefetch_related('subcategories')
    user = request.user
    user_addresses = Address.objects.filter(user=user,is_listed=True)
    user_orders = Order.objects.filter(ordered_user = user).prefetch_related('order_items__product_size__product_data__product_id', 'order_items__product_size__product_data').order_by('-order_date')


    # Pagination
    paginator = Paginator(user_orders, 5)  # Show 5 orders per page
    page_number = request.GET.get('page')
    user_orders = paginator.get_page(page_number)

    try:
        user_wallet = user.wallet

        all_wallet_transactions = user_wallet.transactions.all().order_by('-timestamp')
        wallet_paginator = Paginator(all_wallet_transactions, 5)  # Show 5 transactions per page
        wallet_page_number = request.GET.get('wallet_page')
        wallet_transactions = wallet_paginator.get_page(wallet_page_number)
    except Wallet.DoesNotExist:
        user_wallet = Wallet.objects.create(user=user)
        wallet_transactions = []

    context = {
        'categories' : categories,
        'user' : user,
        'user_addresses' : user_addresses,
        'user_orders' : user_orders,
        'user_wallet': user_wallet,
        'wallet_transactions': wallet_transactions, 
    }

    return render(request,'user_account.html',context)


@csrf_exempt
@login_required
def update_user_info(request):

    if request.method == 'POST':
        user = get_object_or_404(CustomUser, id = request.user.id)
        user.gender = request.POST.get('gender')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.date_of_birth = request.POST.get('dob')
        user.email = request.POST.get('email')
        user.phone_number = request.POST.get('phone_number')
        user.save()
        
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@csrf_exempt
@login_required
def add_address(request):

    if request.method == 'POST':

        categories = Category.objects.all().prefetch_related('subcategories')
        user = request.user

        address_title = request.POST.get('address_title')
        full_name = request.POST.get('full_name')
        address = request.POST.get('address')
        post_office = request.POST.get('post_office')
        pincode = request.POST.get('pincode')
        city = request.POST.get('city')
        state = request.POST.get('state')
        phone = request.POST.get('phone')
        landmark = request.POST.get('landmark')

        errors = validate_address_data(address_title, full_name, address, post_office, pincode, city, state, phone)
        if errors:
            context = {
                'categories' : categories,
                'user' : user,
                'errors': errors,
                'address_title': address_title,
                'full_name': full_name,
                'address': address,
                'post_office': post_office,
                'pincode': pincode,
                'city': city,
                'state': state,
                'phone': phone,
                'landmark': landmark,
            }
            return render(request, 'user_account.html', context)
            
        
        address = Address(
            user=user,
            address_title=address_title,
            name=full_name,
            address_line=address,
            post_office=post_office,
            pin=pincode,
            city=city,
            state=state,
            phone_number=phone,
            landmark=landmark,
        )

        address.save()

        return redirect('user_account')

    return redirect('user_account')

@csrf_exempt
@login_required
def edit_address(request):

    if request.method == 'POST':

        address_id = request.POST.get('address_id')
        if address_id:
            address = get_object_or_404(Address,id=address_id,user=request.user)
        else:
            return JsonResponse({'success': False, 'error': 'Address ID is missing'})
        

        address.name = request.POST.get('name')
        address.address_title = request.POST.get('address_title')
        address.state = request.POST.get('state')
        address.city = request.POST.get('city')
        address.pin = request.POST.get('pin')
        address.post_office = request.POST.get('post_office')
        address.phone_number = request.POST.get('phone_number')
        address.address_line = request.POST.get('address_line')
        address.landmark = request.POST.get('landmark')

        if not address.pin.isdigit() or len(address.pin) != 6:
            # Handle validation error
            return JsonResponse({'success': False, 'error': 'Invalid PIN code'})
        
        address.save()
        return redirect('user_account')
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

    
@login_required
def delete_address(request,address_id):

    address = get_object_or_404(Address, id=address_id,user=request.user)
    address.delete()
    return redirect('user_account')
    

@login_required
def get_address_details(request):

    address_id = request.GET.get('id')
    address = get_object_or_404(Address, id=address_id, user=request.user)

    return JsonResponse({
        'id': address.id,
        'name': address.name,
        'address_title': address.address_title,
        'state': address.state,
        'city': address.city,
        'pin': address.pin,
        'post_office': address.post_office,
        'phone_number': str(address.phone_number),
        'address_line': address.address_line,
        'landmark': address.landmark,
    })

@login_required
@csrf_exempt
def change_password(request):

    if request.method == 'POST':

        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_new_password = request.POST.get('confirm_new_password')

        error_message = validate_password(new_password)

        if error_message:
            return JsonResponse({'success': False, 'errors': [error_message]})
        if new_password != confirm_new_password:
            return JsonResponse({'success': False, 'errors': ['Passwords do not match.']})
        
        user = request.user
        if user.check_password(current_password):

            user.set_password(new_password)
            user.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': ['Incorrect current password.']})
    
    return redirect('user_account')


@login_required
@require_POST
def cancel_order_item(request,item_id):

    item = get_object_or_404(OrderItem, id=item_id, order__ordered_user = request.user)
    wallet = get_object_or_404(Wallet,user=request.user)

    if item.status not in ['Cancelled','Delivered']:
        item.status = 'Cancelled'
        item.save()

        product_size = item.product_size
        product_size.quantity += item.quantity
        product_size.save()

        if item.order.payment_method == 'Wallet' or item.order.payment_method == 'RazorPay':
           wallet_transaction = WalletTransaction(
               
               wallet = wallet,
               transaction_type = 'credit',
               amount = item.get_total_item_price(),
               description = 'cancellation'
           )
           wallet_transaction.save()
    
    return redirect('user_account')


@login_required
@require_POST
def return_order_item(request,item_id):

    order_item = get_object_or_404(OrderItem, id=item_id, order__ordered_user = request.user)

    if order_item.status == 'Delivered' and  order_item.can_request_return():

        order_item.status = 'Returned'
        order_item.return_requested = True
        order_item.save()
        messages.success(request, 'Order return requested successfully.')
        print("item returned")
    else:
        messages.error(request, 'Cannot request return. Return period may have expired.')
        print("item not returned")


    return redirect('user_account')


@login_required
def order_details(request,order_id):

    order = get_object_or_404(Order, id=order_id)

    context = {

        'order' : order,
    }

    return render(request,'order_details.html',context)