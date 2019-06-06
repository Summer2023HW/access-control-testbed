from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.fernet import Fernet
import _thread
import socket
import random
import time
import sys
import re
sys.path.insert(0, "../Library")
from access import *

''' List of tuples (ip_address, socket) representing live connections to other entities in the network '''
LIVE_CONNECTIONS = []
''' Default port to connect to '''
TCP_PORT = 5005
''' Type of this entity in the network '''
type = 'appliance'
''' Specific id of this entity, specifying its nature '''
id = ''
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
Main function that is called with set values for dynamic functioning; top-down code structure is preferred.
'''

def start(set_id, val_water, val_electric):
  global id
  id = set_id
  set_asymmetric_key("0.0.0.0", private_key)
  sock = make_socket()
  if(not bind_socket(sock, '', 12, TCP_PORT)):
    print("Failure to bind local socket, program shutting down.")
    return

  _thread.start_new_thread(listen, (sock,))

  while True:
    numWat = random.randint(0, val_water)
    numElec = random.randint(0, val_electric)
    message = authenticate() + " give " + "w:" + str(numWat) + " e:" + str(numElec)
    print("Sending message: '" + message + "' to ips:")
    for hold in LIVE_CONNECTIONS:
      conn = hold[1]
      if(send(conn, message)):
        print("  Live: " + str(hold[0]))
      else:
        print("  Dead (Removed): " + str(hold[0]))
        close_socket(conn)
        LIVE_CONNECTIONS.remove(hold)
    time.sleep(5)

'''
Defines the functionality of this program to establish a listening socket which processes
received input accordingly.
'''

def listen (sock):
  while True:
    conn, address = sock.accept()
    conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    _thread.start_new_thread(process, (conn,))

'''
Defines the response to incoming messages once a connection has been established
'''

def process(sock):
  while True:
    info = receive(sock)
    if(info == None):
      continue
    if(authorize(info[0])):
      if(info[1] == "who"):
        set_asymmetric_key(sock.getpeername()[0], serialization.load_pem_public_key(
          (info[2] + " " + info[3] + " " + info[4] + " " + info[5] + " " + info[6]).encode(),
          backend=default_backend()
        ))
        send(sock, authenticate() + " " + type + " " + id + " " + shared_key)
      elif(info[1] == "symmetric"):
        set_symmetric_key(sock.getpeername(), Fernet(info[2]))
      elif(info[1] == "contact"):
        list_conn = authenticate()
        for x in LIVE_CONNECTIONS:
          list_conn += " " + x[0]
        send(sock, list_conn)
      elif(info[1] == "new_ip"):
        send(sock, "Received")
        for ip in info[2:]:
          ip_key = ip.split(",")
          new_sock = make_socket()
          if(connect_socket(new_sock, ip_key[0], TCP_PORT) and sum([1 for x in LIVE_CONNECTIONS if x[0] == ip_key[0]]) < 1):
            set_symmetric_key(ip_key[0], Fernet(ip_key[1]))
            LIVE_CONNECTIONS.append((ip, new_sock,))
    else:
      send(sock, "Failed Authorization, Disconnecting")
      close_socket(sock);
