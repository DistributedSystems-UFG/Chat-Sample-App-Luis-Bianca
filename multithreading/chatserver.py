# Sempre que um cliente conectar, o servidor cria uma nova thread
# para "handle" o cliente
from socket import *
import pickle
import threading
import logging
import const

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def broadcast_message(sender, message):
  logging.info('sending message to all users')
  for conn in connected_clients.values():
    if conn != sender:
      conn.send(message)

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
      broadcast_message(src, marshaled_msg_pack)
    else:
      dest_addr = const.registry[dest]
      for dest_conn in connected_clients.values():
        remote_address = dest_conn.getpeername()
        logging.info(remote_address[0])
        logging.info(dest_addr[0])
        if dest_addr[0] == remote_address[0]:
          self.client_conn.send(marshaled_msg_pack)
          break
        else:
          self.client_conn.send(pickle.dumps("NACK"))
          logging.error("Client %s: Destination client is down", self.client_addr)          

    self.client_conn.close()
    remove_client(self.client_conn)

server_sock = socket(AF_INET, SOCK_STREAM)
server_sock.bind(('0.0.0.0', const.CHAT_SERVER_PORT))
server_sock.listen(5)

logging.info("Chat Server is ready...")

connected_clients = {}

while True:
  (conn, addr) = server_sock.accept()
  username = conn.getpeername()[0]
  connected_clients[username] = conn
  logging.info(connected_clients)
  client_thread = ClientThread(conn, addr)
  client_thread.start()