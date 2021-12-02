import telebot
import os, logging, regex, json
import emoji_download, emoji
import base64, requests
from uuid import uuid4
from PIL import Image

logging.basicConfig(
    format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s',
    level=logging.INFO
)
plus_icon = "https://pp.vk.me/c627626/v627626512/2a627/7dlh4RRhd24.jpg"

logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('COMBIMOJI_TOKEN')
IMGBB_TOKEN = os.getenv('IMGBB_API_KEY')

bot = telebot.TeleBot(BOT_TOKEN)


def list_emojis(text: str) -> list[str]:
    emoji_list = []
    data = regex.findall(r'\X', text)
    for word in data:
        if any(char in emoji.UNICODE_EMOJI['en'] for char in word):
            emoji_list.append(word)

    return emoji_list


def log_emojis(emojis):
    with open("data/emojis.txt", "r", encoding="utf-8") as f:
        logged_emojis = set(f.read())
    with open("data/emojis.txt", "a", encoding="utf-8") as f:
        for emoji in emojis:
            if emoji not in logged_emojis:
                f.write(emoji)

                logged_emojis.add(emoji)



@bot.message_handler(commands=["plan_message"])
def plan_message(message):
    answer = """
A few features are currently in progress, a few more are planned for the near future.

Frontend:
 - creating stickers, sticker packs
 - adding bot to chats, chat interaction
 - list of avaliable emojis

Backend:
 - upgrading the image caching system
 - logging user interaction
 - automatic replacement bot system for maintenance times
 - refactoring the code
"""
    bot.reply_to(message, answer)


@bot.message_handler(commands=["start"])
def start_message(message):
    bot.reply_to(message, 'Hi! I combine emojis. Try /help to learn more.')


@bot.message_handler(commands=["help"])
def help_message(message):
    answer = """
Send me a message with 2 emojis.

Example:
\tThis is gross! 🤢\n\tI wanna 💩.

For future update ideas, try /plan.        
"""
    bot.reply_to(message, answer)


def identify_user(user, text):
    name = user.first_name
    if user.last_name:
        name = ' '.join([name, user.last_name])

    logger.info(f"{name} at @{user.username} is using me ...")
    logger.info(text)
    logger.info("-----------------------")


@bot.message_handler(commands=['combine'], content_types=['text'])
def search_emojis_in_chat(message):
    user = message.from_user
    identify_user(user, message.text)


    emojis = list_emojis(message.text)
    if len(emojis) == 2:
        bot.send_message(chat_id=message.chat.id, text="Detected 2 emojis, downloading image...")
        if img_title := emoji_download.download_emoji_combo(emojis[:2]):
            log_emojis(emojis[:2])
            bot.send_message(chat_id=message.chat.id, text="Image exists!")
            bot.send_photo(chat_id=message.chat.id, photo=open(img_title, 'rb'))
            bot.send_message(chat_id=message.chat.id, text="And here's the png source:")
            bot.send_document(chat_id=message.chat.id, data=open(img_title, 'rb'))
        else:
            bot.send_message(chat_id=message.chat.id, text="Image doesn't exist :(")
    else:
        bot.reply_to(message, "Normal message, but I want emojis :]")


def search_emojis_inline(text: str):
    emojis = list_emojis(text)
    if len(emojis) == 2:
        if img_title := emoji_download.download_emoji_combo(emojis[:2]):
            log_emojis(emojis[:2])

            return img_title


def uploadphoto(photo_path: str):
    with open(photo_path, "rb") as file:
        url = "https://api.imgbb.com/1/upload"
        payload = {
            "key": IMGBB_TOKEN,
            "image": base64.b64encode(file.read()),
        }
        response = requests.post(url, payload)
        if response.status_code == 200:
            return {
                "photo_url": response.json()["data"]["url"],
                "thumb_url": response.json()["data"]["thumb"]["url"]
            }
    return None


@bot.inline_handler(lambda query: query.query)
def query(inline_query):
    try:
        photo_path = search_emojis_inline(inline_query.query)
        up_photo = uploadphoto(photo_path=photo_path)
        if up_photo:
            results = [
                telebot.types.InlineQueryResultPhoto(
                    id=str(uuid4()),
                    photo_url=up_photo["photo_url"],
                    thumb_url=up_photo["thumb_url"],
                    description="Make a new emoji! [will send as a picture]",
                )
            ]
            bot.answer_inline_query(inline_query.id, results)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    try:
        os.mkdir("./images")
        logger.info("Directory 'images' has been created")
    except:
        pass
    finally:
        logger.info("-----Bot started-----")
        bot.infinity_polling()