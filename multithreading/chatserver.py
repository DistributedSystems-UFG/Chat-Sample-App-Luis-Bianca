# Sempre que um cliente conectar, o servidor cria uma nova thread
# para "handle" o cliente
from socket import *
import pickle
import threading
import logging
import const

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def send_client_message(dest_ip, dest_port, msg_pack):
  logging.info('sending message')
  client_sock = socket(AF_INET, SOCK_STREAM) # socket for connecting to the destination client

  try:
    client_sock.connect((dest_ip, dest_port))
  except:
    print ("Error: Destination client is down")

  marshaled_msg_pack = pickle.dumps(msg_pack)  # serialize message pack
  client_sock.send(marshaled_msg_pack)  # send to the destination client

  marshaled_reply = client_sock.recv(1024)  # serialized reply from the destination client
  reply = pickle.loads(marshaled_reply)  # deserialize reply

  if reply != "ACK":
    print("Error: Destination client did not receive message properly")
  else:
    pass
  client_sock.close()

def remove_client(conn):
  logging.info('remove client from connected')
  username = None
  for user, client_conn in connected_clients.items():
    if client_conn == conn:
      username = user
      break

  if username:
    del connected_clients[username]

class ClientThread(threading.Thread): # thread to handle the client.
  def __init__(self, conn, addr):
    threading.Thread.__init__(self)
    self.client_conn = conn
    self.client_addr = addr

  def run(self):
    logging.info("Thread started for client: %s", self.client_addr)
    marshaled_msg_pack = self.client_conn.recv(1024)
    msg_pack = pickle.loads(marshaled_msg_pack)
    msg = msg_pack[0]
    dest = msg_pack[1]
    src = msg_pack[2]
    logging.info("RELAYING MSG: " + msg + " - FROM: " + src + " - TO: " + dest)

    if dest == "ALL":
      if len(connected_clients) > 1:
        self.client_conn.send(pickle.dumps("ACK"))
      else:
        self.client_conn.send(pickle.dumps("NACK"))

      for dest_conn in connected_clients.values():
        remote_address = dest_conn.getpeername() # destination client
        if self.client_addr[0] != remote_address[0]:
          dest_port = next((port for name, (ip, port) in const.registry.items() if ip == remote_address[0]), None)
          send_client_message(remote_address[0], dest_port, (msg, src))
    else:
      try:
        dest_addr = const.registry[dest] # retrieve the destination address
      except:
        self.client_conn.send(pickle.dumps("NACK"))
      else:
        self.client_conn.send(pickle.dumps("ACK"))
      for dest_conn in connected_clients.values():
        remote_address = dest_conn.getpeername()
        if dest_addr[0] == remote_address[0]:
          send_client_message(dest_addr[0], dest_addr[1], (msg, src))

server_sock = socket(AF_INET, SOCK_STREAM) # create server socket
server_sock.bind(('0.0.0.0', const.CHAT_SERVER_PORT))
server_sock.listen(5)

logging.info("Chat Server is ready...")

connected_clients = {}

while True:
  (conn, addr) = server_sock.accept()
  username = conn.getpeername()[0]
  connected_clients[username] = conn
  client_thread = ClientThread(conn, addr)
  client_thread.start()