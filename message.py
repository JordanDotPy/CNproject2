
from datetime import datetime


class Message:
    def __init__(self, sender, user_id, subject, message_id):
        self.id = message_id  # Unique ID for the message
        self.sender = sender
        self.user_id = user_id  # ID of the user who posted the message
        self.subject = subject  # Subject is used as content
        self.post_date = datetime.now()

    def format_post_message(self):
        # Formats the message for display
        date_str = self.post_date.strftime('%Y-%m-%d %H:%M:%S')
        return f"\nMessage ID: {self.id}, Sender: {self.sender} (ID: {self.user_id}), Date: {date_str}, Subject: {self.subject}"

    def format_retrieve_message(self):
        date_str = self.post_date.strftime('%Y-%m-%d %H:%M:%S')
        return f"\nSUCCESSFULLY RETRIEVED PUBLIC MESSAGE | Message ID: {self.id}, Sender: {self.sender} (ID: {self.user_id}), Date: {date_str}, Subject: {self.subject}"

    def format_group_message(self, group_name):
        # Formats the message for display
        date_str = self.post_date.strftime('%Y-%m-%d %H:%M:%S')
        return f"\nGroup: {group_name}, Message ID: {self.id}, Sender: {self.sender} (ID: {self.user_id}), Date: {date_str}, Subject: {self.subject}"

    def format_group_retrieve_message(self, group_name):
        date_str = self.post_date.strftime('%Y-%m-%d %H:%M:%S')
        return f"\nSUCCESSFULLY RETRIEVED GROUP MESSAGE | Group: {group_name}, Message ID: {self.id}, Sender: {self.sender}, (ID: {self.user_id}), Date: {date_str}, Subject: {self.subject}"
