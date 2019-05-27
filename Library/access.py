import socket

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
    print(sys.exc_info()[0])

'''
Manage the binding of a socket to listen to a defined ip address ('' for universal) at a default port with
a specified number of live connections on that socket permitted.
Returns Boolean
'''

def bind_socket(sock, ip, num_connections, tcp_port):
  try:
    sock.bind((ip, tcp_port))
    sock.listen(num_connections)
    print("Successful binding of socket to: " + ip)
    return True
  except:
    print("Failure to bind local socket to: " + ip)
    print(sys.exc_info()[0])
    return False

'''
Manage the connecting of a socket to a defined ip address and default port
Returns Boolean
'''

def connect_socket(sock, ip, tcp_port):
  try:
    sock.connect((ip, tcp_port))
    print("Successful connection to ip: " + ip)
    return True
  except:
    print("Failure to connect to ip: " + ip)
    print(sys.exc_info()[0])
    return False

'''
Manage the sending of a message by a defined socket
Returns Boolean
'''

def send(sock, message):
  try:
    sock.send(message.encode())
    print("Sent message: '" + message + "' to: " + str(sock))
    return True
  except:
    print("Failure to send message via socket at ip: " + str(re.findall("\d+\.\d+\.\d+\.\d+", str(sock))))
    print(sys.exc_info()[0])
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
