import telebot
import sqlite3


conn = sqlite3.connect("tokens.db", check_same_thread=False)
curs = conn.cursor()

logger_token, main_token = map(lambda r: r[0], curs.execute('select token from tokens').fetchall())
conn.close()

conn = sqlite3.connect("hashtags.db", check_same_thread=False)
curs = conn.cursor()
bot = telebot.TeleBot(main_token)

bot_logger = telebot.TeleBot(logger_token)

def log(message):
    bot_logger.send_message(307518206,f'#Hashtag получил сообщение!\n user: @{message.from_user.username}\n name: {message.from_user.first_name} {message.from_user.last_name}\n text: {message.text} \n content_type: {message.content_type}', disable_notification=True)

@bot.message_handler(commands=['start','help'])
def send_welcome(message):
    log(message)
    keyboard=telebot.types.ReplyKeyboardMarkup()
    keyboard.add(telebot.types.KeyboardButton('Поделиться местоположением', request_location=True))
    bot.send_message(message.chat.id, "Отправь свою (или любую) геопозицию, а я тебе - популярные хэштеги в этой округе",reply_markup=keyboard)

def expand(dic, lst):
    for l in lst:
        if l in dic.keys():
            dic[l]+=1
        else:
            dic[l]=1

@bot.message_handler(content_types=['location'])
def send_hashtags(message):
    log(message)
    curs.execute(f'select hashtags from hash where ((abs(lat-{message.location.latitude})+abs(lng-{message.location.longitude}))<0.003)')
    dic={}
    for fetch in curs.fetchall():
        print(fetch)
        expand(dic,fetch[0].split('|'))

    bot.send_message(message.chat.id,'Вот список хэштегов:\n'+'\n'.join(list(dict(sorted(dic.items(), key=lambda item: item[1],reverse=True)).keys())[:15]))

bot.polling()