import hashlib
import socket
import sys
import re
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.fernet import Fernet

def make_socket():
  '''
  Create and return a socket
  '''
  
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  return sock

def close_socket(sock):
  '''
  Close a socket
  '''

  try:
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()
  except:
    print("--Error in Socket Closing - Potentially non-fatal--")
    print(sys.exc_info())

def bind_socket(sock, ip, num_connections, tcp_port):
  '''
  Bind a socket. Return True if successful
  '''

  try:
    sock.bind((ip, tcp_port))
    sock.listen(num_connections)
    print("Successful binding of socket to: " + str(sock.getsockname()[0]))
    return True
  
  except:
    if(re.search("Address already in use", str(sys.exc_info()[1])) != None):
      return bind_socket(sock, ip, num_connections, tcp_port + 1)
    print("Failure to bind local socket to: " + ip)
    print(sys.exc_info())
    return False

def connect_socket(sock, ip, tcp_port):
  '''
  Connect a socket to an IP/port. Return True if successful
  '''

  try:
    sock.connect((ip, tcp_port))
    print("Successful connection to: " + str(sock.getpeername()[0]))
    return True
  
  except:
    print("Failure to connect to: " + ip + " from: " + str(sock.getsockname()[0]))
    print(sys.exc_info())
    return False

def send(sock, message):
  '''
  Send a message. Return True if successful
  '''

  try:
    target = sock.getpeername()[0]
  
  except:
    print("-Target address' name unresolved.-")
    target = "?"
  
  print("Sending message: '" + message + "' to: " + str(target))
  
  try:
    to_send = make_encoded(authenticate() + split_term + message)
    
    if(target in communication_list_symmetric):
      to_send = communication_list_symmetric[target].encrypt(to_send)
    
    elif(target in communication_list_asymmetric):
      
      to_send = communication_list_asymmetric[target].encrypt(
        to_send,
        padding.OAEP(
          mgf=padding.MGF1(algorithm=hashes.SHA256()),
          algorithm=hashes.SHA256(),
          label=None
        )
      )

    else:
      handshake_active(sock)
      return send(sock, message)
    
    sock.send(to_send)
    print("Successfully sent message.")
    return True
  
  except:
    print("-Failure to send message from: " + str(sock.getsockname()[0]) + "-")
    print(sys.exc_info())
    return False

def receive(sock):
  '''
  Listen to a socket. Return strings received
  '''
  data, addr = sock.recvfrom(1024)

  try:
    target = sock.getpeername()[0]
  
  except:
    return None
  
  data = make_decoded(data)
  print("Received Message: " + str(data) + " from: " + str(sock.getpeername()[0]))
  
  if(target not in communication_list_asymmetric and target not in communication_list_symmetric):
    handshake_responsive(sock, data)
    return None
  #----   Open Key Cryptography Implementation
  
  if(target in communication_list_symmetric):
    data = communication_list_symmetric[target].decrypt(data)
    print("Decryption: " + str(data))
  
  else:
    data = communication_list_asymmetric[home].decrypt(
      data,
      padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
      )
    )
    print("Decryption: " + str(data))
    
  data = make_decoded(data).split(split_term)
  
  if(len(data) < 1):
    return None
  
  return data

def authorize(info):
  '''
  Authorize authentication key received from a message
  '''
  return info == "auth"

def authenticate():
  '''
  Generate authentification key to send with messages
  '''
  return "auth"

def handshake_active(sock):
  '''
  Handle initial contact between agents (as agent initiating handshake)
  '''
  sock.send(make_encoded(authenticate() + split_term + "key" + split_term + shared_key))
  info, addr = sock.recvfrom(1024)
  info = make_decoded(info).split(split_term)
  communication_list_asymmetric[sock.getpeername()[0]] = recreate_public_key(info[2])

def handshake_responsive(sock, info):
  '''
  Respond to handshake
  '''
  sock.send(make_encoded(authenticate() + split_term + "key" + split_term + shared_key))
  info = info.split(split_term)
  communication_list_asymmetric[sock.getpeername()[0]] = recreate_public_key(info[2])

def recreate_public_key(key):
  '''
  Method to generate an asymmetric public key from the provided root key
  '''
  return serialization.load_pem_public_key(
    make_encoded(key),
    backend=default_backend()
  )

def make_encoded(term):
  '''
  Wraper for encode()
  '''
  try:
    return term.encode()
  except:
    return term

def make_decoded(term):
  '''
  Wrapper for decode()
  '''
  try:
    return term.decode()
  except:
    return term

def set_symmetric_key(ip, key):
  '''
  Assign a given symmetric key to the designated ip address
  '''

  try:
    key = Fernet(make_decoded(key))
  
  except:
    pass
  
  communication_list_symmetric[ip] = key

def set_asymmetric_key(ip, key):
  '''
  Assign a given public key to the designated ip address
  '''

  try:
    key = recreate_public_key(key)

  except:
    pass

  communication_list_asymmetric[ip] = key

''' ip address representing the home device; leads to the asymmetric private key for decryption'''
home = "0.0.0.0"
''' Dictionary object of [ip address : symmetric key] relationships; represents the unique key associated to each ip for decryption'''
communication_list_symmetric = {}
''' Dictionary object of [ip address : asymmetric key] relationships; represents the unique key associated to each ip for decryption'''
communication_list_asymmetric = {}
''' Numerical value representing the desired length of the asymmetric key that should be generated'''
key_length = 2048
''' Asymmetric private key object for decrypting messages received that have been encrypted with the matching public key'''
private_key = rsa.generate_private_key(
  public_exponent=65537,
  key_size=key_length,
  backend=default_backend()
)
''' Asymmetric public key object for encrypting messages; shared to other entities so that they can securely communicate one-way'''
public_key = private_key.public_key()
''' String format of the asymmetric public key that can be sent to other network entities for reconstruction'''
shared_key = make_decoded(public_key.public_bytes(
  encoding=serialization.Encoding.PEM,
  format=serialization.PublicFormat.SubjectPublicKeyInfo))
''' String term used as the common dividing term between components of messages sent between network entities'''
split_term = "::_::"

set_asymmetric_key(home, private_key)
