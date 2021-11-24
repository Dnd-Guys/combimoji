#!/usr/bin/env python3

import logging
import os

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import emoji
import regex
import emoji_download


# Telegram API secret token
TOKEN = os.getenv('COMBIMOJI_TOKEN')


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def list_emojis(text: str) -> list[str]:
    emoji_list = []
    data = regex.findall(r'\X', text)
    for word in data:
        if any(char in emoji.UNICODE_EMOJI['en'] for char in word):
            emoji_list.append(word)

    return emoji_list


def start_message(update, context):
    update.message.reply_text('Hi! I combine emojis. Try /help to learn more.')


def help_message(update, context):
    update.message.reply_text("""Send me a message with 2 emojis.

Example:
\tThis is gross! 🤢\n\tI wanna 💩.

For future update ideas, try /plan.        
""")


def plan_message(update, context):
    update.message.reply_text("""A few features are currently in progress, a few more are planned for the near future.

Frontend:
 - creating stickers, sticker packs
 - adding bot to chats, chat interaction
 - list of avaliable emojis

Backend:
 - upgrading the image caching system
 - logging user interaction
 - automatic replacement bot system for maintenance times
 - refactoring the code
""")


def search_emojis(update, context):
    user = update.message.from_user
    name = user['first_name']
    if user['last_name']:
        name = ' '.join([name, user['last_name']])

    print(f"{name} at @{user['username']} is using me ...")
    print(update.message.text)
    print("-----------------------")

    emojis = list_emojis(update.message.text)
    if len(emojis) >= 2:
        update.message.reply_text("Detected 2 emojis, downloading image...")
        if img_title := emoji_download.download_emoji_combo(emojis[:2]):
            update.message.reply_text("Image exists!")
            update.message.reply_photo(open(img_title, 'rb'))
            update.message.reply_text("And here's the png source:")
            update.message.reply_document(open(img_title, 'rb'))
        else:
            update.message.reply_text("Image doesn't exist :(")
    else:
        update.message.reply_text("Normal message.")


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Updater is a simple Bot frontend, enough for our purposes (for now)
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start_message))
    dp.add_handler(CommandHandler("help", help_message))
    dp.add_handler(CommandHandler("plan", plan_message))
    dp.add_handler(MessageHandler(Filters.text, search_emojis))

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
