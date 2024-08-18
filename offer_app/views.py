from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Offer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import user_passes_test
from .validators import validate_offer_data


# Create your views here.
@user_passes_test(lambda u: u.is_superuser, login_url="/admin_login/")
def offers_view(request):

    offers = Offer.objects.all()

    for offer in offers:
        offer.update_active_status()

    query = request.GET.get('q')

    if query:
        offers = offers.filter(name__icontains=query)
    else:
        offers = offers
    

    context = {

        'offers': offers,
        'query': query,
        'username' : request.user.username,
    }
    return render(request, 'offers.html', context)


@user_passes_test(lambda u: u.is_superuser, login_url="/admin_login/")
def add_offer(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        discount_percentage = request.POST.get('discount_percentage')
        offer_type = request.POST.get('offer_type')

        errors = validate_offer_data(name,start_date,end_date,discount_percentage)

        if errors:
            return JsonResponse({'status': 'error', 'message': errors})
        
         # Create the offer
        offer = Offer(
            name=name,
            start_date=start_date,
            end_date=end_date,
            discount_percentage=discount_percentage,
            offer_type=offer_type,
            is_active = True
        )
        offer.save()
    
        messages.success(request, 'Offer has been added successfully.')
        return JsonResponse({'status': 'success', 'message': 'Offer added successfully'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@user_passes_test(lambda u: u.is_superuser, login_url="/admin_login/")
@csrf_exempt
def edit_offer(request):
    if request.method == 'POST':
        offer_id = request.POST.get('offer_id')
        offer = get_object_or_404(Offer, id=offer_id)

        name = request.POST.get('name')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        discount_percentage = request.POST.get('discount_percentage')
        offer_type = request.POST.get('offer_type')

        errors = validate_offer_data(name,start_date,end_date,discount_percentage)

        if errors:
            return JsonResponse({'status': 'error', 'message': errors})
        
        offer.name = name
        offer.start_date = start_date
        offer.end_date = end_date
        offer.discount_percentage =discount_percentage
        offer.offer_type = offer_type
        offer.is_active = True
        
        offer.save()
        
        messages.success(request, 'Offer has been updated successfully.')
        return JsonResponse({'status': 'success', 'message': 'Offer updated successfully'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@user_passes_test(lambda u: u.is_superuser, login_url="/admin_login/")
@csrf_exempt
def delete_offer(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        offer_id = data.get('offer_id')
        offer = Offer.objects.get(id=offer_id)
        offer.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@user_passes_test(lambda u: u.is_superuser, login_url="/admin_login/")
@require_http_methods(["GET"])
def get_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    data = {
        'id': offer.id,
        'name': offer.name,
        'start_date': offer.start_date.strftime('%Y-%m-%d'),
        'end_date': offer.end_date.strftime('%Y-%m-%d'),
        'discount_percentage': offer.discount_percentage,
        'offer_type': offer.offer_type
    }
    return JsonResponse(data)

    
