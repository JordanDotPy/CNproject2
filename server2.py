import socket
import threading
from message import Message
from manage_user import UserManager
from manage_group import GroupManager


class MessageBoardServer:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.clients = {}  # Store clients as {address: {'username': username, 'client': client_socket}}
        self.public_messages = []  # Store messages as tuples (id, username, post_date, message)
        self.group_messages = {'Group_1': [], 'Group_2': [], 'Group_3': [], 'Group_4': [], 'Group_5': []}
        self.user_manager = UserManager()
        self.group_manager = GroupManager()
        # Create 5 static groups
        for i in range(1, 6):
            self.group_manager.create_group(f"Group_{i}")

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
        self.clients[address] = {'username': username, 'client': client}
        client.send(current_users.encode())
        self.broadcast(f"\n{username} has joined the Message Board.", address)

        # Send the list of available groups to the client
        group_list = "\nAvailable groups: " + ", ".join(self.group_manager.groups.keys())
        client.send(group_list.encode())

        # Send the last two messages to the new user
        last_two_messages = self.public_messages[-2:]
        for msg in last_two_messages:
            client.send(msg.format_post_message().encode())

        while True:
            message = client.recv(1024).decode().strip()
            if not message or message == 'exit':
                # Handle user leaving
                print(f"Connection closed from {address}")
                self.broadcast(f"{username} has left the Message Board.", address)
                del self.clients[address]
                client.close()
                break

            if message.startswith("POST GROUP"):
                # POST to a group with keyword followed by the group ID
                split_message = message.split()
                group_id = split_message[2]
                self.handle_group_post(client, address, message[12:], group_id)
            elif message.startswith("POST"):
                # POST public message to the server for everyone to see
                self.handle_public_post_message(client, address, message[5:])
            elif message.startswith("RETRIEVE GROUP"):
                # RETRIEVE group message with keywords followed by group ID and Group_message ID
                self.handle_group_retrieve(client, message, address)
            elif message.startswith("RETRIEVE"):
                # RETRIEVE a public message
                self.handle_public_retrieve_message(client, message[8:])
            elif message.startswith("JOIN"):
                # JOIN a group with keyword followed by group ID or NAME
                self.handle_join_group(client, address, message)
            elif message.startswith("LEAVE"):
                # LEAVE a group with keyword followed by group ID or NAME
                self.handle_leave_group(client, message, address)

    def handle_public_post_message(self, client, address, message_text):
        user_id = self.user_manager.users[self.clients[address]['username']]
        message_id = len(self.public_messages) + 1
        new_message = Message(self.clients[address]['username'], user_id, message_text, message_id)
        self.public_messages.append(new_message)
        self.broadcast(new_message.format_post_message())

    def handle_group_post(self, client, address, message_text, group_id):
        group_name = f'Group_{group_id}'
        user_id = self.user_manager.users[self.clients[address]['username']]
        message_id = len(self.group_messages[group_name]) + 1
        new_message = Message(self.clients[address]['username'], user_id, message_text, message_id)
        self.group_messages[group_name].append(new_message)
        self.broadcast_group(new_message.format_group_message(group_id), group_id)

    def handle_public_retrieve_message(self, client, message_id):
        try:
            message_id = int(message_id)
            message = next((m for m in self.public_messages if m.id == message_id), None)
            if message:
                client.send(message.format_retrieve_message().encode())
            else:
                client.send(f"Message with ID {message_id} not found.".encode())
        except ValueError:
            client.send("Invalid message ID.".encode())

    def handle_group_retrieve(self, client, message, address):
        _, group_id, message_id = message.split()
        group_name = f"Group_{group_id}"

        if group_name in self.group_manager.groups:
            if self.clients[address]['username'] in self.group_manager.groups[group_name]:
                try:
                    message_id = int(message_id)
                    group_messages = self.group_messages[group_name]
                    retrieved_message = group_messages[message_id] if 0 <= message_id < len(group_messages) else None
                    if retrieved_message:
                        client.send(retrieved_message.format_message().encode())
                    else:
                        client.send(f"Message with ID {message_id} not found in {group_name}.".encode())
                except ValueError:
                    client.send("Invalid message ID.".encode())
            else:
                client.send(f"You are not a member of {group_name}.".encode())
        else:
            client.send(f"Group '{group_id}' does not exist.".encode())

    def handle_join_group(self, client, address, message):
        _, group_identifier = message.split(maxsplit=1)
        print(group_identifier)
        # Determine if the identifier is a name or an ID
        if group_identifier.isdigit():
            # User entered a group ID
            # Group names are formatted like "Group_1", "Group_2", etc.
            group_name = f"Group_{group_identifier}"
        else:
            # User entered a group name
            group_name = group_identifier

        # Check if the group exists and add the user
        if group_name in self.group_manager.groups:
            self.group_manager.add_user_to_group(self.clients[address]['username'], group_name)
            client.send(f"\nYou have joined {group_name}".encode())
        else:
            client.send(f"Group '{group_identifier}' does not exist.".encode())

    def handle_leave_group(self, client, message, address):
        _, group_identifier = message.split(maxsplit=1)

        # Determine if the identifier is a name or an ID
        if group_identifier.isdigit():
            group_name = f"Group_{group_identifier}"  # If user entered a group ID
        else:
            group_name = group_identifier  # If user entered a group name

        # Check if the group exists and remove the user
        if group_name in self.group_manager.groups:
            self.group_manager.remove_user_from_group(self.clients[address]['username'], group_name)
            client.send(f"You have left {group_name}".encode())
        else:
            client.send(f"Group '{group_identifier}' does not exist or you are not a member.".encode())

    def broadcast(self, message, sender_address=None):
        print("BROADCASTING ADDRESSES: ", self.clients.items())
        for address, client_info in self.clients.items():
            if address != sender_address:
                try:
                    print(f"sending {message} to {address}")
                    client_info['client'].send(message.encode())
                except BrokenPipeError:
                    continue

    def broadcast_group(self, message, group_id):
        group_name = f"group_{group_id}"
        if group_name in self.group_manager.groups:
            for username in self.group_manager.groups[group_name]:
                if username in self.clients:  # assuming self.clients maps usernames to client info
                    client_info = self.clients[username]
                    client_info['client'].send(message.encode())


if __name__ == "__main__":
    server = MessageBoardServer()
    server.start()
