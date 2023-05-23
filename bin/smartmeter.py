import _thread
import socket
import sys
import re
#sys.path.insert(0, "../Library")
from access import *

''' Value representing total consumption as recorded by this SmartMeter '''
stored = 0
''' Type of this entity in the network '''
type = 'smart_meter'
''' Specific id of this entity, specifying its nature '''
id = ''
''' Default port to connect to '''
TCP_PORT = 5005

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
    _thread.start_new_thread(process, (conn,))

'''
Method to handle incoming messages on an active socket
'''

def process(sock):
  while True:
    info = receive(sock)
    if(info == None):
      continue
    if(authorize(info[0])):
      if(info[1] == "contact"):
        send(sock, "")
      elif(info[1] == "who"):
        send(sock, type + split_term + id)
      elif(info[1] == "symmetric"):
        set_symmetric_key(sock.getpeername()[0], info[2])
      elif(info[1] == "request"):
        respond_status(sock)
      elif(info[1] == "give"):
        listen_appliance(sock, info)


'''
Given an ip, sets up socket to be responsive and react to expected input from that source
'''

def listen_appliance (sock, first):
  process(first)
  while True:
    data = receive(sock)
    if(data == None):
      continue
    record(data)

'''
Given input that affects stored value of the smart_meter, processes it
'''

def record(data):
  global stored, id
  if(authorize(data[0])):
    val = str(re.search(id[0] + ":\d+", str(data)).group(0))
    val = str(re.search("\d+", val).group(0))
    stored += int(val)
  print("Total " +  id  + " Count: " + str(stored))

'''
Upon request, inform the caller of the status of this Smart Meter
'''

def respond_status (sock):
  send(sock, id  + split_term + "Usage:" + split_term + str(stored))
  close_socket(sock)
