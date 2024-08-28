from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
from order_app.models import Order,OrderItem
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from wallet_app.models import Wallet,WalletTransaction
from django.http import JsonResponse
from datetime import datetime, timedelta
from weasyprint import HTML
import xlsxwriter
from io import BytesIO
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.db.models import Sum, DecimalField,F
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear
from decimal import Decimal
import logging
from product_app.models import Product,ProductColorImage
from django.db.models import Count
from django.shortcuts import render
from weasyprint.text.fonts import FontConfiguration
from django.conf import settings
import os
from django.utils.timezone import make_aware
# from .utils import superuser_required

User = get_user_model()
# Create your views here.

logger = logging.getLogger(__name__)


#=========================DASHBOARD SECTION==============================#
@user_passes_test(lambda u: u.is_superuser, login_url="/admin_login/")
def dashboard(request):

    popular_products = OrderItem.objects.values(
        'product_size__product_data__product_id'
    ).annotate(
        total_orders=Sum('quantity')
    ).order_by('-total_orders')[:6]

    products = []
    for item in popular_products:
        product = Product.objects.get(id=item['product_size__product_data__product_id'])
        product_image = ProductColorImage.objects.filter(product_id=product).first()
        products.append({
            'product': product,
            'total_orders': item['total_orders'],
            'image': product_image.image_1 if product_image else None
        })

    context = {
        'username': request.user.username,
        'popular_products': products
        }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return get_dashboard_data(request)
    return render(request, 'dashboard.html', context)



def get_dashboard_data(request):
    period = request.GET.get('period', 'daily')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    start_date =  make_aware(datetime.strptime(start_date, '%Y-%m-%d')) if start_date else datetime.now() - timedelta(days=30)
    end_date =make_aware(datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)) if end_date else datetime.now()
    
    orders = Order.objects.filter(payment_status='Paid', order_date__range=(start_date, end_date))
    
    trunc_func = {
        'daily': TruncDay,
        'weekly': TruncWeek,
        'monthly': TruncMonth,
        'yearly': TruncYear
    }.get(period, TruncDay)
    
    data = orders.annotate(
        trunc_date=trunc_func('order_date')
    ).values('trunc_date').annotate(
        total=Sum(F('total_amount') + F('discount_amount') + F('offer_discount_total'), output_field=DecimalField()),
        discount=Sum(F('discount_amount') + F('offer_discount_total'), output_field=DecimalField())
    ).order_by('trunc_date')
    
    labels = [item['trunc_date'].strftime('%Y-%m-%d' if period == 'daily' else '%Y-%m-%d' if period == 'weekly' else '%Y-%m' if period == 'monthly' else '%Y') for item in data]
    total_values = [item['total'] for item in data]
    discount_values = [item['discount'] for item in data]
    
    # Calculate refunds
    refund_values = []
    for period_start in data:
        if period == 'daily':
            period_end = period_start['trunc_date'] + timedelta(days=1)
        elif period == 'weekly':
            period_end = period_start['trunc_date'] + timedelta(days=7)
        elif period == 'monthly':
            next_month = period_start['trunc_date'].replace(day=28) + timedelta(days=4)
            period_end = next_month - timedelta(days=next_month.day)
        else:  # yearly
            period_end = period_start['trunc_date'].replace(year=period_start['trunc_date'].year + 1)
        
        period_refunds = OrderItem.objects.filter(
            order__in=orders,
            order__order_date__range=(period_start['trunc_date'], period_end),
            status__in=['Cancelled', 'Return Completed']
        ).aggregate(
            refund_total=Sum(F('quantity') * F('price'), output_field=DecimalField())
        )['refund_total'] or Decimal('0.00')
        
        refund_values.append(period_refunds)
    
    # Calculate overall statistics
    overall_sales_count = orders.count()
    overall_order_amount = sum(total_values)
    total_discount_amount = sum(discount_values)
    final_total_amount = overall_order_amount - total_discount_amount
    overall_refund_amount = sum(refund_values)
    net_sales_amount = final_total_amount - overall_refund_amount
    ordered_items = OrderItem.objects.filter(order__in=orders).aggregate(Sum('quantity'))['quantity__sum'] or 0
    
    # Prepare data for the chart
    net_values = [total - discount - refund for total, discount, refund in zip(total_values, discount_values, refund_values)]
    
    response_data = {
        'labels': labels,
        'total_values': [str(v) for v in total_values],
        'discount_values': [str(v) for v in discount_values],
        'refund_values': [str(v) for v in refund_values],
        'net_values': [str(v) for v in net_values],
        'overall_sales_count': overall_sales_count,
        'overall_order_amount': str(overall_order_amount),
        'total_discount_amount': str(total_discount_amount),
        'final_total_amount': str(final_total_amount),
        'overall_refund_amount': str(overall_refund_amount),
        'net_sales_amount': str(net_sales_amount),
        'ordered_items': ordered_items,
    }

    logger.info(f"Dashboard data: {response_data}")

    return JsonResponse(response_data)
    
#=========================DASHBOARD SECTION END==============================#


#=========================SALES REPORT SECTION==============================#

@user_passes_test(lambda u: u.is_superuser, login_url="/admin_login/")
def sales_report(request):

    orders = Order.objects.filter(payment_status='Paid')

    # Get filter parameters
    start_date = request.GET.get('start_date','')
    end_date = request.GET.get('end_date','')

    if start_date and end_date:
        start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
        end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59))
        orders = orders.filter(order_date__range=(start_date, end_date))

    # Calculate overall sales count
    overall_sales_count = orders.count()

    # Calculate original total without discounts
    overall_order_amount = sum((order.total_amount + order.discount_amount + order.offer_discount_total) for order in orders)

    # Calculate total discount amount (coupons and offers)
    total_discount_amount = sum(order.discount_amount + order.offer_discount_total for order in orders)

    # Calculate final total after discounts
    final_total_amount = overall_order_amount - total_discount_amount

    detailed_orders = []
    overall_refund_amount = 0
    for order in orders:
        original_amount = order.total_amount + order.discount_amount + order.offer_discount_total
        final_amount = original_amount - (order.discount_amount + order.offer_discount_total)
        order_items = OrderItem.objects.filter(order=order)
        refund_amount = 0
        for item in order_items:
            if item.status == 'Cancelled' or item.status == 'Return Completed':
                    refund_amount += item.get_total_item_price()
        overall_refund_amount += refund_amount

        detailed_orders.append({

            'date': order.order_date,
            'order_id': order.order_unique_id,
            'payment_method' : order.payment_method,
            'customer_name': order.ordered_user.username,
            'original_amount' : original_amount,
            'coupon_discount': order.discount_amount,
            'offer_discount': order.offer_discount_total,
            'final_amount': final_amount,
            'refund_amount' : refund_amount,
        })


    paginator = Paginator(detailed_orders, 10)
    page_number = request.GET.get('page',1)
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'detailed_orders': detailed_orders,
            'overall_sales_count': overall_sales_count,
            'overall_order_amount': overall_order_amount,
            'total_discount_amount': total_discount_amount,
            'final_total_amount': final_total_amount - overall_refund_amount,
            'overall_refund_amount': overall_refund_amount,
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
        })
    
    
   
    context ={ 

        'username' : request.user.username,
        'overall_sales_count': overall_sales_count,
        'overall_order_amount': overall_order_amount,
        'total_discount_amount': total_discount_amount,
        'final_total_amount': final_total_amount - overall_refund_amount,
        'detailed_orders': detailed_orders,
        'overall_refund_amount':  overall_refund_amount,
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'start_date_passed' : start_date,
        'end_date_passed' : end_date,
        
        }

    return render(request, 'sales_report.html',context)



@user_passes_test(lambda u: u.is_superuser, login_url="/admin_login/")
def export_pdf(request):
    # Reuse the logic from the dashboard view
    orders = Order.objects.filter(payment_status='Paid')
    
    # Get filter parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date and end_date:
        start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
        end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59))
        orders = orders.filter(order_date__range=(start_date, end_date))

    
    # Calculate overall sales count
    overall_sales_count = orders.count()
    
    # Calculate original total without discounts
    overall_order_amount = sum((order.total_amount + order.discount_amount + order.offer_discount_total) for order in orders)
    
    # Calculate total discount amount (coupons and offers)
    total_discount_amount = sum(order.discount_amount + order.offer_discount_total for order in orders)
    
    # Calculate final total after discounts
    final_total_amount = overall_order_amount - total_discount_amount
    
    detailed_orders = []
    overall_refund_amount = 0
    for order in orders:
        original_amount = order.total_amount + order.discount_amount + order.offer_discount_total
        final_amount = original_amount - (order.discount_amount + order.offer_discount_total)
        order_items = OrderItem.objects.filter(order=order)
        refund_amount = 0
        for item in order_items:
            if item.status == 'Cancelled' or item.status == 'Return Completed':
                refund_amount += item.get_total_item_price()
        overall_refund_amount += refund_amount
        
        detailed_orders.append({
            'date': order.order_date,
            'order_id': order.order_unique_id,
            'payment_method' : order.payment_method,
            'customer_name': order.ordered_user.username,
            'original_amount': original_amount,
            'coupon_discount': order.discount_amount,
            'offer_discount': order.offer_discount_total,
            'final_amount': final_amount,
            'refund_amount': refund_amount,
        })
    
    context = {
        'overall_sales_count': overall_sales_count,
        'overall_order_amount': overall_order_amount,
        'total_discount_amount': total_discount_amount,
        'final_total_amount': final_total_amount - overall_refund_amount,
        'detailed_orders': detailed_orders,
        'overall_refund_amount': overall_refund_amount,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    # Render the HTML template
    html_string = render_to_string('sales_report_pdf_template.html', context)

    # Configure WeasyPrint
    font_config = FontConfiguration()
    base_url = settings.STATIC_ROOT if settings.STATIC_ROOT else os.path.join(settings.BASE_DIR, 'static')
    
    
    # Create a PDF file
    html = HTML(string=html_string, base_url=base_url)
    result = html.write_pdf(font_config=font_config)
    
    # Generate HTTP response
    response = HttpResponse(content_type='application/pdf;')
    response['Content-Disposition'] = 'attachment; filename=sales_report.pdf'
    response['Content-Transfer-Encoding'] = 'binary'
    response.write(result)
    
    return response



@user_passes_test(lambda u: u.is_superuser, login_url="/admin_login/")
def export_excel(request):
    # Reuse the logic from the dashboard view
    orders = Order.objects.filter(payment_status='Paid')
    
    # Get filter parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date and end_date:
        start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
        end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59))
        orders = orders.filter(order_date__range=(start_date, end_date))
    
    # Calculate overall totals
    overall_sales_count = orders.count()
    overall_order_amount = sum((order.total_amount + order.discount_amount + order.offer_discount_total) for order in orders)
    total_discount_amount = sum(order.discount_amount + order.offer_discount_total for order in orders)
    overall_refund_amount = 0
    
    # Create an in-memory output file for the new workbook
    output = BytesIO()
    
    # Create a workbook and add a worksheet
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    
    # Add a bold format to use to highlight cells
    bold = workbook.add_format({'bold': True})
    
    # Write summary data
    worksheet.write(0, 0, "Sales Report Summary", bold)
    worksheet.write(1, 0, "Sales Count:", bold)
    worksheet.write(1, 1, overall_sales_count)
    worksheet.write(2, 0, "Order Amount:", bold)
    worksheet.write(2, 1, overall_order_amount)
    worksheet.write(3, 0, "Discount:", bold)
    worksheet.write(3, 1, total_discount_amount)
    worksheet.write(4, 0, "Refunded Total:", bold)
    worksheet.write(4, 1, "To be calculated")  # Placeholder, will update later
    worksheet.write(5, 0, "Final Amount:", bold)
    worksheet.write(5, 1, "To be calculated")  # Placeholder, will update later
    
    # Add a blank row for separation
    current_row = 7
    
    # Write data headers
    headers = ['Date', 'Order ID', 'Customer', 'Original', 'Coupon', 'Offer', 'Final', 'Refunded']
    for col, header in enumerate(headers):
        worksheet.write(current_row, col, header, bold)
    current_row += 1
    
    # Iterate over the data and write it out row by row
    for order in orders:
        original_amount = order.total_amount + order.discount_amount + order.offer_discount_total
        final_amount = original_amount - (order.discount_amount + order.offer_discount_total)
        order_items = OrderItem.objects.filter(order=order)
        refund_amount = sum(item.get_total_item_price() for item in order_items if item.status in ['Cancelled', 'Return Completed'])
        
        overall_refund_amount += refund_amount
        
        worksheet.write(current_row, 0, str(order.order_date))
        worksheet.write(current_row, 1, order.order_unique_id)
        worksheet.write(current_row, 2, order.ordered_user.username)
        worksheet.write(current_row, 3, original_amount)
        worksheet.write(current_row, 4, order.discount_amount)
        worksheet.write(current_row, 5, order.offer_discount_total)
        worksheet.write(current_row, 6, final_amount)
        worksheet.write(current_row, 7, refund_amount or '-')
        current_row += 1
    
    # Update the summary with the final calculations
    final_total_amount = overall_order_amount - total_discount_amount - overall_refund_amount
    worksheet.write(4, 1, overall_refund_amount)
    worksheet.write(5, 1, final_total_amount)
    
    # Close the workbook before sending the data
    workbook.close()
    
    # Rewind the buffer
    output.seek(0)
    
    # Set up the Http response
    filename = 'sales_report.xlsx'
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename={filename}'
    
    return response

#=========================SALES REPORT SECTION END==============================#


#=========================ADMIN LOGIN,LOGOUT SECTION==============================#   
@never_cache
def adminLogin(request):

    if request.method == 'POST':

        username_or_email = request.POST.get('username_or_email')
        passwrod_check = request.POST.get('password')

        user_admin = authenticate(request, username = username_or_email, password = passwrod_check)

        if user_admin is not None and user_admin.is_superuser:
            
            login(request,user_admin)

            return redirect('dashboard')
    
        else:
            messages.error(request,'Invalid Login Credentials')

    return render(request,'admin_login.html')

@never_cache
def adminLogout(request):

    if request.user.is_superuser:
        logout(request)
    return redirect('admin_login')

#=========================ADMIN LOGIN,LOGOUT SECTION==============================# 


#=========================USER MANAGEMENT SECTION==============================#
@user_passes_test(lambda u: u.is_superuser, login_url="/admin_login/")
def user_management(request):

    user_info = User.objects.all()
    query = request.GET.get('q','')

    if query:
        user_info = user_info.filter(username__icontains = query)

    context = {

        'user_info' : user_info,
        'query' : query,
        'username' : request.user.username,
    }
    return render(request,'user_list.html',context)


@user_passes_test(lambda u: u.is_superuser, login_url="/admin_login/")
def block_user(request, user_id):

    user = get_object_or_404(User, pk=user_id)
    user.is_active = False
    user.save()
    return redirect('user_management')


@user_passes_test(lambda u: u.is_superuser, login_url="/admin_login/")
def unblock_user(request, user_id):

    user = get_object_or_404(User, pk=user_id)
    user.is_active = True
    user.save()
    return redirect('user_management')

#=========================USER MANAGEMENT SECTION END==============================#



#=========================ORDER MANAGEMENT SECTION==============================#
@user_passes_test(lambda u: u.is_superuser, login_url="/admin_login/")
def orders_list(request):
 
    orders = Order.objects.select_related('ordered_user','delivery_address')\
        .prefetch_related('order_items__product_size__product_data__product_id')\
            .order_by('-order_date')

    query = request.GET.get('q', '').strip()
    if query:
        orders = orders.filter(order_unique_id__icontains=query)

    paginator = Paginator(orders,6)
    page = request.GET.get('page',1)
    
    try:

        orders = paginator.page(page)
    
    except PageNotAnInteger:

        orders = paginator.page(1)
    
    except EmptyPage:

        orders = paginator.page(paginator.num_pages)

    
    context = {

        'orders' : orders,
        'query' : query,
        'username' : request.user.username,
    }
    
    return render(request,'order_list.html', context )

def confirm_order(request,item_id):

    order_item = get_object_or_404(OrderItem, id=item_id)
    order_item.status = 'Processing'
    order_item.save()
    # messages.success(request, 'Order item confirmed.')
    return redirect('order_list')

def return_order(request,item_id):

    order_item = get_object_or_404(OrderItem,id=item_id)

    if order_item.return_requested:
        order_item.status = 'Return Confirmed'
        order_item.return_requested = False  # Set return_requested to False
        order_item.save()
        messages.success(request, 'Return request has been processed.')
    else:
        messages.error(request, 'Return request cannot be processed.')

    return redirect('order_list')


@require_POST
def change_order_status(request, item_id):
    order_item = get_object_or_404(OrderItem, id=item_id)
    wallet = get_object_or_404(Wallet,user=order_item.order.ordered_user)
    current_status = order_item.status
    next_status = order_item.get_next_status_choices()[0] if order_item.get_next_status_choices() else None
    if next_status:
        order_item.status = next_status
        if next_status == 'Delivered' and order_item.return_eligible_day_one is None:
            if order_item.order.payment_method == 'COD':
                order_item.order.payment_status = 'Paid'
                order_item.order.save()
            order_item.return_eligible_day_one = timezone.now()
        order_item.save()

    if next_status == 'Return Completed':
        product_size = order_item.product_size
        product_size.quantity += order_item.quantity
        product_size.save()

        wallet_transaction = WalletTransaction(
            wallet = wallet,
            transaction_type = 'credit',
            amount = order_item.get_total_item_price(),
            description = 'return'
        )
        wallet_transaction.save()


    return redirect('order_list') 


@user_passes_test(lambda u: u.is_superuser, login_url="/admin_login/")
def order_info(request, order_id):

    order = get_object_or_404(Order,pk=order_id)

    context = {

        'order' : order,
        'username' : request.user.username,
    }

    return render(request,'order_info.html',context)

#=========================ORDER MANAGEMENT SECTION END==============================#