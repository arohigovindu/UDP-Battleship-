import socket
SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.sendto("JOIN|Arohi".encode(), (SERVER_IP, SERVER_PORT))
data, address = client_socket.recvfrom(1024)
print("Server:", data.decode())
client_socket.sendto("PLACE|Ship1|E5|H".encode(), (SERVER_IP, SERVER_PORT))
data, address = client_socket.recvfrom(1024)
print("Server:", data.decode())
client_socket.close()