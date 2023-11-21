import socket
import threading
from message import Message
from manage_user import UserManager


class MessageBoardServer:
    def __init__(self, host='localhost', port=8889):
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
                client.send(f"Username '{username}' is already taken. Please choose a different username.\n Enter Username: ".encode())
            else:
                self.user_manager.add_user(username)
                break

        print(f"Received username: {username}")  # Debugging line
        current_users = self.user_manager.display_current_users()
        client.send(current_users.encode())
        self.clients[address] = {'username': username, 'client': client}
        self.broadcast(f"\n{username} has joined the group.", address)

        while True:
            message = client.recv(1024).decode().strip()
            if not message or message == 'exit':
                break

            if message.startswith("POST"):
                self.handle_post_message(client, address, message[5:])  # Pass the message text after 'POST'
            elif message.startswith("RETRIEVE"):
                self.handle_retrieve_message(client, message[8:])  # Pass the message ID

        # Handle user leaving
        print(f"Connection closed from {address}")
        self.broadcast(f"{username} has left the group.", address)
        del self.clients[address]
        client.close()

    def handle_post_message(self, client, address, message_text):
        user_id = self.user_manager.users[self.clients[address]['username']]
        message_id = len(self.messages) + 1
        new_message = Message(self.clients[address]['username'], user_id, message_text, message_id)
        self.messages.append(new_message)
        self.broadcast(new_message.format_post_message())

    def handle_retrieve_message(self, client, message_id):
        try:
            message_id = int(message_id)
            message = next((m for m in self.messages if m.id == message_id), None)
            if message:
                client.send(message.format_retrieve_message().encode())
            else:
                client.send(f"Message with ID {message_id} not found.".encode())
        except ValueError:
            client.send("Invalid message ID.".encode())

    def broadcast(self, message, sender_address=None):
        for address, client_info in self.clients.items():
            if address != sender_address:
                try:
                    print(f"sending {message} to {address}")
                    client_info['client'].send(message.encode())
                except BrokenPipeError:
                    continue


if __name__ == "__main__":
    server = MessageBoardServer()
    server.start()
