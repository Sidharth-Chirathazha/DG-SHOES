from django.shortcuts import render,redirect,get_object_or_404
from .models import Product,ProductColorImage,ProductSize
from django.contrib.auth.decorators import user_passes_test
from category_app.models import Category,SubCategory
from django.utils.text import slugify
from django.http import JsonResponse
from django.http import HttpResponseBadRequest
from django.core.paginator import Paginator
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from offer_app.models import Offer
from django.urls import reverse
from decimal import Decimal
import base64
from django.core.files.base import ContentFile
from .validators import (
    validate_product_name,
    validate_category_and_subcategory,
    validate_description,
    validate_color_name,
    validate_images,
    validate_size,
    validate_quantity,
    validate_price,
    validate_product_name_for_edit
)
from django.contrib import messages
from django.core.exceptions import ValidationError


#=========================PRODUCT LIST VIEW==============================#
# Create your views here.
@user_passes_test(lambda u: u.is_superuser, login_url="/admin_login/")
def productList(request):

    products_info = Product.objects.distinct('product_name').prefetch_related('productcolorimage_set')
    query = request.GET.get('q','')
    offers = Offer.objects.filter(is_active = True, offer_type = 'product')

    if query:

        products_info = products_info.filter(product_name__icontains=query)

    
    paginator = Paginator(products_info,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
     
    context = {

        'page_obj' : page_obj,
        'query' : query,
        'offers' : offers
    }

    return render(request,'product_list.html',context)

#=========================PRODUCT LIST VIEW END==============================#



#=========================PRODUCT ADD AND EDIT SECTION==============================#
@user_passes_test(lambda u: u.is_superuser, login_url="/admin_login/")
def addProduct(request):

    if request.method == 'POST':
        try:
            product_name = request.POST.get('product_name')
            category_id = request.POST.get('category')
            subcategory_id = request.POST.get('subcategory')
            description = request.POST.get('description')
            color_name = request.POST.get('color')
            size = request.POST.get('size')
            image1 = request.FILES.get('product_image1')
            image2 = request.FILES.get('product_image2')
            image3 = request.FILES.get('product_image3')
            price = request.POST.get('price')
            quantity = request.POST.get('quantity')

            context = {
                'product_name': product_name,
                'category_id': category_id,
                'subcategory_id': subcategory_id,
                'description': description,
                'color_name': color_name,
                'size': size,
                'price': price,
                'quantity': quantity,
                'categories' : Category.objects.all(),
                'subcategories' : SubCategory.objects.all(),
                'sizes' : [size[0] for size in ProductSize.SIZE_CHOICES],
            }

            # Perform validations
            validate_product_name(product_name)
            validate_category_and_subcategory(category_id, subcategory_id)
            validate_description(description)
            validate_color_name(color_name)
            validate_images([image1, image2, image3])
            validate_size(size)
            validate_quantity(quantity)
            validate_price(price)

            price = Decimal(price)

            category = Category.objects.get(id=category_id)
            subcategory = SubCategory.objects.get(id=subcategory_id)

            if not subcategory.is_listed:
                
                is_listed = False
            else :
                is_listed = True

            product = Product(
                product_name = product_name,
                description = description,
                category_id = category,
                subcategory_id =subcategory,
                price = price,
                is_listed = is_listed,

            )
            product.save()

            product.slug = slugify(f'{product.subcategory_id.subcategory_name}-{product.product_name}')
            product.save()

            product_color_data = ProductColorImage(

                color_name = color_name,
                product_id = product,
                image_1 = image1,
                image_2 = image2,
                image_3 = image3
            )

            product_color_data.save()

            product_size =  ProductSize(

                size = size,
                product_data = product_color_data,
                quantity = quantity
            )

            product_size.save()

            messages.success(request, "Product added successfully!")
            return redirect('product_list')  # Replace with the appropriate URL
        except ValidationError as e:
            error_message = ' '.join(e.messages)
            messages.error(request, error_message)
            return render(request,'product_add.html',context)

    context = {

        'categories' : Category.objects.all(),
        'subcategories' : SubCategory.objects.all(),
        'sizes' : [size[0] for size in ProductSize.SIZE_CHOICES],
    }
    return render(request,'product_add.html',context)


@user_passes_test(lambda u: u.is_superuser, login_url="/admin_login/")
def editProduct(request,product_id):

    product = get_object_or_404(Product, id=product_id)
    product_images = product.productcolorimage_set.all().prefetch_related('product_size')

    if request.method == 'POST':
        try:
            product_name = request.POST.get('product_name')
            category_id = request.POST.get('category')
            subcategory_id = request.POST.get('subcategory')
            description = request.POST.get('description')
            price = request.POST.get('price')

            validate_product_name_for_edit(product_name,product_id)
            validate_category_and_subcategory(category_id,subcategory_id)
            validate_description(description)
            validate_price(price)

            price = Decimal(price)

            if not category_id:
                return HttpResponseBadRequest("Category ID is required.")
            if not subcategory_id:
                return HttpResponseBadRequest("Subcategory ID is required.")

            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                return HttpResponseBadRequest(f"Category with ID {category_id} does not exist.")

            try:
                subcategory = SubCategory.objects.get(id=subcategory_id)
            except SubCategory.DoesNotExist:
                return HttpResponseBadRequest(f"Subcategory with ID {subcategory_id} does not exist.")

            product.product_name = product_name
            product.description = description
            product.price = price
            product.category_id = category
            product.subcategory_id = subcategory
            product.save()


            messages.success(request, "Product updated successfully!")
            return redirect('product_list')  # Replace with the appropriate URL
        except ValidationError as e:
            error_message = ' '.join(e.messages)
            messages.error(request, error_message)
            return redirect(reverse('product_edit', args=[product_id]))
        
    context = {

        'product' : product,
        'categories': Category.objects.all(),
        'subcategories': SubCategory.objects.all(),

    }
    return render(request,'product_edit.html',context)

#=========================PRODUCT ADD AND EDIT SECTION END==============================#


#=========================PRODUCT COLOR VARIANT SECTION==============================#

def list_products_view(request,color_image_id):
    
    color_image = get_object_or_404(ProductColorImage,id=color_image_id)
    color_image.is_listed = True
    color_image.save()
    return redirect('variant_list',product_id=color_image.product_id.id)

def unlist_products_view(request,color_image_id):

    color_image = get_object_or_404(ProductColorImage,id=color_image_id)
    color_image.is_listed = False
    color_image.save()
    return redirect('variant_list', product_id=color_image.product_id.id)



@user_passes_test(lambda u: u.is_superuser, login_url="/admin_login/")
def variant_list_view(request,product_id):

    product = get_object_or_404(Product, id = product_id)
    related_products = Product.objects.filter(product_name = product.product_name)
    color_images_related = ProductColorImage.objects.filter(product_id__in=related_products)
    

    paginator = Paginator(color_images_related, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'product' : product,
        'related_products' : related_products,
        'page_obj' : page_obj,
    }

    return render(request,'variant_list.html',context)



@user_passes_test(lambda u: u.is_superuser, login_url="/admin_login/")
def add_color_variant(request,product_id):

    product = get_object_or_404(Product,id=product_id)
    
    if request.method == 'POST':
        try:
            color = request.POST.get('color')
            product_image1 = request.FILES.get('product_image1')
            product_image2 = request.FILES.get('product_image2')
            product_image3 = request.FILES.get('product_image3')

            validate_color_name(color)

            if ProductColorImage.objects.filter(product_id = product, color_name = color).exists():

                messages.error(request, "This color variant already exists for the product.") 
                return render(request, 'add_color_variant.html', {'product': product})
            
            product_color_image = ProductColorImage.objects.create(

                color_name = color,
                product_id = product,
                image_1 = product_image1,
                image_2 = product_image2,
                image_3 = product_image3

            )

            ProductSize.objects.create(

                size='6',
                product_data=product_color_image,
                quantity=0
            )

            messages.success(request, "Variant added successfully!")
            return redirect('variant_list',product_id = product_id)
        except ValidationError as e:
            error_message = ' '.join(e.messages)
            messages.error(request, error_message)
            return redirect(reverse('add_color_variant', args=[product_id]))

    return render(request, 'add_color_variant.html', {'product': product})

#=========================PRODUCT COLOR VARIANT SECTION END==============================#


#=========================PRODUCT SIZE VARIANT SECTION==============================#
@user_passes_test(lambda u: u.is_superuser, login_url="/admin_login/")
@csrf_exempt
def add_size_quantity(request, color_image_id):
    color_variant = get_object_or_404(ProductColorImage, id=color_image_id)

    if request.method == 'POST':
        
        size = request.POST.get('size')
        quantity = request.POST.get('quantity')

        # Check if the size already exists for this color variant
        if ProductSize.objects.filter(product_data=color_variant, size=size).exists():
            error_message = "This size already exists for the color variant."
            sizes = [size[0] for size in ProductSize.SIZE_CHOICES]

            existing_sizes = ProductSize.objects.filter(product_data = color_variant).values_list('size',flat=True)
            available_sizes = [size for size in sizes if size not in existing_sizes]
            return render(request, 'add_size_quantity.html', {'color_variant': color_variant, 'sizes': available_sizes, 'error_message': error_message})

        ProductSize.objects.create(
            size=size,
            product_data=color_variant,
            quantity=quantity
        )

        return redirect('variant_list',product_id = color_variant.product_id.id)  # Replace with appropriate view name

    sizes = [size[0] for size in ProductSize.SIZE_CHOICES]
    existing_sizes = ProductSize.objects.filter(product_data = color_variant).values_list('size',flat=True)
    available_sizes = [size for size in sizes if size not in existing_sizes]

    return render(request, 'add_size_quantity.html', {'color_variant': color_variant, 'sizes': available_sizes})


@user_passes_test(lambda u: u.is_superuser, login_url="/admin_login/")
@csrf_exempt
def edit_size_quantity(request, color_image_id):
    color_variant = get_object_or_404(ProductColorImage, id=color_image_id)
    sizes = ProductSize.objects.filter(product_data=color_variant)

    if request.method == 'POST':
        for size in sizes:
            size_id = size.id
            new_quantity = request.POST.get(f'quantity_{size_id}')
            if new_quantity:
                size_instance = get_object_or_404(ProductSize, id=size_id)
                size_instance.quantity = int(new_quantity)
                size_instance.save()

         # Handle cropped image uploads
        for i in range(1, 4):
            cropped_image_data = request.POST.get(f'cropped_image{i}')
            if cropped_image_data:
                format, imgstr = cropped_image_data.split(';base64,')
                ext = format.split('/')[-1]
                data = ContentFile(base64.b64decode(imgstr), name=f'image_{i}.{ext}')
                
                if i == 1:
                    color_variant.image_1 = data
                elif i == 2:
                    color_variant.image_2 = data
                elif i == 3:
                    color_variant.image_3 = data

        color_variant.save()

        return redirect('variant_list', product_id=color_variant.product_id.id)

    return render(request, 'edit_size_quantity.html', {'color_variant': color_variant, 'sizes': sizes})

#=========================PRODUCT SIZE VARIANT SECTION END==============================#



#=========================FEATURED PRODUCTS AND OFFER SECTION==============================#
@user_passes_test(lambda u: u.is_superuser, login_url="/admin_login/")
@require_POST
def toggle_featured(request,product_id):

    product = get_object_or_404(Product,id=product_id)
    product.featured = not product.featured
    product.save()

    return redirect('product_list')


@user_passes_test(lambda u: u.is_superuser, login_url="/admin_login/")
def apply_or_disable_offer_product(request,product_id):
    product = get_object_or_404(Product, id=product_id)
    offer_id = request.POST.get('offer_id')
    disable_offer = request.POST.get('disable')
    

    if offer_id:
        offer = get_object_or_404(Offer,id=offer_id)
        if offer.offer_type == 'product':
            if product.is_offer_applied == False:
                product.is_offer_applied = True
                product.applied_offer = offer
                product.discount_percentage = offer.discount_percentage
                product.save()
            else:
                product.save()

    elif disable_offer:   
        product.is_offer_applied = False
        product.discount_percentage = 0
        product.applied_offer = None
        product.save()

    return redirect(reverse('product_list'))

#=========================FEATURED PRODUCTS AND OFFER SECTION==============================#