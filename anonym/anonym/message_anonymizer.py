import logging
import inject
from telebot.apihelper import ApiTelegramException
from tengi.telegram.inbox_handler import *
from tengi import TelegramBot, telegram_bot_utils, Hasher, Config
from tengi.telegram.constants import TELEGRAM_USER_ID, GROUP_ANONYM_BOT_ID

from anonym.state.enabled_chats import EnabledChats

logger = logging.getLogger(__file__)


class MessageAnonymizer(TelegramInboxHandler):
    config = inject.attr(Config)
    telegram_bot = inject.attr(TelegramBot)
    enabled_chats = inject.attr(EnabledChats)
    hasher = inject.attr(Hasher)

    def message(self, message: types.Message) -> bool:
        chat_id = message.chat.id
        chat_hash = self.hasher.trimmed(chat_id)
        sender_user_id = message.from_user.id

        if not telegram_bot_utils.is_group_message(message):
            logger.debug(f'Ignoring message in non-group chat {chat_hash}')
            return False

        if not self.enabled_chats.is_enabled(chat_id):
            enable_only_for = self.config['enable_only_for']
            if len(enable_only_for) > 0:
                logger.info(f'Ignoring message in disabled chat {chat_hash}')
                return False
            else:
                logger.info(f'Automatically enabling for chat {chat_hash}')
                self.enabled_chats.enable(chat_id)

        if sender_user_id == TELEGRAM_USER_ID:
            logger.debug(f'Skipping {TELEGRAM_USER_ID} message')
            return False

        logger.info(f'Anonymizing message, chat {chat_hash}')

        # Delete the message
        try:
            self.telegram_bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        except ApiTelegramException as ex:
            logger.info(f'Got an exception when trying to hide password, most likely bot does not have admin '
                        f'rights: {ex}')
            error_message = '🚫Cannot anonymize the message. Give me "Delete messages" admin right.'
            self.telegram_bot.send_text(chat_id, text=error_message)
            logger.warning(f'Cannot delete message, no admin rights, chat {message.chat.id} "{message.chat.title}"')
            return True

        # Remove the user from the group
        is_sender_admin = False
        try:
            member = self.telegram_bot.bot.get_chat_member(chat_id=chat_id, user_id=sender_user_id)
            is_sender_admin = (member.status in ('creator', 'administrator')) or (sender_user_id == GROUP_ANONYM_BOT_ID)
            if not is_sender_admin:
                try:
                    self.telegram_bot.bot.kick_chat_member(chat_id=chat_id, user_id=sender_user_id)
                    # Kicked user is automatically banned thus won't be allowed to post future comments
                    self.telegram_bot.bot.unban_chat_member(chat_id=chat_id, user_id=sender_user_id)
                except ApiTelegramException as e:
                    error_message = '🚫Cannot remove the user from the chat to ensure anonymity. Give me "Ban users" ' \
                                    'admin right.'
                    self.telegram_bot.send_text(chat_id, text=error_message)
                    logger.warning(f'Cannot delete user, no admin rights, chat {chat_hash}')
        except Exception as e:
            logger.exception(e)

        # Don't resend message if it contains links for non admins
        should_resend = True

        if message.content_type in ['new_chat_members', 'left_chat_member']:
            should_resend = False

        if should_resend and (not is_sender_admin):
            forbidden_entity_types = self.config['forbidden_entities']
            contains_forbidden_entity = telegram_bot_utils.message_contains_entity(message,
                                                                                   entity_types=forbidden_entity_types)
            should_resend = should_resend and (not contains_forbidden_entity)

        # Resend message
        if should_resend:
            self.telegram_bot.resend_message(chat_id=chat_id, src_message=message)

            # if message.content_type == 'text':
            #     if message.reply_to_message is None:
            #         bot.send_message(message.chat.id, message.html_text)
            #     else:
            #         bot.reply_to(message.reply_to_message, message.html_text)
            # elif message.content_type == 'photo':
            #     photos = message.json['photo']
            #     if len(photos) >= 1:
            #         bot.send_photo(message.chat.id,
            #                        photos[0]['file_id'],
            #                        caption=message.html_caption,
            #                        reply_to_message_id=reply_to_message_id)
            #     else:
            #         print("Strange photo with 0 photos", message)
            # elif message.content_type == 'sticker':
            #     bot.send_sticker(message.chat.id,
            #                      message.sticker.file_id,
            #                      reply_to_message_id=reply_to_message_id)
            # elif message.content_type == 'document':
            #     bot.send_document(message.chat.id,
            #                       message.document.file_id,
            #                       caption=message.html_caption,
            #                       reply_to_message_id=reply_to_message_id)
            # elif message.content_type == 'audio':
            #     bot.send_audio(message.chat.id,
            #                    message.audio.file_id,
            #                    caption=message.html_caption,
            #                    reply_to_message_id=reply_to_message_id)
            # elif message.content_type == 'video':
            #     bot.send_video(message.chat.id,
            #                    message.video.file_id,
            #                    caption=message.html_caption,
            #                    reply_to_message_id=reply_to_message_id)
            # elif message.content_type in ('video_note', 'voice', 'location', 'contact'):
            #     # These are ignored as potentially de-anonymising messages
            #     pass
            # else:
            #     logger.error(f'Unhandled content_type: {message}')
        else:
            logger.debug('Skipping message resend as it contains forbidden entities')

        return True

    # @bot.message_handler(func=lambda m: True, content_types=['new_chat_members', 'left_chat_member'])
    # def handle_member_join_leave(message):
    #     try:
    #         bot.delete_message(message.chat.id, message.message_id)
    #     except Exception as e:
    #         logger.exception(e)


