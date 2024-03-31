from ..helper import int_to_hex, hex_to_int
import pyotp


def get_transaction_id(str_number):
    no = str(hex_to_int(str_number))
    return no[8:]

