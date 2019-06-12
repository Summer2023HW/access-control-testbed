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

'''
Main function that is called with set values for dynamic functioning; top-down code structure is preferred.
Sends a message periodically.
'''

def start(set_id, val_water, val_electric):
  global id
  id = set_id
  sock = make_socket()
  if(not bind_socket(sock, '', 12, TCP_PORT)):
    print("Failure to bind local socket, program shutting down.")
    return

  _thread.start_new_thread(listen, (sock,))

  while True:
    numWat = random.randint(0, val_water)
    numElec = random.randint(0, val_electric)
    message = "give" + split_term + "w:" + str(numWat) + split_term + "e:" + str(numElec)
    build = "Sent message: '" + message + "' to ips:"
    for hold in LIVE_CONNECTIONS:
      conn = hold[1]
      if(send(conn, message)):
        build += "\n  Live:" + str(hold[0])
      else:
        build += "\n  Dead (Removed):" + str(hold[0])
        close_socket(conn)
        LIVE_CONNECTIONS.remove(hold)
    print(build)
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
Receives a message
'''

def process(sock):
  while True:
    info = receive(sock)
    if(info == None):
      continue
    if(authorize(info[0])):
      if(info[1] == "who"):
        react_identity(sock)
      elif(info[1] == "symmetric"):
        react_receive_symmetric_key(sock, info)
      elif(info[1] == "contact"):
        react_provide_contacts(sock)
      elif(info[1] == "new_ip"):
        react_new_contacts(sock, info)
    else:
      send(sock, "Failed Authorization, Disconnecting")
      close_socket(sock);

'''
Method to define how this entity should respond to having its identity requested
Responds with a message
'''

def react_identity(sock):
  send(sock, type + split_term + id)

'''
Method to define how this entity should react to having its contact list requested
Responds with a message
'''

def react_provide_contacts(sock):
  list_conn = ""
  for x in LIVE_CONNECTIONS:
    list_conn += split_term + x[0]
  send(sock, list_conn[len(split_term):])

'''
Method to define how this entity should react to being directly given a symmetric key from another entity
Does NOT respond with a message
'''

def react_receive_symmetric_key(sock, info):
  set_symmetric_key(sock.getpeername()[0], info[2])

'''
Method to define how this entity should react to being given a list of new ip addresses to communicate with
Does NOT respond with a message
'''

def react_new_contacts(sock, info):
  for ip in info[2:]:
    ip_key = ip.split(",")
    new_sock = make_socket()
    if(connect_socket(new_sock, ip_key[0], TCP_PORT) and sum([1 for x in LIVE_CONNECTIONS if x[0] == ip_key[0]]) < 1):
      set_symmetric_key(ip_key[0], ip_key[1])
      LIVE_CONNECTIONS.append((ip, new_sock,))
