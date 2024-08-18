from django.db import models
from user.models import CustomUser
from product_app.models import ProductSize
from account_app.models import Address
from coupon_app.models import Coupons
from django.utils import timezone
from datetime import timedelta
from django.utils.crypto import get_random_string
from decimal import Decimal
import uuid

# Create your models here.

class Order(models.Model):

    PAYMENT_METHOD_CHOICES = [
        ('COD', 'Cash on Delivery'),
        ('Wallet', 'Wallet'),
        ('RazorPay', 'RazorPay'),
        # Add more payment methods as needed
    ]
    PAYMENT_STATUS_CHOICES = [     
        ('Pending','Pending'),
        ('Paid','Paid'),
    ]

    ordered_user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='orders')
    delivery_address = models.ForeignKey(Address,on_delete=models.SET_NULL,null=True,blank=True,related_name='order_address')
    delivery_name = models.CharField(max_length=255,blank=False, null=False)
    delivery_address_title = models.CharField(max_length=255,blank=False, null=False)
    delivery_state = models.CharField(max_length=100,blank=False, null=False)
    delivery_city = models.CharField(max_length=100,blank=False, null=False)
    delivery_pin = models.CharField(max_length=6,blank=False, null=False)
    delivery_post_office = models.CharField(max_length=100,blank=False, null=False)
    delivery_phone_number = models.CharField(max_length=15,blank=False, null=False)
    delivery_address_line = models.TextField(blank=False,null=False,default="add")
    delivery_landmark = models.CharField(max_length=255, null=True, blank=True)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    order_date = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    order_unique_id = models.CharField(max_length=8, unique=True, blank=True)
    coupon = models.ForeignKey(Coupons,null=True,blank=True,on_delete=models.SET_NULL)
    discount_amount = models.DecimalField(null=True,blank=True,max_digits=10, decimal_places=2, default=0)
    offer_discount_total = models.DecimalField(null=True,blank=True,max_digits=10, decimal_places=2, default=0)
    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    invoice_number = models.CharField(max_length=50, unique=True, null=True, blank=True)

    def __str__(self):
        return f"Order {self.id} by {self.ordered_user.username}"
    
    def get_subtotal(self):
        return self.total_amount + self.discount_amount
    
    def save(self, *args, **kwargs):
        if not self.order_unique_id:
            self.order_unique_id = self.generate_unique_id()
        super(Order, self).save(*args, **kwargs)

    @staticmethod
    def generate_unique_id():
        unique_id = 'OID' + get_random_string(5, allowed_chars='0123456789')
        while Order.objects.filter(order_unique_id=unique_id).exists():
            unique_id = 'OID' + get_random_string(5, allowed_chars='0123456789')
        return unique_id
    
    def set_delivery_address(self, address):
        self.delivery_address = address
        self.delivery_name = address.name
        self.delivery_address_title = address.address_title
        self.delivery_state = address.state
        self.delivery_city = address.city
        self.delivery_pin = address.pin
        self.delivery_post_office = address.post_office
        self.delivery_phone_number = address.phone_number
        self.delivery_address_line = address.address_line
        self.delivery_landmark = address.landmark

    def generate_invoice_number(self):
        # Generate a unique invoice number if it doesn't exist
        if not self.invoice_number:
            self.invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"
            self.save()
        return self.invoice_number
    

    
class OrderItem(models.Model):

    ORDER_ITEM_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
        ('Returned', 'Returned'),
        ('Return Confirmed', 'Return Confirmed'),
        ('Return Processing', 'Return Processing'),
        ('Waiting For Pickup','Waiting For Pickup'),
        ('Return Completed','Return Completed'),
        # Add more statuses as needed
    ]

    status_order = {
        'Pending': ['Processing'],
        'Processing': ['Shipped'],
        'Shipped': ['Out for Delivery'],
        'Out for Delivery': ['Delivered'],
        'Delivered': [],
        'Cancelled': [],
        'Returned': ['Return Confirmed'],
        'Return Confirmed' : ['Return Processing'],
        'Return Processing' : ['Waiting For Pickup'],
        'Waiting For Pickup' : ['Return Completed'],
        'Return Completed' : [],
    }

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product_size = models.ForeignKey(ProductSize, on_delete=models.CASCADE,related_name= 'order_products')
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at the time of ordering
    status = models.CharField(max_length=20, choices=ORDER_ITEM_STATUS_CHOICES, default='Pending')
    return_eligible_day_one = models.DateTimeField(null=True, blank=True)
    return_requested = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} of {self.product_size.product_data.product_id.product_name} (Size: {self.product_size.size})"

    def get_total_item_price(self):
        return self.quantity * self.price

    def get_next_status_choices(self):
        return self.status_order.get(self.status, [])
    
    def can_request_return(self):

        if self.status == 'Delivered' and not self.return_requested:
            if self.return_eligible_day_one is not None:
                return timezone.now() <= self.return_eligible_day_one + timedelta(days=5)
        return False
    
    