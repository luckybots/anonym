from inject import Binder
import inject
from tengi import *

from anonym.setup import constants
from anonym.command.params import command_params
from anonym.state.enabled_chats import EnabledChats
from anonym.anonym.message_anonymizer import MessageAnonymizer
from anonym.command.handler_enabling import CommandHandlerEnabling


def bind_app_dependencies(binder: Binder):
    binder.bind_to_constructor(App, lambda: App(update_funcs=[inject.instance(TelegramInboxHub).update],
                                                update_seconds=constants.UPDATE_SECONDS,
                                                restart_seconds=constants.RESTART_SECONDS))
    binder.bind(Config, Config(config_path=constants.config_path(),
                               example_path=constants.config_example_path()))
    binder.bind_to_constructor(Hasher, lambda: Hasher(config=inject.instance(Config)))
    binder.bind_to_constructor(TelegramBot, lambda: TelegramBot(token=inject.instance(Config)['bot_token']))
    binder.bind_to_constructor(TelegramCursor,
                               lambda: TelegramCursor(bot=inject.instance(TelegramBot),
                                                      look_back_days=constants.BOT_LOOK_BACK_DAYS,
                                                      long_polling_timeout=constants.LONG_POLLING_TIMEOUT))

    binder.bind_to_constructor(CommandHandlerPool, lambda: CommandHandlerPool(handlers=[
        CommandHandlerEssentials(),
        CommandHandlerPassword(),
        CommandHandlerConfig(),
        CommandHandlerEnabling(),
    ]))
    binder.bind_to_constructor(CommandParser, lambda: CommandParser(handler_pool=inject.instance(CommandHandlerPool),
                                                                    params=command_params))
    binder.bind_to_constructor(CommandHub, lambda: CommandHub(config=inject.instance(Config),
                                                              telegram_bot=inject.instance(TelegramBot),
                                                              parser=inject.instance(CommandParser),
                                                              handler_pool=inject.instance(CommandHandlerPool)))
    binder.bind_to_constructor(MessagesLogger,
                               lambda: MessagesLogger(dir_path=constants.messages_log_dir(),
                                                      file_name_prefix=constants.MESSAGES_LOG_PREFIX,
                                                      command_parser=inject.instance(CommandHub).parser,
                                                      hasher=inject.instance(Hasher),
                                                      chat_types=constants.MESSAGES_LOG_CHAT_TYPES))
    binder.bind_to_constructor(TelegramInboxHub,
                               lambda: TelegramInboxHub(telegram_cursor=inject.instance(TelegramCursor),
                                                        chain_handlers=[inject.instance(CommandHub),
                                                                        inject.instance(MessageAnonymizer)]))

    binder.bind_to_constructor(EnabledChats,
                               lambda: EnabledChats(state_file_path=constants.enabled_chats_state_path()))
