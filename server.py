import asyncio


class MessageBoardServer:
    def __init__(self):
        self.active_users = set()
        self.messages = []

    async def handle_client(self, reader, writer):
        while True:
            data = await reader.read(100)
            message = data.decode()
            addr = writer.get_extra_info('peername')

            if message == 'QUIT':
                print(f"Closing the connection to {addr}")
                writer.close()
                await writer.wait_closed()
                break

            print(f"Received {message} from {addr}")
            self.messages.append(message)
            self.notify_users(message)
            # Send the latest 2 messages to the client
            latest_messages = self.messages[-2:]
            response = '\n'.join(latest_messages).encode()
            writer.write(response)
            await writer.drain()

    def notify_users(self, message):
        # Send a notification to all connected users
        pass  # Replace with logic to notify users

    async def main(self, host, port):
        server = await asyncio.start_server(self.handle_client, host, port)

        addr = server.sockets[0].getsockname()
        print(f'Serving on {addr}')

        async with server:
            await server.serve_forever()


if __name__ == "__main__":
    # Replace 'localhost' and '8888' with your server's address and port
    server = MessageBoardServer()
    asyncio.run(server.main('localhost', 8888))
