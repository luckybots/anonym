import signal
import sys
import time
import telebot

from anocom.config import Config
from anocom import settings
from anocom.settings import default_logger as logger
from anocom.command_parser import CommandParser

config = Config(settings.config_path())
bot = telebot.TeleBot(config.bot_token, parse_mode='HTML')  # You can set parse_mode by default. HTML or MARKDOWN
command_parser = CommandParser()


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    try:
        logger.info(f'Welcome received: "{message.text}"')
        public_help_message = \
"""
I'm Anonymizer bot. You can use me to establish anonymous comments in your channel.
If you want to use me in your channel do the following:
1️⃣ Go to @anocom_chat, provide the name of the discussion group of your channel and ask to enable anocom_bot for it.
2️⃣ Wait for my admin to confirm your request.
3️⃣ Add me to your channel's discussion group and write at least one message in this group.
4️⃣ Message @anocom_chat about step 3️⃣ completion.
5️⃣ Provide me with an admin rights to "Delete messages" and "Ban users" in your discussion group.

❗️Note that after you enable Anonymizer in your group all the messages in the group will be anonymized and users will be kicked from the group after each message.
"""
        bot.send_message(message.chat.id, public_help_message)
    except Exception as e:
        logger.exception(e)


@bot.message_handler(func=lambda m: True, content_types=['new_chat_members', 'left_chat_member'])
def handle_member_join_leave(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except Exception as e:
        logger.exception(e)


@bot.message_handler(func=lambda m: True,
                     content_types=['text', 'audio', 'document', 'photo', 'sticker', 'video', 'video_note', 'voice',
                                    'location', 'contact'])
def handle_message(message):
    try:
        logger.debug(message)

        try_handle_commands(message)
        try_resend_message(message)
    except Exception as e:
        logger.exception(e)


def try_handle_commands(message):
    if message.chat.type != 'private':
        logger.debug('Message ignored by command handler as it was sent not in private chat')
        return

    if message.content_type != 'text':
        logger.debug('Message ignored by command handler as it is not a text message')
        return

    text = message.text
    if text is None:
        logger.debug('Message ignored by command handler as it does not have text')
        return

    #     args = command_parser.parse_command('enable --group_id -12312312312 --password DJ6{eqrg%Jmh6B7h')
    args = command_parser.parse_command(text)

    if command_parser.error_message is not None:
        logger.debug(f'Message ignored by command handler as parser raised an error "{command_parser.error_message}"')
        return  # Most likely it's not a command, just ignore it

    logger.info(f'Bot command: "{args.command}"')
    if args.password is None:
        logger.warning('Command requested without a password')
        return

    if args.password != config.admin_password:
        logger.warning('Command requested with a wrong password')
        return

    if args.command == 'help':
        commands_help_message = '<pre>' + command_parser.format_help() + '</pre>'
        bot.send_message(message.chat.id, commands_help_message)
        return

    if args.command in ('enable', 'disable'):
        group_id = args.group_id
        if group_id is None:
            logger.info(f'Received {args.command} command without group_id')
            bot.send_message(message.chat.id, '--group_id is required')
            return

        if args.command == 'enable':
            if group_id in config.enabled_group_ids:
                logger.info(f'Group {group_id} is already enabled')
                bot.send_message(message.chat.id, f'Group {group_id} is already enabled')
                return
            config.add_enabled_group_id(group_id)
            logger.info(f'Group {group_id} enabled')
            bot.send_message(message.chat.id, f'Group {group_id} enabled')
            return

        elif args.command == 'disable':
            if group_id not in config.enabled_group_ids:
                logger.info(f'Group {group_id} is not enabled')
                bot.send_message(message.chat.id, f'Group {group_id} is not enabled')
                return
            config.remove_enabled_group_id(group_id)
            logger.info(f'Group {group_id} disabled')
            bot.send_message(message.chat.id, f'Group {group_id} disabled')
            return
        else:
            raise Exception(f'Unhandled command {args.command}')


def try_resend_message(message):
    if message.chat.type not in ("group", "supergroup"):
        return

    if message.chat.id not in config.enabled_group_ids:
        logger.info(f'Ignoring message in disabled chat {message.chat.id} "{message.chat.title}"')
        return

    # telegram_notifications_user_id makes messages forwarding from the channel to the group
    telegram_notifications_user_id = 777000
    if message.from_user.id == telegram_notifications_user_id:
        logger.debug('Skipping telegram_notifications_user_id message')
        return

    logger.info(f'Anonymizing message, chat {message.chat.id} "{message.chat.title}"')

    # Delete the message
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except Exception as e:
        error_message = '🚫Cannot anonymize the message. Give me "Delete messages" admin right.'
        bot.send_message(message.chat.id, error_message)
        logger.warning(f'Cannot delete message, no admin rights, chat {message.chat.id} "{message.chat.title}"')
        return

    # Remove the user from the group
    is_admin = False
    try:
        member = bot.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
        logger.debug(member)
        # group_anonymous_bot_id - bot that makes group admins anonymous
        group_anonymous_bot_id = 1087968824
        is_admin = (member.status in ('creator', 'administrator')) \
                   or (message.from_user.id == group_anonymous_bot_id)
        if not is_admin:
            try:
                bot.kick_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
                bot.unban_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
            except Exception as e:
                error_message = '🚫Cannot remove the user from the chat to ensure anonymity. Give me "Ban users" admin right.'
                bot.send_message(message.chat.id, error_message)
                logger.warning(f'Cannot delete user, no admin rights, chat {message.chat.id} "{message.chat.title}"')

    except Exception as e:
        logger.exception(e)

    # Don't resend message if it contains links for non admins
    should_resend = True
    if not is_admin:
        entities = []
        if 'entities' in message.json:
            entities.extend(message.json['entities'])
        if 'caption_entities' in message.json:
            entities.extend(message.json['caption_entities'])
        unallowed_entity_types = ['mention', 'url', 'text_link', 'email', 'phone_number']
        contains_unallowed_entity = any([x['type'] in unallowed_entity_types for x in entities])
        should_resend = should_resend and (not contains_unallowed_entity)

    # Resend message
    if should_resend:
        reply_to_message_id = None if (message.reply_to_message is None) else message.reply_to_message.message_id

        if message.content_type == 'text':
            if message.reply_to_message is None:
                bot.send_message(message.chat.id, message.html_text)
            else:
                bot.reply_to(message.reply_to_message, message.html_text)
        elif message.content_type == 'photo':
            photos = message.json['photo']
            if len(photos) >= 1:
                bot.send_photo(message.chat.id,
                               photos[0]['file_id'],
                               caption=message.html_caption,
                               reply_to_message_id=reply_to_message_id)
            else:
                print("Strange photo with 0 photos", message)
        elif message.content_type == 'sticker':
            bot.send_sticker(message.chat.id,
                             message.sticker.file_id,
                             reply_to_message_id=reply_to_message_id)
        elif message.content_type == 'document':
            bot.send_document(message.chat.id,
                              message.document.file_id,
                              caption=message.html_caption,
                              reply_to_message_id=reply_to_message_id)
        elif message.content_type == 'audio':
            bot.send_audio(message.chat.id,
                           message.audio.file_id,
                           caption=message.html_caption,
                           reply_to_message_id=reply_to_message_id)
        elif message.content_type == 'video':
            bot.send_video(message.chat.id,
                           message.video.file_id,
                           caption=message.html_caption,
                           reply_to_message_id=reply_to_message_id)
        elif message.content_type in ('video_note', 'voice', 'location', 'contact'):
            # These are ignored as potentially de-anonymising messages
            pass
        else:
            logger.error(f'Unhandled content_type: {message}')
    else:
        logger.debug('Skipping message resend as it contains unallowed entities')


if __name__ == '__main__':
    # KeyboardInterrupt catching doesn't work as telebot catches it internally and sends as a different error
    def sigint_handler(sig, frame):
        logger.info('Ctrl+C pressed')
        logger.info('Bot finished')
        sys.exit(0)
    signal.signal(signal.SIGINT, sigint_handler)

    logger.info('Bot started')
    while True:
        try:
            bot.polling()
        except Exception as e:
            logger.exception(e)

        logger.info(f'Restarting in {settings.RESTART_TIMEOUT:,} seconds')
        time.sleep(settings.RESTART_TIMEOUT)
