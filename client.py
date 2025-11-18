import socket
import threading
import sys

HOST = 'localhost'
PORT = 8888

def receive_messages(client_socket):
    """Receive and display messages from server"""
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            message = data.decode('utf-8')
            print(f"\nReceived: {message}")
            print("> ", end="", flush=True)
    except Exception as e:
        print(f"\nError receiving messages: {e}")

def main():
    # Create socket and connect to server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect((HOST, PORT))
        print(f"Connected to server at {HOST}:{PORT}")
        print("Type 'send <data>' to send data, or 'quit' to exit")
        print("> ", end="", flush=True)
        
        # Start thread to receive messages
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        receive_thread.daemon = True
        receive_thread.start()
        
        # Main loop for sending messages
        while True:
            user_input = input()
            
            if user_input.lower() == 'quit':
                break
            
            if user_input.startswith('send '):
                message = user_input[5:]  # Extract data after "send "
                client_socket.send(message.encode('utf-8'))
                print("> ", end="", flush=True)
            else:
                print("Invalid command. Use 'send <data>' or 'quit'")
                print("> ", end="", flush=True)
                
    except ConnectionRefusedError:
        print(f"Could not connect to server at {HOST}:{PORT}")
        print("Make sure the server is running.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
        print("Disconnected from server")

if __name__ == "__main__":
    main()

