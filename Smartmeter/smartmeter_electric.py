import _thread
import socket
import sys
import re
sys.path.insert(0, "../Library")
from access import *

''' Value representing total consumed electricity as recorded by this SmartMeter '''
electric = 0
''' Type of this entity in the network '''
type = 'smart_meter'
''' Specific id of this entity, specifying its nature '''
id = 'electric'
''' Default port to connect to '''
TCP_PORT = 5005

'''
Main function that is called after all functions are defined; binds listening socket and responds to received messages.
'''

def main():
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
        send(conn, authenticate() + " " + type + " " + id)
      elif(info[1] == "request"):
        respond_status(conn)
      elif(info[1] == "give"):
        _thread.start_new_thread(listen, (conn, info,))
    else:
      send(conn, "Failed Authorization, Disconnecting")
      close_socket(conn)

'''
Given an ip, sets up socket to be responsive and react to expected input from that source
'''

def listen (new_sock, first):
  global electric
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
  if(authorize(data[0])):
    val = str(re.search("w:\d+", str(data)).group(0))
    val = str(re.search("\d+", val).group(0))
    water += int(val)
  print("Total Water Count: " + str(water))

'''
Upon request, inform the caller of the status of this Smart Meter
'''

def respond_status (sock):
  send(sock, "Electric Usage: " + str(electric))
  close_socket(sock)

#----------------------------------------------------------------------------------------------

main()
