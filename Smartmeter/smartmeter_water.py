import socket
import _thread
import re

''' Value representing total consumed water as recorded by this SmartMeter '''
water = 0
''' Default port to connect to '''
TCP_PORT = 5005
''' Type of this entity in the network '''
type = 'smart_meter'
''' Specific id of this entity, specifying its nature '''
id = 'water'

'''
Main function that is called after all functions are defined; binds listening socket and responds to received messages.
'''

def main():
  sock = make_socket()
  bind_socket(sock, '', 12)

  while True:
    conn, address = sock.accept()
    conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    info, addr = conn.recvfrom(1024)
    info = info.decode().split()
    if(len(info) < 1):
      continue
    print("Received Message: " + str(info) + " from " + str(addr))
    if(authorize(info[0])):
      if(info[1] == "who"):
        send(conn, authenticate() + " " + type + " " + id)
      elif(info[1] == "new_ip"):
        send(conn, "Received")
        for x in info[2:]:
          _thread.start_new_thread(listen, (x,))
      elif(info[1] == "request"):
        respond_status(conn)
    else:
      send(conn, "Failed Authorization, Disconnecting")
      close_socket(conn)

'''
Given an ip, sets up socket to be responsive and react to expected input from that source
'''

def listen (ip_address):
  new_sock = make_socket()
  if(not connect_socket(new_sock, ip_address)):
    return
  while True:
    data, addr = new_sock.recvfrom(1024)
    data = data.decode().split()
    print("Received Message: " + str(data) + " from " + str(addr))
    if(authorize(data[0])):
      val = re.search("w:\d+", str(components[1]))
      val = val.split("w:")[0]
      water += int(val)
    print("Total Water Count: " + water)

'''
Upon request, inform the caller of the status of this Smart Meter
'''

def respond_status (sock):
  send(sock, "Water Usage: " + str(water))
  close_socket(sock)

#-------  Generic Below  ----------------------------------------------------------------------

'''
Manage the creation of a socket; setting initial values
Returns Socket
'''

def make_socket():
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  return sock

'''
Manage the closing of a socket; calling shutdown and then closing
'''

def close_socket(sock):
  try:
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()
  except:
    print("Error in Socket Closing - Potentially non-fatal")

'''
Manage the binding of a socket to listen to a defined ip address ('' for universal) at a default port with
a specified number of live connections on that socket permitted.
Returns Boolean
'''

def bind_socket(sock, ip, num_connections):
  try:
    sock.bind((ip, TCP_PORT))
    sock.listen(num_connections)
    print("Successful binding of socket to: " + ip)
    return True
  except:
    print("Failure to bind local socket to: " + ip)
    return False

'''
Manage the connecting of a socket to a defined ip address and default port
Returns Boolean
'''

def connect_socket(sock, ip):
  try:
    sock.connect((ip, TCP_PORT))
    print("Successful connection to ip: " + ip)
    return True
  except:
    print("Failure to connect to ip: " + ip)
    return False

'''
Manage the sending of a message by a defined socket
Returns Boolean
'''

def send(sock, message):
  try:
    sock.send(message.encode())
    return True
  except:
    print("Failure to send message via socket at ip: " + str(re.findall("\d+\.\d+\.\d+\.\d+", str(sock))))
    return False

'''
Authorize authentification key received from a message
Returns Boolean
'''

def authorize(info):
  return info == "auth"

'''
Generate authentification key to send with messages
Returns String
'''

def authenticate():
  return "auth"

#----------------------------------------------------------------------------------------------

main()
