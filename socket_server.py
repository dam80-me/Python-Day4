# server.py

import socket
import os

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)
FILE_SAVE_DIR = 'received_files' # Directory where received files will be saved

def start_server():
    # Create the directory to save received files if it doesn't exist
    if not os.path.exists(FILE_SAVE_DIR):
        os.makedirs(FILE_SAVE_DIR)
        print(f"Created directory: {FILE_SAVE_DIR}")

    # Create a TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Bind the socket to the host and port
        s.bind((HOST, PORT))
        # Listen for incoming connections (allow up to 1 pending connection)
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")

        while True:
            # Accept a new connection
            conn, addr = s.accept()
            with conn: # 'with' statement ensures the socket is closed automatically
                print(f"Connected by {addr}")
                try:
                    # Step 1: Receive the filename
                    # We expect the filename to be sent first, and it should be relatively small.
                    # A more robust protocol might send the length of the filename first.
                    filename_data = conn.recv(1024) # Receive up to 1024 bytes for the filename
                    if not filename_data:
                        print(f"No filename data received from {addr}. Closing connection.")
                        continue # Go back to listening for a new client

                    filename = filename_data.decode('utf-8')
                    # Basic security: Sanitize the filename to prevent directory traversal
                    filename = os.path.basename(filename)
                    save_path = os.path.join(FILE_SAVE_DIR, filename)

                    print(f"Receiving file: '{filename}'")
                    print(f"Saving to: '{save_path}'")
                    with open(save_path.rstrip(), 'w') as f:
        # The 'with' statement ensures the file is properly closed.
        # Writing nothing to it results in an empty file.
                     pass
                    # Step 2: Receive the file content and write it
                    with open(save_path.rstrip(), 'wb') as f: # Open in binary write mode
                        while True:
                            bytes_read =conn.recv(4096)
                            print (bytes_read) # Read data in chunks of 4KB
                            if not bytes_read: # If recv() return empty bytes
                                break
                            f.write (bytes_read) # Write the received bytes to
                    print(f"Successfully received and saved '{filename}' from {addr}")

                except Exception as e:
                    print(f"Error during file transfer for {addr}: {e}")
                finally:
                    print(f"Connection from {addr} closed.")

if __name__ == "__main__":
    start_server()