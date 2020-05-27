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

day = date.day
month = date.month
year = date.year

cities_list = []
with open("world_cities_sinoptik_use.txt", "r") as file:
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
        "Привет, {0.first_name}!\n"
        "Я - <b>{1.first_name}</b>.\n"
        "Напиши мне название города и когда ты хочешь узнать погоду".format(
            message.from_user, bot.get_me()
        ),
        parse_mode="html",
        reply_markup=markup,
    )


def delete_punctuation(my_list):
    # Убираем пунктуацию из текста
    message_list = []
    for text in my_list:
        reformated_text = text.translate(str.maketrans("", "", string.punctuation))
        message_list.append(reformated_text.lower())
    return message_list


def translator_from_eng(my_list):
    # Переводчик с английского
    translated_message_list = []
    translator = Translator(to_lang="Russian")
    for word in my_list:
        translation = translator.translate(word)
        translated_message_list.append(translation)
    return translated_message_list


def levenshtein_distance(my_list):
    # Расстояние Левенштейна
    new_message_list = []
    levenshtein_distance_threshold = 0.74
    for world_1 in my_list:
        for world_2 in cities_list:
            if (
                abs(len(world_1) - len(world_2)) / len(world_1)
                < 1 - levenshtein_distance_threshold
            ):
                dist = edit_distance(world_1.lower(), world_2.lower())
                l = len(world_2)
                similarity = 1 - dist / l
                if similarity == 1:
                    new_message_list.insert(0, world_2.lower())
                elif similarity > 0.74:
                    new_message_list.append(world_2.lower())
    return new_message_list


@bot.message_handler(content_types=["text"])
def conversation(message):
    message_text = message.text.split()

    text_without_punctuation = delete_punctuation(message_text)

    translated_text = translator_from_eng(text_without_punctuation)

    checked_text_on_mistakes = levenshtein_distance(translated_text)

    if message.chat.type == "private":
        try:
            if (
                checked_text_on_mistakes[0] == "сейчас"
                or checked_text_on_mistakes[0] == "сегодня"
            ):
                r = requests.get(
                    f"https://sinoptik.ua/погода-{checked_text_on_mistakes[1]}/{date}"
                )
            elif checked_text_on_mistakes[0] == "завтра":
                r = requests.get(
                    f"https://sinoptik.ua/погода-{checked_text_on_mistakes[1]}/{year}-0{month}-{day +1}"
                )
            html = BeautifulSoup(r.content, "html.parser")

            if (
                r.status_code == 200
                and checked_text_on_mistakes[0] == "сегодня"
                or checked_text_on_mistakes[0] == "завтра"
            ):
                temperature_night = html.select("#content")[0].select(".p2 ")[2].text
                temperature_morning = html.select("#content")[0].select(".p4 ")[2].text
                temperature_day = html.select("#content")[0].select(".p6 ")[2].text
                temperature_evening = html.select("#content")[0].select(".p8 ")[2].text
                bot.send_message(
                    message.chat.id,
                    f"B {checked_text_on_mistakes[1].title()} {checked_text_on_mistakes[0]} температура \n"
                    f"утром {temperature_morning}\n"
                    f"днем {temperature_day}\n"
                    f"вечером {temperature_evening}\n"
                    f"ночью {temperature_night}\n",
                )
            elif r.status_code == 200 and checked_text_on_mistakes[0] == "сейчас":
                temperature = html.select("#content")[0].select(".today-temp")[0].text
                bot.send_message(
                    message.chat.id,
                    f"Сейчас в {checked_text_on_mistakes[1].title()} {temperature}",
                )
        except:
            bot.send_message(
                message.chat.id,
                f"Не могу найти {translated_text[0].title()}\n"
                f"Попробуйте другой город или в другом формате\n"
                f"Например: <город> <сейчас, сегодня или завтра>",
            )


# RUN
bot.polling(none_stop=True)