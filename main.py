import json
import random
import re
import nltk
from telegram import Update #новая входящая информация
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters



config_file = open("config.json", "r")
BOT_CONFIG = json.load(config_file)
#тексты
x = []
#классы
y = []
#задача: определить по иксу игрек
for name,data in BOT_CONFIG["intents"].items():
    for example in data['examples']:
        x.append(example)
        y.append(name)

from sklearn.feature_extraction.text import TfidfVectorizer
vectorizer = TfidfVectorizer()
vectorizer.fit(x) #передаем набор текстов, чтобы векторайзер проанализировал
#print(vectorizer.vocabulary_)
x_vectorized = vectorizer.transform(x) #трансформируем тексты в вкетора

from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier()
model.fit (x_vectorized, y) #модель научится по икс определять игрек



def filter(text):# минус знаки плюс нижний регистр
    text=text.lower() #регистр
    #бдуем удалять из текста знаки препинания с помощью регулярных выражений
    punctuation = r"[^\w\s]" #выражение удаляет знаки препинания
    return re.sub(punctuation, "", text) #заменяем знаки преп на пустоту


def IsMatching(text1,text2): #сравниваем два текста
    text1 = filter(text1);
    text2 = filter(text2);
    distance =  nltk.edit_distance(text1,text2)
    average_length = (len(text1)+len(text2))/2
    return distance/average_length <0.3

def getIntent(text): #понимать намерение по тексту
    all_intents = BOT_CONFIG["intents"]
    #пройти по всем намерениям и положить название в name и остальное
    #в переменную дата
    for name, data in all_intents.items():
        #пройти по все примерам этого инетнта, и положить текст
        # в переменную example
        for example in data ["examples"]:
            if IsMatching(text,example):
                return name


def getAnswer (intent):
    responses = BOT_CONFIG["intents"][intent]["responses"]
    return random.choice(responses)


def bot(text):
    intent = getIntent(text)

    if not intent:
        test = vectorizer.transform([text])
        intent = model.predict(test)[0]


    if intent:
        return getAnswer(intent)
#заглушка
    failure_phrases  =BOT_CONFIG["failure_phrases"]
    return random.choice(failure_phrases)


BOT_KEY = '5113853755:AAGNbJ_MZMP4mhjsuQCTwADO7kgHKba6c0k'

def hello(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f'Hello {update.effective_user.first_name}')

# Функция будет вызвана при получении сообщения
def botMessage(update: Update, context: CallbackContext):
    text = update.message.text # Что нам написал пользователь
    print(f"Message: {text}")
    nameus = update.message.from_user.first_name
    reply = nameus+'!:) '+ bot(text)  # Готовим ответ
    update.message.reply_text(reply) # Отправляем ответ обратно пользователю


updater = Updater(BOT_KEY)

updater.dispatcher.add_handler(CommandHandler('hello', hello)) # Конфигурация, при получении команды hello вызвать функцию hello
# Конфигурацию, при получении любого текстового сообщения будет вызвана функция botMessage
updater.dispatcher.add_handler(MessageHandler(Filters.text, botMessage))

updater.start_polling()
updater.idle()

