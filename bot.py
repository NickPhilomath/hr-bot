import os
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, CallbackContext, ConversationHandler, filters
from pymongo import MongoClient

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


# constants
HR_MANAGER_ID = 992519627

CONTROL_CANCEL = '❌ Bekor qilish'
CONTROL_BACK = 'Orqaga qaytish ↩️'

TEXT_HR_INTRO = """
BOTning ushbu bo'limi anketani to'ldirish ✍️ va 'Saidoff' kompaniyasi ishga joylashish uchun mo'ljallangan.

Bu yerda siz anketangizni 📄 to'ldirishingiz va Kompaniyamizdagi mavjud bo'sh ish o'rinlari bilan tanishishingiz mumkin!   
"""

TEXT_FEMALE = '👩‍🦰 Ayol kishi'
TEXT_MALE = '👨‍🦱 Erkak kishi'

TEXT_POSITIONS = '💼 Sizni qiziqtirgan vakansiya nomini kiriting'

TEXT_NAME = '👤 Ismingizni kiriting'

TEXT_PHONE = "📱 Bog'lanish uchun aloqa telefon raqamingizni kiriting"

TEXT_RESUME = "📄 Resumeyingizni PDF formatida jo'nating"

TEXT_CONFIRMAION = "❔ Kiritilgan malumotlarni tekshiring va to'g'riligiga ishon hosil qiling."

TEXT_CONFIRM = "✅ Tasdiqlash"

TEXT_CONFIRMED = "✅ Murojaat qilganingiz uchun tashakkur. Biz sizning arizangizni qabul qildik. Qisqa muddatda siz bilan bog'lanamiz"

TEXT_CANCELLED = "Ariza berish jarayoni bekor qilindi. Qayta ishga tushuring uchun /start bosing."

# MongoDB setup
# client = MongoClient('mongodb://localhost:27017/')
# db = client.hr_bot
# applications = db.applications


INTRO_GENDER, POSITION, NAME, PHONE, RESUME, CONFIRMATION, CONFIRMED = range(7)



def get_reply_keys_layout(keys = None):
    # control_keys = [CONTROL_CANCEL, CONTROL_BACK]
    control_keys = [CONTROL_CANCEL]
    return [keys, control_keys] if keys else [control_keys]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = get_reply_keys_layout([TEXT_FEMALE, TEXT_MALE])
    await update.message.reply_text(TEXT_HR_INTRO)
    await update.message.reply_text(
        "Tanlang: ",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    )
    return POSITION

async def position(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['gender'] = update.message.text

    reply_keyboard = get_reply_keys_layout()
    await update.message.reply_text(
        TEXT_POSITIONS,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    )
    return NAME

async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['position'] = update.message.text
    reply_keyboard = get_reply_keys_layout()
    await update.message.reply_text(
        TEXT_NAME,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    )
    return PHONE

async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text
    reply_keyboard = get_reply_keys_layout()
    await update.message.reply_text(
        TEXT_PHONE,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    )
    return RESUME

async def resume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['phone'] = update.message.text
    reply_keyboard = get_reply_keys_layout()
    await update.message.reply_text(
        TEXT_RESUME,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    )
    return CONFIRMATION

async def confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['resume'] = update.message.message_id
    context.user_data['resume_file_name'] = update.message.document.file_name

    reply_keyboard = get_reply_keys_layout(
        [TEXT_CONFIRM]
    )
    confirm_message = (
        f"1. Ism: {context.user_data['name']}\n"
        f"2. Gender: {context.user_data['gender']}\n"
        f"3. Telefon: {context.user_data['phone']}\n"
        f"4. Vakansiya: {context.user_data['position']}\n"
        f"5. Resume fayl: {context.user_data['resume_file_name']}\n"
        # f"5. t.me/c/{update.message.chat_id}/{context.user_data['resume']}\n"
    )
    await update.message.reply_text(confirm_message)
    await update.message.reply_text(
        TEXT_CONFIRMAION, 
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    )
    return CONFIRMED

async def confirmed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    await update.message.reply_text(
        TEXT_CONFIRMED, 
        reply_markup=ReplyKeyboardRemove()
    )

    # forward to HR
    hr_message = (
        f"New job application received:\n\n"
        f"Name: {context.user_data['name']}\n"
        f"Gender: {context.user_data['gender']}\n"
        f"Phone: {context.user_data['phone']}\n"
        f"Position: {context.user_data['position']}\n"
        # f"Resume: {context.user_data['resume']}"
    )
    await context.bot.send_message(chat_id=HR_MANAGER_ID, text=hr_message)
    await context.bot.forward_message(
        chat_id=HR_MANAGER_ID, 
        from_chat_id=update.message.chat_id, 
        message_id=context.user_data['resume']
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Application process cancelled.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Hello world')


async def control_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(TEXT_CANCELLED, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def make_control_back(state):
    async def control_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(f"back from state: {state}")
        return state - 1
    return control_back

def include_control_handlers(handlers):
    return [
        MessageHandler(filters.Regex(f'^({CONTROL_CANCEL})$'), control_cancel),
        MessageHandler(filters.Regex(f'^({CONTROL_BACK}$)'), make_control_back(2)),
    ] + handlers


def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()
    # updater = Updater(token here)
    # dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            POSITION: include_control_handlers(
                [MessageHandler(filters.TEXT & ~filters.COMMAND, position)]
            ),
            NAME: include_control_handlers(
                [MessageHandler(filters.TEXT & ~filters.COMMAND, name)]
            ),
            PHONE: include_control_handlers(
                [MessageHandler(filters.TEXT & ~filters.COMMAND, phone)]
            ),
            RESUME: include_control_handlers(
                [MessageHandler(filters.TEXT & ~filters.COMMAND, resume)]
            ),
            CONFIRMATION: include_control_handlers(
                [MessageHandler(filters.Document.FileExtension("pdf") & ~filters.COMMAND, confirmation)]
            ),
            CONFIRMED: [
                MessageHandler(filters.Regex(f'^({TEXT_CONFIRM})$'), confirmed)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('hello', hello))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

