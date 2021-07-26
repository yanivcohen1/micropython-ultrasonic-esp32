import ucryptolib
import uhashlib

SECRET_KEY = b'1234567890123456'
def encrypt(str):
    enc = ucryptolib.aes(SECRET_KEY, 1)
    data_bytes = str.encode("utf-8")
    encrypt_res = enc.encrypt(data_bytes + b'\x00' * ((16 - (len(data_bytes) % 16)) % 16))
    return encrypt_res

def decrypt(encrypt_bytes_res): # b'\xfe!F\x87?\xdb\x19\x18\xcdM\x83\x9b\xaa\x02\xa9\x04'
    dec = ucryptolib.aes(SECRET_KEY, 1)
    decrypt_res = dec.decrypt(encrypt_bytes_res)
    str_res = decrypt_res.decode("utf-8")
    return str_res

def sha256(str):  # one direction encription on decrypt
    enc_bytes = str.encode("utf-8") # b"test"
    return uhashlib.sha256(enc_bytes).digest() # b'\xc7\xb1\x8a\xd0D\x7f\x94|*C\x04\x95\x1abJY'

# inc_res = encrypt('str to encript')
# print(inc_res)
# dec_res = decrypt(inc_res)
# print(dec_res)
