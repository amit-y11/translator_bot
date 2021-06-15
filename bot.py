from telegram.ext.dispatcher import run_async
from telegram.ext import Updater,CommandHandler,MessageHandler,Filters,ConversationHandler, PicklePersistence
from google_trans_new import google_translator
import telegram
import logging
from languages import LANGUAGES
import os
lang1,maintext=range(2)

bot_token = os.environ.get("bot_token","")

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


LANGCODES = dict(map(reversed, LANGUAGES.items()))

@run_async
def start(update,context):
	first=update.message.chat.first_name
	update.message.reply_text("Hi! "+str(first)+ "\nWelcome to Translator Bot. I can translate text to any language you want , just send me a text to start translating,\nNow you can also add me in groups , click /groups to know how to use me in groups")

@run_async
def main_text(update,context):
	text_data=context.user_data['text_data']=[]
	text=update.message.text
	text_data.append(text)
	update.message.reply_text("Send language in which you want to translate")
	return lang1

@run_async
def list(update,context):
	update.message.reply_text("Here are the list of supported languages \nhttps://telegra.ph/Supported-Languages-08-25")

@run_async
def language(update,context):
	lang=update.message.text
	text_data=context.user_data['text_data'][0]
	if languagecheck(lang)==True:
		dest=getdest(lang)
		text=trans(text_data,update,context,dest)
		message="""
----------------------------------------
💬 Translation :            
{}                
----------------------------------------
🗣️ Pronunciation :        
<strong>{}</strong>     
----------------------------------------

"""
		message1="""
----------------------------------------
💬 Translation :            
{}               
----------------------------------------
"""
		if not text["pronunciation"]:
			context.bot.send_message(chat_id=update.message.chat_id , text=message1.format(text["text"]),parse_mode=telegram.ParseMode.HTML )
		else:
			context.bot.send_message(chat_id=update.message.chat_id , text=message.format(text["text"],text["pronunciation"]),parse_mode=telegram.ParseMode.HTML )
		return ConversationHandler.END
	else:
		update.message.reply_text('Please send correct language\nclick >> /list to see the list of supported languages\nclick >> /cancel to cancel current operation')
	
	

def trans(text,dest='en'):
    ''' Translator Function
    it Translate the text to the destionation language'''
    translator = google_translator()
    try:
        result=translator.translate(text,lang_tgt=dest,pronounce=True)
        res={"text": result [0],"pronunciation": result [2]}
    except Exception as e:
        res={"text":"Error :"+e}
    return  res

def cancel(update, context):
	update.message.reply_text("current operation cancelled")
	return ConversationHandler.END

def languagecheck(text):
	if str(text).lower() in LANGCODES:
		return True
	else:
		return False

def getdest(dest="english"):
    try:
        return LANGCODES[dest.lower()]
    except:
        return False

def translates(update,context):
	try:
		text=update.message.reply_to_message.text
	except AttributeError:
		update.message.reply_text("This command should be used in reply to a message you want to translate")
	
	lang="".join(context.args)
	if len(lang)==0:
		update.message.reply_text("You didn't specified the language")
	else:
		if languagecheck(lang)==True:
			dest=getdest(lang)
			text=trans(text,update, context,dest)
			message="💬 {}\n\n<b><i>🗣️ {}</i></b>".format(text["text"],text["pronunciation"])
			message1="💬 {}".format(text["text"])
			if not text["pronunciation"]:
				update.message.reply_text(message1,parse_mode=telegram.ParseMode.HTML)
			else:
				update.message.reply_text(message,parse_mode=telegram.ParseMode.HTML)
		else:
			update.message.reply_text("Invalid Language! \nsee the list of supported languages : https://telegra.ph/Supported-Languages-08-25")

def groups(update,context):
	update.message.reply_text("Add me to any group and translate any message to any language by replying to a message by command /tr or /translate followed by language in which you want to translate ,the format should be /tr <i>language</i> or /translate <i>language</i>\nfor example : /tr english or /translate english",parse_mode=telegram.ParseMode.HTML)

persistence=PicklePersistence('translatedata')
def main():
	updater = Updater(bot_token, use_context=True, persistence=persistence)
	dp = updater.dispatcher
	conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.private & ~Filters.command,main_text)],

        states={
            lang1: [MessageHandler(Filters.text & ~Filters.command, language)]
        },

        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=False
    )
	dp.add_handler(CommandHandler('translate', translates))
	dp.add_handler(CommandHandler('tr', translates))
	dp.add_handler(CommandHandler ('list',list))
	dp.add_handler(CommandHandler('groups', groups))
	dp.add_handler(CommandHandler('start', start,Filters.private))
	dp.add_handler(conv_handler)

	updater.start_polling()
	updater.idle()


if __name__ == '__main__':
    main()
