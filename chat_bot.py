import telebot
import config
import random
from weather_forecast_bot import temperature
from telebot import types

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def welcome(message):
    # keyboard
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Random number")
    item2 = types.KeyboardButton("How are you?")

    markup.add(item1, item2)

    bot.send_message(message.chat.id,
                     "Hello!, {0.first_name}!\n"
                     "I am - <b>{1.first_name}</b>.\n"
                     "Type Weather to get info about weather today in Kyiv\n"
                     "Type Photo and i will send you an interesting photo".format(
                         message.from_user, bot.get_me()),
                     parse_mode='html', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def conversation(message):
    if message.chat.type == 'private':
        if message.text == 'Weather':
            # info about weather
            bot.send_message(message.chat.id, 'Today in Kyiv' + ' ' + temperature)
        elif message.text == 'Random number':
            bot.send_message(message.chat.id, str(random.randint(0, 100)))
        elif message.text == 'Photo':
            sti = open('static/corgey2.jpeg', 'rb')
            bot.send_photo(message.chat.id, sti)
        elif message.text == 'How are you?':
            markup = types.InlineKeyboardMarkup(row_width=2)
            item1 = types.InlineKeyboardButton("Good", callback_data='good')
            item2 = types.InlineKeyboardButton("Bad", callback_data='bad')

            markup.add(item1, item2)

            bot.send_message(message.chat.id, 'Fine, and yours?', reply_markup=markup)
        else:
            bot.send_message(message.chat.id, 'I don`t know what to answer.')


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
