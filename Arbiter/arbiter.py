import socket
import re
import subprocess
import time
import _thread
import sys
sys.path.insert(0, "../Library")
from access import *

''' List of entity types in the network; i.e., Appliance/SmartMeter/etc.. Dynamically grown. '''
types = []
''' List of Connection objects representing entities in the network that have live connections '''
connections = []
''' List of Strings representing what ips have been contacted and connected to thus far '''
live_ip = []
''' Type of this entity in the network '''
type = "arbiter"
''' Default port to connect to '''
TCP_PORT = 5005

'''
Main method that is called after all functions are defined; top-down code structure is preferred.
Periodically scans the network and establishes contact to all ips, authorizing them as certain
kinds of entities and disseminating information accordingly.
'''

def main():
  sock = make_socket()
  bind_socket(sock, '', 24, TCP_PORT)
  while True:
    for x in scan_network():
      if(x not in live_ip):
        _thread.start_new_thread(new_connection, (x,))
    for dev_type in types:
      for conn in connections[types.index(dev_type)]:
        if(dev_type == "appliance"):
          send = update_list(conn, "smartmeter")
          conn.send_new_ip(send)
        elif(dev_type == "smartmeter"):
          send = update_list(conn, "appliance")
          conn.send_new_ip(send)
        elif(dev_type == "device"):
          send = update_list(conn, "smartmeter")
          conn.send_new_ip(send)
    time.sleep(2)

'''
Method to generate a list of all ip addresses that the Arbiter can detect to query
them about their nature.
Returns a list of Strings
'''

def scan_network():
  #subprocess.Popen(['./ping_network.sh'], stdout=subprocess.PIPE).communicate()
  raw_ip = subprocess.Popen(['arp','-a'], stdout=subprocess.PIPE).communicate()
  expression = '\d+\.\d+\.\d+\.\d+'
  return re.findall(expression, str(raw_ip))

'''
Method to establish a new connection given a viable ip address; attempts to create
a new Connection object from the provided ip and reacts accordingly to a failure
in this set-up.
'''

def new_connection(ip):
  conn = Connection(ip)
  if(conn.open()):
    live_ip.append(ip)
    if(conn.id not in types):
      types.append(conn.id)
      connections.append([])
    connections[types.index(conn.id)].append(conn)
    print("Succesfully established connection to: " + ip)
  else:
    print("Failed to establish connection to: " + ip)

'''
Method that checks the existing list of connected device ips against those recorded
as being known to a particular network entity, producing a list of new ips to provide.
Returns a List of Strings
'''

def update_list(conn, type):
  send = []
  for app in connections[types.index(type)]:
    if(app.ip not in conn.contacts):
      send.append(app.ip)
  return send

#----------------------------------------------------------------------------------------------

'''
Class representing an established connection to an entity in the network that
the Arbiter has jurisdiction over
'''

class Connection:
  ''' Type of entity this Connection reaches to '''
  type = ""
  ''' Specific id of the entity that this Connection reaches to '''
  id = ""
  ''' ip address of the entity that this Connection reaches to '''
  ip = ""
  ''' List of ip addresses that this entity is in contact with (as instructed by the Arbiter)'''
  contacts = []
  ''' Socket object that manages the connection to the entity that this Connection represents'''
  socket = None

  '''
  Method to establish a Connection object based on given ip address; 'open' method
  completes the initialization by making contact to the entity at that ip.
  '''

  def __init__(self, in_ip):
    self.ip = in_ip

  '''
  Method to make contact to the entity associated to the given ip address, maintain
  a connection to it and establish what kind of entity it is in the network.
  Returns a Boolean
  '''

  def open(self):
    self.socket = make_socket()
    if(not connect_socket(self.socket, self.ip, TCP_PORT)):
      return False
    send(self.socket, authenticate() + " who")
    data, addr = self.socket.recvfrom(1024)
    data = data.decode().split()
    auth = data[0]
    target_type = data[1]
    target_id = data[2]
    if(authorize(auth)):
      self.id = target_id
      self.type = target_type
      return True
    else:
      close_socket(self.socket)
      return False

  '''
  Method to handle sending a list of ip addresses to the connected network entity to be
  added to their list of contacts.
  '''

  def send_new_ip(self, ips):
    if(ips == []):
      return
    message = authenticate() + " new_ip"
    for ip in ips:
      message += " " + ip
    if(send(self.socket, message)):
      self.contacts += ips

main()
