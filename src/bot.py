from api_request import ChequeChecker
from ast import literal_eval
import telebot
import tempfile
from telebot import types
import json

API_TOKEN = open('../tokens/bot.txt', 'r').read()
CHEQUE_TOKEN = open('../tokens/chequecheck.txt', 'r').read()
USERS = [user.rstrip() for user in open("../data/users.txt", 'r').readlines()]
JSON_PATH = "../data/data.json"
JSON_CLEAR = "../data/data_clean.json"
current_users = set()  # TODO get rid of this global sh*t
current_user = ""

bot = telebot.TeleBot(API_TOKEN)
checker = ChequeChecker(CHEQUE_TOKEN)


@bot.message_handler(content_types=['photo'])
def photo(message):
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    try:
        with tempfile.NamedTemporaryFile(mode="wb") as jpg:
            jpg.write(downloaded_file)

            keyboard = types.InlineKeyboardMarkup(row_width=1)
            for element in checker.process_cheque(jpg.name):
                button = types.InlineKeyboardButton(text=element['name'],
                                                    callback_data=str({'type': 'product',
                                                                       'data': element['sum'] / 100}))
                keyboard.add(button)
            bot.send_message(message.chat.id, "Hello", reply_markup=keyboard)
        global current_user
        current_user = "@{}".format(message.from_user.username)
    except TypeError as e:
        print("Error: {}".format(e))


@bot.message_handler(commands=['clear'])
def clear(message):
    if message.from_user.username == "typical_nick_name":
        with open(JSON_PATH, "w") as file, open(JSON_CLEAR, "r") as clean:
            file.write(clean.read())
        bot.reply_to(message, text="Successful clean")
    else:
        bot.reply_to(message, text="You don't have permissions to do that")


@bot.message_handler(commands=['debt']) # TODO add hints for commands
def obtain_debt(message):
    debter, owner = message.text.split(' ')[1:]
    with open(JSON_PATH, "r") as file:
        json_data = json.load(file)
        if owner in json_data.keys() and debter in json_data[owner].keys():
            bot.reply_to(message, text="{} owns {} {} rubles".format(debter, owner, json_data[owner][debter]))
        else:
            bot.reply_to(message, text="Wrong names")


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data:
        data = literal_eval(call.data)

        if data['type'] == 'user':
            current_users.add(data['user'])
        elif data['type'] == 'product':
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            for user in USERS:
                button = types.InlineKeyboardButton(text=user, callback_data=str({'type': 'user',
                                                                                  'user': user,
                                                                                  'data': data['data']}))
                keyboard.add(button)
            button = types.InlineKeyboardButton(text="Done", callback_data=str({'type': 'done_signal',
                                                                                'data': data['data']}))
            keyboard.add(button)
            bot.send_message(chat_id=call.message.chat.id, text="Выберите людей", reply_markup=keyboard)
        elif data['type'] == 'done_signal':
            debt_per_one = data['data'] / len(USERS) if len(current_users) == 0 else data['data'] / len(current_users)
            with open(JSON_PATH, "r") as file:
                json_data = json.load(file)
            for user in current_users:
                print("{} owes {} {}".format(user, current_user, debt_per_one))
                json_data[current_user][user] += debt_per_one
                json_data[user][current_user] -= debt_per_one
            with open(JSON_PATH, "w") as file:
                json.dump(json_data, file)

            bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
            current_users.clear()  # TODO send item that been done


bot.infinity_polling()
