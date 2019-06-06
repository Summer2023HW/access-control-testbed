from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.fernet import Fernet
import subprocess
import _thread
import socket
import time
import sys
import re
sys.path.insert(0, "../Library")
from access import *

''' List of entity types in the network; i.e., Appliance/SmartMeter/etc.. Dynamically grown. '''
types = ['smart_meter', 'appliance', 'arbiter', 'device']
''' List of Connection objects representing entities in the network that have live connections '''
connections = [[],[],[],[]]
''' List of Strings representing what ips have been contacted and connected to thus far '''
live_ip = []
'''  List of Strings representing what ips have been contacted and failed to reach '''
dead_ip = []
''' Type of this entity in the network '''
type = "arbiter"
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


'''
Main method that is called after all functions are defined; top-down code structure is preferred.
Periodically scans the network and establishes contact to all ips, authorizing them as certain
kinds of entities and disseminating information accordingly.
'''

def main():
  global dead_ip
  set_asymmetric_key("0.0.0.0", private_key)
  sock = make_socket()
  bind_socket(sock, '', 24, TCP_PORT)
  count = 0
  while True:
    print("Establishing new connections: ")
    for x in scan_network():
      if(x not in live_ip and x not in dead_ip):
        _thread.start_new_thread(new_connection, (x,))
    print("Managing existing connections: ")
    for dev_type in types:
      print("Type:" + access.split_term + dev_type)
      for conn in connections[types.index(dev_type)]:
        if(not conn.ready):
          continue
        try:
          print("ip:" + access.split_term + str(conn.sock.getpeername()))
        except:
          print("ip: ?")
        if(dev_type == "appliance"):
          send = update_list(conn, "smart_meter")
          conn.send_new_ip(send)
        elif(dev_type == "device"):
          send = update_list(conn, "smart_meter")
          conn.send_new_ip(send)
    time.sleep(2)
    count = (count + 1) % 10
    if(count == 0):
      print("Updating arp cache via bash script ping_network.sh...")
      dead_ip = []
      subprocess.Popen(['./ping_network.sh'], stdout=subprocess.PIPE).communicate()
      for dev_type in types:
        for conn in connections[types.index(dev_type)]:
          conn.update_contacts()


'''
Method to generate a list of all ip addresses that the Arbiter can detect to query
them about their nature.
Returns a list of Strings
'''

def scan_network():
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
    if(conn.type not in types):
      types.append(conn.type)
      connections.append([])
    connections[types.index(conn.type)].append(conn)
    print("Succesfully established connection to:" + access.split_term + ip)
  else:
    dead_ip.append(ip)
    print("Failed to establish connection to:" + access.split_term + ip)

'''
Method that checks the existing list of connected device ips against those recorded
as being known to a particular network entity, producing a list of new ips to provide.
Returns a List of Strings
'''

def update_list(conn, type):
  send = []
  for app in connections[types.index(type)]:
    if(app.ip not in conn.contacts):
      send.append(app.ip + "," + app.symmetric_key)
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
  sock = None
  '''   '''
  ready = False
  ''' '''
  public_key = ""
  ''' '''
  symmetric_key = ""

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
    self.sock = make_socket()
    if(not connect_socket(self.sock, self.ip, TCP_PORT)):
      return False
    send(self.sock, authenticate() + access.split_term + "who" + access.split_term + str(shared_key))
    data = receive(self.sock)
    if(data == None):
      return False
    auth = data[0]
    target_type = data[1]
    target_id = data[2]
    target_public_key = data[3]
    if(authorize(auth)):
      self.id = target_id
      self.type = target_type
      self.ready = True
      self.public_key = serialization.load_pem_public_key(
        data[3],
        password=None,
        backend=default_backend()
      )
      self.symmetric_key = Fernet.generate_key()
      send(self.sock, authenticate() + access.split_term + "symmetric" + access.split_term + self.symmetric_key)
      set_symmetric_key(self.sock.getpeername()[0], Fernet(self.symmetric_key))
      return True
    else:
      close_socket(self.sock)
      return False

  '''
  Method to handle sending a list of ip addresses to the connected network entity to be
  added to their list of contacts.
  '''

  def send_new_ip(self, ips):
    if(ips == []):
      return
    message = authenticate() + access.split_term + "new_ip"
    for ip in ips:
      message += access.split_term + "" + ip
    if(send(self.sock, message)):
      self.contacts += ips

  '''
  Method to handle updating the list of contacts according to those that the connected
  device is still communicating with.
  '''

  def update_contacts(self,):
    send(self.sock, authenticate() + access.split_term + "contact")
    data = receive(self.sock)
    if(data == None):
      return
    self.contacts = []
    if(authorize(data[0])):
      for x in data[1:]:
        self.contacts.append(x)

#----------------------------------------------------------------------------------------------

main()
