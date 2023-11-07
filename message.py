from datetime import datetime


class Message:
    def __init__(self, sender, subject, content):
        self.id = None  # This will be set by the server
        self.sender = sender
        self.subject = subject
        self.content = content
        self.post_date = datetime.now()

    def format_message(self):
        # Formats the message for display
        pass
