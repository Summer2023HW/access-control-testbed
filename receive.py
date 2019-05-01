import socket

UDP_IP = "192.168.2.69" #ip of the receiving machine
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

while True:             #listens continuously
  data, addr = sock.recvfrom(1024)  #specify 1024 bytes received
  print "received message:", data   #do something with result in data
