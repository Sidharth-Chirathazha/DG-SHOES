from django.shortcuts import render,redirect,get_object_or_404
from django.views.decorators.http import require_POST
from .models import Cart,CartItem,Wishlist
from product_app.models import Product,ProductColorImage,ProductSize
from user.models import CustomUser
from category_app.models import Category
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from coupon_app.models import Coupons

# Create your views here.


#=========================CART MANAGEMENT SECTION==============================#
@login_required
def cart_view(request):

    user = request.user
    cart,created = Cart.objects.get_or_create(user=user)
    cart_items = CartItem.objects.filter(cart=cart).select_related('product', 'product_color', 'product_size')
    

    categories = Category.objects.filter(is_listed = True).prefetch_related('subcategories').filter(subcategories__is_listed =True).distinct()
    cart_total = sum(item.get_total_price() for item in cart_items)
    zero_quantity_detected = False
    cart_items_with_max_quantity = []
    for item in cart_items:
        max_quantity = min(item.product_size.quantity, 5)
        if item.product_size.quantity == 0:
            zero_quantity_detected = True
        cart_items_with_max_quantity.append({
            'item': item,
            'max_quantity': max_quantity,
        })

   
    context = {

        'cart_items_with_max_quantity': cart_items_with_max_quantity,
        'cart_total' : cart_total,
        'categories' : categories,
        'zero_quantity_detected' : zero_quantity_detected
    }

    return render(request,'cart_detail.html',context)



@login_required
@require_POST
def add_to_cart(request):

    user = request.user
    product_color_id = request.POST.get('variant')
    product_size_id = request.POST.get('size')
    quantity = int(request.POST.get('quantity'))

    product_size = get_object_or_404(ProductSize, id=product_size_id)
    product_color = get_object_or_404(ProductColorImage, id=product_color_id)
    product = product_color.product_id

    if quantity > product_size.quantity:
        messages.error(request, "Requested quantity exceeds available stock.")
        return redirect('product_detail', pk=product.pk)
    

    cart, created = Cart.objects.get_or_create(user=user)
    
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, product_size=product_size, product_color=product_color)
    
    if not created:
        if cart_item.quantity + quantity > product_size.quantity:
            messages.error(request, "Requested quantity exceeds available stock.")
            return redirect('product_detail', pk=product.pk)
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity

    cart_item.save()

    return redirect('cart_detail')

@login_required
@require_POST
def update_cart_item_quantity(request):

    item_id = request.POST.get('item_id')
    new_quantity = int(request.POST.get('quantity'))

    cart_item = CartItem.objects.get(id=item_id)
    available_quantity = cart_item.product_size.quantity

    if new_quantity == 0:
        cart_item.delete()
        message = "Item removed from cart."

    elif new_quantity <= available_quantity:
        cart_item.quantity = new_quantity
        cart_item.save()
        message = "Cart updated successfully."

    else:
        new_quantity = available_quantity
        cart_item.quantity = new_quantity
        cart_item.save()
        message = f"Quantity adjusted to available stock: {available_quantity}"
    
    
    cart = Cart.objects.get(user=request.user)
    cart_items = cart.items.all()
    cart_total = sum(item.get_total_price() for item in cart_items)

    return JsonResponse({
        
        'status': 'success',
        'message': message,
        'new_quantity': new_quantity,
        'item_total': cart_item.get_total_price(),
        'cart_total': cart_total,
        'available_quantity': available_quantity,
    })


@login_required
def delete_cart_item(request, item_id):

    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    return redirect('cart_detail')


@login_required
def clear_cart(request):

    cart = get_object_or_404(Cart, user=request.user)
    cart.items.all().delete()
    return redirect('cart_detail')

#=========================CART MANAGEMENT SECTION END==============================#


#=========================WISHLIST MANAGEMENT SECTION==============================#
@login_required
def wishlist_view(request):

    wishlist_items = Wishlist.objects.filter(user=request.user)
    categories = Category.objects.filter(is_listed = True).prefetch_related('subcategories').filter(subcategories__is_listed =True).distinct()

    wishlist_data = []

    for item in wishlist_items:

        sizes = ProductSize.objects.filter(product_data = item.product_variant)

        size_data = [
            {
                'size' : size.size,
                'quantity' : size.quantity,
                'in_stock' : size.quantity>0,
            }
            for size in sizes
        ]
        wishlist_data.append({
            'item' : item,
            'size_data' : size_data
        })

    context = {

        'wishlist_data' : wishlist_data,
        'categories' : categories,
    }


    return render(request,'wishlist.html',context)


@login_required
def add_to_wishlist(request,product_variant_id):

    product_variant = get_object_or_404(ProductColorImage,id=product_variant_id)

    wishlist_item,created = Wishlist.objects.get_or_create(user=request.user,product_variant=product_variant)

    if not created:

        messages.error(request,"Item already exist in wishlist")

    else:
       
        messages.success(request, 'Item added to your wishlist.')
    
    return redirect('wishlist')

@require_POST
@login_required
def add_to_cart_from_wishlist(request,wishlist_item_id):

    wishlist_item = get_object_or_404(Wishlist,id=wishlist_item_id,user=request.user)
    product_variant = wishlist_item.product_variant
    selected_size = request.POST.get(f'size_{wishlist_item.id}')

    if not selected_size:
        messages.error(request, 'Please select a size before adding to cart.')
        return redirect('wishlist')

    product_size = get_object_or_404(ProductSize, product_data=product_variant, size=selected_size)
    product = product_variant.product_id

    cart, _ = Cart.objects.get_or_create(user=request.user)

    cart_item_exists = CartItem.objects.filter(
        cart=cart,
        product=product,
        product_size=product_size,
        product_color=product_variant
    ).exists()

    if cart_item_exists:
        messages.error(request, 'Item already exists in your cart.')
    else:
        cart,created = Cart.objects.get_or_create(user=request.user)
        cart_item,created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            product_size = product_size,
            product_color = product_variant,
            defaults={'quantity': 1},
        )

        if created:
            messages.success(request, 'Item added to cart.')

        # Remove the item from the wishlist
        wishlist_item.delete()

    return redirect('wishlist')

@require_POST
@login_required
def add_all_items_to_cart(request):

    wishlist_items = Wishlist.objects.filter(user=request.user)
    cart, _ = Cart.objects.get_or_create(user=request.user)

    for wishlist_item in wishlist_items:
        product_variant = wishlist_item.product_variant
        selected_size = request.POST.get(f'size_{wishlist_item.id}')

        if not selected_size:
            messages.error(request, f'Please select a size for {product_variant.product_id.product_name} before adding to cart.')
            continue

        product_size = get_object_or_404(ProductSize,product_data=product_variant,size=selected_size)
        product = product_variant.product_id

        # Check if the item is already in the cart
        cart_item_exists = CartItem.objects.filter(
            cart=cart,
            product=product,
            product_size=product_size,
            product_color=product_variant
        ).exists()

        if cart_item_exists:
            messages.error(request, f'{product_variant.product_id.product_name}({product_variant.color_name}) already exists in your cart.')
        else:
            cart_item,created = CartItem.objects.get_or_create(
                cart=cart,
                product_size = product_size,
                product = product,
                product_color = product_variant,
                defaults={'quantity': 1},

            )
            if created:
                messages.success(request, f'{product_variant.product_id.product_name} added to cart.')
            wishlist_item.delete()


    return redirect('wishlist')

@login_required
def clear_wishlist(request):

    Wishlist.objects.filter(user=request.user).delete()
    return redirect('wishlist')

@login_required
def remove_wishlist_item(request, wishlist_item_id):

    wishlist_item = get_object_or_404(Wishlist, id=wishlist_item_id, user=request.user)
    wishlist_item.delete()
    if not wishlist_item:
        messages.info(request,'Item removed successfully.')
    else:
        messages.error(request,'Unable to delete item.')
    return redirect('wishlist')

#=========================WISHLIST MANAGEMENT SECTION END==============================#





