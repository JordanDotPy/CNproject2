class UserManager:
    def __init__(self):
        self.users = {}  # {username: user_id}
        self.next_user_id = 1

    def add_user(self, username):
        if username not in self.users:
            self.users[username] = self.next_user_id
            self.next_user_id += 1
        return self.users[username]
