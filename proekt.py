import telebot, requests, json
from telebot import types;
from datetime import date
from datetime import datetime

bot = telebot.TeleBot('5026664493:AAHWA-WmJxShpXO5z5RSbgtPhjXtQi7QtkQ');
API_KEY = 'c40cda821f05dfc14f7cc9c90c52c50d'

mainKB= telebot.types.ReplyKeyboardMarkup(True,True)
mainKB.row('Погода сейчас', 'Прогноз на неделю')
mainKB.row('Поменять город', 'Сформировать данные')


MAINCITY = {}

@bot.message_handler(commands=['start'])
def start_handler(message):
    mesg = bot.send_message(message.chat.id, '*Привет '+message.from_user.first_name + '*, для начала введи название своего города!',  parse_mode= "Markdown")
    bot.register_next_step_handler(mesg,setCity)#отлавливаем следующее сообщение от пользователя в фукнции setCity


@bot.message_handler(content_types=['text'])
def get_text_message(message):
    global MAINCITY
    client_id = message.from_user.id
    if('name' in MAINCITY): #проверка на наличии данных о городе для поиска инфы
        if(message.text=='Сформировать данные'):
            with open("data.json", "r") as read_file: #открываем и читаем данные из файла
                bot.send_document(message.chat.id, read_file) # отправляем пользователю
            with open('data.json', 'w') as outfile:
                json.dump([], outfile) #чистим файл с данными
        elif(message.text=='Погода сейчас'):
            r = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={MAINCITY['name']}&units=metric&lang=ru&appid={API_KEY}") #Отправляем апи запрос
            r = r.json() #полученный ответ приводим в формат json
            addData(r) #записываем в файл с данными
            info = f"*{MAINCITY['name']}, {date.today().strftime('%B, %d')}*\n\n" #парсим нужные данные из ответа
            info += f"Температура: *{r['main']['temp']}°C, {r['weather'][0]['description']}*\n"
            info += f"Ощущается как: *{r['main']['feels_like']}°C*\n"
            info += f"Скорость ветра: *{r['wind']['speed']} м\с*\n"
            bot.send_message(message.chat.id, text=info, parse_mode= "Markdown", reply_markup = mainKB)
        if(message.text=='Поменять город'):
            mesg = bot.send_message(message.chat.id, 'Введи название города:',  parse_mode= "Markdown")
            bot.register_next_step_handler(mesg,setCity) #отлавливаем следующее сообщение от пользователя в фукнции setCity
        if(message.text=='Прогноз на неделю'):
            r = requests.get(f"https://api.openweathermap.org/data/2.5/onecall?lat={MAINCITY['lat']}&lon={MAINCITY['lon']}&exclude=current,minutely,hourly&units=metric&lang=ru&appid={API_KEY}")
            r = r.json()
            addData(r)
            info = f"*{MAINCITY['name']}*\n\n"
            for day in r['daily']: #Проходимся по каждому дню
                info += f"*{datetime.utcfromtimestamp(day['dt']).strftime('%B, %d')}*\n"
                info += f"Температура: *{day['temp']['day']}°C, {day['weather'][0]['description']}*\n"
                info += f"Ощущается как: *{day['feels_like']['day']}°C*\n"
                info += f"Скорость ветра: *{day['wind_speed']} м\с*\n\n"
            bot.send_message(message.chat.id, text=info, parse_mode= "Markdown", reply_markup = mainKB)
    else: #Если пользователь не ввел город
        mesg = bot.send_message(message.chat.id, '*Привет '+message.from_user.first_name + '*, для начала введи название своего города!',  parse_mode= "Markdown")
        bot.register_next_step_handler(mesg,setCity)#отлавливаем следующее сообщение от пользователя в фукнции setCity

def setCity(message):
    if(message.text != ''):
        r = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={API_KEY}") #проверяем есть ли такой город
        if(r.status_code == 200): #елси ответ вернулся с кодом 200, то город введен верно
            global MAINCITY #объявляем доступ к глобальной переменой
            r = r.json()
            MAINCITY = {'name':message.text.capitalize(), 'lat':r['coord']['lat'],'lon':r['coord']['lon']} #Записываем информацию о городе
            bot.send_message(message.chat.id, text=f'Ваш город *{message.text.capitalize()}* добавлен!', parse_mode= "Markdown", reply_markup = mainKB)
        else:
            mesg = bot.send_message(message.chat.id, text=f'Такого города *{message.text.capitalize()}* не существует! Попробуйте ввести заного:', parse_mode= "Markdown") #просим заного ввести город
            bot.register_next_step_handler(mesg,setCity) #зацикливаем данный шаг, пока не будет введен правильный город

def addData(r):
    with open("data.json", "r") as read_file: # открываем файл
        data = json.load(read_file)# записываем данные из файла в переменную
        data.append(r) #добавляем в список переданный ответ r
        with open('data.json', 'w', encoding="utf-8") as outfile:
            json.dump(data, outfile) #сохраняем данные

bot.polling(none_stop=True, interval=1);
