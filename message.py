
from datetime import datetime

class Message:
    def __init__(self, sender, user_id, subject, message_id):
        self.id = message_id  # Unique ID for the message
        self.sender = sender
        self.user_id = user_id  # ID of the user who posted the message
        self.subject = subject  # Subject is used as content
        self.post_date = datetime.now()

    def format_message(self):
        # Formats the message for display
        date_str = self.post_date.strftime('%Y-%m-%d %H:%M:%S')
        return f"Message ID: {self.id}, Sender: {self.sender} (ID: {self.user_id}), Date: {date_str}, Subject: {self.subject}"
