# Uso de multithreading para que o cliente possa receber e enviar mensagens simultaneamente,
# ou seja, ele envia mensagem por uma thread e recebe por outra

from socket import *
import sys
import pickle
import threading
import const

class RecvHandler(threading.Thread):
  def __init__(self, sock):
    threading.Thread.__init__(self)
    self.client_socket = sock
    
  def run(self):
    while True:
      (conn, addr) = self.client_socket.accept()
      marshaled_msg_pack = conn.recv(1024)
      msg_pack = pickle.loads(marshaled_msg_pack)
      print("\nMESSAGE FROM: " + msg_pack[1] + ": " + msg_pack[0])
      conn.send(pickle.dumps("ACK"))
      conn.close()
    return

try:
  me = str(sys.argv[1])
except:
  print('Usage: python3 chatclient.py <Username>')

def send_message():
  while True:
    dest = input("ENTER DESTINATION: ")
    msg = input("ENTER MESSAGE: ")

    server_sock = socket(AF_INET, SOCK_STREAM)
    try:
      server_sock.connect((const.CHAT_SERVER_HOST, const.CHAT_SERVER_PORT))
    except:
      print("Server is down. Exiting...")
      exit(1)

    msg_pack = (msg, dest, me)
    marshaled_msg_pack = pickle.dumps(msg_pack)
    server_sock.send(marshaled_msg_pack)
    marshaled_reply = server_sock.recv(1024)
    reply = pickle.loads(marshaled_reply)
    if reply != "ACK":
      print("Error: Server did not accept the message (dest does not exist?)")
    else:
      pass
    server_sock.close()

client_sock = socket(AF_INET, SOCK_STREAM)
my_port = const.registry[me][1]
client_sock.bind(('0.0.0.0', my_port))
client_sock.listen(5)
recv_handler = RecvHandler(client_sock)
recv_handler.start() # start receiving messages thread

send_thread = threading.Thread(target=send_message)
send_thread.start() # start sending messages thread

send_thread.join()
