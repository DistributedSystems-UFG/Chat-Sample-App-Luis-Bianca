from socket  import * # networking
import pickle # object serialization
import const

server_sock = socket(AF_INET, SOCK_STREAM) # create server socket
server_sock.bind(('0.0.0.0', const.CHAT_SERVER_PORT))
server_sock.listen(5)

print("Chat Server is ready...")

while True:
    (conn, addr) = server_sock.accept()

    marshaled_msg_pack = conn.recv(1024) # receive serialized message
    msg_pack = pickle.loads(marshaled_msg_pack) # deserialize message
    msg = msg_pack[0]
    dest = msg_pack[1]
    src = msg_pack[2]
    print("RELAYING MSG: " + msg + " - FROM: " + src + " - TO: " + dest)

    try:
        dest_addr = const.registry[dest] # retrieve the destination address
    except:
        conn.send(pickle.dumps("NACK"))
        continue
    else:
        conn.send(pickle.dumps("ACK"))
    conn.close() # close the connection with client

    client_sock = socket(AF_INET, SOCK_STREAM) # socket for connecting to the destination client
    dest_ip = dest_addr[0]
    dest_port = dest_addr[1]

    try:
        client_sock.connect((dest_ip, dest_port))
    except:
        print ("Error: Destination client is down")
        continue

    msg_pack = (msg, src)  # message pack
    marshaled_msg_pack = pickle.dumps(msg_pack)  # serialize message pack
    client_sock.send(marshaled_msg_pack)  # send to the destination client

    marshaled_reply = client_sock.recv(1024)  # serialized reply from the destination client
    reply = pickle.loads(marshaled_reply)  # deserialize reply

    if reply != "ACK":
        print("Error: Destination client did not receive message properly")
    else:
        pass
    client_sock.close()