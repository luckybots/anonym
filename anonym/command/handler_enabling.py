import inject
import logging
from tengi.command.command_handler import *

from anonym.state.enabled_chats import EnabledChats

logger = logging.getLogger(__file__)


class CommandHandlerEnabling(CommandHandler):
    enabled_chats = inject.attr(EnabledChats)

    def get_cards(self) -> Iterable[CommandCard]:
        return [CommandCard(command_str='/enable',
                            description='Enable bot for given chat',
                            is_admin=True),
                CommandCard(command_str='/disable',
                            description='Disable bot for a given chat',
                            is_admin=True),
                ]

    def handle(self, context: CommandContext):
        chat_id = context.get_mandatory_arg('chat_id')
        try:
            chat_id = int(chat_id)
        except ValueError:
            context.reply(f'chat_id must be integer')
            return
        if context.command == '/enable':
            if self.enabled_chats.is_enabled(chat_id):
                context.reply('Already enabled')
                return
            self.enabled_chats.enable(chat_id)
            context.reply('Done')
        elif context.command == '/disable':
            if not self.enabled_chats.is_enabled(chat_id):
                context.reply('Not enabled')
                return
            self.enabled_chats.disable(chat_id)
            context.reply('Done')
        else:
            raise ValueError(f'Unhandled command: {context.command}')
