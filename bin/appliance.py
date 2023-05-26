#!/usr/bin/python3

"""Simulates an IoT appliance.

Usage: ./appliance.py [name] [power] [water]

Forked from reithger/access-control-testbed. Written by Ada Clevinger, 2019.
Updated by Hayden Walker, 2023.
"""

import _thread
import random
import socket
import sys
import time

from access import *


class Appliance:
  """An IoT appliance.
  """

  def __init__(self, name, power, water):
    """Create a new appliance.
    
    Args:
      name: Appliance name
      power: Power consumption
      water: Water consumption
    """

    # Live connections stored as (ip_address, socket) tuples 
    self.LIVE_CONNECTIONS = []

    # Port to connect to
    self.TCP_PORT = 5005
    
    # Type of entity
    self.type = 'appliance'

    # ID (name) of appliance
    self.id = name

    # power consumption
    self.val_electric = power

    # water consumption
    self.val_water = water

  def start(self):
    """Start the appliance.
    """

    # make a socket
    sock = make_socket()

    # attempt to bind; stop running if bind fails
    if not bind_socket(sock, '', 12, self.TCP_PORT):
      print("Failure to bind local socket, program shutting down.", file=sys.stderr)
      return

    # create a new thread to listen to the socket
    _thread.start_new_thread(self.listen, (sock,))

    while True:
      # randomly generate data
      numWat = random.randint(0, self.val_water)
      numElec = random.randint(0, self.val_electric)

      # build message to send to clients
      message = "give" + split_term + "w:" + str(numWat) + split_term + "e:" + str(numElec)

      # build status message
      status = "Sent message: '" + message + "' to ips:"
      
      # for each live connection, attempt to send message
      for hold in self.LIVE_CONNECTIONS:
        conn = hold[1]

        # attempt to send
        if send(conn, message):
          status += "\n  Live:" + str(hold[0])

        # if send fails, remove connection
        else:
          status += "\n  Dead (Removed):" + str(hold[0])
          close_socket(conn)
          self.LIVE_CONNECTIONS.remove(hold)
      
      # print status message
      print(status)

      # wait 5 seconds
      time.sleep(5)

  def listen (self, sock):
    """Listen to a socket.

    Args:
      sock: Socket to listen to.
    """

    while True:
      conn, address = sock.accept()
      conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      _thread.start_new_thread(self.process, (conn,))

  def process(self, sock):
    """Respond to a message receved from a socket.

    Args:
      sock: Socket to receive input from.
    """

    while True:
      # receive information
      info = receive(sock)

      # do nothing if no information is received
      if(info == None):
        continue
      
      # if authorization fails, close the connection
      if not authorize(info[0]):
        send(sock, "Failed Authorization, Disconnecting")
        close_socket(sock)
        return

      # react to being asked for identity
      if info[1] == "who":
        self.react_identity(sock)
      
      # react to being given a key
      elif info[1] == "symmetric":
        self.react_receive_symmetric_key(sock, info)
      
      # react to being asked for live contacts
      elif info[1] == "contact":
        self.react_provide_contacts(sock)
      
      # react to a new contact
      elif info[1] == "new_ip":
        self.react_new_contacts(sock, info)

  def react_identity(self, sock):
    """Send identifying information.

    Args:
      sock: Socket to send to.
    """
    send(sock, self.type + split_term + self.id)

  def react_provide_contacts(self, sock):
    """Provide list of live contacts.

    Will send a list of active connections.

    Args:
      sock: Socket to send list to.
    """
    
    # build up list of contacts
    list_conn = ""
    for connection in self.LIVE_CONNECTIONS:
      list_conn += split_term + connection[0]
    
    # send list
    send(sock, list_conn[len(split_term):])

  def react_receive_symmetric_key(self, sock, info):
    """Update symmetric key.

    Args:
      sock:
      info:
    """
    set_symmetric_key(sock.getpeername()[0], info[2])

  def react_new_contacts(self, sock, info):
    """Add a new contact

    Args:
      sock:
      info:
    """

    for ip in info[2:]:
      ip_key = ip.split(",")
      new_sock = make_socket()


      if connect_socket(new_sock, ip_key[0], self.TCP_PORT) and \
        sum([1 for x in self.LIVE_CONNECTIONS if x[0] == ip_key[0]]) < 1:
        set_symmetric_key(ip_key[0], ip_key[1])
        self.LIVE_CONNECTIONS.append((ip, new_sock,))

# Start if run directly
if __name__ == '__main__':
  # Attempt to start
  try:
    Appliance(sys.argv[1], int(sys.argv[2]), int(sys.argv[3])).start()

  # Print error message if failed
  except IndexError:
    print(f'Usage: {sys.argv[0]} [name] [power consumption] [water consumption]', file=sys.stderr)
