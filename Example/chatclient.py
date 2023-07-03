from socket import * # networking
import sys
import pickle # object serialization
import threading
import const

class RecvHandler(threading.Thread):
  def __init__(self, sock):
    threading.Thread.__init__(self)
    self.client_socket = sock

  def run(self):
    while True:
      (conn, addr) = self.client_socket.accept()  # accept an incoming connection
      marshaled_msg_pack = conn.recv(1024)  # receive a serialized message
      msg_pack = pickle.loads(marshaled_msg_pack)  # deserialize the message
      print("\nMESSAGE FROM: " + msg_pack[1] + ": " + msg_pack[0])
      conn.send(pickle.dumps("ACK"))
      conn.close()  # close the connection
    return

try:
  me = str(sys.argv[1])  # get the username from the command line arguments
except:
  print('Usage: python3 chatclient.py <Username>')
    
client_sock = socket(AF_INET, SOCK_STREAM)  # create socket for the client
my_port = const.registry[me][1]
client_sock.bind(('0.0.0.0', my_port))
client_sock.listen(5)  # listening for incoming connections

recv_handler = RecvHandler(client_sock)  # create a thread for handling incoming messages
recv_handler.start()  # start the thread

while True:
  server_sock = socket(AF_INET, SOCK_STREAM)  # socket for connecting to the server
  dest = input("ENTER DESTINATION: ")
  msg = input("ENTER MESSAGE: ")

  try:
    server_sock.connect((const.CHAT_SERVER_HOST, const.CHAT_SERVER_PORT))
  except:
    print("Server is down. Exiting...")
    exit(1)

  msg_pack = (msg, dest, me)  # message pack
  marshaled_msg_pack = pickle.dumps(msg_pack)  # serialize message pack
  server_sock.send(marshaled_msg_pack)  # send message pack to the server

  marshaled_reply = server_sock.recv(1024)  # serialized reply from the server
  reply = pickle.loads(marshaled_reply)  # Ddserialize the reply

  if reply != "ACK":
    print("Error: Server did not accept the message (destination does not exist?)")
  else:
    pass

  server_sock.close()
