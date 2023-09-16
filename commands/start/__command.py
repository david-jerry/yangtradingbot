from datetime import datetime, timedelta
from decimal import Decimal
import os
import pickle

import django

from logger import LOGGER

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, helpers
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    filters,
    CallbackContext,
    ConversationHandler,
)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yangbot.settings')
django.setup()


from utils_data import load_user_data, save_user_data

from .__buttons import (
    language_markup,
    start_button_markup,
    start_button_markup2,
    home_markup,
)

from constants import (
    help_message,
    about_message,
    terms_message,
    language_message,
    welcome_message,
)


async def terms_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot

    # Fetch the bot's profile photo
    bot_profile_photos = await bot.get_user_profile_photos(bot.id, limit=1)
    bot_profile_photo = bot_profile_photos.photos[0][0] if bot_profile_photos else None
    await update.message.reply_photo(
        bot_profile_photo,
        caption=terms_message,
        parse_mode=ParseMode.HTML,
        reply_markup=home_markup,
    )
    # await update.message.reply_text(terms_message, parse_mode=ParseMode.HTML)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot

    # Fetch the bot's profile photo
    bot_profile_photos = await bot.get_user_profile_photos(bot.id, limit=1)
    bot_profile_photo = bot_profile_photos.photos[0][0] if bot_profile_photos else None
    await update.message.reply_text(
        help_message, parse_mode=ParseMode.HTML, reply_markup=home_markup
    )


async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot

    # Fetch the bot's profile photo
    bot_profile_photos = await bot.get_user_profile_photos(bot.id, limit=1)
    bot_profile_photo = bot_profile_photos.photos[0][0] if bot_profile_photos else None
    await update.message.reply_text(
        language_message, parse_mode=ParseMode.HTML, reply_markup=language_markup
    )


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot

    # Fetch the bot's profile photo
    bot_profile_photos = await bot.get_user_profile_photos(bot.id, limit=1)
    bot_profile_photo = bot_profile_photos.photos[0][0] if bot_profile_photos else None
    await update.message.reply_photo(
        bot_profile_photo,
        caption=about_message,
        parse_mode=ParseMode.HTML,
        reply_markup=home_markup,
    )


async def start_command(update: Update, context: CallbackContext):
    context.user_data.clear()
    ConversationHandler.END
    user = update.message.from_user
    bot = context.bot
    user_id = str(user.id)

    context.user_data["message_stack"] = []
    user_initial_data = await load_user_data(user_id)

    if user_initial_data != None:
        first_name = user_initial_data.first_name
        last_name = user_initial_data.last_name
    else:
        first_name = user.first_name
        last_name = user.last_name
        

    # Fetch the bot's profile photo
    bot_profile_photos = await bot.get_user_profile_photos(bot.id, limit=1)
    bot_profile_photo = bot_profile_photos.photos[0][0] if bot_profile_photos else None

    

    # welcome_message = create_welcome_message()

    user_data = await load_user_data(user_id)
    language_code = user_data.chosen_language if user_data is not None else user.language_code
    
    if user_data == None:
        data = {
            "user_id": user_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": f"{user_id}@mail.com",
            "chosen_language": language_code,
            "wallet_address": None,
            "wallet_private_key": None,
            "wallet_phrase": None,
            "agreed_to_terms": False,
        }
        await save_user_data(data)
        
    user_awaited_data = await load_user_data(user_id)

    status = user_awaited_data.agreed_to_terms


    if not status:
        start_button_mu = start_button_markup
    else:
        start_button_mu = start_button_markup2

    # Send the bot's profile photo along with the welcome message
    if bot_profile_photo:
        await update.message.reply_photo(
            bot_profile_photo,
            caption=welcome_message,
            parse_mode=ParseMode.HTML,
            reply_markup=start_button_mu,
        )
    else:
        await update.message.reply_text(
            welcome_message, parse_mode=ParseMode.HTML, reply_markup=start_button_markup
        )
    
