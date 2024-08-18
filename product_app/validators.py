from django.core.exceptions import ValidationError
from django.core.validators import validate_image_file_extension
from decimal import Decimal
import re
from .models import Product, Category, SubCategory


def normalize_string(name):
    #Normalize the product name by stripping spaces and converting to lowercase
    return ''.join(name.split()).lower()

def validate_product_name(product_name):
    if not product_name:
        raise ValidationError('Product name required.')
    
     # Normalize the product name for comparison
    normalized_name = normalize_string(product_name)

    # Get all product names and normalize them for comparison
    existing_products = Product.objects.all()
    for product in existing_products:
        if normalize_string(product.product_name) == normalized_name:
            raise ValidationError('Product name already exists.')
        
    # Validate format (starts with an alphabet, contains valid characters)
    if not re.match(r'^[A-Za-z][A-Za-z0-9!@#$%^&*()_+=\-\.,?\s]*$', product_name):
        raise ValidationError('Product name must start with an alphabet and can contain letters, numbers, spaces, and special characters.')
    
def validate_product_name_for_edit(product_name, product_id):
    if not product_name:
        raise ValidationError('Product name required.')
    
     # Normalize the product name for comparison
    normalized_name = normalize_string(product_name)

    # Get all product names and normalize them for comparison
    existing_products = Product.objects.exclude(id=product_id)
    for product in existing_products:
        if normalize_string(product.product_name) == normalized_name:
            raise ValidationError('Product name already exists.')
        
    # Validate format (starts with an alphabet, contains valid characters)
    if not re.match(r'^[A-Za-z][A-Za-z0-9!@#$%^&*()_+=\-\.,?\s]*$', product_name):
        raise ValidationError('Product name must start with an alphabet and can contain letters, numbers, spaces, and special characters.')
    
        

def validate_category_and_subcategory(category_id, subcategory_id):
    if not category_id:
        raise ValidationError('Category is required.')
    if not subcategory_id:
        raise ValidationError('Subcategory is required.')
    
def validate_description(description):
    if not description:
        raise ValidationError('Description is required.')
    if not re.match(r'^[A-Za-z0-9][A-Za-z0-9!@#$%^&*()_+=\-.,?:;\s]*$', description):
        raise ValidationError('Description must start with a letter or number and can contain letters, numbers, spaces, and special characters.')
    

def validate_color_name(color_name):
    valid_colors = ['red', 'green', 'blue', 'yellow', 'black', 'white','grey','pink','brown']  # Add more colors as needed
    normalized_color_name = normalize_string(color_name)
    # Normalize all valid colors for comparison
    normalized_valid_colors = [normalize_string(color) for color in valid_colors]
    if normalized_color_name not in normalized_valid_colors:
        raise ValidationError(f'{color_name} is not a valid color.')
    
def validate_images(images):
    for image in images:
        if image:
            validate_image_file_extension(image)
        else:
            raise ValidationError('All images are required.')

def validate_size(size):
    if not size or not size.isdigit() or int(size) <= 0:
        raise ValidationError('Size must be a positive integer.')

def validate_quantity(quantity):
    if not quantity or not quantity.isdigit() or int(quantity) < 0:
        raise ValidationError('Quantity must be a non-negative integer.')

def validate_price(price):
    try:
        price = Decimal(price)
        if price <= 0:
            raise ValidationError('Price must be a positive decimal.')
    except:
        raise ValidationError('Invalid price value.')