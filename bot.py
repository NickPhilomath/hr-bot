import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, CallbackContext, ConversationHandler, filters
from pymongo import MongoClient

# configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


BOT_TOKEN = '7078276780:AAG3y8pwJVB7h3Rxp_W1ypZZiTDd6iNOEbo'
HR_MANAGER_ID = 992519627

CONTROL_CANCEL = '❌ Bekor qilish'
CONTROL_BACK = 'Orqaga qaytish ↩️'

TEXT_HR_INTRO = """
BOTning ushbu bo'limi anketani to'ldirish ✍️ va 'Saidoff' kompaniyasi ishga joylashish uchun mo'ljallangan.

Bu yerda siz anketangizni 📄 to'ldirishingiz va Kompaniyamizdagi mavjud bo'sh ish o'rinlari bilan tanishishingiz mumkin!   
"""

TEXT_FEMALE = '👩‍🦰 Ayol kishi'
TEXT_MALE = '👨‍🦱 Erkak kishi'

TEXT_POSITIONS = '💼 Sizni qiziqtirgan vakansiyani tanlang'

TEXT_NAME = '👤 Ismingizni kiriting'

TEXT_PHONE = "📱 Bog'lanish uchun aloqa telefon raqamingizni kiriting"

TEXT_RESUME = "📄 Resumeyingizni PDF formatida jo'nating"

# MongoDB setup
# client = MongoClient('mongodb://localhost:27017/')
# db = client.hr_bot
# applications = db.applications


INTRO_GENDER, POSITION, NAME, PHONE, RESUME, CONFIRMATION = range(6)

def get_reply_keys_layout(keys = None):
    control_keys = [CONTROL_CANCEL, CONTROL_BACK]
    return [keys, control_keys] if keys else [control_keys]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = get_reply_keys_layout([TEXT_FEMALE, TEXT_MALE])
    await update.message.reply_text(TEXT_HR_INTRO)
    await update.message.reply_text(
        "Tanlang: ",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return POSITION

async def position(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['gender'] = update.message.text

    reply_keyboard = get_reply_keys_layout()
    await update.message.reply_text(
        TEXT_POSITIONS,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return NAME

async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['position'] = update.message.text
    reply_keyboard = get_reply_keys_layout()
    await update.message.reply_text(
        TEXT_NAME,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return PHONE

async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text
    reply_keyboard = get_reply_keys_layout()
    await update.message.reply_text(
        TEXT_PHONE,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return RESUME

async def resume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['phone'] = update.message.text
    reply_keyboard = get_reply_keys_layout()
    await update.message.reply_text(
        TEXT_RESUME,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return CONFIRMATION

async def confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print(update.message)
    # file = update.message.document.get_file()
    # file.download('resume.pdf')
    # context.user_data['resume'] = 'resume.pdf'
    
    # Save data to MongoDB
    print("==> user data: ", context.user_data)
    # applications.insert_one(context.user_data)
    
    await update.message.reply_text('Thank you for applying. We have received your application.')
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Application process cancelled.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Hello world')




def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()
    # updater = Updater(token here)
    # dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            POSITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, position)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone)],
            RESUME: [MessageHandler(filters.TEXT & ~filters.COMMAND, resume)],
            CONFIRMATION: [MessageHandler(filters.Document.FileExtension("pdf") & ~filters.COMMAND, confirmation)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('hello', hello))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

    # updater.start_polling()
    # updater.idle()

if __name__ == '__main__':
    main()

