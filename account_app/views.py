from django.shortcuts import render,redirect,get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from category_app.models import Category
from django.contrib.auth.decorators import login_required
from user.models import CustomUser
from user.validators import validate_password
from .models import Address
from .validators import validate_address_data,validate_first_name,validate_last_name,phone_validate
from order_app.models import Order,OrderItem
from django.views.decorators.http import require_POST
from product_app.models import ProductSize
from django.utils import timezone
from django.contrib import messages
from wallet_app.models import Wallet,WalletTransaction
from django.core.paginator import Paginator
import razorpay
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.contrib.auth import logout

# Create your views here.

#=========================USER ACCOUNT VIEW==============================#
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

#=========================USER ACCOUNT VIEW END==============================#



#=========================USER INFO EDIT SECTION==============================#
@csrf_exempt
@login_required
def update_user_info(request):

    if request.method == 'POST':
        user = get_object_or_404(CustomUser, id = request.user.id)
        gender = request.POST.get('gender')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        date_of_birth = request.POST.get('dob')
        phone_number = request.POST.get('phone_number')
        
        first_name_error = validate_first_name(first_name)
        last_name_error = validate_last_name(last_name)
        phone_error = phone_validate(phone_number, user_id=user.id)

        # Check for any validation errors
        errors = {}
        if first_name_error:
           errors['first_name'] = first_name_error
        if last_name_error:
            errors['last_name'] = last_name_error
        if phone_error:
            errors['phone_number'] = phone_error

        if errors:
            return JsonResponse({'success': False, 'error': errors}, status=400)
        
        user.gender = gender
        user.first_name = first_name
        user.last_name = last_name
        user.date_of_birth = date_of_birth
        user.phone_number = phone_number
        user.save()
        
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

#=========================USER INFO EDIT SECTION END==============================#


#=========================USER ADDRESS ADD AND EDIT SECTION==============================#

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
        
        # Check if there is a 'next' parameter in the POST data
        next_page = request.POST.get('next')
        if next_page:
            return redirect(next_page)

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
        

        address.name = request.POST.get('full_name')
        address.address_title = request.POST.get('address_title')
        address.state = request.POST.get('state')
        address.city = request.POST.get('city')
        address.pin = request.POST.get('pincode')
        address.post_office = request.POST.get('post_office')
        address.phone_number = request.POST.get('phone')
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
        'full_name': address.name,
        'address_title': address.address_title,
        'state': address.state,
        'city': address.city,
        'pincode': address.pin,
        'post_office': address.post_office,
        'phone': str(address.phone_number),
        'address_line': address.address_line,
        'landmark': address.landmark,
    })

#=========================USER ADDRESS ADD AND EDIT SECTION END==============================#


#=========================USER PASSWORD SECTION==============================#
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
            logout(request)
            return JsonResponse({'success': True, 'message': 'Password changed successfully. You have been logged out.'})
        else:
            return JsonResponse({'success': False, 'errors': ['Incorrect current password.']})
    
    return redirect('user_account')

#=========================USER PASSWORD SECTION END==============================#


#=========================USER ORDERS SECTION==============================#
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
    else:
        messages.error(request, 'Cannot request return. Return period may have expired.')


    return redirect('user_account')


@login_required
def order_details(request,order_id):

    order = get_object_or_404(Order, id=order_id)

    context = {

        'order' : order,
    }

    return render(request,'order_details.html',context)

#=========================USER ORDERS SECTION END==============================#


#=========================PAYMENT RETRY SECTION==============================#
@login_required
@csrf_exempt
def retry_payment(request,order_id):

    try:
        order = Order.objects.get(id=order_id, ordered_user=request.user, payment_status='Pending')

    except Order.DoesNotExist:
        messages.error(request, 'Invalid order or payment already completed.')
        return redirect('order_details')  # Redirect to order history or appropriate page
    
    amount = int(order.total_amount * 100)

    try:
        # Create a new Razorpay order
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create({
            'amount': amount,
            'currency': 'INR',
            'payment_capture': '1'
        })

        # Update the order with the new Razorpay order ID
        order.razorpay_order_id = razorpay_order['id']
        order.save()

        # Return the Razorpay order details to the frontend
        return JsonResponse({
            'id': razorpay_order['id'],
            'amount': amount,
            'currency': 'INR',
            'key': settings.RAZORPAY_KEY_ID,
            'order_id': order.id,
        })
    except Exception as e:
        # print(f"Error creating Razorpay order for retry: {str(e)}")
        return JsonResponse({'error': 'Failed to create Razorpay order for retry'}, status=500)
    
#=========================PAYMENT RETRY SECTION END==============================#



#=========================INVOICE SECTION==============================#

def generate_invoice_pdf(order,order_items):
    # Render the HTML template with the order context
    html = render_to_string('Invoice.html', {'order': order,'order_items' : order_items})
    
    # Create a BytesIO buffer to receive the PDF content
    pdf_buffer = BytesIO()
    
    # Create a PDF using xhtml2pdf
    pisa_status = pisa.CreatePDF(
        html, dest=pdf_buffer
    )
    
    if pisa_status.err:
        return None
    
    pdf_buffer.seek(0)
    return pdf_buffer


def download_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    
    # Check if the user has permission to download this invoice
    if request.user != order.ordered_user:
        return HttpResponseForbidden("You don't have permission to download this invoice.")
    
    # Check if the payment status is 'Paid'
    if order.payment_status != 'Paid':
        return HttpResponseForbidden("Invoice is not available. Payment status is not 'Paid'.")
    
    # Generate invoice number if it doesn't exist
    invoice_number = order.generate_invoice_number()
    
    # Generate the PDF
    pdf_buffer = generate_invoice_pdf(order,order_items)

    if pdf_buffer is None:
        return HttpResponse("There was an error generating the PDF.", status=500)
    
    # Create the HTTP response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice_number}.pdf"'
    response.write(pdf_buffer.getvalue())
    
    return response

#=========================INVOICE SECTION END==============================#