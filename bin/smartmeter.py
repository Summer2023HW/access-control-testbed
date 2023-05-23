#!/usr/bin/python3

"""Simulates a smart meter.

Usage: ./smartmeter.py [name]

Forked from reithger/access-control-testbed. Written by Ada Clevinger, 2019.
Updated by Hayden Walker, 2023
"""

import _thread
import re
import socket
import sys

from access import *


class Smartmeter:
  """A smart meter.

  Forked from reithger/access-control-testbed. Written by Ada Clevinger, 2019. 
  Updated by Hayden Walker, 2023.
  """

  def __init__(self, name):
    """Create a new smart meter.

    Args:
      name: Name of smart meter
    """

    # total consumption
    self.stored = 0
    
    # type of entity
    self.type = 'smart_meter'
    
    # meter name
    self.id = name
    
    # port
    self.TCP_PORT = 5005

  def start(self):
    """Start the smart meter.
    """

    # make a socket
    sock = make_socket()

    # attempt to bind socket
    if not bind_socket(sock, '', 12, self.TCP_PORT):
      print("Failed to bind local socket.", file=sys.stderr)
      return

    # process connections
    while True:
      conn, address = sock.accept()
      conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      _thread.start_new_thread(self.process, (conn,))

  def process(self, sock):
    """Handle incoming messages on an active socket.

    Args:
      sock: Socket to process input from
    """

    while True:
      info = receive(sock)

      # do nothing if no information received
      if(info == None):
        continue
      
      # do nothing if connection is not authorized
      if not authorize(info[0]):
        continue;

      # respond to 'contact'
      if(info[1] == "contact"):
        send(sock, "")

      # respond to 'who'
      elif(info[1] == "who"):
        send(sock, self.type + split_term + self.id)
      
      # set symmetric key
      elif(info[1] == "symmetric"):
        set_symmetric_key(sock.getpeername()[0], info[2])
      
      # respond to 'request'
      elif(info[1] == "request"):
        self.respond_status(sock)
      
      # respond to 'give'
      elif(info[1] == "give"):
        self.listen_appliance(sock, info)

  def listen_appliance(self, sock, first):  
    """Listen to an appliance.

    Args:
      sock:
      first:
    """

    self.process(first)

    while True:
      # receive data
      data = receive(sock)
      
      # do nothing if no data is received
      if(data == None):
        continue

      # store data received
      self.record(data)

  def record(self, data):
    """Store data from an appliance.

    Args:
      data: Data to parse and store
    """

    if authorize(data[0]):
      # parse data and add to sum
      val = str(re.search(self.id[0] + ":\d+", str(data)).group(0))
      val = str(re.search("\d+", val).group(0))
      stored += int(val)
    
    print("Total " +  self.id  + " Count: " + str(self.stored))

  def respond_status(self, sock):
    """Respond with meter status.

    Args:
      sock: Active socket
    """
    send(sock, self.id  + split_term + "Usage:" + split_term + str(self.stored))
    close_socket(sock)

# Start if run directly
if __name__ == '__main__':
  # Attempt to start
  try:
    Smartmeter(sys.argv[1]).start()

  # Print error message if failed
  except IndexError:
    print(f'Usage: {sys.argv[0]} [name]', file=sys.stderr)
