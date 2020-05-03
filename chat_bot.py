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
                     "Please write the name of the city whose weather you want to know".format(
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
                bot.send_message(message.chat.id, 'Today in' + ' ' + message.text.title() + ' ' + temperature)
        else:
            bot.send_message(message.chat.id, 'Cannot find that town, please try another town')


# @bot.message_handler(content_types=['text'])
# def conversation(message):
#     if message.chat.type == 'private':
#         if message.text == 'Weather':
#             # info about weather
#             bot.send_message(message.chat.id, 'Today in Kyiv' + ' ' + temperature)
#         elif message.text == 'Random number':
#             bot.send_message(message.chat.id, str(random.randint(0, 100)))
#         elif message.text == 'Photo':
#             sti = open('static/corgey2.jpeg', 'rb')
#             bot.send_photo(message.chat.id, sti)
#         elif message.text == 'How are you?':
#             markup = types.InlineKeyboardMarkup(row_width=2)
#             item1 = types.InlineKeyboardButton("Good", callback_data='good')
#             item2 = types.InlineKeyboardButton("Bad", callback_data='bad')
#
#             markup.add(item1, item2)
#
#             bot.send_message(message.chat.id, 'Fine, and yours?', reply_markup=markup)
#         else:
#             bot.send_message(message.chat.id, 'I don`t know what to answer.')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data == 'good':
                bot.send_message(call.message.chat.id, 'It`s fine')
            elif call.data == 'bad':
                bot.send_message(call.message.chat.id, 'Hold on')

            # remove inline buttons
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="How are you?",
                                  reply_markup=None)

            # show alert
            bot.answer_callback_query(callback_query_id=call.id, show_alert=True,
                                      text="Something is written")

    except Exception as e:
        print(repr(e))


# RUN
bot.polling(none_stop=True)
