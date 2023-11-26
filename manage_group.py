class GroupManager:
    def __init__(self):
        self.groups = {}  # format: {group_name: set_of_usernames}

    def create_group(self, group_name):
        if group_name not in self.groups:
            self.groups[group_name] = set()

    def delete_group(self, group_name):
        if group_name in self.groups:
            del self.groups[group_name]

    def add_user_to_group(self, username, group_name):
        if group_name in self.groups:
            self.groups[group_name].add(username)

    def remove_user_from_group(self, username, group_name):
        if group_name in self.groups and username in self.groups[group_name]:
            self.groups[group_name].remove(username)
