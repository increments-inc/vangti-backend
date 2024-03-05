from ..helper import int_to_hex, hex_to_int
import pyotp


def get_transaction_no(transaction_id, created_at):
    string_no = f"{created_at.date().strftime('%Y%m%d')}{transaction_id}"
    return int_to_hex(int(string_no))

#
# def get_transaction_id(str_number):
#     no = str(hex_to_int(str_number))
#     return no[8:]


def generate_transaction_pin():
    base_otp = pyotp.TOTP('base32secret3232').now()
    return base_otp

