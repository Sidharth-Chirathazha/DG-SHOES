from django.utils import timezone
from django.core.exceptions import ValidationError
import re
from datetime import datetime, date

def validate_coupon_data(title, description, valid_from, expiry, discount_amount, discount_percentage, min_limit):
    errors = []
    cleaned_data = {}

    # Title validation
    if not title or not isinstance(title, str):
        errors.append("Title is required and must be a string.")
    elif title.startswith(' '):
        errors.append("Title should not start with a space.")
    elif not re.match(r'^[A-Za-z0-9 ]+$', title):
        errors.append("Title should only contain letters, numbers, and spaces.")

    # Description validation
    if not description or not isinstance(description, str):
        errors.append("Description is required and must be a string.")
    # elif not re.match(r'^[A-Za-z]', description):
    #     errors.append("Description should start with a letter.")
    elif description.startswith(' '):
        errors.append("Description should not start with a space.")

    # Date validation
    today = timezone.now().date()

    # Check if valid_from is a valid date
    if not isinstance(valid_from, date):
        try:
            valid_from = datetime.strptime(valid_from, '%Y-%m-%d').date()
        except ValueError:
            errors.append("Valid from date must be a valid date in the format YYYY-MM-DD.")
    
    if isinstance(valid_from, date) and valid_from < today:
        errors.append("Valid from date must be today or a future date.")

    # Check if expiry is a valid date
    if not isinstance(expiry, date):
        try:
            expiry = datetime.strptime(expiry, '%Y-%m-%d').date()
        except ValueError:
            errors.append("Expiry date must be a valid date in the format YYYY-MM-DD.")
    
    if isinstance(expiry, date) and isinstance(valid_from, date):
        if expiry <= valid_from:
            errors.append("Expiry date must be after the valid from date.")

    
    try:
        cleaned_data['min_limit'] = float(min_limit)
        if cleaned_data['min_limit'] < 1000:
            errors.append("Minimum limit must be a number of at least 1000.")
    except ValueError:
        errors.append("Minimum limit must be a valid number.")

    # Discount amount and discount percentage validation
    has_discount_amount = discount_amount not in (None, '')
    has_discount_percentage = discount_percentage not in (None, '')

    if has_discount_amount and has_discount_percentage:
        errors.append("Only one of discount amount or discount percentage can be set.")
    elif not has_discount_amount and not has_discount_percentage:
        errors.append("Either discount amount or discount percentage must be set.")
    else:
        if has_discount_amount:
            try:
                cleaned_data['discount_amount'] = float(discount_amount)
                cleaned_data['discount_percentage'] = None
                if cleaned_data['discount_amount'] < 0:
                    errors.append("Discount amount must be a non-negative number.")
                elif cleaned_data['min_limit'] - cleaned_data['discount_amount'] < 500:
                    errors.append("Discount amount should be at least 500 less than the minimum limit.")
            except ValueError:
                errors.append("Discount amount must be a valid number.")
        
        if has_discount_percentage:
            try:
                cleaned_data['discount_percentage'] = float(discount_percentage)
                cleaned_data['discount_amount'] = None
                if cleaned_data['discount_percentage'] < 0 or cleaned_data['discount_percentage'] > 75:
                    errors.append("Discount percentage must be a number between 0 and 75.")
            except ValueError:
                errors.append("Discount percentage must be a valid number.")

    if errors:
        raise ValidationError(errors)

    return cleaned_data


# The rest of the code remains the same
