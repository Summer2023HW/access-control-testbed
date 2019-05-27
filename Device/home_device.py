import socket
import sys
sys.path.insert(0, "../Library")
from access import *

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

#----------------------------------------------------------------------------------------------

main()
