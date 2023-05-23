import socket
import _thread

TCP_IP = '' #ip of the receiving machine
TCP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((TCP_IP, TCP_PORT))
sock.listen(6)  #up to 6 active cions

def listen(c):
  while True:
    data, addr = c.recvfrom(1024)
    print ("received message: ", data.decode(), " from ", addr)   #do something with result in data
    c.send(b"Received")
    if(data == "close"):
      c.close()
      break

while True:             #listens continuously
  c, addr = sock.accept()  #specify 1024 bytes received
  _thread.start_new_thread(listen, (c,))

sock.close()
