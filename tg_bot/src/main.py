import telebot
from dotenv.main import load_dotenv
import os
import requests
import time
import base64

load_dotenv()
api_token = os.environ["API_TOKEN_TELEGRAM"]
url = os.environ["BACKEND_ADRESS"]
volume_path = os.environ["VOLUME_ADRESS"]

bot = telebot.TeleBot(api_token, parse_mode="HTML")


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Отправь мне пачку изображений")


@bot.message_handler(content_types=['document'])
def get_broadcast_picture(message):
    user_id = str(message.from_user.id)
    file_path = bot.get_file(message.document.file_id).file_path
    file = bot.download_file(file_path)
    try:
        os.mkdir(volume_path+'user_' + user_id)
    except:
        print("Попытка повторного создания папки пользователя")
    else:
        print("Создание папки для user: "+user_id)
        
    with open(volume_path+'user_' + user_id + '/' + str(file_path.split('/')[1]), "wb") as new_file:
        new_file.write(file)


@bot.message_handler(content_types=['photo'])
def get_broadcast_picture(message):
    bot.reply_to(message, "Внимание, фото отправлено не как документ, качество снижено!")
    user_id = str(message.from_user.id)
    file_path = bot.get_file(message.photo[-1].file_id).file_path
    file = bot.download_file(file_path)
    print(file_path.split('/')[1])
    try:
        os.mkdir(volume_path+'user_' + user_id)
    except:
        print("Попытка повторного создания папки пользователя")
    with open(volume_path+'user_' + user_id + '/' + str(file_path.split('/')[1]), "wb") as new_file:
        new_file.write(file)


@bot.message_handler(commands=['done'])
def job_process(message):  
    user_id = str(message.from_user.id)  
    initial_job_responce = requests.get(url+"add_job/picture/user_"+user_id)
    print(initial_job_responce.json())
    
    job_id = initial_job_responce.json()['job_id']
    
    status_response = requests.get(url+"job_status/"+job_id)
    job_status = status_response.json()['job_status']
    print("Status of job",job_id,":", job_status)
    max_fetches = 0
    while job_status != "finished" and max_fetches < 30:
        status_response = requests.get(url+"job_status/"+job_id)
        job_status = status_response.json()['job_status']
        max_fetches += 1
        print("Status of job",job_id,":", job_status)
        time.sleep(5)
    if job_status == "finished":
        result_responce = requests.get(url+"job_result/"+job_id)
        result = result_responce.json()['job_result']
        # print('Job', job_id, "result:", result)
        bot.send_message(message.from_user.id, "Обработка фото успешно завершена")
        images = [telebot.types.InputMediaPhoto(base64.b64decode(img)) for img in result]
        bot.send_media_group(message.from_user.id, images)


bot.polling(none_stop=True)