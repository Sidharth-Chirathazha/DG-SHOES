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
# from .utils import superuser_required

User = get_user_model()
# Create your views here.


@user_passes_test(lambda u: u.is_superuser, login_url="/admin_login/")
def dashboard(request):

   
    context = { 'username' : request.user.username}

    return render(request, 'dashboard.html',context)



    
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


def forgot_admin_password(request):

    return render(request, )


@user_passes_test(lambda u: u.is_superuser, login_url="/admin_login/")
def user_management(request):

    user_info = User.objects.all()
    query = request.GET.get('q','')

    if query:
        user_info = user_info.filter(username__icontains = query)

    context = {

        'user_info' : user_info,
        'query' : query,
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


@user_passes_test(lambda u: u.is_superuser, login_url="/admin_login/")
def orders_list(request):

    orders = Order.objects.select_related('ordered_user','delivery_address').prefetch_related('order_items__product_size__product_data__product_id')

    query = request.GET.get('q')
    if query:
        orders = orders.filter(order_unique_id__icontains=query)

    page = request.GET.get('page',1)
    paginator = Paginator(orders,6)

    try:

        orders = paginator.page(page)
    
    except PageNotAnInteger:

        orders = paginator.page(1)
    
    except EmptyPage:

        orders = paginator.page(paginator.num_pages)


    context = {

        'orders' : orders,
        'query' : query,
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
    current_status = order_item.status
    next_status = order_item.get_next_status_choices()[0] if order_item.get_next_status_choices() else None
    if next_status:
        order_item.status = next_status
        if next_status == 'Delivered' and order_item.return_eligible_day_one is None:
            order_item.return_eligible_day_one = timezone.now()
        order_item.save()

    if next_status == 'Return Completed':
        product_size = order_item.product_size
        product_size.quantity += order_item.quantity
        product_size.save()


    return redirect('order_list') 


@user_passes_test(lambda u: u.is_superuser, login_url="/admin_login/")
def order_info(request, order_id):

    order = get_object_or_404(Order,pk=order_id)

    context = {

        'order' : order,
    }

    return render(request,'order_info.html',context)