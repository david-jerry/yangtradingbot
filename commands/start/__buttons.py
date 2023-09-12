import os
import pickle
import re


import django
from logger import LOGGER

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CallbackContext, ConversationHandler
from telegram.constants import ParseMode

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yangbot.settings')
django.setup()

from constants import (
    help_message,
    about_message,
    terms_message,
    language_message,
    welcome_message,
    wallets_message,
    wallets_asset_message,
)
from utils import attach_wallet_function, generate_wallet, get_wallet_balance
from utils_data import load_user_data, save_user_data, update_user_data

# ------------------------------------------------------------------------------
# HOME BUTTONS
# ------------------------------------------------------------------------------
home = InlineKeyboardButton("🏡 Home", callback_data="home")

home_keyboard = [[home]]
home_markup = InlineKeyboardMarkup(home_keyboard)

# ------------------------------------------------------------------------------
# BACK OR FORWARD BUTTONS
# ------------------------------------------------------------------------------
back = InlineKeyboardButton("⏪ ", callback_data="direct_left")
forward = InlineKeyboardButton("⏩ ", callback_data="direct_right")

direction_keyboard = [[back, forward]]
direction_markup = InlineKeyboardMarkup(direction_keyboard)


# ------------------------------------------------------------------------------
# WALLET NETWORK CHAIN BUTTONS
# ------------------------------------------------------------------------------
eth = InlineKeyboardButton("🎫 ETH", callback_data="chain_eth")
bsc = InlineKeyboardButton("🎫 BSC", callback_data="chain_bsc")
arb = InlineKeyboardButton("🎫 ARB", callback_data="chain_arb")
base = InlineKeyboardButton("🎫 BASE", callback_data="chain_base")

chain_keyboard = [
    [home],
    [eth, bsc, arb, base],
]
chain_markup = InlineKeyboardMarkup(chain_keyboard)

asset_eth = InlineKeyboardButton("🎫 ETH", callback_data="asset_chain_eth")
asset_bsc = InlineKeyboardButton("🎫 BSC", callback_data="asset_chain_bsc")
asset_arb = InlineKeyboardButton("🎫 ARB", callback_data="asset_chain_arb")
asset_base = InlineKeyboardButton("🎫 BASE", callback_data="asset_chain_base")

asset_chain_keyboard = [
    [home],
    [asset_eth, asset_bsc, asset_arb, asset_base],
]

asset_chain_markup = InlineKeyboardMarkup(asset_chain_keyboard)

attach_wallet = InlineKeyboardButton("Attach Wallet", callback_data="connect_attach")
detach_wallet = InlineKeyboardButton("Detach Wallet", callback_data="connect_detach")
detach_confirm = InlineKeyboardButton("Confirm Detach", callback_data="connect_confirm")
create_wallet = InlineKeyboardButton("Create Wallet", callback_data="connect_create")
connect_keyboard = [[home], [attach_wallet, back], [create_wallet]]
detach_keyboard = [[home], [detach_wallet, back], [create_wallet]]
detach_confirm_keyboard = [[home], [detach_confirm, back], [create_wallet]]

connect_markup = InlineKeyboardMarkup(connect_keyboard)
detach_markup = InlineKeyboardMarkup(detach_keyboard)
detach_confirm_markup = InlineKeyboardMarkup(detach_confirm_keyboard)

# ------------------------------------------------------------------------------
# LANGUAGE BUTTONS
# ------------------------------------------------------------------------------

english = InlineKeyboardButton("🇺🇸 English (en)", callback_data="language_en")
french = InlineKeyboardButton("🇫🇷 French (fr)", callback_data="language_fr")
dutch = InlineKeyboardButton("🇩🇪 German (de)", callback_data="language_de")
spanish = InlineKeyboardButton("🇪🇸 Spanish (es)", callback_data="language_es")
italian = InlineKeyboardButton("🇮🇹 Italian (it)", callback_data="language_it")

language_keyboard = [[english, french, dutch, spanish, italian], [home]]
language_markup = InlineKeyboardMarkup(language_keyboard)


# ------------------------------------------------------------------------------
# TERMS & CONDITION BUTTONS
# ------------------------------------------------------------------------------

accept_terms_button = InlineKeyboardButton(
    "Accept Conditions", callback_data="terms_accept"
)
decline_terms_button = InlineKeyboardButton(
    "Decline Conditions", callback_data="terms_decline"
)
terms_keyboard = [[accept_terms_button, decline_terms_button]]
terms_markup = InlineKeyboardMarkup(terms_keyboard)

# ------------------------------------------------------------------------------
# START BUTTONS
# ------------------------------------------------------------------------------
about = InlineKeyboardButton("About Us", callback_data="start_about")
language = InlineKeyboardButton("Language Choice", callback_data="start_language")
help = InlineKeyboardButton("Help Commands", callback_data="start_help")
wallets = InlineKeyboardButton("Wallets", callback_data="start_wallets")
wallets_assets = InlineKeyboardButton(
    "Wallet Assets", callback_data="start_wallet_assets"
)
configuration = InlineKeyboardButton("Preference", callback_data="start_configuration")
terms = InlineKeyboardButton("Accept Terms", callback_data="start_terms")
snipe = InlineKeyboardButton("Sniper", callback_data="start_sniper")
copy_trade = InlineKeyboardButton("Copy Trade", callback_data="start_trade")
token_transfer = InlineKeyboardButton(
    "Token Transfer", callback_data="start_token_transfer"
)
ads_1 = InlineKeyboardButton("Ads Placement Space", callback_data="ads_placement")

start_keyboard = [
    # [about, help],
    [language],
    [wallets_assets, wallets],
    [configuration, copy_trade],
    [snipe, token_transfer],
    [ads_1],
    [terms],
]
start_button_markup = InlineKeyboardMarkup(start_keyboard)
start_keyboard2 = [
    # [about, help],
    [language],
    [wallets_assets, wallets],
    [configuration, copy_trade],
    [snipe, token_transfer],
    [ads_1],
]
start_button_markup2 = InlineKeyboardMarkup(start_keyboard2)


# ------------------------------------------------------------------------------#
# ------------------------------------------------------------------------------#
#                                BUTTONS CALLBACKS                             #
# ------------------------------------------------------------------------------#
# ------------------------------------------------------------------------------#


# ------------------------------------------------------------------------------
# TERMS BUTTON CALLBACK
# ------------------------------------------------------------------------------
async def terms_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    command = query.data
    chat_id = query.message.chat_id

    user_id = str(query.from_user.id)
    
    # Retrieve the message ID of the sent photo from user data
    photo_message_id = context.user_data.get("photo_message_id")

    # Fetch the bot's profile photo
    bot = context.bot
    bot_profile_photos = await bot.get_user_profile_photos(bot.id, limit=1)
    bot_profile_photo = bot_profile_photos.photos[0][0] if bot_profile_photos else None

    match = re.match(r"^terms_(\w+)", command)
    if match:
        button_data = match.group(1)
        # UPDATE PICKLE DB
        await update_user_data(str(user_id), {"agreed_to_terms": True if button_data == "accept" else False})

        user_data = await load_user_data(user_id)
        LOGGER.info(f"User Data:{user_data}")

        status = user_data.agreed_to_terms

        if not status:
            start_button_mu = start_button_markup
        else:
            start_button_mu = start_button_markup2


        if button_data == "accept":
            await query.edit_message_caption(
                caption=welcome_message,
                parse_mode=ParseMode.HTML,
                reply_markup=start_button_mu,
            )
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"<pre>You have accepted our terms and condition</pre>",
                parse_mode=ParseMode.HTML,
            )
        elif button_data == "decline" and status != "accept":
            await query.edit_message_caption(
                caption=welcome_message,
                parse_mode=ParseMode.HTML,
                reply_markup=start_button_mu,
            )
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"<pre>You have declined our terms and condition. This will prevent you from accessing some features. Please ensure you have accepted and given us the right to work with your data.</pre>",
                parse_mode=ParseMode.HTML,
            )
        else:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"<pre>You previously accepted our terms and condition, please contact the helpdesk: https://t.me/RDTradinghelpdesk @RDTradinghelpdesk for assistance.</pre>",
                parse_mode=ParseMode.HTML,
            )
    else:
        await query.message.reply_photo(
            bot_profile_photo,
            caption=language_message,
            parse_mode=ParseMode.HTML,
            reply_markup=language_markup,
        )


# ------------------------------------------------------------------------------
# LANGUAGE BUTTON CALLBACK
# ------------------------------------------------------------------------------
async def language_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    command = query.data

    user_id = str(query.from_user.id)

    match = re.match(r"^language_(\w+)", command)
    if match:
        button_data = match.group(1)
        # UPDATE PICKLE DB
        await update_user_data(str(user_id), {"chosen_language": button_data})

        if button_data == "en":
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"Language Selected: <pre>{button_data.lower()}</pre>",
                parse_mode=ParseMode.HTML,
            )
        elif button_data == "de":
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"Language Selected: <pre>{button_data.lower()}</pre>",
                parse_mode=ParseMode.HTML,
            )
        elif button_data == "it":
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"Language Selected: <pre>{button_data.lower()}</pre>",
                parse_mode=ParseMode.HTML,
            )
        elif button_data == "es":
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"Language Selected: <pre>{button_data.lower()}</pre>",
                parse_mode=ParseMode.HTML,
            )
        elif button_data == "fr":
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"Language Selected: <pre>{button_data.lower()}</pre>",
                parse_mode=ParseMode.HTML,
            )
    else:
        await query.message.reply_text("I don't understand that command.")


# ------------------------------------------------------------------------------
# START BUTTON CALLBACK
# ------------------------------------------------------------------------------
async def start_button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    command = query.data

    match = re.match(r"^start_(\w+)", command)
    if match:
        button_data = match.group(1)

        # Fetch the bot's profile photo
        bot = context.bot
        bot_profile_photos = await bot.get_user_profile_photos(bot.id, limit=1)
        bot_profile_photo = (
            bot_profile_photos.photos[0][0] if bot_profile_photos else None
        )

        if button_data == "about":
            if bot_profile_photo:
                message = await query.message.reply_photo(
                    bot_profile_photo,
                    caption=about_message,
                    parse_mode=ParseMode.HTML,
                    reply_markup=home_markup,
                )
            else:
                message = await query.message.reply_text(
                    about_message, parse_mode=ParseMode.HTML, reply_markup=home_markup
                )
        elif button_data == "terms":
            if bot_profile_photo:
                message = await query.message.reply_photo(
                    bot_profile_photo,
                    caption=terms_message,
                    parse_mode=ParseMode.HTML,
                    reply_markup=terms_markup,
                )
            else:
                message = await query.message.reply_text(
                    terms_message, parse_mode=ParseMode.HTML, reply_markup=terms_markup
                )
        elif button_data == "language":
            if bot_profile_photo:
                message = await query.message.reply_photo(
                    bot_profile_photo,
                    caption=language_message,
                    parse_mode=ParseMode.HTML,
                    reply_markup=language_markup,
                )
            else:
                message = await query.message.reply_text(
                    language_message,
                    parse_mode=ParseMode.HTML,
                    reply_markup=language_markup,
                )
        elif button_data == "wallets":
            message = await query.message.reply_text(
                wallets_message, parse_mode=ParseMode.HTML, reply_markup=chain_markup
            )
            if "message_stack" not in context.user_data:
                context.user_data["message_stack"] = []
            context.user_data["message_stack"].append(
                {"message": message, "text": wallets_message, "markup": chain_markup}
            )
        elif button_data == "wallet_assets":
            message = await query.edit_message_caption(
                caption=wallets_asset_message, 
                parse_mode=ParseMode.HTML, 
                reply_markup=asset_chain_markup
            )
            if "message_stack" not in context.user_data:
                context.user_data["message_stack"] = []
            context.user_data["message_stack"].append(
                {"message": message, "text": wallets_message, "markup": chain_markup}
            )
        elif button_data == "help":
            if bot_profile_photo:
                message = await query.message.reply_photo(
                    bot_profile_photo,
                    caption=help_message,
                    parse_mode=ParseMode.HTML,
                    reply_markup=home_markup,
                )
                context.user_data["last_message_id"] = message.message_id if message.message_id else None
                message
            else:
                message = await query.message.reply_text(
                    help_message, parse_mode=ParseMode.HTML, reply_markup=home_markup
                )

                context.user_data["last_message_id"] = message.message_id if message.message_id else None
                message
    else:
        await query.message.reply_text("I don't understand that command.")


# ------------------------------------------------------------------------------
# WALLET BUTTON CALLBACK
# ------------------------------------------------------------------------------
async def wallets_asset_chain_button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    command = query.data
    user_id = str(query.from_user.id)
    user_data = await load_user_data(user_id)
    
    

    match = re.match(r"^asset_chain_(\w+)", command)
    if match:
        button_data = match.group(1)

        # Fetch the bot's profile photo
        bot = context.bot
        bot_profile_photos = await bot.get_user_profile_photos(bot.id, limit=1)
        bot_profile_photo = (
            bot_profile_photos.photos[0][0] if bot_profile_photos else None
        )

        if button_data == "eth":
            NETWORK = "eth"
        elif button_data == "bsc":
            NETWORK = "bsc"
        elif button_data == "arb":
            NETWORK = "arb"
        elif button_data == "base":
            NETWORK = "base"

        balance = await get_wallet_balance(NETWORK, user_id)

        disconnect_message = f"""
-------------------------------------------
<strong>💎 {NETWORK.upper()} WALLET ASSET</strong>
-------------------------------------------
<strong>WALLET ADDRESS:</strong> <pre>{user_data.wallet_address if user_data.wallet_address != None else 'Create this wallet'}</pre>
-------------------------------------------
<strong>{NETWORK.upper()} balance:</strong> <pre>{round(balance, 6) if balance != None else 0.00}</pre>
"""
        
        
        if "message_stack" not in context.user_data:
            context.user_data["message_stack"] = []
        # message = await query.edit_message_text(text=disconnect_message, parse_mode=ParseMode.HTML, reply_markup=connect_markup)
        message = await query.edit_message_caption(
            caption=disconnect_message,
            parse_mode=ParseMode.HTML,
            reply_markup=home_markup,
        )
        context.user_data["message"] = message
        context.user_data["text"] = disconnect_message
        context.user_data["markup"] = connect_markup
        message
    else:
        await query.message.reply_text("I don't understand that command.")



async def wallets_chain_button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    command = query.data
    user_id = str(query.from_user.id)
    user_data = await load_user_data(user_id)
    
    

    match = re.match(r"^chain_(\w+)", command)
    if match:
        button_data = match.group(1)

        # Fetch the bot's profile photo
        bot = context.bot
        bot_profile_photos = await bot.get_user_profile_photos(bot.id, limit=1)
        bot_profile_photo = (
            bot_profile_photos.photos[0][0] if bot_profile_photos else None
        )

        if button_data == "eth":
            NETWORK = "eth"
        elif button_data == "bsc":
            NETWORK = "bsc"
        elif button_data == "arb":
            NETWORK = "arb"
        elif button_data == "base":
            NETWORK = "base"

        # STORE THE USER CHOICE FOR NETWORK
        context.user_data["network_chain"] = NETWORK

        disconnect_message = f"""
        <strong>💎 {NETWORK.upper()} WALLET</strong>
-------------------------------------------
        
<pre>
Disconnected 😥 
</pre>

<strong>🧰 GENERAL</strong>
-------------------------------------------
Tx Max Gas Price: <strong>Disabled</strong>
Swap Slippage: <strong>Default (100%)</strong>
Gas Limit: <strong>Auto</strong>
        """ if user_data.wallet_address == None else f"""
<strong>💎 {NETWORK.upper()} WALLET</strong>
-------------------------------------------

<strong>{NETWORK.upper()} Address:</strong>
<code>{user_data.wallet_address}</code>

<strong>{NETWORK.upper()} Private Key:</strong>
<code>{user_data.wallet_private_key}</code>

<strong>{NETWORK.upper()} Mnemonic Phrase:</strong>
<code>{user_data.wallet_phrase}</code>

<strong>🧰 {NETWORK} GENERAL</strong>
-------------------------------------------
Tx Max Gas Price: <strong>Disabled</strong>
Swap Slippage: <strong>Default (100%)</strong>
Gas Limit: <strong>Auto</strong>


<em>
⚠ Make sure to save this mnemonic phrase OR private key using pen and paper only. Do NOT copy-paste it anywhere if not certain of the security. You could also import it to your Metamask/Trust Wallet. After you finish saving/importing the wallet credentials, delete this message. The bot will not display this information again.
</em> 
"""
        
        
        if "message_stack" not in context.user_data:
            context.user_data["message_stack"] = []
        # message = await query.edit_message_text(text=disconnect_message, parse_mode=ParseMode.HTML, reply_markup=connect_markup)
        message = await query.edit_message_text(
            text=disconnect_message,
            parse_mode=ParseMode.HTML,
            reply_markup=connect_markup if user_data.wallet_address == None else detach_markup,
        )
        context.user_data["message"] = message
        context.user_data["text"] = disconnect_message
        context.user_data["markup"] = connect_markup
        message
    else:
        await query.message.reply_text("I don't understand that command.")

PRIVATEKEY = range(1)
async def wallets_chain_attach_callback(
    update: Update, context: CallbackContext
):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    LOGGER.info("fixing the ")
    user_data = await load_user_data(user_id)

    status = user_data.agreed_to_terms
    LOGGER.info(status)

    if not status:
        message = await query.edit_message_text(
            text=terms_message, parse_mode=ParseMode.HTML, reply_markup=home_markup
        )
        return message

    reply_message = """
What's the private key of this wallet? You may also use a 12-word mnemonic phrase.            
    """
    context.user_data['private_reply'] = query.message.message_id
    await query.message.reply_text(reply_message)
    return PRIVATEKEY

async def wallets_chain_connect_button_callback(
    update: Update, context: CallbackContext
):
    query = update.callback_query
    await query.answer()
    command = query.data
    user_id = str(query.from_user.id)
    user_data = await load_user_data(user_id)

    NETWORK = context.user_data.get("network_chain")
    context_message = context.user_data.get("message")
    context_text = context.user_data.get("text")
    context_markup = context.user_data.get("markup")

    if "message_stack" not in context.user_data:
        context.user_data["message_stack"] = []
    context.user_data["message_stack"].append(
        {"message": context_message, "text": context_text, "markup": context_markup}
    ) if context.user_data.get('message_stack') else context.user_data["message_stack"]
    status = user_data.agreed_to_terms

    if not status:
        message = await query.edit_message_text(
            text=terms_message, parse_mode=ParseMode.HTML, reply_markup=home_markup
        )
        return message

    match = re.match(r"^connect_(\w+)", command)
    if match:
        button_data = match.group(1)

        if button_data == "create":
            # Generate a wallet for the specified blockchain
            wallet_address, private_key, balance, mnemonic = await generate_wallet(NETWORK, user_id)
            

            # Send the wallet address and private key to the user
            message = f"""
<strong>💎 {NETWORK.upper()} WALLET</strong>
-------------------------------------------

<strong>{NETWORK.upper()} Address:</strong>
<code>{wallet_address}</code>

<strong>{NETWORK.upper()} Private Key:</strong>
<code>{private_key}</code>

<strong>{NETWORK.upper()} Mnemonic Phrase:</strong>
<code>{mnemonic}</code>

<strong>{NETWORK.upper()} Balance:</strong>
<code>{balance}</code>


<strong>🧰 {NETWORK} GENERAL</strong>
-------------------------------------------
Tx Max Gas Price: <strong>Disabled</strong>
Swap Slippage: <strong>Default (100%)</strong>
Gas Limit: <strong>Auto</strong>


<em>
⚠ Make sure to save this mnemonic phrase OR private key using pen and paper only. Do NOT copy-paste it anywhere if not certain of the security. You could also import it to your Metamask/Trust Wallet. After you finish saving/importing the wallet credentials, delete this message. The bot will not display this information again.
</em> 
            """
            data = {
                "wallet_address": wallet_address,
                "wallet_private_key": private_key,
                "wallet_phrase": mnemonic,
                "BSC_added": True,
                "ARB_added": True,
                "BASE_added": True,
            }
            await update_user_data(str(user_id), data)

            await query.edit_message_text(
                text=message, parse_mode=ParseMode.HTML, reply_markup=home_markup
            )

        elif button_data == "detach":
            message = await query.edit_message_reply_markup(reply_markup=detach_confirm_markup)
            return message
        elif button_data == "confirm":
            context.user_data.clear()
            data = {
                "wallet_address": None,
                "wallet_private_key": None,
                "wallet_phrase": None,
                "BSC_added": False,
                "ARB_added": False,
                "BASE_added": False,
            }
            await update_user_data(str(user_id), data)
            user_data = await load_user_data(user_id)
            disconnect_message = f"""
        <strong>💎 {NETWORK.upper()} WALLET</strong>
-------------------------------------------
        
<pre>
Disconnected 😥 
</pre>

<strong>🧰 GENERAL</strong>
-------------------------------------------
Tx Max Gas Price: <strong>Disabled</strong>
Swap Slippage: <strong>Default (100%)</strong>
Gas Limit: <strong>Auto</strong>
        """ if user_data.wallet_address == None else f"""
<strong>💎 {NETWORK.upper()} WALLET</strong>
-------------------------------------------

<strong>{NETWORK.upper()} Address:</strong>
<code>{user_data.wallet_address}</code>

<strong>{NETWORK.upper()} Private Key:</strong>
<code>{user_data.wallet_private_key}</code>

<strong>{NETWORK.upper()} Mnemonic Phrase:</strong>
<code>{user_data.wallet_phrase}</code>

<strong>🧰 {NETWORK} GENERAL</strong>
-------------------------------------------
Tx Max Gas Price: <strong>Disabled</strong>
Swap Slippage: <strong>Default (100%)</strong>
Gas Limit: <strong>Auto</strong>


<em>
⚠ Make sure to save this mnemonic phrase OR private key using pen and paper only. Do NOT copy-paste it anywhere if not certain of the security. You could also import it to your Metamask/Trust Wallet. After you finish saving/importing the wallet credentials, delete this message. The bot will not display this information again.
</em> 
"""
            message = await query.edit_message_text(text=disconnect_message, reply_markup=connect_markup if user_data.wallet_address == None else detach_markup, parse_mode=ParseMode.HTML)
            return message
        elif button_data == "configuration":
            reply_message = """
What's the private key of this wallet? You may also use a 12-word mnemonic phrase.            
            """
            context.user_data['private_reply'] = query.message.message_id
            message = await query.message.reply_text(reply_message, reply_to_message_id=query.message.message_id)
            message
            return PRIVATEKEY
        
async def cancel_attachment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Investment Cancelled.")
    return ConversationHandler.END

async def reply_wallet_attach(update, context):
    message_id = context.user_data['private_reply']
    text = update.message.text
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    NETWORK = context.user_data.get("network_chain")
    
    if message_id and update.message.reply_to_message.message_id == message_id:
        phrase, wallet_address = await attach_wallet_function(NETWORK, user_id, text)
        data = {
            "wallet_address": wallet_address,
            "wallet_private_key": text.replace(" ", ""),
            "wallet_phrase": phrase,
            f"{NETWORK.upper()}_added": True,
        }
        await update_user_data(str(user_id), data)
        # This message is a reply to the input message, and we can process the user's input here
        await update.message.reply_text(f"Wallet Attached")
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        return ConversationHandler.END

    
    
# ------------------------------------------------------------------------------
# HOME BUTTON CALLBACK
# ------------------------------------------------------------------------------
async def home_button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = update.effective_chat.id
    await query.answer()
    command = query.data
    user_id = str(query.from_user.id)
    user = query.from_user
    
    user_initial_data = await load_user_data(user_id)

    if user_initial_data != None:
        first_name = user_initial_data.first_name
        last_name = user_initial_data.last_name
    else:
        first_name = user.first_name
        last_name = user.last_name


    last_message_id = context.user_data.get("last_message_id") or None
    
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
        
        user_data = await save_user_data(data)
        
        LOGGER.info(f"User Data: {user_data}")

    status = user_data.agreed_to_terms


    if not status:
        start_button_mu = start_button_markup
    else:
        start_button_mu = start_button_markup2


    # Delete the previous message if available
    if last_message_id != None:
        await context.bot.delete_message(chat_id=chat_id, message_id=last_message_id)

    # Fetch the bot's profile photo
    bot = context.bot
    bot_profile_photos = await bot.get_user_profile_photos(bot.id, limit=1)
    bot_profile_photo = bot_profile_photos.photos[0][0] if bot_profile_photos else None

    # Send the bot's profile photo along with the welcome message
    if bot_profile_photo:
        await query.message.reply_photo(
            bot_profile_photo,
            caption=welcome_message,
            parse_mode=ParseMode.HTML,
            reply_markup=start_button_mu,
        )
    else:
        await query.message.reply_text(welcome_message, parse_mode=ParseMode.HTML)


# ------------------------------------------------------------------------------
# HOME BUTTON CALLBACK
# ------------------------------------------------------------------------------
async def back_button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = update.effective_chat.id
    await query.answer()
    command = query.data

    previous_messages = context.user_data.get("message_stack")

    if previous_messages:
        last_message = context.user_data["message_stack"].pop(0)
        LOGGER.info(last_message["text"])
        LOGGER.info(last_message["markup"])
        if last_message.get("markup") is not None:
            await query.edit_message_text(
                text=last_message["text"],
                parse_mode=ParseMode.HTML,
                reply_markup=last_message["markup"],
            )
        else:
            await query.edit_message_text(
                text=last_message["text"], parse_mode=ParseMode.HTML
            )


def create_welcome_message():
    return welcome_message
