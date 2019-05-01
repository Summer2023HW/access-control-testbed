import socket

UDP_IP = "192.168.2.69"     #ip of receiving machine
UDP_PORT = 5005

Message = input()       #just grabs command line input

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.sendto(Message.encode(), (UDP_IP, UDP_PORT))   #encode string; the Message.encode part is where we put the message
