from typeguard import typechecked
from typing import List, Optional
from tengine.state.preserver import *
from tengine import telegram_bot_utils


class EnabledChats(Preserver):
    def __init__(self, state_file_path: Path):
        super().__init__(state_file_path)

    @typechecked
    def is_enabled(self, chat_id: int):
        enabled_chats = self.ensure_enabled_chats()
        return chat_id in enabled_chats

    @typechecked
    def enable(self, chat_id: int):
        assert not self.is_enabled(chat_id)
        enabled_chats = self.ensure_enabled_chats()
        enabled_chats.append(chat_id)
        self.update_enabled_chats(enabled_chats)

    @typechecked
    def disable(self, chat_id: int):
        assert self.is_enabled(chat_id)
        enabled_chats = self.ensure_enabled_chats()
        enabled_chats = [x for x in enabled_chats if (x != chat_id)]
        self.update_enabled_chats(enabled_chats)

    @typechecked
    def ensure_enabled_chats(self) -> list:
        if 'enabled_chats' not in self.state:
            self.state['enabled_chats'] = []
        return self.state['enabled_chats']

    @typechecked
    def update_enabled_chats(self, enabled_chats: list):
        self.state['enabled_chats'] = enabled_chats
