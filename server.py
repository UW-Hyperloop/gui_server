import socket
import threading

HOST = 'localhost'
PORT = 8888

# Store connected clients
connected_clients = {}
clients_lock = threading.Lock()
shutdown_flag = threading.Event()

def handle_client(client_socket, address):
    """Handle communication with a connected client"""
    print(f"Client connected from {address}")
    
    # Add client to connected clients
    with clients_lock:
        connected_clients[address] = client_socket
    
    try:
        while True:
            # Receive data from client
            data = client_socket.recv(1024)
            if not data:
                break
            
            message = data.decode('utf-8')
            print(f"Received from {address}: {message}")
            
    except Exception as e:
        print(f"Error handling client {address}: {e}")
    finally:
        # Remove client from connected clients
        with clients_lock:
            if address in connected_clients:
                del connected_clients[address]
        client_socket.close()
        print(f"Client {address} disconnected")

def console_input_handler(server_socket):
    """Handle console input for sending messages to clients"""
    print("Type 'send <data>' to send to all clients, or 'quit' to exit server")
    print("> ", end="", flush=True)
    
    while not shutdown_flag.is_set():
        try:
            user_input = input()
            
            if user_input.lower() == 'quit':
                print("Shutting down server...")
                shutdown_flag.set()
                # Close server socket to break out of accept()
                try:
                    server_socket.close()
                except:
                    pass
                break
            
            if user_input.startswith('send '):
                message = user_input[5:]  # Extract data after "send "
                
                # Send to all connected clients
                with clients_lock:
                    if not connected_clients:
                        print("No clients connected")
                        print("> ", end="", flush=True)
                        continue
                    
                    disconnected = []
                    for address, client_socket in connected_clients.items():
                        try:
                            client_socket.send(message.encode('utf-8'))
                            print(f"Sent to {address}: {message}")
                        except Exception as e:
                            print(f"Error sending to {address}: {e}")
                            disconnected.append(address)
                    
                    # Remove disconnected clients
                    for address in disconnected:
                        if address in connected_clients:
                            del connected_clients[address]
                
                print("> ", end="", flush=True)
            else:
                print("Invalid command. Use 'send <data>' or 'quit'")
                print("> ", end="", flush=True)
                
        except EOFError:
            break
        except Exception as e:
            print(f"Error in console handler: {e}")
            print("> ", end="", flush=True)

def main():
    # Create socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Bind to host and port
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    
    # Set socket timeout to allow checking shutdown flag
    server_socket.settimeout(1.0)
    
    print(f"Server listening on {HOST}:{PORT}")
    
    # Start console input handler thread
    console_thread = threading.Thread(target=console_input_handler, args=(server_socket,))
    console_thread.daemon = True
    console_thread.start()
    
    try:
        while not shutdown_flag.is_set():
            try:
                # Accept incoming connection
                client_socket, address = server_socket.accept()
                
                # Handle client in a separate thread
                client_thread = threading.Thread(
                    target=handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
            except socket.timeout:
                # Timeout is expected, continue to check shutdown flag
                continue
            except OSError:
                # Socket was closed, break out of loop
                break
            
    except KeyboardInterrupt:
        print("\nShutting down server...")
        shutdown_flag.set()
    finally:
        # Close all client connections
        with clients_lock:
            for address, client_socket in list(connected_clients.items()):
                try:
                    client_socket.close()
                except:
                    pass
            connected_clients.clear()
        
        # Close server socket
        try:
            server_socket.close()
        except:
            pass
        
        print("Server shut down complete")

if __name__ == "__main__":
    main()

