from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os
import datetime
from googletrans import Translator

# 获取环境变量中的Token
TELEGRAM_TOKEN = os.environ.get("7483670865:AAHa6_XpyLCzZKn9xa8cKpwtkWkFrw1a8DA")
ADMIN_CHAT_ID = os.environ.get("5564654941")  # 用你的 Telegram 用户ID替换

translator = Translator()

# 设置中俄双语菜单
menu_keyboard = [
    [KeyboardButton("📝 下单 / Оформить заказ")],
    [KeyboardButton("🔍 查询物流轨迹 / Отследить посылку")],
    [KeyboardButton("💬 建议 / Оставить предложение")],
    [KeyboardButton("📄 关于我们 / О нас")]
]
markup = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)

# 状态控制
user_state = {}

# 查询物流信息
def lookup_order_status(order_number):
    try:
        with open("logistics.txt", "r", encoding="utf-8") as f:
            for line in f:
                if order_number.upper() in line:
                    return line.strip()
    except:
        return "未找到物流文件。\nФайл с логистикой не найден."
    return (
        f"未找到订单号 {order_number}。\n"
        f"Информация по номеру {order_number} не найдена."
    )

# 自动翻译内容
def auto_translate(text, dest='zh-cn'):
    try:
        return translator.translate(text, dest=dest).text
    except:
        return "翻译出错 / Ошибка перевода"

# 记录日志
def log_user_message(user, text):
    with open("logs.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now()}] {user}: {text}\n")

# 启动命令
def start(update, context):
    msg = (
        "欢迎使用物流机器人 / Добро пожаловать!\n"
        "请选择下方菜单功能 / Пожалуйста, выберите действие:"
    )
    update.message.reply_text(msg, reply_markup=markup)

# 主消息处理器
def handle_message(update, context):
    text = update.message.text.strip()
    chat_id = update.effective_chat.id
    user = update.message.from_user.first_name
    log_user_message(user, text)

    state = user_state.get(chat_id)

    if text == "📄 关于我们 / О нас":
        with open("about.txt", "r", encoding="utf-8") as f:
            update.message.reply_text(f.read())

    elif text == "📝 下单 / Оформить заказ":
        user_state[chat_id] = "ordering"
        update.message.reply_text("请发送您的下单内容。\nПожалуйста, отправьте данные для оформления заказа.")

    elif text == "💬 建议 / Оставить предложение":
        user_state[chat_id] = "suggesting"
        update.message.reply_text("请发送您的建议。\nПожалуйста, отправьте ваши предложения.")

    elif text == "🔍 查询物流轨迹 / Отследить посылку":
        user_state[chat_id] = "tracking"
        update.message.reply_text("请输入您的订单号。\nПожалуйста, введите номер заказа.")

    elif state == "ordering":
        context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"📦 新下单：\n{text}")
        update.message.reply_text("您的下单内容已提交。\nВаш заказ отправлен.")
        user_state.pop(chat_id)

    elif state == "suggesting":
        context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"💬 用户建议：\n{text}")
        update.message.reply_text("感谢您的建议！\nСпасибо за ваше предложение.")
        user_state.pop(chat_id)

    elif state == "tracking":
        result = lookup_order_status(text)
        update.message.reply_text(result)
        user_state.pop(chat_id)

    else:
        translation = auto_translate(text, 'ru' if translator.detect(text).lang == 'zh-cn' else 'zh-cn')
        update.message.reply_text(f"🤖 自动翻译:\n{translation}")

# 主函数
def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    print("🚀 机器人已启动（中俄双语 + 多功能）")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()