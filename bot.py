from telegram import ChatAction,InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext.dispatcher import run_async
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters,CallbackQueryHandler,PicklePersistence
import logging
import os
from functools import wraps
import requests
from gtts import gTTS
from pyrogram import Client
api_key = os.environ.get("api_key","3f36c7420b88957") # bot token
token = os.environ.get("bot_token","2048630384:AAHZZS4M4XtFm8SdOmArfVKWzESucKJPGiQ") # api key from https://ocr.space/ocrapi

def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and context
#Your bot will repond when you type / and then respective commands e.g /start , /help
@run_async     
@send_typing_action
def start(update,context):
    """Send a message when the command /start is issued."""
    global first
    first=update.message.chat.first_name
    update.message.reply_text('Hi! '+str(first)+' \n\nWelcome to Optical Character Recognizer Bot. \n\nJust send a clear image to me and i will recognize the text in the image and send it as a message!')

@run_async
@send_typing_action
def convert_image(update,context):
        file_id = update.message.photo[-1].file_id
        newFile=context.bot.get_file(file_id)
        file= newFile.file_path
        context.user_data['filepath']=file
        keyboard = [[InlineKeyboardButton("English ", callback_data='eng'), InlineKeyboardButton("Russian", callback_data='rus'),InlineKeyboardButton("Czech", callback_data='cze')],
                    [InlineKeyboardButton("Chinese simplified", callback_data='chs'), InlineKeyboardButton("Chinese Traditional", callback_data='cht')],[InlineKeyboardButton("Japanese", callback_data='jpn')] ,
                    [InlineKeyboardButton("Arabic", callback_data='ara'),InlineKeyboardButton("Afrikans", callback_data='AFR'), InlineKeyboardButton("German", callback_data='gre')],
                    [InlineKeyboardButton("Italian", callback_data='ita'),InlineKeyboardButton("Indonesian", callback_data='eng'),InlineKeyboardButton("French", callback_data='fre')],
                    [InlineKeyboardButton ("Spanish", callback_data='spa'),InlineKeyboardButton("Portuguese", callback_data='por'),InlineKeyboardButton("Korean", callback_data='kor')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Select Language : ', reply_markup=reply_markup)

@run_async
def button(update,context):
    filepath=context.user_data['filepath']
    query = update.callback_query
    query.answer()
    query.edit_message_text("Extracting text please wait ...")
    data=requests.get(f"https://api.ocr.space/parse/imageurl?apikey={api_key}&url={filepath}&language={query.data}&detectOrientation=True&filetype=JPG&OCREngine=1&isTable=True&scale=True")
    data=data.json()
    print(data)
    if data:
        message=data['ParsedResults'][0]['ParsedText']
        tts = gTTS(message, lang='en')
        tts.save('mk.mp3')
        with open('mk.mp3', 'rb') as speech:
            bot.sendChatAction(chat_id, 'UPLOAD_AUDIO')
            bot.sendVoice(chat_id, voice=speech, caption=None)
            speech.close()
    else:
        query.edit_message_text(text="⚠️Something went wrong, please try again ⚠️")

persistence=PicklePersistence('userdata')
def main(): 
    bot_token=token
    API_ID = "1888138"
    API_HASH = "82426a55e53c4c3003db9d7f5971cbed"
    bot = Client(
        "bot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=bot_token,
        workers=2
    )
    updater = Updater(bot_token,use_context=True,persistence=persistence)
    dp=updater.dispatcher
    dp.add_handler(CommandHandler('start',start))
    dp.add_handler(MessageHandler(Filters.photo, convert_image))
    dp.add_handler(CallbackQueryHandler(button))
    bot.start
    updater.start_polling(clean=True)
    updater.idle()
 
	
if __name__=="__main__":
	main()
