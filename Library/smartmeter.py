from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.fernet import Fernet
import _thread
import socket
import sys
import re
sys.path.insert(0, "../Library")
from access import *

''' Value representing total consumption as recorded by this SmartMeter '''
stored = 0
''' Type of this entity in the network '''
type = 'smart_meter'
''' Specific id of this entity, specifying its nature '''
id = ''
''' Default port to connect to '''
TCP_PORT = 5005
''' '''
private_key = rsa.generate_private_key(
  public_exponent=65537,
  key_size=2048,
  backend=default_backend()
)
''' '''
public_key = private_key.public_key()
''' '''
shared_key = public_key.public_bytes(
  encoding=serialization.Encoding.PEM,
  format=serialization.PublicFormat.SubjectPublicKeyInfo
).decode()

print("Shared Key:")
print(shared_key)

'''
Main function that is called with set values for dynamic functioning; binds listening socket and responds to received messages.
'''

def start(set_id):
  global id
  id = set_id
  sock = make_socket()
  if(not bind_socket(sock, '', 12, TCP_PORT)):
    print("Failure to bind local socket, program shutting down.")
    return

  while True:
    conn, address = sock.accept()
    conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    info = receive(conn)
    if(info == None):
      continue
    if(authorize(info[0])):
      if(info[1] == "who"):
        _thread.start_new_thread(listen_arbiter, (conn, info,))
      elif(info[1] == "request"):
        respond_status(conn)
      elif(info[1] == "give"):
        _thread.start_new_thread(listen_appliance, (conn, info,))
    else:
      send(conn, "Failed Authorization, Disconnecting")
      close_socket(conn)

'''
Given a socket to the arbiter, keep it open for further transmission
'''

def listen_arbiter (new_sock, info):
  re_key = info[2]
  print(re_key)
  set_asymmetric_key(new_sock.getpeername()[0], serialization.load_pem_public_key(
      re_key.encode(),
      backend=default_backend()
    ))
  send(new_sock, authenticate() + access.split_term + type + access.split_term + id + access.split_term + shared_key)
  while True:
    info = receive(new_sock)
    if(info == None):
      continue
    if(authorize(info[0])):
      if(info[1] == "contact"):
        send(new_sock, authenticate())
      elif(info[1] == "symmetric"):
        set_symmetric_key(sock.getpeername(), Fernet(info[2]))

'''
Given an ip, sets up socket to be responsive and react to expected input from that source
'''

def listen_appliance (new_sock, first):
  process(first)
  while True:
    data = receive(new_sock)
    if(data == None):
      continue
    process(data)

'''
Given input that affects stored value of the smart_meter, processes it
'''

def process(data):
  global stored, id
  if(authorize(data[0])):
    val = str(re.search(id[0] + ":\d+", str(data)).group(0))
    val = str(re.search("\d+", val).group(0))
    stored += int(val)
  print("Total" + access.split_term +  id  + access.split_term + "Count:" + access.split_term +  str(stored))

'''
Upon request, inform the caller of the status of this Smart Meter
'''

def respond_status (sock):
  send(sock, id  + access.split_term + "Usage:" + access.split_term + str(stored))
  close_socket(sock)
