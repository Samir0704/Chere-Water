import re

def phone_number_validator(phone_number):
    regex_txt  = "^998[012345789][0-9]{8}$"
    if re.match(regex_txt, phone_number):
        return True
    return False