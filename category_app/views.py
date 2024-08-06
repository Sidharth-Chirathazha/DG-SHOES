from django.shortcuts import render,redirect,get_object_or_404
from .models import Category,SubCategory
from django.contrib.auth.decorators import user_passes_test
from product_app.models import Product
from offer_app.models import Offer
from django.contrib import messages
from django.urls import reverse

# Create your views here.

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

            category = Category.objects.get(category_name__iexact = category_name)
            print("Category already exists")
        else:

            category = Category(category_name = category_name,image = category_image)
            category.save()
            print("category created")

        
        categories = Category.objects.all()

    return render(request,'category_list.html',{'categories':categories})


# def deleteCategory(request,category_name):

#     if request.method == 'POST':

#         Category.objects.filter(category_name=category_name).delete()

#     return redirect('category_list')
    
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

                print("Category already exists")
            else:

                subcategory = SubCategory(subcategory_name = subcategory_name,category = parent_category,image=subcategory_image)
                subcategory.save()
                print("category created")

        
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

    print(f"Unlisted {len(products_under)} products under {subcategory.subcategory_name}")


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
    
    print(f"Listed {len(products_under)} products under {subcategory.subcategory_name}")

           
    return redirect('subcategory_list')


def apply_or_disable_offer(request,subcategory_id):

    subcategory = get_object_or_404(SubCategory,id=subcategory_id)
    offer_id = request.POST.get('offer_id')
    disable_offer = request.POST.get('disable')

    if offer_id:
        offer = get_object_or_404(Offer, id=offer_id)
        if offer.offer_type == 'subcategory':
            subcategory.discount_percentage = offer.discount_percentage
            subcategory.is_offer_applied = True
            subcategory.save()
            products = Product.objects.filter(subcategory_id = subcategory)
            for product in products:
                if product.is_offer_applied == False:
                    product.discount_percentage = offer.discount_percentage
                    product.is_offer_applied = True
                    product.save()
                else:
                    product.save()

    elif disable_offer:
        subcategory.is_offer_applied = False
        subcategory.discount_percentage = 0
        subcategory.save()
        products = Product.objects.filter(subcategory_id=subcategory)
        for product in products:
            product.discount_percentage = 0
            product.is_offer_applied = False
            product.save()
        
    return redirect(reverse('subcategory_list'))


