import telebot
from telebot import types
from dotenv.main import load_dotenv
import os
import requests
import time
import base64
import io
from PIL import Image
import json



###-------------INITIALIZATION-STEPS--------------
### ENVIRONMENT VARIABLES INITIALIZATION
load_dotenv()
api_token = os.getenv("API_TOKEN_TELEGRAM")
url = os.getenv("BACKEND_ADRESS")
volume_path = os.getenv("VOLUME_ADRESS")

### TELEGRAM BOT INITIALIZATION
bot = telebot.TeleBot(api_token, parse_mode="HTML")

### STRING OF PATH FROM USER_ID
def path(user_id):
    return str(volume_path + 'user_' + user_id + '/')

### UPDATING PERSON'S PHOTOS
def update_photo(user_id, file, filename, updating_person_idx, max_files_per_person):
    if updating_person_idx == 0:
        bot.send_message(user_id, "Для изменения \ добавления фотографий пожалуйста воспользуйтесь меню команд")
    else:
        file_cnt = get_files_from_folder(f'{path(user_id)}person_{updating_person_idx}/')
        if file_cnt >= int(max_files_per_person):
            bot.send_message(user_id, f"Превышен лимит фотографий для личности №{updating_person_idx}. Фото не сохранено.")
            config_changes({"CURR_UPDATING_PERSON":0}, user_id)
            return False
        else:
            with open(f'{path(user_id)}person_{updating_person_idx}/{filename}', "wb") as new_file:
                new_file.write(file)
            return True

### GET FILECOUNT FROM FOLDER
def get_files_from_folder(path):
    cnt = 0
    for file in os.listdir(path):
        if os.path.isfile(f'{path}{file}'):
            cnt += 1
    return cnt
    
### GET SUBFOLDER COUNT FROM FOLDER
def get_folders_from_folder(path):
    cnt = 0
    for folder in os.listdir(path):
        if os.path.isdir(f'{path}{folder}'):
            cnt += 1
    return cnt
###----------------------------------------------


###-------------USER-CONFIG-STEPS----------------
### DEFAULT USER CONFIG
default_cfg = {
        "NUM_LOADED_PERSONS":0,
        "PROMPT":"A man img in a black suit",
        "CURR_UPDATING_PERSON":0,
        "ALLOWED_MAX_PERSONS":2,
        "ALLOWED_IMG_PER_PERSON":4,
        "PERSON_TO_GENERATE":0,
        "GENERATE_MAX_IMG":1,
        "GENERATE_STYLE_STRENGTH":20,
        "GENERATE_MAX_STEPS":50
    }

### CONFIG CREATION
def create_config(user_id):
    CFG_PATH = path(user_id)
    with open(CFG_PATH + 'config.cfg', 'w') as settings_file:
        json.dump(default_cfg, settings_file)

### GETTER FOR CONFIG VALUES
def from_config(user_id, key):
    CFG_PATH = path(user_id)
    with open(CFG_PATH + 'config.cfg', 'r') as settings_file:
        settings = json.load(settings_file)
    return settings[key]

### HANDLING SETTINGS CHANGES
def config_changes(changed_settings, user_id):
    CFG_PATH = path(user_id)
    # loading json settings
    with open(CFG_PATH + 'config.cfg', 'r') as settings_file:
        settings = json.load(settings_file)
    # updating settings
    for key, value in changed_settings.items():
        settings[key] = value
    # saving settings
    with open(CFG_PATH + 'config.cfg', 'w') as settings_file:
        json.dump(settings, settings_file)
        
### MARKUP INLINE BUTTONS CREATION HELPER
def create_inline_markup(arr, row_width=1):
    markup = types.InlineKeyboardMarkup(row_width=row_width)
    for button in arr:
        markup.add(types.InlineKeyboardButton(button['text'], callback_data=button['callback_data']))
    return markup
###----------------------------------------------


###------------------BOT-LOGIC-------------------
### /start COMMAND
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_id = str(message.from_user.id)
    try:
        os.mkdir(volume_path+'user_' + user_id)
    except:
        print("Попытка повторного создания папки пользователя")
        bot.reply_to(message, "Для навигации по боту используйте меню.")
    else:
        create_config(user_id)
        print("Создание папки и конфигурационного файла для user: "+user_id)
        buttons = [{'text': 'Создать личность', 'callback_data':'make_person'}]
        markup = create_inline_markup(buttons)
        bot.reply_to(message, "Здравствуй\! \n Для начала тебе понадобится создать *\'личность\'*\. \n Личность \- один человек\, лицо которого ты хочешь видеть в сгенерированных картинках\. Для начала доступна одна личность\. \n Для создания личности воспользуйся *кнопкой ниже*", reply_markup=markup, parse_mode='MarkdownV2')
        
        
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.message:
        user_id = str(call.message.chat.id)
        if call.data == 'make_person':
            new_person_idx = from_config(user_id, "NUM_LOADED_PERSONS") + 1
            max_persons = from_config(user_id, "ALLOWED_MAX_PERSONS")
            if new_person_idx > max_persons:
                bot.send_message(user_id, "Превышен лимит максимальных личностей. **Операция не выполнена**", parse_mode='MarkdownV2')
                # bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="ТЕКСТ", parse_mode='Markdown')
            else:
                os.mkdir(f'{path(user_id)}person_{new_person_idx}')
                file_cnt = get_folders_from_folder(f'{path(user_id)}/')
                config_changes({"NUM_LOADED_PERSONS":file_cnt}, user_id)
                config_changes({"CURR_UPDATING_PERSON":new_person_idx}, user_id)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Отправьте до *4* фото с лицом человека в хорошем качестве\. \n Для отличного результата лицо должно быть *четким* и занимать большую часть фотографии", parse_mode='MarkdownV2')
                buttons=[{'text':'Готово', 'callback_data':'person_ready'}]
                markup = create_inline_markup(buttons)
                bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=markup)
        if call.data == 'person_ready':
            buttons = [{'text':'Готово', 'callback_data':'prompt_ready'}]
            markup = create_inline_markup(buttons)
            bot.send_message(user_id, 'Введите промпт с помощью команды ```copy \/prompt \(текст\) ``` \n \n Пока только на английском\. \n Для работы *НЕОБХОДИМО*\, чтобы в промпте присутствовало кодовое слово \n \(*man img \/ woman img*\, в зависимости от пола\) \n Вставляйте кодовое слово в ту часть промпта\, где вы упоминаете личность\, которую собираетесь сгенеирировать\. \n \n *ВАЖНО\!* \n _Используйте кодовое слово только один раз_\! \n Пример промпта\: \n ``` A photo of a man img sitting in a car smoking crack a crackhead nigga\. ``` \n В дальнейшем для смены промпта используйте *_ту же команду_*', reply_markup=markup, parse_mode='MarkdownV2')
        if call.data == 'prompt_ready':
            bot.send_message(user_id, "*Отлично\!* \n \n Вы готовы к генерации изображений\. \n Для генерации изображений достаточно воспользоваться командой ```copy \/generate \(число\) ``` где число \- номер личности\. \n \n В данном случае используйте команду \n *\/generate 1* \n В дальнейшем используйте связки \n *\/prompt* для смены промпта \n *\/generate* для генерации изображений", parse_mode='MarkdownV2')
                

# @bot.inline_handler(lambda query: len(query.query) > 0)
# def query_text(query):
#     kb = types.InlineKeyboardMarkup()
#     # Добавляем колбэк-кнопку с содержимым "test"
#     kb.add(types.InlineKeyboardButton(text="Нажми меня", callback_data="test"))
#     results = []
#     single_msg = types.InlineQueryResultArticle(
#         id="1", title="Press me",
#         input_message_content=types.InputTextMessageContent(message_text="Я – сообщение из инлайн-режима"),
#         reply_markup=kb
#     )
#     results.append(single_msg)
#     bot.answer_inline_query(query.id, results)


### PROMPT CHANGING /prompt command
@bot.message_handler(commands=['prompt'])
def send_welcome(message):
    user_id = str(message.from_user.id)
    config_changes({"CURR_UPDATING_PERSON":0}, user_id)
    bot.reply_to(message, "Промпт сохранен")
    prompt = ' '.join(message.text.split()[1:])
    config_changes({'PROMPT':prompt}, user_id)
    print(f'Prompt change for user {user_id} as: {prompt}')
    
### CHOOSING PERSON TO GENERATE /choose_person
@bot.message_handler(commands=['choose_person'])
def set_person_image(message):
    config_changes({"CURR_UPDATING_PERSON":0}, user_id)
    user_id = str(message.from_user.id)
    choosed_person_idx = message.text.split()[-1]
    max_persons = from_config(user_id, "ALLOWED_MAX_PERSONS")
    if choosed_person_idx > max_persons:
        bot.send_message(user_id, "Выше лимита максимальных личностей. Операция не выполнена")
    else:
        if os.path.exists(f'{path(user_id)}person_{choosed_person_idx}'):
            config_changes({"PERSON_TO_GENERATE":choosed_person_idx}, user_id)
            bot.send_message(user_id, "Для генерации выбрана личность под номером {choosed_person_idx}")


### COMMAND FOR SETTING UP PERSON IMAGES /new_person
@bot.message_handler(commands=['new_person'])
def set_person_image(message):
    user_id = str(message.from_user.id)
    new_person_idx = from_config(user_id, "NUM_LOADED_PERSONS") + 1
    max_persons = from_config(user_id, "ALLOWED_MAX_PERSONS")
    if new_person_idx > max_persons:
        bot.send_message(user_id, "Превышен лимит максимальных личностей. Операция не выполнена")
    else:
        os.mkdir(f'{path(user_id)}person_{new_person_idx}')
        file_cnt = get_folders_from_folder(f'{path(user_id)}/')
        config_changes({"NUM_LOADED_PERSONS":file_cnt}, user_id)
        config_changes({"CURR_UPDATING_PERSON":new_person_idx}, user_id)
        bot.send_message(user_id, "Отправьте до 4 фото с лицом человека в хорошем качестве. Для отличного результата лицо должно быть четким и занимать большую часть фотографии.")
        
### COMMAND FOR UPDATING PERSON IMAGES /update_person
@bot.message_handler(commands=['update_person'])
def set_person_image(message):
    user_id = str(message.from_user.id)
    if len(message.text.split()) != 2:
        bot.send_message(user_id, "Неправильный формат команды. Пожалуйста, введите /update_person (номер личности)")
        return
    person_idx = int(message.text.split()[-1])
    max_persons = from_config(user_id, "ALLOWED_MAX_PERSONS")
    if person_idx > max_persons:
        bot.send_message(user_id, "Превышен лимит максимальных личностей. Операция не выполнена")
    else:
        if os.path.exists(f'{path(user_id)}person_{person_idx}'):
            for file in os.listdir(f'{path(user_id)}person_{person_idx}'):
                os.remove(f'{path(user_id)}person_{person_idx}/{file}')
            config_changes({"CURR_UPDATING_PERSON":person_idx}, user_id)
            bot.send_message(user_id, "Отправьте до 4 фото с лицом человека в хорошем качестве. Для отличного результата лицо должно быть четким и занимать большую часть фотографии.")
        else:
            bot.send_message(user_id, "Личность не найдена.")

### RECEIVING DOCUMENT FOR PERSON CHANGES
@bot.message_handler(content_types=['document'])
def get_broadcast_picture(message):
    user_id = str(message.from_user.id)
    updating_person_idx = from_config(user_id, "CURR_UPDATING_PERSON")
    max_files_per_person = from_config(user_id, "ALLOWED_IMG_PER_PERSON")
    file_path = bot.get_file(message.document.file_id).file_path
    file = bot.download_file(file_path)
    result_bool = update_photo(user_id, file, str(file_path.split('/')[1]), updating_person_idx, max_files_per_person)
    # if result_bool:
        # bot.send_message(user_id, "Фото успешно сохранено")

### RECEIVING PHOTO FOR PERSON CHANGES
@bot.message_handler(content_types=['photo'])
def get_broadcast_picture(message):
    # bot.reply_to(message, "Внимание, фото отправлено не как документ, качество снижено!")
    user_id = str(message.from_user.id)
    updating_person_idx = from_config(user_id, "CURR_UPDATING_PERSON")
    max_files_per_person = from_config(user_id, "ALLOWED_IMG_PER_PERSON")
    file_path = bot.get_file(message.photo[-1].file_id).file_path
    file = bot.download_file(file_path)
    result_bool = update_photo(user_id, file, str(file_path.split('/')[1]), updating_person_idx, max_files_per_person)
    if not result_bool:
        bot.send_message(user_id, "Для изменения \ добавления фотографий пожалуйста воспользуйтесь меню команд")
    # else:
        # bot.send_message(user_id, "Фото успешно сохранено")

### GENERATING AND RECEIVING PROMPT WITH SAVED SETTINGS /generate
@bot.message_handler(commands=['generate'])
def job_processing(message):
    user_id = str(message.from_user.id)
    if len(message.text.split()) != 2:
        bot.send_message(user_id, "Неправильный формат команды. Пожалуйста, введите /generate (номер личности)")
        return
    person_idx = int(message.text.split()[-1])
    config_changes({"CURR_UPDATING_PERSON":0}, user_id)
    # GETTING CONFIG SETTINGS
    generating_person_idx = person_idx
    prompt = from_config(user_id, "PROMPT")
    num_images_user = from_config(user_id, "GENERATE_MAX_IMG")
    num_steps_user = from_config(user_id, "GENERATE_MAX_STEPS")
    style_strength_user = from_config(user_id, "GENERATE_STYLE_STRENGTH")
    
    data={
                "foldername": f'user_{user_id}',
                "idx_person": generating_person_idx,
                "prompt": prompt,
                "num_images_user": num_images_user,
                "num_steps_user": num_steps_user,
                "style_strength_user": style_strength_user
            }
    
    # POST TO BACKEND SERVER FOR ADDING A JOB TO RQ
    response = requests.post(url+"add_job/picture",json=data)
    bot.send_message(user_id, str(response.json()))
    job_id = response.json()['job_id']
    status_response = requests.get(url+"job_status/"+job_id)
    job_status = status_response.json()['job_status']
    max_fetches = 0
    while job_status != "finished" and max_fetches < 40 and job_status != 'failed':
        status_response = requests.get(url+"job_status/"+job_id)
        job_status = status_response.json()['job_status']
        max_fetches += 1
        print("Status of job",job_id,":", job_status)
        time.sleep(5)
    if job_status == "finished":
        bot.send_message(message.from_user.id, "Обработка фото успешно завершена\! \n \n *Ваше фото\:*", parse_mode='MarkdownV2')
        for filename in os.listdir(volume_path+'user_' + user_id):
            if os.path.isfile(f'{path(user_id)}{filename}') and filename[-3:] != 'cfg':
                bot.send_photo(message.from_user.id, open(volume_path + 'user_' + user_id + "/" +filename, 'rb'))
                os.remove(volume_path + 'user_' + user_id + "/" +filename)
    if job_status == 'failed':
        bot.send_message(user_id, "При обработке возникал ошибка. Мозина извинити?")
        
### /done BOT COMMAND
@bot.message_handler(commands=['done'])
def job_process(message):
    user_id = str(message.from_user.id)
    config_changes({"CURR_UPDATING_PERSON":0}, user_id)
    folder_cnt = get_folders_from_folder(f'{path(user_id)}/')
    config_changes({"NUM_LOADED_PERSONS":folder_cnt}, user_id)
    


bot.polling(none_stop=True)