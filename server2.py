import socket
import threading
from message import Message
from manage_user import UserManager

class MessageBoardServer:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.clients = {}  # Store clients as {address: {'username': username, 'client': client_socket}}
        self.messages = []  # Store messages as tuples (id, username, post_date, message)
        self.user_manager = UserManager()

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        print(f"Server listening on {self.host}:{self.port}")
        try:
            while True:
                client, address = self.sock.accept()
                threading.Thread(target=self.handle_client, args=(client, address)).start()
        except KeyboardInterrupt:
            print("Shutting down the server...")
            self.shutdown()

    def shutdown(self):
        for address, client_info in self.clients.items():
            client_info['client'].close()
        self.sock.close()
        print("Server successfully shut down.")

    def handle_client(self, client, address):
        print(f"New connection from {address}")

        while True:
            username = client.recv(1024).decode().strip()

            # Check if username is already taken
            print(self.user_manager.users)
            if username in self.user_manager.users:
                client.send(f"Username '{username}' is already taken. Please choose a different username.\n".encode())
            else:
                self.user_manager.add_user(username)
                break

        print(f"Received username: {username}")  # Debugging line
        current_users = self.user_manager.display_current_users()
        client.send(current_users.encode())
        self.clients[address] = {'username': username, 'client': client}
        self.broadcast(f"{username} has joined the group.", address)

        # After receiving the username, send the list of connected users
        connected_users = "Connected users: " + ", ".join([info['username'] for addr, info in self.clients.items() if addr != address])
        client.send(connected_users.encode())

        while True:
            try:
                message = client.recv(1024).decode().strip()
                print(f"Received message from {address}: {message}")  # Debugging line
                if not message:
                    break

                # Process and broadcast the message
                self.process_message(username, message)

            except ConnectionResetError:
                break

        # Handle user leaving
        print(f"Connection closed from {address}")
        self.broadcast(f"{username} has left the group.", address)
        del self.clients[address]
        client.close()

    def process_message(self, username, message_text):
        # Retrieve the user_id for the given username
        if username in self.user_manager.users:
            user_id = self.user_manager.users[username]
        else:
            print(f"Error: Username '{username}' not found in user manager.")
            return  # Optionally handle this error more gracefully

        message_id = len(self.messages) + 1
        new_message = Message(username, user_id, message_text, message_id)
        formatted_message = new_message.format_message()
        self.messages.append(new_message)
        self.broadcast(formatted_message)

    def broadcast(self, message, sender_address=None):
        for address, client_info in self.clients.items():
            if address != sender_address:
                try:
                    client_info['client'].send(message.encode())
                except BrokenPipeError:
                    continue

if __name__ == "__main__":
    server = MessageBoardServer()
    server.start()
