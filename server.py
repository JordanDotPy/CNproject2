import socket
from threading import Thread


class BulletinBoardServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = {}  # Maps client sockets to usernames
        self.messages = []  # Stores the last two messages

    def start_server(self):
        # Code to initialize and start the server socket in a way that it listens indefinitely
        pass

    def accept_connections(self):
        # Code to accept incoming client connections in a loop
        pass

    def client_thread(self, client_socket):
        # Handles the client connection
        # Gets the username and welcomes the user
        # Notifies others of the new user
        # Shows the last 2 messages and the list of users
        pass

    def broadcast(self, message, exclude_socket=None):
        # Sends a message to all connected clients, except the one specified
        pass

    def remove_client(self, client_socket):
        # Removes a client from the server and notifies others
        pass

    def stop_server(self):
        # Code to stop the server gracefully
        pass


if __name__ == "__main__":
    server = BulletinBoardServer('localhost', 12345)
    server.start_server()
