from django.shortcuts import render,redirect,get_object_or_404
from .models import Coupons
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ValidationError
import logging
from django.contrib.auth.decorators import user_passes_test
from django.utils.dateformat import format
from django.db.models import Q
from django.utils import timezone
from .validators import validate_coupon_data
from datetime import datetime


logger = logging.getLogger(__name__)


# Create your views here.

@user_passes_test(lambda u: u.is_superuser, login_url="/admin_login/")
def coupons_view(request):

    query = request.GET.get('q', '')
   

   # Get all coupons and update their status
    all_coupons = Coupons.objects.all()
    for coupon in all_coupons:
        coupon.update_active_status()

    if query:
        coupons = all_coupons.filter(
            Q(title__icontains=query) | 
            Q(code__icontains=query) | 
            Q(description__icontains=query)
        )
    else:
        coupons = all_coupons

    if request.method == 'POST':
        coupon_id = request.POST.get('coupon_id')
        action = request.POST.get('action')
        coupon = get_object_or_404(Coupons,id=coupon_id)

        if action == 'enable' and not coupon.is_expired():
            coupon.is_active = True
        elif action == 'disable':
            coupon.is_active = False
        coupon.save()
        return redirect('coupons')
    
    context = {

        'coupons': coupons,
        'query': query,
        'username' : request.user.username,
    }

    return render(request,'coupons.html',context)




@user_passes_test(lambda u: u.is_superuser, login_url="/admin_login/")
def add_coupon(request):

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        valid_from = request.POST.get('valid_from')
        expiry = request.POST.get('expiry')
        discount_amount = request.POST.get('discount_amount')
        discount_percentage = request.POST.get('discount_percentage')
        min_limit = request.POST.get('min_limit')
        is_active = request.POST.get('is_active') == 'True'

        try:
            cleaned_data = validate_coupon_data(title, description, valid_from, expiry, discount_amount, discount_percentage, min_limit)
            # If validation passes, proceed with saving the coupon
            # Use cleaned_data to create your Coupon object
            coupon = Coupons(
                title=title,
                description=description,
                valid_from=valid_from,
                expiry=expiry,
                discount_amount=cleaned_data.get('discount_amount'),
                discount_percentage=cleaned_data.get('discount_percentage'),
                min_limit=cleaned_data['min_limit'],
                is_active=is_active
            )
            coupon.save()
            messages.success(request, 'Coupon created successfully.')
            return redirect('coupons')  # or wherever you want to redirect after successful creation
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)

    return redirect('coupons')



@user_passes_test(lambda u: u.is_superuser, login_url="/admin_login/")
def edit_coupon(request,coupon_id):

    try:
        coupon = Coupons.objects.get(id=coupon_id)
    except Coupons.DoesNotExist:
        messages.error(request, 'Coupon not found.')
        return redirect('coupons')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        valid_from = request.POST.get('valid_from')
        expiry = request.POST.get('expiry')
        discount_amount = request.POST.get('discount_amount')
        discount_percentage = request.POST.get('discount_percentage')
        min_limit = request.POST.get('min_limit')
        is_active = request.POST.get('is_active') == 'True'

        try :

            cleaned_data = validate_coupon_data(title, description, valid_from, expiry, discount_amount, discount_percentage, min_limit)


            # Update the coupon fields
            coupon.title = title
            coupon.description = description
            coupon.valid_from = valid_from
            coupon.expiry = expiry
            coupon.discount_amount = cleaned_data.get('discount_amount')
            coupon.discount_percentage = cleaned_data.get('discount_percentage')
            coupon.min_limit = cleaned_data['min_limit']
            coupon.is_active = is_active
            coupon.save()

            messages.success(request, 'Coupon updated successfully!')
        
        except Coupons.DoesNotExist:
            messages.error(request, 'Coupon not found.')
        except ValidationError as e:
            messages.error(request, f'Error updating coupon: {str(e)}')
        except Exception as e:
            logger.error(f"Error updating coupon: {e}", exc_info=True)
            messages.error(request, 'An error occurred while updating the coupon.')

        return redirect('coupons')

    # context = {
    #     'coupon': coupon,
    #     'formatted_valid_from': coupon.valid_from.strftime('%Y-%m-%d') if coupon.valid_from else '',
    #     'formatted_expiry': coupon.expiry.strftime('%Y-%m-%d') if coupon.expiry else '',
    # }

    return redirect('coupons')