import socket
import threading
import sys


class MessageBoardClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.running = True

    def start(self):
        # Connect to the server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

        # Start a new thread for listening to messages from the server
        listener_thread = threading.Thread(target=self.listen_to_server)
        listener_thread.start()

        # Prompt for and send the username to the server
        print("-----Welcome to the message board!-----")
        username = input("Enter your username: ")
        self.send_message(username)

        # Main loop for sending messages
        self.print_commands()
        while self.running:
            message = input()
            self.send_message(message)

            if message.lower() == "exit":
                self.running = False
                break

        # Wait for listener thread to finish
        listener_thread.join()
        self.socket.close()

    def send_message(self, message):
        self.socket.sendall(message.encode())

    def listen_to_server(self):
        while self.running:
            try:
                message = self.socket.recv(1024).decode()
                if message:
                    print(message)
            except:
                print("Error reading from server")
                self.running = False

    def print_commands(self):
        print("\nTo send a message, type \"POST\" followed by the message subject.")
        print("To retrieve a message, type \"RETRIEVE\" followed by the message ID.")
        print("To join a group, type \"JOIN\" followed by the group name")
        print("To leave a group, type \"LEAVE\" followed by the group name")
        print("To post a group message, type \"POST GROUP\" followed by the group ID along with the message subject")
        print("To retrieve a group message, type \"RETRIEVE GROUP\" followed by the group message ID")
        print("To retrieve a list of active users and what groups they are in, type \"LIST USERS\"")


if __name__ == "__main__":
    client = MessageBoardClient("localhost", 8889)  # Adjust the host and port if needed
    client.start()
