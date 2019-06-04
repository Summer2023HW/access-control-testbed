import hashlib
import socket
import sys
import re

communication_list = {}

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
    print("--Error in Socket Closing - Potentially non-fatal--")
    print(sys.exc_info())

'''
Manage the binding of a socket to listen to a defined ip address ('' for universal) at a default port with
a specified number of live connections on that socket permitted.
Returns Boolean
'''

def bind_socket(sock, ip, num_connections, tcp_port):
  try:
    sock.bind((ip, tcp_port))
    sock.listen(num_connections)
    print("Successful binding of socket to: " + str(sock.getsockname()[0]))
    return True
  except:
    if(re.search("Address already in use", str(sys.exc_info()[1])) != None):
      return bind_socket(sock, ip, num_connections, tcp_port + 1)
    print("Failure to bind local socket to: " + ip)
    print(sys.exc_info())
    return False

'''
Manage the connecting of a socket to a defined ip address and default port
Returns Boolean
'''

def connect_socket(sock, ip, tcp_port):
  try:
    sock.connect((ip, tcp_port))
    handshake(sock, ip)
    print("Successful connection to: " + str(sock.getpeername()[0]))
    return True
  except:
    print("Failure to connect to: " + ip + " from: " + str(sock.getsockname()[0]))
    print(sys.exc_info())
    return False

'''
Manage the sending of a message by a defined socket
Returns Boolean
'''

def send(sock, message):
  try:
    sock.send(message.encode())
    print("Sent message: '" + message + "' to: " + str(sock.getpeername()[0]))
    return True
  except:
    print("Failure to send message from: " + str(sock.getsockname()[0]))
    print(sys.exc_info())
    return False

'''
Manage the receiving/listening for data input from a connected socket
Returns a List of Strings
'''

def receive(sock):
    data, addr = sock.recvfrom(1024)
    data = data.decode().split()
    if(len(data) < 1):
      return None
    try:
      print("Received Message: " + str(data) + " from: " + str(sock.getpeername()[0]))
    except:
      print("Received Message: " + str(data) + " from: ?")
    return data


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

'''

'''

def set_key(ip, key):
  communication_list[ip] = key
