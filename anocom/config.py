import json


class Config:
    def __init__(self, config_path):
        self.config_path = config_path
        with open(self.config_path, 'r') as f:
            self.dict = json.load(f)

        assert 'bot_token' in self.dict
        assert 'admin_password' in self.dict

        if 'enabled_group_ids' not in self.dict:
            self.dict['enabled_group_ids'] = []

    def save_to_disk(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.dict, f)

    @property
    def bot_token(self):
        return self.dict['bot_token']

    @property
    def admin_password(self):
        return self.dict['admin_password']

    @property
    def enabled_group_ids(self):
        list_ids = [] if 'enabled_group_ids' not in self.dict else self.dict['enabled_group_ids']
        return tuple(list_ids)

    @enabled_group_ids.setter
    def enabled_group_ids(self, value):
        self.dict['enabled_group_ids'] = list(value)
        self.save_to_disk()

    def add_enabled_group_id(self, group_id):
        list_ids = list(self.enabled_group_ids)
        assert group_id not in list_ids
        list_ids.append(group_id)
        self.enabled_group_ids = list_ids

    def remove_enabled_group_id(self, group_id):
        list_ids = list(self.enabled_group_ids)
        assert group_id in list_ids
        list_ids.remove(group_id)
        self.enabled_group_ids = list_ids
