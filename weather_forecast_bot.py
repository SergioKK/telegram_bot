import telebot
import config
import requests
from bs4 import BeautifulSoup

r = requests.get('https://sinoptik.ua/погода-киев')
html = BeautifulSoup(r.content, 'html.parser')
bot = telebot.TeleBot(config.TOKEN)
# This is parse info about today temperature
for el in html.select('#content'):
    temperature = el.select('.today-temp')[0].text

