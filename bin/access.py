"""Access control library.

Forked from reithger/access-control-testbed. Written by Ada Clevinger, 2019.
Updated by Hayden Walker, 2023.
"""

import re
import socket
import sys

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa


# term separator
split_term = "::_::"

def make_socket():
  """Create and return a socket.

  Returns:
    A socket.
  """
  
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  return sock

def close_socket(sock):
  """Close a socket.

  Args:
    sock: Socket to close
  """

  # attempt to close socket
  try:
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()

  # display error message if it fails
  except:
    print("Error closing socket.", file=sys.stderr)
    print(sys.exc_info(), file=sys.stderr)

def bind_socket(sock, ip, num_connections, tcp_port):
  """Bind a socket.

  Args:
    sock:
    ip:
    num_connections:
    tcp_port:
  
  Returns:
    True if successful, otherwise False.
  """

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

def connect_socket(sock, ip, tcp_port):
  """Connect a socket to an IP/port.

  Args:
    sock:
    ip:
    tcp_port:

  Returns:
    True if successful, otherwise False.
  """

  try:
    sock.connect((ip, tcp_port))
    print("Successful connection to: " + str(sock.getpeername()[0]))
    return True
  
  except:
    print("Failure to connect to: " + ip + " from: " + str(sock.getsockname()[0]))
    print(sys.exc_info())
    return False

def send(sock, message):
  """Send a message.

  Args:
    sock:
    message:
  
  Returns:
    True if successful, otherwise False.   
  """

  try:
    target = sock.getpeername()[0]
  
  except:
    print("-Target address' name unresolved.-")
    target = "?"
  
  print("Sending message: '" + message + "' to: " + str(target))
  
  try:
    to_send = make_encoded(authenticate() + split_term + message)
    
    if(target in communication_list_symmetric):
      to_send = communication_list_symmetric[target].encrypt(
        to_send,
        padding.OAEP(
          mgf=padding.MGF1(algorithm=hashes.SHA256()),
          algorithm=hashes.SHA256(),
          label=None
        )
      )
    
    elif(target in communication_list_asymmetric):
      to_send = communication_list_asymmetric[target].encrypt(
        to_send,
        padding.OAEP(
          mgf=padding.MGF1(algorithm=hashes.SHA256()),
          algorithm=hashes.SHA256(),
          label=None
        )
      )

    else:
      handshake_active(sock)
      return send(sock, message)
    
    sock.send(to_send)
    print("Successfully sent message.")
    return True
  
  except:
    print("-Failure to send message from: " + str(sock.getsockname()[0]) + "-")
    print(sys.exc_info())
    return False

def receive(sock):
  """Listen to a socket.

  Args:
    sock: 

  Returns:
    List of strings received.
  """

  # receive data
  data, addr = sock.recvfrom(1024)

  # attempt to get IP address of peer
  try:
    target = sock.getpeername()[0]
  except:
    return None
  
  # decode data from base64?
  data = make_decoded(data)
  #data = eval(data)

  # print encrypted string
  print("Received Message: " + str(data) + " from: " + str(target))
  
  # initiate handshake?
  if (target not in communication_list_asymmetric) and \
    (target not in communication_list_symmetric):
    handshake_responsive(sock, data)
    return None
  
  #----   Open Key Cryptography Implementation  
  # if target in communication_list_symmetric:
  #   # data = communication_list_symmetric[target].decrypt(data)
  #   data = private_key.decrypt(
  #     data,
  #     padding.OAEP(
  #       mgf=padding.MGF1(algorithm=hashes.SHA256()),
  #       algorithm=hashes.SHA256(),
  #       label=None
  #     )
  #   )
  #
  #  # print("Decryption: " + str(data))
  #  # print("Decryption: " + str(data))
  #
  # else:
  #   #data = communication_list_asymmetric[home].decrypt(
  #   data = private_key.decrypt(
  #     data,
  #     padding.OAEP(
  #       mgf=padding.MGF1(algorithm=hashes.SHA256()),
  #       algorithm=hashes.SHA256(),
  #       label=None
  #     )
  #   )

  # decrypt message
  decrypted = private_key.decrypt(
    data,
    padding.OAEP(
      mgf=padding.MGF1(algorithm=hashes.SHA256()),
      algorithm=hashes.SHA256(),
      label=None
    )
  )

  # print decrypted message
  print("Decryption: " + str(decrypted))

  message_string = str(decrypted)[2:]

  #data = make_decoded(data).split(split_term)
  message = message_string.split(split_term)


  print(message, file=sys.stderr) # debug string

  if(len(message) < 1):
    return None
  
  return message

def authorize(info):
  """Authorize authentication key received from a message.

  Returns:
    True if key is authorized, otherwise False.
  """

  return info == "auth"

def authenticate():
  """Return an authentication key.

  Returns:
    Authentication key.
  """

  return "auth"

def handshake_active(sock):
  """Handle initial contact between agents (as agent initiating handshake)

  Args:
    sock:
  """

  sock.send(make_encoded(authenticate() + split_term + "key" + split_term + shared_key))
  info, addr = sock.recvfrom(1024)
  info = make_decoded(info).split(split_term)
  communication_list_asymmetric[sock.getpeername()[0]] = recreate_public_key(info[2])

def handshake_responsive(sock, info):
  """Respond to handshake.

  Args:
    sock:
    info:
  """

  # auth::_::key::_::[key]::_::[key]
  sock.send(make_encoded(authenticate() + split_term + "key" + split_term + shared_key))
  

  # not sure if make_decoded is needed here
  info = make_decoded(info).split(split_term)
  
  communication_list_asymmetric[sock.getpeername()[0]] = recreate_public_key(info[2])

def recreate_public_key(key):
  """Method to generate an asymmetric public key from the provided root key.

  Args:
    key:
  
  Returns:

  """
  return serialization.load_pem_public_key(
    make_encoded(key),
    backend=default_backend()
  )

def make_encoded(term):
  """Wrapper for encode()

  Args:
    term:
  
  Returns:

  """

  try:
    return term.encode()
  except:
    return term

def make_decoded(term):
  """Wrapper for decode()

  Args:
    term:

  Returns:

  """
  try:
    return term.decode()
  except:
    return term

def set_symmetric_key(ip, key):
  """Assign a symmetric key to an ip address.

  Args:
    ip:
    key:
  """

  try:
    key = Fernet(make_decoded(key))
  
  except:
    pass
  
  communication_list_symmetric[ip] = key

def set_asymmetric_key(ip, key):
  """Assign a public key to an ip address.

  Args:
    ip:
    key:
  """

  try:
    key = recreate_public_key(key)

  except:
    pass

  communication_list_asymmetric[ip] = key

# home device IP address
home = "0.0.0.0"

# dictionary of {ip address : symmetric key} pairs
communication_list_symmetric = {}

# dictionary of {ip address : asymmetric key} pairs
communication_list_asymmetric = {}

# length of asymmetric key to generate
key_length = 2048

# asymmetric private key
private_key = rsa.generate_private_key(
  public_exponent=65537,
  key_size=key_length,
  backend=default_backend()
)

# asymmetric public key
public_key = private_key.public_key()

# asymmetric public key that can be sent to other network entities
shared_key = make_decoded(public_key.public_bytes(
  encoding=serialization.Encoding.PEM,
  format=serialization.PublicFormat.SubjectPublicKeyInfo))

# term separator
split_term = "::_::"

set_asymmetric_key(home, private_key)
