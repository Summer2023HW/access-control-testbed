import _thread
import random
import socket
import time
import re
import sys
sys.path.insert(0, "../Library")
from access import *

''' List of tuples (ip_address, socket) representing live connections to other entities in the network '''
LIVE_CONNECTIONS = []
''' Default port to connect to '''
TCP_PORT = 5005
''' Type of this entity in the network '''
type = 'appliance'
''' Specific id of this entity, specifying its nature '''
id = 'fridge'

'''
Main function that is called after all functions are defined; top-down code structure is preferred.
'''

def main():
  sock = make_socket()
  if(not bind_socket(sock, '', 12, TCP_PORT)):
    print("Failure to bind local socket, program shutting down.")
    return

  _thread.start_new_thread(listen, (sock,))

  while True:
    numWat = random.randint(0, 50)
    numElec = random.randint(0, 100)
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
        send(sock, authenticate() + " " + type + " " + id)
      elif(info[1] == "contact"):
        list_conn = authenticate()
        for x in LIVE_CONNECTIONS:
          list_conn += " " + x[0]
        send(sock, list_conn)
      elif(info[1] == "new_ip"):
        send(sock, "Received")
        for ip in info[2:]:
          new_sock = make_socket()
          if(connect_socket(new_sock, ip, TCP_PORT) and sum([1 for x in LIVE_CONNECTIONS if x[0] == ip_address]) < 1):
            LIVE_CONNECTIONS.append((ip, new_sock,))
    else:
      send(sock, "Failed Authorization, Disconnecting")
      close_socket(sock);

#----------------------------------------------------------------------------------------------

main()
