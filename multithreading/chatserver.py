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
    logging.info("__init__")
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
    logging.info(msg_pack)

    if dest == "ALL":
      dest_addr = const.registry[dest]
      # for dest_conn in connected_clients.values():
      #   remote_address = dest_conn.getpeername() # client ip
      #   if dest_addr[0] == remote_address[0]:
      #     send_client_message(dest_addr[0], dest_addr[1], (msg, src))
    else:
      dest_addr = const.registry[dest]
      for dest_conn in connected_clients.values():
        remote_address = dest_conn.getpeername()
        if dest_addr[0] == remote_address[0]:
          send_client_message(dest_addr[0], dest_addr[1], (msg, src))

    # self.client_conn.close()
    # remove_client(self.client_conn)

server_sock = socket(AF_INET, SOCK_STREAM) # create server socket
server_sock.bind(('0.0.0.0', const.CHAT_SERVER_PORT))
server_sock.listen(5)

logging.info("Chat Server is ready...")

connected_clients = {}
logging.info(connected_clients)

while True:
  (conn, addr) = server_sock.accept()
  username = conn.getpeername()[0]
  connected_clients[username] = conn
  logging.info(connected_clients)
  client_thread = ClientThread(conn, addr)
  client_thread.start()