import socket
import threading

# Server configuration
HOST = '127.0.0.1'  # Localhost
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

clients = []
clients_lock = threading.Lock()

def broadcast(message, sender_socket):
    """Sends a message to all connected clients except the sender."""
    with clients_lock:
        for client in clients:
            if client != sender_socket:
                try:
                    client.sendall(message)
                except socket.error:
                    # If sending fails, assume client is disconnected and remove it
                    remove_client(client)

def handle_client(conn, addr):
    """Handles a single client connection."""
    print(f"Connected by {addr}")
    with clients_lock:
        clients.append(conn)

    try:
        while True:
            data = conn.recv(1024)  # Receive up to 1024 bytes
            if not data:
                # If no data is received, the client has disconnected
                break
            message = f"{addr}: {data.decode()}".encode() # Decode bytes to string, add sender info, encode back to bytes
            print(f"Received from {addr}: {data.decode()}")
            broadcast(message, conn) # Broadcast the message to other clients
    except ConnectionResetError:
        print(f"Connection reset by {addr}")
    finally:
        # Clean up the connection
        print(f"Disconnected from {addr}")
        remove_client(conn)
        conn.close()

def remove_client(client_socket):
    """Removes a client from the list."""
    with clients_lock:
        if client_socket in clients:
            clients.remove(client_socket)

def start_server():
    """Starts the TCP chat server."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()  # Accept a new connection
            # Start a new thread to handle the client
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()

if __name__ == "__main__":
    start_server()
