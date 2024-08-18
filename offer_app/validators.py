
from django.utils import timezone
from django.core.exceptions import ValidationError
import re
from datetime import datetime, date



def validate_offer_data(name,start_date,end_date,discount_percentage):

    errors = []
# Offername validation
    if not name or not isinstance(name, str):
        errors.append("Offer name is required and must be a string.")
    # elif not re.match(r'^[A-Za-z]', description):
    #     errors.append("Description should start with a letter.")
    elif name.startswith(' '):
        errors.append("Offer name should not start with a space.")

    # Date validation
    today = timezone.now().date()

    # Check if valid_from is a valid date
    if not isinstance(start_date, date):
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            errors.append("Start date must be a valid date in the format YYYY-MM-DD.")
    
    if isinstance(start_date, date) and start_date < today:
        errors.append("Start date must be today or a future date.")

    # Check if expiry is a valid date
    if not isinstance(end_date, date):
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            errors.append("Expiry date must be a valid date in the format YYYY-MM-DD.")
    
    if isinstance(end_date, date) and isinstance(start_date, date):
        if end_date <= start_date:
            errors.append("Expiry date must be after the valid from date.")


    if discount_percentage is not None:
        try:
            discount_percentage = float(discount_percentage)
            if discount_percentage < 0 or discount_percentage > 75:
                errors.append("Discount percentage must be a number between 0 and 75.")
        except ValueError:
            errors.append("Discount percentage must be a valid number.")

    return errors