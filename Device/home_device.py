import socket

smartmeters = []
TCP_IP = input("Arbiter IP: ")
key = input("Network Key: ")
auth = None
TCP_PORT = 5005

id = 'device'
type = 'home'

def listen(ip_address):
  conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  conn.connect((ip_address, TCP_PORT))
  while True:
    info, addr = conn.recvfrom(1024)
    if(authorize(info.decode()[0])):
      new_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      new_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      new_sock.connect((info.decode()[2], TCP_PORT))
      smartmeters.append((info.decode()[1], new_sock,))

def authorize(auth):
  return True

try:
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  sock.connect((TCP_IP, TCP_PORT))
  print("Successful connection to Arbiter")
except:
  print("Failed to connect to Arbiter")

while True:
  if(auth == None):
    sock.send((key + " " + id + " " + type).encode())
    info, addr = sock.recvfrom(1024)
    if(info.decode().split()[0] != "Authorized"):
      print("Invalid Network Key")
      key = input("Network Key: ")
    else:
      print("Valid Network Key, Authorization Granted")
      auth = info.decode()[1]
      _thread.start_new_thread()
  else:
    statement = "Available SmartMeters: "
    for con in smartmeters:
      statement += "'" + con[0] + "'"
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
