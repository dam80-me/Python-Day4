# client.py
import socket

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

def start_client():
    # Create a socket object using IPv4 (AF_INET) and TCP (SOCK_STREAM)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Connect to the server
        s.connect((HOST, PORT))
        print(f"Connected to server {HOST}:{PORT}")

        while True:
            message = input("Enter message to send (type 'bye' to exit): ")
            if not message:
                continue

            # Send the message (must be bytes)
            s.sendall(message.encode('utf-8'))

            if message.lower() == "bye":
                print("Client closing connection.")
                break

            # Receive response from the server
            data = s.recv(1024)
            print(f"Received from server: {data.decode('utf-8')}")

    print("Client closed.")

if __name__ == "__main__":
    start_client()