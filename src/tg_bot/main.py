import telebot
import os

bot = telebot.TeleBot("6893066835:AAH-PP6Ig9GydrsX08U1Vx6KIsGRDiFVkEw", parse_mode="HTML")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Отправь мне пачку изображений")
 
@bot.message_handler(content_types=['document'])
def get_broadcast_picture(message):
    user_id = str(message.from_user.id)
    file_path = bot.get_file(message.document.file_id).file_path
    file = bot.download_file(file_path)
    print(file_path.split('/')[1])
    try:
        os.mkdir('./data/user_' + user_id)
    except:
        print("Попытка повторного создания папки пользователя")
    with open('./data/user_' + user_id + '/' + str(file_path.split('/')[1]), "wb") as new_file:
        new_file.write(file)
        
        
@bot.message_handler(content_types=['photo'])
def get_broadcast_picture(message):
    bot.reply_to(message, "Внимание, фото отправлено не как документ, качество снижено!")
    user_id = str(message.from_user.id)
    file_path = bot.get_file(message.photo[-1].file_id).file_path
    file = bot.download_file(file_path)
    print(file_path.split('/')[1])
    try:
        os.mkdir('./data/user_' + user_id)
    except:
        print("Попытка повторного создания папки пользователя")
    with open('./data/user_' + user_id + '/' + str(file_path.split('/')[1]), "wb") as new_file:
        new_file.write(file)
 
bot.infinity_polling()