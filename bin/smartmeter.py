import _thread
import socket
import re
from access import *

class Smartmeter:
  def __init__(self, name):
    '''
    Create a new smart meter
    '''

    # total consumption
    self.stored = 0
    
    # type of entity
    self.type = 'smart_meter'
    
    # meter name
    self.id = name
    
    # port
    self.TCP_PORT = 5005

  def start(self):
    '''
    Start the smart meter
    '''
    sock = make_socket()
    if(not bind_socket(sock, '', 12, self.TCP_PORT)):
      print("Failure to bind local socket, program shutting down.")
      return

    while True:
      conn, address = sock.accept()
      conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      _thread.start_new_thread(self.process, (conn,))

  def process(self, sock):
    '''
    Handle incoming messages on an active socket
    '''

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
          self.respond_status(sock)
        elif(info[1] == "give"):
          self.listen_appliance(sock, info)

  def listen_appliance(self, sock, first):  
    '''
    Listen to an appliance (given an IP)
    '''
    self.process(first)
    while True:
      data = receive(sock)
      if(data == None):
        continue
      self.record(data)

  def record(self, data):
    '''
    Process input
    '''
    global stored, id
    if(authorize(data[0])):
      val = str(re.search(id[0] + ":\d+", str(data)).group(0))
      val = str(re.search("\d+", val).group(0))
      stored += int(val)
    print("Total " +  id  + " Count: " + str(stored))

  def respond_status(self, sock):
    '''
    Respond with meter status
    '''
    send(sock, id  + split_term + "Usage:" + split_term + str(stored))
    close_socket(sock)

# Start if run directly
if __name__ == '__main__':
  # Attempt to start
  try:
    Smartmeter(sys.argv[1]).start()

  # Print error message if failed
  except IndexError:
    print(f'Usage: {sys.argv[0]} [name]', file=sys.stderr)
