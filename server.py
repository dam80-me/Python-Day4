import socket
import threading
import pickle
import time

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = []  # List to store connected client sockets and their addresses
        self.lock = threading.Lock() # Lock for thread-safe access to self.clients

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allow reuse of address
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"Server listening on {self.host}:{self.port}")

        while True:
            conn, addr = self.server_socket.accept()
            print(f"Connected by {addr}")
            with self.lock:
                self.clients.append((conn, addr))
            # Start a new thread to handle this client
            client_handler = threading.Thread(target=self.handle_client, args=(conn, addr))
            client_handler.start()

    def handle_client(self, conn, addr):
        try:
            while True:
                # Receive data from the client
                data = conn.recv(4096)
                if not data:
                    break # Client disconnected

                try:
                    message = pickle.loads(data)
                    print(f"Received from {addr}: {message}")

                    # Forward the message to other clients
                    self.broadcast_message(message, sender_conn=conn)

                except pickle.UnpicklingError:
                    print(f"Could not unpickle data from {addr}. Data: {data}")
                    break

        except Exception as e:
            print(f"Error handling client {addr}: {e}")
        finally:
            print(f"Client {addr} disconnected.")
            with self.lock:
                self.clients.remove((conn, addr))
            conn.close()

    def broadcast_message(self, message, sender_conn):
        with self.lock:
            for client_conn, client_addr in self.clients:
                if client_conn != sender_conn: # Don't send back to the sender
                    try:
                        client_conn.sendall(pickle.dumps(message))
                        print(f"Forwarded message to {client_addr}: {message}")
                    except Exception as e:
                        print(f"Error sending to {client_addr}: {e}")
                        # Remove problematic client (optional, but good for robustness)
                        self.clients.remove((client_conn, client_addr))
                        client_conn.close()

if __name__ == "__main__":
    server = Server(HOST, PORT)
    server.start()