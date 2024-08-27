from django.shortcuts import render,redirect,get_object_or_404
from .models import Category,SubCategory
from django.contrib.auth.decorators import user_passes_test
from product_app.models import Product
from offer_app.models import Offer
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

# Create your views here.

#=========================CATEGORY MANAGEMENT SECTION==============================#
@user_passes_test(lambda u: u.is_superuser, login_url="/admin_login/")
def categoryList(request):
    context = {

        'username'  : request.user.username,
        'categories' : Category.objects.all()
    }
    return render(request,'category_list.html',context)


@user_passes_test(lambda u: u.is_superuser, login_url="/admin_login/")
def addCategory(request):

    if request.method == 'POST':

        category_name = request.POST['category_name']
        category_image = request.FILES.get('category_image')

        category_exists = Category.objects.filter(category_name__iexact = category_name).exists()

        if category_exists:
            messages.error(request,f"Category {category_name} already exists.")
        else:
            category = Category(category_name = category_name,image = category_image)
            category.save()

        
        categories = Category.objects.all()

    return render(request,'category_list.html',{'categories':categories})


@user_passes_test(lambda u: u.is_superuser, login_url="/admin_login/")
def editCategory(request):
    if request.method == 'POST':
        category_id = request.POST['category_id']
        category_name = request.POST['category_name']
        category_image = request.FILES.get('category_image')

        category_exists = Category.objects.filter(category_name__iexact = category_name).exclude(id=category_id).exists()

        if category_exists:
            messages.error(request,f"Category {category_name} already exists.")
        else:
            category = get_object_or_404(Category, id=category_id)
            category.category_name = category_name
            if category_image:
                category.image = category_image
            category.save()
            messages.success(request,f"Category {category_name} updated successfully.")
            return redirect('category_list') 

    return redirect('category_list')
#=========================CATEGORY MANAGEMENT SECTION END==============================#


#=========================SUBCATEGORY MANAGEMENT SECTION==============================#    
@user_passes_test(lambda u: u.is_superuser, login_url="/admin_login/")
def subcategoryList(request):

    subcategories = SubCategory.objects.all()
    offers = Offer.objects.filter(is_active = True, offer_type = 'subcategory')

    context = {

        'username'  : request.user.username,
        'subcategories' : subcategories,
        'categories' : Category.objects.all(),
        'offers' : offers,
     }
    return render(request,'subcategory_list.html',context)

@user_passes_test(lambda u: u.is_superuser, login_url="/admin_login/")
def addSubCategory(request):

    if request.method == 'POST':
        try:

            subcategory_name = request.POST['subcategory_name']
            subcategory_image = request.FILES.get('subcategory_image')
            parent_category_id = request.POST['parent_category']

            try:

                parent_category = Category.objects.get(id=parent_category_id)

            except Category.DoesNotExist:

                parent_category = None

            subcategory_exists = SubCategory.objects.filter(subcategory_name__iexact = subcategory_name,
                                                            category = parent_category).exists()

            if subcategory_exists:

                messages.error(request,f"Subcategory {subcategory_name} already exists.")
            else:

                subcategory = SubCategory(subcategory_name = subcategory_name,category = parent_category,image=subcategory_image)
                subcategory.save()
                messages.success(request,f"{subcategory_name} added successfully.")

        
            context = {

                'subcategories' : SubCategory.objects.all(),
                'categories' : Category.objects.all()
            }

            return render(request,'subcategory_list.html',context)
        
        except KeyError as e:
            print(f"KeyError: {e}") 
    
    context = {

                'subcategories' : SubCategory.objects.all(),
                'categories' : Category.objects.all()
            }

    return render(request,'subcategory_list.html',context)



@user_passes_test(lambda u: u.is_superuser, login_url="/admin_login/")
@require_http_methods(["GET", "POST"])
def editSubCategory(request, subcategory_id):
    subcategory = get_object_or_404(SubCategory, id=subcategory_id)
    
    if request.method == 'GET':
        data = {
            'id': subcategory.id,
            'name': subcategory.subcategory_name,
            'parent_category_id': subcategory.category.id if subcategory.category else '',
            'image_url': subcategory.image.url if subcategory.image else ''
        }
        return JsonResponse(data)
    
    elif request.method == 'POST':
        try:
            subcategory_name = request.POST['subcategory_name']
            parent_category_id = request.POST['parent_category']
            
            try:
                parent_category = Category.objects.get(id=parent_category_id)
            except Category.DoesNotExist:
                parent_category = None
            
            subcategory_exists = SubCategory.objects.filter(
                subcategory_name__iexact=subcategory_name,
                category=parent_category
            ).exclude(id=subcategory_id).exists()
            
            if subcategory_exists:
                return JsonResponse({'status': 'error', 'message': f"Subcategory {subcategory_name} already exists."})
            else:
                subcategory.subcategory_name = subcategory_name
                subcategory.category = parent_category
                
                if 'subcategory_image' in request.FILES:
                    subcategory.image = request.FILES['subcategory_image']
                
                subcategory.save()
                return JsonResponse({'status': 'success', 'message': f"{subcategory_name} updated successfully."})
        
        except KeyError as e:
            print(f"KeyError: {e}")
            return JsonResponse({'status': 'error', 'message': "An error occurred while updating the subcategory."})


def unlist_subcategory(request,category_id,subcategory_id):

    if request.method == 'POST':

        category = get_object_or_404(Category,id=category_id)
        subcategory = get_object_or_404(SubCategory,id=subcategory_id,category=category)

        subcategory.is_listed = False
        subcategory.save()
        
        products_under = Product.objects.filter(subcategory_id=subcategory)
        for product in products_under:
            product.is_listed = False
            product.save()


    return redirect('subcategory_list')


def list_subcategory(request,category_id,subcategory_id):

    if request.method == 'POST':

        category = get_object_or_404(Category,id=category_id)
        subcategory = get_object_or_404(SubCategory,id=subcategory_id,category=category)

        subcategory.is_listed = True
        subcategory.save()

        products_under = Product.objects.filter(subcategory_id=subcategory)
        for product in products_under:
            product.is_listed = True
            product.save()
           
    return redirect('subcategory_list')

#=========================SUBCATEGORY MANAGEMENT SECTION END==============================#

#=========================OFFER APPLY SECTION==============================#
def apply_or_disable_offer(request,subcategory_id):

    subcategory = get_object_or_404(SubCategory,id=subcategory_id)
    offer_id = request.POST.get('offer_id')
    disable_offer = request.POST.get('disable')

    if offer_id:
        offer = get_object_or_404(Offer, id=offer_id)
        if offer.offer_type == 'subcategory':
            subcategory.discount_percentage = offer.discount_percentage
            subcategory.is_offer_applied = True
            subcategory.applied_offer = offer
            subcategory.save()
            products = Product.objects.filter(subcategory_id = subcategory)
            for product in products:
                if product.is_offer_applied == False:
                    product.discount_percentage = offer.discount_percentage
                    product.is_offer_applied = True
                    product.applied_offer = offer
                    product.save()
                else:
                    product.save()

    elif disable_offer:
        subcategory.is_offer_applied = False
        subcategory.discount_percentage = 0
        subcategory.applied_offer = None
        subcategory.save()
        products = Product.objects.filter(subcategory_id=subcategory)
        for product in products:
            product.discount_percentage = 0
            product.is_offer_applied = False
            product.applied_offer = None
            product.save()
        
    return redirect(reverse('subcategory_list'))

#=========================OFFER APPLY SECTION END==============================#
