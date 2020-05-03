import telebot
import config
from telebot import types
import requests
from bs4 import BeautifulSoup

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def welcome(message):
    # keyboard
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Киев")
    item2 = types.KeyboardButton("Одесса")

    markup.add(item1, item2)

    bot.send_message(message.chat.id,
                     "Hello, {0.first_name}!\n"
                     "I am - <b>{1.first_name}</b>.\n"
                     "Please, write the name of the city for witch you need to look up the weather".format(
                         message.from_user, bot.get_me()),
                     parse_mode='html', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def conversation(message):
    if message.chat.type == 'private':
        r = requests.get('https://sinoptik.ua/погода-' + message.text)
        html = BeautifulSoup(r.content, 'html.parser')
        if r.status_code == 200:
            for el in html.select('#content'):
                temperature = el.select('.today-temp')[0].text
                bot.send_message(message.chat.id, 'Now in ' + message.text.title() + ' ' + temperature)
        else:
            bot.send_message(message.chat.id,
                             'Cannot find that town ' + message.text.title() + '\nPlease try another city')


# RUN
bot.polling(none_stop=True)
