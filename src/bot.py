from api_request import ChequeChecker
import telebot
from telebot import types


API_TOKEN = open('./tokens/bot.txt', 'r').read()
CHEQUE_TOKEN = open('./tokens/chequecheck.txt', 'r').read()

bot = telebot.TeleBot(API_TOKEN)
checker = ChequeChecker(CHEQUE_TOKEN)


@bot.message_handler(content_types=['photo'])
def photo(message):
    fileID = message.photo[-1].file_id
    file_info = bot.get_file(fileID)
    downloaded_file = bot.download_file(file_info.file_path)

    with open("image.jpg", 'wb') as new_file:
        new_file.write(downloaded_file)
    print(x := ('\n'.join(str(i) for i in checker.process_cheque('image.jpg'))))
    bot.reply_to(message, x)


bot.infinity_polling()
