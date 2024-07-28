import re
# from django.core.exceptions import ValidationError

def validate_first_name(first_name):
    pattern = r'^[a-zA-Z]{3}(?:[a-zA-Z ]{0,27})?$'
    if not re.match(pattern,first_name):
        return 'Enter a valid First name'
    if not first_name.strip():
        return 'Name cannot be blank'
    
def validate_last_name(last_name):
    pattern = r'^[a-zA-Z ]+$'
    if not re.match(pattern,last_name):
        return 'Enter a valid Last name'
    if last_name.startswith(' '):
        return 'Last name cannot start with a space'
    if not last_name.strip():
        return 'Name cannot be blank'

def validate_username(username):

    pattern = r'^(?!\d|_|\s)[a-zA-Z0-9_]{3,30}$'
    if not re.match(pattern,username):
        return 'Invalid Username ! Username should 6-30 characters long and should start with a letter'
    if not username.strip():
        return 'Username cannot be blank'
    if username != username.strip():
        return 'Username should not contain unwanted spaces'    
    return None


def validate_email(email):

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern,email):
        return 'Enter a valid Email'
    if not email.strip():
        return 'Email cannot be blank'
    if email != email.strip():
        return 'Email should not contain unwanted spaces'
    return None

def phone_validate(phone):

    pattern = r'^[9876]\d{9}$'
    if not re.match(pattern,phone):
        return 'Enter a valid phone number'
    if not phone.strip():
        return 'Phone number cannot be blank'
    return None

def validate_password(password):

    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,30}$'
    if not re.match(pattern, password):
        return 'Password must be 6-30 characters long, include at least one uppercase letter, one lowercase letter, one number, and one special character.'
    if not password.strip():
        return 'Password cannot be empty'
    return None

