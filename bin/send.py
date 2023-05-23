import socket
import re

TCP_IP = input("ip: ")     #ip of receiving machine
TCP_PORT = 5005

try:
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.connect((TCP_IP, TCP_PORT))
  print("Successful connection to target ip")
except:
  print("Failed to connect to target ip")

Message = input("message: ")       #just grabs command line input

while True:
    try:
      sock.send(Message.encode())   #encode string; the Message.encode part is where we put the message
    except:
      print("Failure to send message to ip " + str(TCP_IP))
    print(sock.recv(1024).decode())
    sock.close()
    tin = input("ip: ")     #ip of receiving machine
    if(tin == "close"):
        break
    if(len(re.findall("\d+\.\d+\.\d+\.\d+", tin)) == 1):
        TCP_IP = tin
    else:
        print("Invalid ip, resorting to previous ip")
    Message = input("message: ")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((TCP_IP, TCP_PORT))
sock.close()
