# Sempre que um cliente conectar, o servidor cria uma nova thread
# para "handle" o cliente
from socket import *
import pickle
import const
import threading

class ClientHandler(threading.Thread): # thread to handle the client.
  def __init__(self, conn, addr):
    threading.Thread.__init__(self)
    self.client_conn = conn
    self.client_addr = addr

  def run(self):
    marshaled_msg_pack = self.client_conn.recv(1024)
    msg_pack = pickle.loads(marshaled_msg_pack)
    msg = msg_pack[0]
    dest = msg_pack[1]
    src = msg_pack[2]
    print("RELAYING MSG: " + msg + " - FROM: " + src + " - TO: " + dest)

    try:
      dest_addr = const.registry[dest]
    except KeyError:
      self.client_conn.send(pickle.dumps("NACK"))
      self.client_conn.close()
      return

    self.client_conn.send(pickle.dumps("ACK"))
    self.client_conn.close()

    client_sock = socket(AF_INET, SOCK_STREAM)
    dest_ip = dest_addr[0]
    dest_port = dest_addr[1]

    try:
      client_sock.connect((dest_ip, dest_port))
    except:
      print("Error: Destination client is down")
      client_sock.close()
      return

    msg_pack = (msg, src)
    marshaled_msg_pack = pickle.dumps(msg_pack)
    client_sock.send(marshaled_msg_pack)
    marshaled_reply = client_sock.recv(1024)
    reply = pickle.loads(marshaled_reply)
    if reply != "ACK":
      print("Error: Destination client did not receive message properly")
    else:
      pass
    client_sock.close()

server_sock = socket(AF_INET, SOCK_STREAM)
server_sock.bind(('0.0.0.0', const.CHAT_SERVER_PORT))
server_sock.listen(5)

print("Chat Server is ready...")

while True:
  (conn, addr) = server_sock.accept() # When a new client connection is accepted,
  client_handler = ClientHandler(conn, addr) # a new ClientHandler thread is created
  client_handler.start()
