import socket

smartmeters = []
TCP_IP = input("Arbiter IP: ")
key = input("Network Key: ")
auth = None
TCP_PORT = 5005

type = 'device'
id = 'home'

'''

'''

def main():
  sock = make_socket()
  connect_socket(sock, TCP_IP)

  while True:
    if(auth == None):
      send(sock, key + " " + id + " " + type)
      info, addr = sock.recvfrom(1024)
      info = info.decode().split()
      if(info[0] != "Authorized"):
        print("Invalid Network Key")
        key = input("Network Key: ")
      else:
        print("Valid Network Key, Authorization Granted")
        auth = info[1]
        _thread.start_new_thread(listen, (sock,))
    else:
      statement = "Available SmartMeters:"
      for con in smartmeters:
        statement += " '" + con[0] + "'"
      print(statement)
      choice = input("Which SmartMeter would you like to query?")
      select = False
      for con in smartmeters:
        if(choice == con[0]):
          con[1].send("auth device")
          print("Response: " + con[1].recv(1024).decode())
          select = True
      if(!select):
        print("Invalid choice, please try again.")

'''

'''

def listen(conn):
  while True:
    info, addr = conn.recvfrom(1024)
    info = info.decode().split()
    if(authorize(info[0])):
      new_sock = make_socket()
      connect_socket(new_sock, info[2])
      new_sock.connect((info[2], TCP_PORT))
      smartmeters.append((info[1], new_sock,))

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
