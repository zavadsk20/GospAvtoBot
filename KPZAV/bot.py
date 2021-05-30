import telebot
import config
import random
import requests
import codecs
import datetime
import time
import avtoupdate
import mysql.connector
import logging
from telebot import types
import json
import re
import test

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="1234",
  database="gospavto"
)
bot = telebot.TeleBot(config.TOKEN)


logger = logging.getLogger()
logger.setLevel(logging.INFO)

# create the logging file handler
fh = logging.FileHandler("GospAvtoBotLog.log")

formatter = logging.Formatter('%(asctime)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
starttime = "00:00"
endtime = "00:45"
pole = ["id:  ", "Код ЄДРПОУ:  ",  "Власник:  ", "Статус:  ",
    "licIssueDate:  ", "Початок дії ліцензії:  ", "Кінець дії ліцензії:  ",
    "Номер ТЗ:  ", "Тип ТЗ:  ", "Статус ТЗ:  ", "Марка ТЗ:  ", "Модель ТЗ:  ",
    "vhclWt:  ", "loadCap:  ", "Дата випуску ТЗ:  ", "Кільк. сид. місць:  ",
    "vchlVIN:  ", "certTypeID:  ", "vhclSerie:  ", "docNum:  ", "certSeries:  ",
    "certNum:  ", "certDateFrom:  ", "certDateTo:  ",
    "taxMark:  ", "taxType:  ", "taxSeries:  "]
proverka =["1. Пошук за ЄДРПОУ", "2. Пошук за державним номером", "3. Пошук за П.І.Б.",
"4. Пошук за назвою організації", "5. Створити підиску", "6. Перевірити підписки",
"7. Про автора", "8. Про програму"]

@bot.message_handler(commands=['start'])
#Виведення привітання та ініціалізація кнопок
def welcome(message):
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    item1 = types.KeyboardButton("1. Пошук за ЄДРПОУ")
    item2 = types.KeyboardButton("2. Пошук за державним номером")
    item3 = types.KeyboardButton("3. Пошук за П.І.Б.")
    item4 = types.KeyboardButton("4. Пошук за назвою організації")
    item5 = types.KeyboardButton("5. Створити підиску")
    item6 = types.KeyboardButton("6. Перевірити підписки")
    item7 = types.KeyboardButton("7. Про автора")
    item8 = types.KeyboardButton("8. Про програму")
    
 
    markup.add(item1, item2, item3, item4, item5, item6, item7, item8)
    bot.send_message(message.chat.id,
    "Вітаю, {0.first_name}!\nЯ - <b>{1.first_name}</b> - бот, що надасть інформацію про транспортні засоби".format(message.from_user, bot.get_me()),
    parse_mode='html')
    bot.send_message(message.chat.id,
    "Для початку роботи оберіть критерій пошуку автомобіля:".format(message.from_user, bot.get_me()),
    parse_mode='html', reply_markup=markup)  
    bot.register_next_step_handler(message, GetMessageFromUser)
    logger.info("Work started on id %s" % message.chat.id)

@bot.message_handler(commands=['clearsubs'])
#Очистка списку підписок
def ClearSubs(message):
    mycursor = mydb.cursor()
    sql = "delete from subs where user_id = '%s'" % message.chat.id
    mycursor.execute(sql)
    mydb.commit()
    bot.send_message(message.chat.id, "Список підписок очищено.")
    logger.info("Clear subscriptions by id %s" % message.chat.id)

@bot.message_handler(content_types=['text'])
#Первинна обробка повідомлень користувача
def GetMessageFromUser(message):
    if time.strftime("%H:%M") >= starttime and time.strftime("%H:%M") <= endtime and datetime.datetime.now().weekday() == 5:
        if message.chat.id == 252114270 and message.text == 'Оновлення':
            mycursor = mydb.cursor()
            newtab()
            sql = "select user_id from subs group by user_id"
            mycursor.execute(sql)
            myresult = mycursor.fetchall()
            for x in myresult:
                for x1 in x:
                    ViewSUBS(x1)
        else:
            bot.send_message(message.chat.id, 'Проводимо оновлення інформації. \nСпробуйте пізніше')
    else:
        if message.chat.type == 'private':
            if message.text == '1. Пошук за ЄДРПОУ' :
                bot.send_message(message.chat.id, 'Введіть ЄДРПОУ:')
                bot.register_next_step_handler(message, Search1)
            elif message.text == '2. Пошук за державним номером' :
                bot.send_message(message.chat.id, 'Введіть державний номер:')
                bot.register_next_step_handler(message, Search2) 
            elif message.text == '3. Пошук за П.І.Б.' :
                bot.send_message(message.chat.id, 'Введіть П.І.Б.:')
                bot.register_next_step_handler(message, Search3)
            elif message.text == '4. Пошук за назвою організації' :
                bot.send_message(message.chat.id, 'Введіть назву організації:')
                bot.register_next_step_handler(message, Search3)
            elif message.text == '5. Створити підиску' :
                bot.send_message(message.chat.id, 'Для початку роботи оберіть критерій пошуку автомобіля:')
                bot.register_next_step_handler(message, ChoiceSub)
            elif message.text == '6. Перевірити підписки' :
                ViewSUBS(message.chat.id)
            elif message.text == '7. Про автора' :
                bot.send_message(message.chat.id, 'Розробив студент ХАІ, гр. 535Б Завадський Д. С.')
            elif message.text == '8. Про програму' :
                bot.send_message(message.chat.id, "Це бот з отримання інформації про транспортні засоби, як засоби провадження" +\
                    " господарської діяльності Особливості роботи з даним ботом:\n" + \
                    "1. Бот видає одразу всі записи в яких фігурує ваш запит\n" + \
                    "2. При пошуку за ПІБ можна шукати за неповною інформацією, тобто, відсутність окремо ім\'я," + \
                    " прізвища або по батькові це не проблема.")
            else:
                bot.send_message(message.chat.id, 'Для початку роботи оберіть критерій пошуку автомобіля:')


@bot.message_handler(content_types=['text'])
#Пошук за ЄДРПОУ
def Search1(message):
    for x in proverka:
        if message.text == x:
            GetMessageFromUser(message)
            return
    ms = message.text
    mycursor = mydb.cursor()
    sql = "SELECT * FROM item where OKPOCode = \'%s\'" % (ms)
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    n = 0
    for i in myresult:
        str1 = ""
        a = 0
        for x in i:
            str1 += pole[a] 
            str1 += str(x) + "\n"
            a += 1
        bot.send_message(message.chat.id, str1)
        n = n + 1
    if n == 0:
        bot.send_message(message.chat.id, "Дані відсутні")
    logger.info("Search for EDRPOU by id %s" % message.chat.id)
@bot.message_handler(content_types=['text'])
#Пошук за номером транспортного засобу
def Search2(message):
    for x in proverka:
        if message.text == x:
            GetMessageFromUser(message)
            return
    ms = message.text
    ms = test.NewLetter(ms)
    mycursor = mydb.cursor()
    sql = "SELECT * FROM item where vhclNum = \'%s\'" % (ms)
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    n = 0    
    for i in myresult:
        str1 = ""
        a = 0
        for x in i:
            str1 += pole[a] 
            str1 += str(x) + "\n"
            a += 1
        bot.send_message(message.chat.id, str1)
        n = n + 1
    if n == 0:
        bot.send_message(message.chat.id, "Дані відсутні")
    logger.info("Search by car number by id %s" % message.chat.id)
@bot.message_handler(content_types=['text'])
#Пошук за ПІБ, або за назвою організації
def Search3(message):
    for x in proverka:
        if message.text == x:
            GetMessageFromUser(message)
            return
    ms = "^" + message.text
    mycursor = mydb.cursor()
    sql = "SELECT * FROM item where carrierName REGEXP \'%s\'" % (ms)
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    n = 0
    for i in myresult:
        str1 = "" 
        a = 0
        for x in i:
            str1 += pole[a] 
            str1 += str(x) + "\n"
            a += 1
        bot.send_message(message.chat.id, str1)
        n = n + 1
    if n == 0:
        bot.send_message(message.chat.id, "Дані відсутні") 
    logger.info("Search by name or organization by id %s" % message.chat.id) 

@bot.message_handler(content_types=['text'])
#Вибір критерію пошуку для створення підписки
def ChoiceSub(message):
    if time.strftime("%H:%M") >= starttime and time.strftime("%H:%M") <= endtime and datetime.datetime.now().weekday() == 5 :
        bot.send_message(message.chat.id, 'Проводимо оновлення інформації. \nСпробуйте пізніше')
    else:
        if message.text == '1. Пошук за ЄДРПОУ' :
            bot.send_message(message.chat.id, 'Введіть ЄДРПОУ:')
            bot.register_next_step_handler(message, Sub1)
        elif message.text == '2. Пошук за державним номером' :
            bot.send_message(message.chat.id, 'Введіть державний номер:')
            bot.register_next_step_handler(message, Sub2) 
        elif message.text == '3. Пошук за П.І.Б.' :
            bot.send_message(message.chat.id, 'Введіть П.І.Б.:')
            bot.register_next_step_handler(message, Sub3)
        elif message.text == '4. Пошук за назвою організації' :
            bot.send_message(message.chat.id, 'Введіть назву організації:')
            bot.register_next_step_handler(message, Sub3)
        else:
            bot.send_message(message.chat.id, 'Для початку роботи оберіть критерій пошуку автомобіля:')
            bot.register_next_step_handler(message, ChoiceSub)

@bot.message_handler(content_types=['text'])
#Підписка на набір даних за кодом ЄДРПОУ
def Sub1(message):   
    for x in proverka:
        if message.text == x:
            GetMessageFromUser(message)
            return
    mycursor = mydb.cursor()
    ms = message.text
    sql = "insert subs(user_id, OKPOCode) value ('%s', %s)"
    val = (message.chat.id, ms)
    mycursor.execute(sql, val)
    mydb.commit()
    bot.send_message(message.chat.id, "Підписку успішно створено.")
    logger.info("created a subscription for id %s" % message.chat.id)
@bot.message_handler(content_types=['text'])
#Підписка на набір даних за номером транспортного засобу
def Sub2(message):  
    for x in proverka:
        if message.text == x:
            GetMessageFromUser(message)
            return 
    mycursor = mydb.cursor()
    ms = message.text
    ms = test.NewLetter(ms)
    sql = "insert subs(user_id, vhclNum) value ('%s', %s)"
    val = (message.chat.id, ms)
    mycursor.execute(sql, val)
    mydb.commit()
    bot.send_message(message.chat.id, "Підписку успішно створено.")
    logger.info("created a subscription for id %s" % message.chat.id)
@bot.message_handler(content_types=['text'])
#Підписка на набір даних за ПІБ, або за назвою організації
def Sub3(message):   
    for x in proverka:
        if message.text == x:
            GetMessageFromUser(message)
            return
    mycursor = mydb.cursor()
    ms = message.text
    sql = "insert subs(user_id, carrierName) value ('%s', %s)"
    val = (message.chat.id, ms)
    mycursor.execute(sql, val)
    mydb.commit()
    bot.send_message(message.chat.id, "Підписку успішно створено.")
    logger.info("created a subscription for id %s" % message.chat.id)
#Головна функція перевірки підписок, яка викликає дочірні
def ViewSUBS(c_id):
    mycursor = mydb.cursor()
    sql = "select OKPOCode, carrierName, vhclNum from subs where user_id = '%s'" % (c_id)
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    number =len(myresult)
    if number != 0:
        for x in myresult:
            if x[0] != None:
                View1(c_id, x[0])
            elif x[1] != None:
                View3(c_id, x[1])
            elif x[2] != None:
                View2(c_id, x[2])
    else:
        bot.send_message(c_id, "Нажаль нам невдалось нічого знайти.")
#Перегляд підписок заданих за ЄДРПОУ
def View1(c_id, textsearch):  
    mycursor = mydb.cursor()
    sql = "SELECT * FROM item where OKPOCode = \'%s\'" % (textsearch)
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    n = 0
    for i in myresult:
        str1 = ""
        a = 0
        for x in i:
            str1 += pole[a] 
            str1 += str(x) + "\n"
            a += 1
        bot.send_message(c_id, str1)
        n = n + 1
    if n == 0:
        bot.send_message(c_id, "Дані відсутні")
    logger.info("Search for EDRPOU by id %s" % c_id)
#Перегляд підписок заданих за номером транспортного засобу  
def View2(c_id, textsearch):  
    textsearch = test.NewLetter(textsearch)
    mycursor = mydb.cursor()
    sql = "SELECT * FROM item where vhclNum = \'%s\'" % (textsearch)
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    n = 0    
    for i in myresult:
        str1 = ""
        a = 0
        for x in i:
            str1 += pole[a] 
            str1 += str(x) + "\n"
            a += 1
        bot.send_message(c_id, str1)
        n = n + 1
    if n == 0:
        bot.send_message(c_id, "Дані відсутні")
    logger.info("Search by car number by id %s" % c_id)
#Перегляд підписок заданих за ПІБ, або назвою організації
def View3(c_id, textsearch):  
    ms = "^" + textsearch
    mycursor = mydb.cursor()
    sql = "SELECT * FROM item where carrierName REGEXP \'%s\'" % (ms)
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    n = 0
    for i in myresult:
        str1 = "" 
        a = 0
        for x in i:
            str1 += pole[a] 
            str1 += str(x) + "\n"
            a += 1
        bot.send_message(c_id, str1)
        n = n + 1
    if n == 0:
        bot.send_message(c_id, "Дані відсутні")  
    logger.info("Search by name or organization by id %s" % c_id)
#Запуск оновлення бази даних
def newtab():
    if time.strftime("%H:%M") >= starttime and time.strftime("%H:%M") <= endtime and datetime.datetime.now().weekday() == 5:
        mydb.disconnect()
        avtoupdate.fill()
        mydb.connect()
#         # RUN
bot.polling(none_stop=True)