from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import os, datetime
from googletrans import Translator

TOKEN = os.getenv("7483670865:AAHa6_XpyLCzZKn9xa8cKpwtkWkFrw1a8DA")
ADMIN_CHAT_ID = int(os.getenv("5564654941", "0"))

translator = Translator()
user_state = {}

keyboard = [
    [KeyboardButton("📦 下单 / Заказать"), KeyboardButton("🚚 查询物流 / Отследить трек")],
    [KeyboardButton("💬 建议 / Предложение"), KeyboardButton("ℹ 关于我们 / О нас")]
]
markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def log_msg(user, text):
    with open("logs.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now()}] {user}: {text}\n")

def lookup_order(order):
    try:
        with open("logistics.txt", "r", encoding="utf-8") as f:
            for line in f:
                if order in line:
                    return line.strip()
    except:
        return "未找到物流文件。\nФайл с логистикой не найден."
    return f"未找到订单号 {order}。\nИнформация по номеру {order} не найдена."

def start(update: Update, context: CallbackContext):
    update.message.reply_text("欢迎使用物流机器人 / Добро пожаловать!\n请选择功能 / Пожалуйста, выберите:", reply_markup=markup)

def handle(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    user = update.message.from_user.username or update.message.from_user.first_name
    log_msg(user, text)
    state = user_state.get(update.effective_chat.id)

    if text in ["ℹ 关于我们 / О нас"]:
        with open("about.txt", "r", encoding="utf-8") as f:
            update.message.reply_text(f.read())
    elif text in ["📦 下单 / Заказать"]:
        user_state[update.effective_chat.id] = "ordering"
        update.message.reply_text("请发送下单内容。\nПожалуйста, отправьте данные для заказа.")
    elif text in ["💬 建议 / Предложение"]:
        user_state[update.effective_chat.id] = "suggesting"
        update.message.reply_text("请发送您的建议。\nПожалуйста, отправьте ваше предложение.")
    elif text in ["🚚 查询物流 / Отследить трек"]:
        user_state[update.effective_chat.id] = "tracking"
        update.message.reply_text("请输入订单号。\nВведите номер заказа.")
    elif state == "ordering":
        context.bot.send_message(chat_id=ADMIN_CHAT_ID, text="💼 新订单:\n" + text)
        update.message.reply_text("您的订单已提交。\nВаш заказ принят.")
        user_state.pop(update.effective_chat.id)
    elif state == "suggesting":
        context.bot.send_message(chat_id=ADMIN_CHAT_ID, text="💬 建议:\n" + text)
        update.message.reply_text("感谢建议！\nСпасибо за предложение.")
        user_state.pop(update.effective_chat.id)
    elif state == "tracking":
        result = lookup_order(text)
        update.message.reply_text(result)
        user_state.pop(update.effective_chat.id)
    else:
        lang = translator.detect(text).lang
        trans = translator.translate(text, dest='ru' if lang == 'zh-cn' else 'zh-cn')
        update.message.reply_text(f"自动翻译:\n{trans.text}")

def main():
    updater = Updater(TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle))
    print("Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
