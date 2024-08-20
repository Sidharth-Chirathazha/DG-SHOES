import re
from django.contrib.auth import get_user_model

User = get_user_model()
def validate_address_data(address_title, full_name, address, post_office, pincode, city, state, phone):
    errors = {}

    # Regex Patterns
    name_pattern = re.compile(r'^[A-Za-z][A-Za-z ]*$')
    address_title_pattern = re.compile(r'^[A-Za-z0-9][A-Za-z0-9 ]*$')
    address_pattern = re.compile(r'^[A-Za-z0-9][A-Za-z0-9\s!@#$%^&*()-_=+]*$')
    post_office_pattern = re.compile(r'^[A-Za-z][A-Za-z ]*$')
    pincode_pattern = re.compile(r'^[1-9][0-9]{5}$')
    city_state_pattern = re.compile(r'^[A-Za-z][A-Za-z ]*$')
    phone_pattern = re.compile(r'^[789][0-9]{9}$')

    if not name_pattern.match(full_name):
        errors['full_name'] = 'Invalid Full Name'
    if not address_title_pattern.match(address_title):
        errors['address_title'] = 'Invalid Address Title'
    if not address_pattern.match(address):
        errors['address'] = 'Invalid Address'
    if not post_office_pattern.match(post_office):
        errors['post_office'] = 'Invalid Post Office'
    if not pincode_pattern.match(pincode):
        errors['pincode'] = 'Invalid Pincode'
    if not city_state_pattern.match(city):
        errors['city'] = 'Invalid City'
    if not city_state_pattern.match(state):
        errors['state'] = 'Invalid State'
    if not phone_pattern.match(phone):
        errors['phone'] = 'Invalid Phone Number'

    return errors


def validate_username(username):

    pattern = r'^(?!\d|_|\s)[a-zA-Z0-9_]{3,30}$'
    if not re.match(pattern,username):
        return 'Invalid Username ! Username should 6-30 characters long and should start with a letter'
    if not username.strip():
        return 'Username cannot be blank'
    if username != username.strip():
        return 'Username should not contain unwanted spaces'    
    return None

def phone_validate(phone, user_id=None):
    pattern = r'^[9876]\d{9}$'
    if not re.match(pattern, phone):
        return 'Enter a valid phone number.'
    if not phone.strip():
        return 'Phone number cannot be blank.'
    
    # Exclude the current user when checking if the phone number already exists
    if User.objects.exclude(id=user_id).filter(phone_number=phone).exists():
        return 'Phone number already exists.'
    return None

def validate_password(password):

    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,30}$'
    if not re.match(pattern, password):
        return 'Password must be 6-30 characters long, include at least one uppercase letter, one lowercase letter, one number, and one special character.'
    if not password.strip():
        return 'Password cannot be empty'
    return None

def validate_first_name(first_name):
    pattern = r'^[a-zA-Z]{3}(?:[a-zA-Z ]{0,27})?$'
    if not re.match(pattern, first_name):
        return 'Enter a valid First name.'
    if not first_name.strip():
        return 'First name cannot be blank.'
    return None
    
def validate_last_name(last_name):
    pattern = r'^[a-zA-Z ]+$'
    if not re.match(pattern, last_name):
        return 'Enter a valid Last name.'
    if last_name.startswith(' '):
        return 'Last name cannot start with a space.'
    if not last_name.strip():
        return 'Last name cannot be blank.'
    return None