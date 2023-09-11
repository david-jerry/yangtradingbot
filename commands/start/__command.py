from datetime import datetime, timedelta
from decimal import Decimal
import pickle

from logger import LOGGER

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, helpers
from telegram.constants import ParseMode
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, filters, CallbackContext

from utils_data import save_user_data

from .__buttons import language_markup, start_button_markup, start_button_markup2, home_markup

from constants import help_message, about_message, terms_message, language_message, welcome_message

global user_data
try:
    with open('user_data.pkl', 'rb') as file:
        user_data = pickle.load(file)
except FileNotFoundError:
    user_data = {}
    
    
async def terms_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot

    # Fetch the bot's profile photo
    bot_profile_photos = await bot.get_user_profile_photos(bot.id, limit=1)
    bot_profile_photo = bot_profile_photos.photos[0][0] if bot_profile_photos else None
    await update.message.reply_photo(bot_profile_photo, caption=terms_message, parse_mode=ParseMode.HTML, reply_markup=home_markup)
    # await update.message.reply_text(terms_message, parse_mode=ParseMode.HTML)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot

    # Fetch the bot's profile photo
    bot_profile_photos = await bot.get_user_profile_photos(bot.id, limit=1)
    bot_profile_photo = bot_profile_photos.photos[0][0] if bot_profile_photos else None
    await update.message.reply_text(help_message, parse_mode=ParseMode.HTML, reply_markup=home_markup)

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot

    # Fetch the bot's profile photo
    bot_profile_photos = await bot.get_user_profile_photos(bot.id, limit=1)
    bot_profile_photo = bot_profile_photos.photos[0][0] if bot_profile_photos else None
    await update.message.reply_text(language_message, parse_mode=ParseMode.HTML, reply_markup=language_markup)
    
async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot

    # Fetch the bot's profile photo
    bot_profile_photos = await bot.get_user_profile_photos(bot.id, limit=1)
    bot_profile_photo = bot_profile_photos.photos[0][0] if bot_profile_photos else None
    await update.message.reply_photo(bot_profile_photo, caption=about_message, parse_mode=ParseMode.HTML, reply_markup=home_markup)

async def start_command(update: Update, context: CallbackContext):
    user = update.message.from_user
    bot = context.bot
    user_id = str(user.id)
    
    context.user_data["message_stack"] = []

    # Fetch the bot's profile photo
    bot_profile_photos = await bot.get_user_profile_photos(bot.id, limit=1)
    bot_profile_photo = bot_profile_photos.photos[0][0] if bot_profile_photos else None

    first_name = user.first_name
    last_name = user.last_name

    welcome_message = create_welcome_message()
    
    if user_id not in user_data:
        initialize_user_data(user_id, first_name, last_name, language_code)

    status = user_data[user_id]['agreed_to_terms']
    
    language_code = user_data[user_id]['chosen_language'] or user.language_code

    if status != 'accept':
        start_button_mu = start_button_markup
    else:
        start_button_mu = start_button_markup2

    # Send the bot's profile photo along with the welcome message
    if bot_profile_photo:
        await update.message.reply_photo(bot_profile_photo, caption=welcome_message, parse_mode=ParseMode.HTML, reply_markup=start_button_mu)
    else:
        await update.message.reply_text(welcome_message, parse_mode=ParseMode.HTML, reply_markup=start_button_markup)
        
def initialize_user_data(user_id, first_name, last_name, language_code):
    user_data[user_id] = {
        'user_id': user_id,
        'first_name': first_name,
        'last_name': last_name,
        'email': None,
        'chosen_language': language_code,
        
        'wallet_address': '',
        'wallet_private_key': '',
        'wallet_phrase': '',
                    
        'agreed_to_terms': 'undecided'
    }
    save_user_data(user_data)


def create_welcome_message():
    return welcome_message
