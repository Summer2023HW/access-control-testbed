#!/usr/bin/python3

"""Network arbiter.

Forked from reithger/access-control-testbed. Written by Ada Clevinger, 2019.
Updated by Hayden Walker, 2023.
"""

import _thread
import re
import subprocess
import time

from access import *
from cryptography.fernet import Fernet


class Connection:
  """Class representing an established connection to an entity in the network that
  the Arbiter has jurisdiction over
  """

  def __init__(self, in_ip, port):
    """Create a new Connection.
    
    Connection is not open until open() is called.

    Args:
      in_ip: IP to connect to.
      port: Port on which to connect.
    """
        
    # ip address of the entity that this Connection reaches to 
    self.ip = in_ip

    # Type of entity this Connection reaches to
    self.type = ""
    
    self.TCP_PORT = port

    # Specific id of the entity that this Connection reaches to 
    self.id = ""

    # List of ip addresses that this entity is in contact with (as instructed by the Arbiter)
    self.contacts = []
    
    # Socket object that manages the connection to the entity that this Connection represents
    self.sock = None
    
    self.ready = False
  
    self.symmetric_key = ""
  
  def open(self):
    """Open the connection.
    
    Returns:
      True if successful.
    """

    self.sock = make_socket()

    if(not connect_socket(self.sock, self.ip, self.TCP_PORT)):
      return False
    
    send(self.sock, "who")
    data = receive(self.sock)
    
    if(data == None):
      return False
    
    auth = data[0]
    target_type = data[1]
    target_id = data[2]
    
    if(authorize(auth)):
      self.id = target_id
      self.type = target_type
      self.ready = True
      self.symmetric_key = Fernet.generate_key()
      send(self.sock, "symmetric" + split_term + make_decoded(self.symmetric_key))
      set_symmetric_key(self.sock.getpeername()[0], self.symmetric_key)
      return True
    
    else:
      close_socket(self.sock)
      return False
    
  def send_new_ip(self, ips):
    """Send a list of IP addresses.

    Args:
      ips: List of IP addresses to send.
    """
  
    if(ips == []):
      return
    
    message = "new_ip"
    
    for ip in ips:
      message += split_term + "" + ip
    
    if(send(self.sock, message)):
      self.contacts += ip
      
  def update_contacts(self):
    """Update list of contacts.
    """

    send(self.sock, "contact")
    data = receive(self.sock)
    
    if(data == None):
      return
    
    self.contacts = []
    
    if(authorize(data[0])):
      for x in data[1:]:
        self.contacts.append(x)


class Arbiter:
  """Network arbiter.
  """
  
  def __init__(self):
    """Create a new Arbiter.
    """

    # List of entity types in the network; i.e., Appliance/SmartMeter/etc.. Dynamically grown.
    #self.types = ['smart_meter', 'appliance', 'arbiter', 'device']
    self.types = []

    # List of Connection objects representing entities in the network that have live connections.
    #self.connections = [[],[],[],[]]
    self.connections = []
    
    # List of Strings representing what ips have been contacted and connected to thus far
    self.live_ip = []
    
    #  List of Strings representing what ips have been contacted and failed to reach
    self.dead_ip = []
    
    # Type of this entity in the network 
    self.type = "arbiter"
    
    # Default port to connect to
    self.TCP_PORT = 5005

  def main(self):
    """Periodically scans the network and establishes contact with connected IPs.
    """

    sock = make_socket()
    bind_socket(sock, '', 24, self.TCP_PORT)
    count = 0
    
    while True:
      print("Establishing new connections: ")
      
      for x in self.scan_network():
        if(x not in self.live_ip and x not in self.dead_ip):
          _thread.start_new_thread(self.new_connection, (x,))
      
      print("Managing existing connections: ")
      
      for dev_type in self.types:
        print("Type: " +  dev_type)
        for conn in self.connections[self.types.index(dev_type)]:
          if(not conn.ready):
            continue
          try:
            target = conn.sock.getpeername()
          except:
            target = "?"
          print("ip: " + str(target))
          if(dev_type == "appliance"):
            conn.send_new_ip(self.update_list(conn, "smart_meter")) # TODO: error here?
          elif(dev_type == "device"):
            conn.send_new_ip(self.update_list(conn, "smart_meter"))
      
      count = (count + 1) % 10
      
      if(count == 0):
        _thread.start_new_thread(self.update_arp, ())
      
      time.sleep(2)

  def update_arp(self):
    """Update the list of connected devices that this network entity is in contact with via a bash script
    ping_network.sh.
    
    Delegated to its own method so it could be multithreaded during the time.sleep(2).
    """

    print("Updating arp cache via bash script ping_network.sh...")
    dead_ip = []
    subprocess.Popen(['./ping_network.sh'], stdout=subprocess.PIPE).communicate()
    
    for dev_type in self.types:
      for conn in self.connections[self.types.index(dev_type)]:
        conn.update_contacts()

  def scan_network(self):
    """Generate a list of all ip addresses that the Arbiter can detect.

    Returns:
      List of IP addresses.
    """

    raw_ip = subprocess.Popen(['arp','-a'], stdout=subprocess.PIPE).communicate()
    expression = '\d+\.\d+\.\d+\.\d+'
    ip_list = re.findall(expression, str(raw_ip))
    
    if(len(ip_list) == 0):
      f = open("../network_ip.txt", "r")
      ip_list = []
      for line in f:
        ip_list.append(line)
    
    return ip_list

  def new_connection(self, ip):
    """Method to establish a new connection given a viable ip address.
    
    Attempts to create a new Connection object from the provided ip.

    Args:
      ip: IP to connect to.
    """

    conn = Connection(ip, self.TCP_PORT)

    if(conn.open()):
      self.live_ip.append(ip)

      if(conn.type not in self.types):
        self.types.append(conn.type)
        self.connections.append([])

      self.connections[self.types.index(conn.type)].append(conn)
      print("Succesfully established connection to: " + ip)

    else:
      self.dead_ip.append(ip)
      print("Failed to establish connection to: " + ip)

  def update_list(self, conn, type):
    """Update list of connected IPs.

    Returns:
      Updated list of IPs.
    """

    send = []
    
    if type not in self.types:
      self.types.append(type)
      self.connections.append([])

    for app in self.connections[self.types.index(type)]:
      if(app.ip not in conn.contacts):
        send.append(str(app.ip) + "," + str(app.symmetric_key))
    
    return send

# start the arbiter if run directly
if __name__ == "__main__":
  Arbiter().main()