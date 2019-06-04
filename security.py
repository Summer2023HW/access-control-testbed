print("Symmetric Key via Fernet")
from cryptography.fernet import Fernet

key = Fernet.generate_key()
f = Fernet(key)
mes = b"My secret message"
token = f.encrypt(mes)
print(key)
print(f)
print(mes)
print(token)
print(f.decrypt(token))

#----------------------------------------------------------------------------------------------

print("Asymmetric Key via RSA")
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)
public_key = private_key.public_key()
ciphertext = public_key.encrypt(
  mes,
  padding.OAEP(
    mgf=padding.MGF1(algorithm=hashes.SHA256()),
    algorithm=hashes.SHA256(),
    label=None
  )
)
plaintext = private_key.decrypt(
  ciphertext,
  padding.OAEP(
    mgf=padding.MGF1(algorithm=hashes.SHA256()),
    algorithm=hashes.SHA256(),
    label=None
  )
)
priv = private_key.private_bytes(
  encoding=serialization.Encoding.PEM,
  format=serialization.PrivateFormat.PKCSB,
  encryption_algorithm=serialization.NoEncryption()
)
publ = public_key.public_key(
  encoding=serialization.Encoding.PEM,
  format=serialization.PublicFormat.SubjectPublicKeyInfo
)
print(private_key)
print(priv)
print(public_key)
print(publ)
print(mes)
print(ciphertext)
print(plaintext)
