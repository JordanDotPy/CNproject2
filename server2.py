import socket
import threading
from message import Message
from manage_user import UserManager
from manage_group import GroupManager


class MessageBoardServer:
    def __init__(self, host='localhost', port=8889):
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
                client.send(f"Username '{username}' is already taken. Please choose a different username.\nRe-enter Username below: ".encode())
            else:
                self.user_manager.add_user(username)
                break

        print(f"Received username: {username}")  # Debugging line
        current_users = self.display_active_users_and_groups()
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
                self.broadcast(f"\n{username} has left the Message Board.", address)
                # remove the user from any group they didnt leave before exiting message board
                for group_name in self.group_manager.groups.keys():
                    if username in self.group_manager.groups[group_name]:
                        self.group_manager.remove_user_from_group(self.clients[address]['username'], group_name)
                # delete the client as well as the username from active users
                del self.clients[address]
                del self.user_manager.users[username]
                client.close()
                break

            if message.startswith("POST GROUP"):
                # POST to a group with keyword followed by the group ID and the message subject
                split_message = message.split()
                group_id = split_message[2]
                print("GROUP ID: ", group_id)
                self.handle_group_post(client, address, message[12:], group_id)
            elif message.startswith("POST"):
                # POST public message to the server for everyone to see
                self.handle_public_post_message(client, address, message[5:])
            elif message.startswith("RETRIEVE GROUP") and len(message.split()) == 4:
                # RETRIEVE group message with keywords followed by group ID and Group_message ID
                self.handle_group_retrieve(client, message, address)
            elif message.startswith("RETRIEVE"):
                # RETRIEVE a public message
                self.handle_public_retrieve_message(client, message[8:])
            elif message.startswith("JOIN") and len(message.split()) == 2:
                # JOIN a group with keyword followed by group ID or NAME
                self.handle_join_group(client, address, message)
            elif message.startswith("LEAVE"):
                # LEAVE a group with keyword followed by group ID or NAME
                self.handle_leave_group(client, message, address)
            elif message == "LIST USERS":
                client.send(self.display_active_users_and_groups().encode())
            else:
                bad_format_message = "\nThe formatting of your message seems to be invalid."
                display_keys = "\nTo send a message, type \"POST\" followed by the message subject." \
                               "\nTo retrieve a message, type \"RETRIEVE\" followed by the message ID." \
                               "\nTo join a group, type \"JOIN\" followed by the group name" \
                               "\nTo leave a group, type \"LEAVE\" followed by the group name" \
                               "\nTo post a group message, type \"POST GROUP\" followed by the group ID along with the message subject" \
                               "\nTo retrieve a group message, type \"RETRIEVE GROUP\" followed by the group message ID" \
                               "\nTo retrieve a list of active users and what groups they are in, type \"LIST USERS\""
                client.send(bad_format_message.encode())
                client.send(display_keys.encode())

    def handle_public_post_message(self, client, address, message_text):
        # create a formatted message based on client's information, add the message to the public_messages list, and broadcast to all users
        user_id = self.user_manager.users[self.clients[address]['username']]
        message_id = len(self.public_messages) + 1
        new_message = Message(self.clients[address]['username'], user_id, message_text, message_id)
        self.public_messages.append(new_message)
        self.broadcast(new_message.format_post_message())

    def handle_group_post(self, client, address, message_text, group_id):
        group_name = f'Group_{group_id}'
        if group_name in self.group_manager.groups:
            # check is user is within the group he wants to post the message from
            if self.clients[address]['username'] in self.group_manager.groups[group_name]:
                try:
                    # create a formatted message based on client's information, add the message to the group's list, and broadcast to all users within the group
                    user_id = self.user_manager.users[self.clients[address]['username']]
                    message_id = len(self.group_messages[group_name]) + 1
                    new_message = Message(self.clients[address]['username'], user_id, message_text, message_id)
                    self.group_messages[group_name].append(new_message)
                    self.broadcast_group(new_message.format_group_message(group_id), group_id)
                except ValueError:
                    client.send("\nInvalid Group ID.".encode())
            else:
                not_in_group = f"\nYou are not apart of {group_name}"
                return client.send(not_in_group.encode())
        else:
            client.send(f"\n{group_name} does not exist.".encode())

    def handle_public_retrieve_message(self, client, message_id):
        try:
            # with given message ID, find the ID within public message list and retrieve it
            message_id = int(message_id)
            message = next((m for m in self.public_messages if m.id == message_id), None)
            if message:
                client.send(message.format_retrieve_message().encode())
            else:
                client.send(f"\nPublic message with ID {message_id} not found.".encode())
        except ValueError:
            client.send("\nInvalid public message ID.".encode())

    def handle_group_retrieve(self, client, message, address):
        _, _, group_id, message_id = message.split()
        print("RETRIEVE GROUP GROUP ID: ", group_id)
        group_name = f"Group_{group_id}"

        if group_name in self.group_manager.groups:
            # check is user is within the group he wants to retrieve the message from
            if self.clients[address]['username'] in self.group_manager.groups[group_name]:
                try:
                    message_id = int(message_id)
                    print('MESSAGE ID: ', message_id)
                    group_messages = self.group_messages[group_name]
                    print("LENGTH OF GROUP MESSAGE: ", len(group_messages))
                    retrieved_message = group_messages[message_id - 1] if 0 < message_id <= len(group_messages) else None
                    # message was found in the right group
                    if retrieved_message:
                        client.send(retrieved_message.format_group_retrieve_message(group_name).encode())
                    else:
                        client.send(f"\nMessage with ID {message_id} not found in {group_name}.".encode())
                # improper use of message ID
                except ValueError:
                    client.send("\nInvalid message ID.".encode())
            else:
                client.send(f"\nYou are not a member of {group_name}.".encode())
        else:
            client.send(f"\nGroup_{group_id} does not exist.".encode())

    def handle_join_group(self, client, address, message):
        _, group_id = message.split(maxsplit=1)
        # Determine if the identifier is a name or an ID
        if group_id.isdigit():
            # User entered a group ID
            # Group names are formatted like "Group_1", "Group_2", etc.
            group_name = f"Group_{group_id}"
        else:
            # User entered a group name
            group_name = group_id
            group_id = group_id.split("_")
            group_id = group_id[1]

        # Check if the group exists and add the user
        if group_name in self.group_manager.groups:
            if self.clients[address]['username'] in self.group_manager.groups[group_name]:
                already_in_group = "\nYou have already joined this group."
                client.send(already_in_group.encode())
            else:
                # broadcast to group that user has joined the group
                self.group_manager.add_user_to_group(self.clients[address]['username'], group_name)
                user_joined_group = f"\n{self.clients[address]['username']} has joined {group_name}"
                self.broadcast_group(user_joined_group, group_id)
                # print the last two messages from the group
                for msg in self.group_messages[group_name][-2:]:
                    try:
                        client.send(msg.format_group_message(group_id).encode())
                    except IndexError:
                        continue
        else:
            client.send(f"\nGroup '{group_id}' does not exist.".encode())

    def handle_leave_group(self, client, message, address):
        _, group_id = message.split(maxsplit=1)

        # Determine if the identifier is a name or an ID
        if group_id.isdigit():
            group_name = f"Group_{group_id}"  # If user entered a group ID
        else:
            group_name = group_id  # If user entered a group name
            group_id = group_id.split("_")
            group_id = group_id[1]

        # Check if the group exists and remove the user
        if group_name in self.group_manager.groups:
            if self.clients[address]['username'] in self.group_manager.groups[group_name]:
                # broadcast to group that user has left the group
                user_left_group = f"\n{self.clients[address]['username']} has left {group_name}"
                self.broadcast_group(user_left_group, group_id)
                self.group_manager.remove_user_from_group(self.clients[address]['username'], group_name)
            else:
                client.send(f"\nYou are not apart of Group_{group_id}.".encode())
        else:
            client.send(f"\nGroup_'{group_id}' does not exist.".encode())

    def display_active_users_and_groups(self):
        # Compile a list of all active users
        active_users_info = "\nActive Users: " + ", ".join([info['username'] for info in self.clients.values()])

        # Compile information about users in each group
        group_info = ""
        for group_name, users in self.group_manager.groups.items():
            group_users = ", ".join(users)
            group_info += f"\nGroup {group_name}: {group_users}"

        return active_users_info + group_info

    def broadcast(self, message, sender_address=None):
        print("BROADCASTING ADDRESSES: ", self.clients.items())
        # send message to all the active users
        for address, client_info in self.clients.items():
            if address != sender_address:
                try:
                    print(f"sending {message} to {address}")
                    client_info['client'].send(message.encode())
                except BrokenPipeError:
                    continue

    def broadcast_group(self, message, group_id):
        group_name = f"Group_{group_id}"
        # figure out if given group name is one of the 5 static groups
        if group_name in self.group_manager.groups:
            # check if user is apart pof said group and send message to all group users
            for username in self.group_manager.groups[group_name]:
                for _, client_info in self.clients.items():
                    if client_info['username'] == username:
                        client_info['client'].send(message.encode())


if __name__ == "__main__":
    server = MessageBoardServer()
    server.start()
