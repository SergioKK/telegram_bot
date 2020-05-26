import datetime
import random
import string
import telebot
import config
from telebot import types
import requests
from bs4 import BeautifulSoup
from nltk.metrics.distance import edit_distance
from translate import Translator

bot = telebot.TeleBot(config.TOKEN)

date = datetime.date.today()

cities_list = []
with open("cities2.txt", "r") as file:
    for item in file:
        cities_list.append(item.split()[0])


@bot.message_handler(commands=["start"])
def welcome(message):
    # keyboard
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton(f"Киев сейчас")
    item2 = types.KeyboardButton(f"Лондон сегодня")

    markup.add(item1, item2)

    bot.send_message(
        message.chat.id,
        "Hello, {0.first_name}!\n"
        "I am - <b>{1.first_name}</b>.\n"
        "Please, write the name of the city for witch you need to look up the weather".format(
            message.from_user, bot.get_me()
        ),
        parse_mode="html",
        reply_markup=markup,
    )


@bot.message_handler(content_types=["text"])
def conversation(message):
    message_text = message.text.split()
    date_request = date

    # Убираем пунктуацию из текста
    message_list = []
    for text in message_text:
        reformated_text = text.translate(str.maketrans("", "", string.punctuation))
        message_list.append(reformated_text.lower())

    # Переводчик с английского
    translated_message_list = []
    translator = Translator(to_lang="Russian")
    for word in message_text:
        translation = translator.translate(word)
        translated_message_list.append(translation)

    # Расстояние Левенштейна
    new_message_list = []
    for world_1 in translated_message_list:
        for world_2 in cities_list:
            dist = edit_distance(world_1.lower(), world_2.lower())
            l = len(world_2)
            similarity = 1 - dist / l
            if similarity == 1:
                new_message_list.insert(0, world_2.lower())
            elif similarity > 0.74:
                new_message_list.append(world_2.lower())

    if message.chat.type == "private":
        try:
            if new_message_list[0] == 'сейчас':
                r = requests.get(
                    f"https://sinoptik.ua/погода-{new_message_list[1].lower()}/{date_request}"
                )
            elif new_message_list[0] == 'сегодня':
                r = requests.get(
                    f"https://sinoptik.ua/погода-{new_message_list[1]}/{date_request}"
                )
            elif new_message_list[0] == 'завтра':
                r = requests.get(
                    f"https://sinoptik.ua/погода-{new_message_list[1]}/{date_request.day + 1}"
                )
            html = BeautifulSoup(r.content, "html.parser")
            if (
                r.status_code == 200
                and new_message_list[0] == 'сегодня'
                or new_message_list[0] == 'завтра'
            ):

                temperature_morning = html.select("#content")[0].select(".p4 ")[2].text
                temperature_day = html.select("#content")[0].select(".p6 ")[2].text
                temperature_evening = html.select("#content")[0].select(".p8 ")[2].text
                bot.send_message(
                    message.chat.id,
                    f"B {new_message_list[1].title()} {new_message_list[0]} температура \n"
                    f"утром {temperature_morning}\n"
                    f"днем {temperature_day}\n"
                    f"вечером {temperature_evening}\n",
                )
            elif r.status_code == 200 and new_message_list[0] == 'сейчас':
                temperature = html.select("#content")[0].select(".today-temp")[0].text
                bot.send_message(
                    message.chat.id,
                    f"Сейчас в {new_message_list[1].title()} {temperature}",
                )
            else:
                bot.send_message(
                    message.chat.id,
                    f"Не могу найти {new_message_list[1].title()}\n"
                    f"Попробуйте пожалуйста другой город",
                )
        except:
            bot.send_message(
                message.chat.id,
                f"Я что-то напутал\nПопробуйте в формате: <город> сейчас, сегодня или завтра",
            )


# RUN
bot.polling(none_stop=True)
