import socket
import os

# Configuration
HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server
BUFFER_SIZE = 4096  # How much data to send at once

def run_file_client():
    """
    Connects to the server and sends a specified file.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            print(f"Connected to server at {HOST}:{PORT}")
        except ConnectionRefusedError:
            print("Connection refused. Make sure the server is running.")
            return
        except Exception as e:
            print(f"Could not connect to server: {e}")
            return

        file_to_send = input("Enter the path to the file you want to send: ")

        if not os.path.exists(file_to_send):
            print(f"Error: File '{file_to_send}' not found.")
            return
        
        if not os.path.isfile(file_to_send):
            print(f"Error: '{file_to_send}' is not a regular file.")
            return

        filename = os.path.basename(file_to_send)
        file_size = os.path.getsize(file_to_send)


        try:
            # 1. Send filename (with a newline terminator)
            print(f"Sending filename '{filename}'...")
            s.sendall(f"{filename}\n".encode('utf-8'))
            
            # Add a small delay, sometimes helpful for socket buffer flushing
            # (though not strictly necessary with proper socket usage)
            # import time
            # time.sleep(0.1) 

            # 2. Open file for reading in binary mode
            print(f"Opening file '{file_to_send}' ({file_size} bytes) for sending...") 
            with open(file_to_send,'rb') as f:
                sent_bytes = 0
                while True:
                    bytes_read = f.read = f.read (BUFFER_SIZE)
                    if not bytes_read:
                        # File is done reading
                        break
                    s.sendall(bytes_read)
                    sent_bytes +=len(bytes_read)
                    # Optional: print prograss
                    print(f"\rSent {sent_bytes}/{file_size} bytes...", end='')
        
            print(f"\nSuccessfully sent '{filename}'.")
        
        except Exception as e:
            print(f"An error occurred during file transfer: {e}")
        finally:
            s.shutdown(socket.SHUT_WR) # Signal that client is done sending data
            # The server will read until it gets 0 bytes, then close its side.
            # Client can still receive if server sends something back (not this exercise).
            print("Client finished sending data.")
            #s.close()
            print("Client socket closed.")

if __name__ == '__main__':
    run_file_client()