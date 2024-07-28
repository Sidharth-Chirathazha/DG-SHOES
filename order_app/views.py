from django.shortcuts import render,redirect,get_object_or_404
from category_app.models import Category
from account_app.models import Address
from cart_app.models import Cart, CartItem
from django.contrib import messages
from django.utils import timezone
from .models import Order,OrderItem
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.loader import render_to_string

# Create your views here.

@login_required
def checkout_view(request):

    categories = Category.objects.all().prefetch_related('subcategories')
    user = request.user
    user_addresses = Address.objects.filter(user=user,is_listed=True)

    try:
        cart = Cart.objects.get(user=user)
        cart_items = CartItem.objects.filter(cart=cart)
        cart_total = sum(item.get_total_price() for item in cart_items)
    except Cart.DoesNotExist:
        cart_items = []
        cart_total = 0

    if request.method == 'POST':
        selected_address_id = request.POST.get('selected_address')
        payment_method = request.POST.get('payment_method')

        if not selected_address_id:
            messages.error(request,'Please select a delivery address.')
        elif not payment_method:
            messages.error(request,'Please select a payment method.')
        else:
            selected_address = Address.objects.get(id=selected_address_id)

            # Create the Order
            order = Order.objects.create(

                ordered_user = user,
                payment_method = payment_method,
                total_amount = cart_total,
                order_date = timezone.now()
            )
            order.set_delivery_address(selected_address)
            order.save()

            # Create OrderItems and update product quantities
            for cart_item in cart_items:
                OrderItem.objects.create(

                    order = order,
                    product_size = cart_item.product_size,
                    quantity = cart_item.quantity,
                    price = cart_item.product.price,
                    status = 'Pending'
                )

            # Decrease product quantity
            cart_item.product_size.quantity -= cart_item.quantity
            cart_item.product_size.save()

        # Clear the cart
        cart_items.delete()

        # messages.success(request,'Order placed successfully.')
        return redirect('order_success',order_id = order.id)

    
    context = {

        'categories' : categories,
        'user' : user,
        'user_addresses' : user_addresses,
        'cart_items' : cart_items,
        'cart_total' : cart_total,
    }

    return render(request,'checkout.html',context)

@login_required
def order_success_view(request,order_id):

    order = get_object_or_404(Order, id = order_id)
    order_items = OrderItem.objects.filter(order=order)
    categories = Category.objects.all().prefetch_related('subcategories')
    user = request.user

    context = {
        'order': order,
        'order_items': order_items,
        'categories': categories,
        'user' : user,
    }

    return render(request, 'order_success.html', context)

# @login_required
# def order_success_view(request,order_id):

#     order = get_object_or_404(Order, id = order_id)

#     if request.user != order.ordered_user:
#         return JsonResponse({"error": "You don't have permission to view this order"}, status=403)

#     order_items = OrderItem.objects.filter(order=order)

#     items_data = [{

#         "product_name" = item.product_size.product_data.product_id.product_name,
#         "color": item.product_size.product_data.color_name if hasattr(item, 'product_color') else None,
#         "size": item.product_size.size if hasattr(item, 'product_size') else None,
#         "quantity": item.quantity,
#         "price": float(item.price)

#     } for item in order_items]

#     context = {
#         'order': order,
#         'order_items': order_items,
#         'categories': categories,
#         'user' : user,
#     }

#     return render(request, 'order_success.html', context)


