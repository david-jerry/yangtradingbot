from decimal import Decimal
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
from utils import attach_wallet_function, back_variable, generate_wallet, get_default_gas_price, get_default_gas_price_gwei, get_wallet_balance
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
# CONFIGURATION BUTTONS
# ------------------------------------------------------------------------------
pback = InlineKeyboardButton("⏪ ", callback_data="presets_left")
pforward = InlineKeyboardButton("⏩ ", callback_data="presets_right")
buy = InlineKeyboardButton("🛠 BUY ", callback_data="presets_buy")
sell = InlineKeyboardButton("🛠 SELL", callback_data="presets_sell")
approve = InlineKeyboardButton("🛠 APPROVE", callback_data="presets_approve")
maxdelta = InlineKeyboardButton("📝  Max Gas Delta", callback_data="config_maxdelta")
deldelta = InlineKeyboardButton("⌫ Remove Delta", callback_data="presets_deldelta")
slippage = InlineKeyboardButton("📝  Slippage", callback_data="config_slippage")
delslippage = InlineKeyboardButton("⌫ Remove Slippage", callback_data="presets_delslippage")
maxgas = InlineKeyboardButton("📝  Max Gas Limit", callback_data="config_maxgas")
delgas = InlineKeyboardButton("⌫ Remove Gas Limit", callback_data="presets_delgas")

NETWORK_CHAINS = ["ETH", "BSC", "ARP", "BASE"]
SELECTED_CHAIN_INDEX = 0


# ------------------------------------------------------------------------------
# BUY BUTTONS
# ------------------------------------------------------------------------------
maxbuytax = InlineKeyboardButton("📝 Max Buy Tax", callback_data="config_maxbuytax")
maxselltax = InlineKeyboardButton("📝 Max Sell Tax", callback_data="config_maxselltax")
delbuytax = InlineKeyboardButton("⌫ Remove Buy Tax", callback_data="presets_delbuytax")
delselltax = InlineKeyboardButton("⌫ Remove Buy Tax", callback_data="presets_delselltax")


# ------------------------------------------------------------------------------
# SELL BUTTONS
# ------------------------------------------------------------------------------
sellhi = InlineKeyboardButton("📝 Sell-Hi Tax", callback_data="config_sellhi")
selllo = InlineKeyboardButton("📝 Sell-Lo Tax", callback_data="config_selllo")
sellhiamount = InlineKeyboardButton("📝 Sell-Hi Amount", callback_data="config_sellhiamount")
sellloamount = InlineKeyboardButton("📝 Sell-Lo Amount", callback_data="config_sellloamount")
delsellhi = InlineKeyboardButton("⌫ Remove Sell-Hi", callback_data="presets_delsellhi")
delselllo = InlineKeyboardButton("⌫ Remove Sell-Lo", callback_data="presets_delselllo")
delsellhiamount = InlineKeyboardButton("⌫ Remove Sell-Hi Amount", callback_data="presets_delsellhiamount")
delsellloamount = InlineKeyboardButton("⌫ Remove Sell-Lo Amount", callback_data="presets_delsellloamount")

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

accept_terms_button = InlineKeyboardButton("Accept Conditions", callback_data="terms_accept")
decline_terms_button = InlineKeyboardButton("Decline Conditions", callback_data="terms_decline")
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
configuration = InlineKeyboardButton("Configuration", callback_data="start_configuration")
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
    context.user_data["last_message_id"] = query.message.message_id

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
    context.user_data["last_message_id"] = query.message.message_id

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

def build_preset_keyboard():
    global PRESETNETWORK
    PRESETNETWORK = NETWORK_CHAINS[SELECTED_CHAIN_INDEX]
    chain = InlineKeyboardButton(f"🛠 {PRESETNETWORK}", callback_data=f"presets_{PRESETNETWORK}")
    preset_keyboard = [
        [home],
        [pback, chain, pforward],
        [buy, sell, approve],
        [maxdelta, deldelta],
        [slippage, delslippage],
        [maxgas, delgas]
    ]
    preset_markup = InlineKeyboardMarkup(preset_keyboard)
    
    return preset_markup  
    
    
def build_buy_keyboard(user_data):
    
    deldupebuy = InlineKeyboardButton(f"{'❌' if not user_data.dupe_buy else '✅'} Dupe Buy", callback_data="presets_deldupebuy")
    delautobuy = InlineKeyboardButton(f"{'❌' if not user_data.auto_buy else '✅'} Auto Buy", callback_data="presets_delautobuy")

    buy_keyboard = [
        [home], 
        [back],
        [deldupebuy, delautobuy],
        [maxbuytax, delbuytax], 
        [maxselltax, delselltax],
        [maxgas, delgas],
    ]
    buy_markup = InlineKeyboardMarkup(buy_keyboard)
    return buy_markup

def build_sell_keyboard(user_data):
    delautosell = InlineKeyboardButton(f"{'❌' if not user_data.auto_sell else '✅'} Auto Sell", callback_data="presets_delautosell")

    sell_keyboard = [
        [home], 
        [back],
        [delautosell],
        [sellhi, delsellhi],
        [selllo, delselllo], 
        [sellhiamount, delsellhiamount],
        [sellloamount, delsellloamount],
        [maxgas, delgas],
    ]
    sell_markup = InlineKeyboardMarkup(sell_keyboard)

    return sell_markup

def build_approve_keyboard(user_data):
    autoapprove = InlineKeyboardButton(f"{'❌' if not user_data.auto_approve else '✅'} Auto Approve", callback_data="presets_delautoapprove")
    approve_keyboard = [
        [home], 
        [back],
        [autoapprove],
        [maxgas, delgas],
    ]
    approve_markup = InlineKeyboardMarkup(approve_keyboard)
    return approve_markup

    
async def start_button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    command = query.data
    user_id = str(query.from_user.id)
    context.user_data["last_message_id"] = query.message.message_id
    gas_price = await get_default_gas_price_gwei()

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
            back_variable(message, context, wallets_message, chain_markup, False, False)
        elif button_data == "wallet_assets":
            message = await query.edit_message_caption(
                caption=wallets_asset_message, 
                parse_mode=ParseMode.HTML, 
                reply_markup=asset_chain_markup
            )
            back_variable(message, context, wallets_asset_message, asset_chain_markup, True, False)
        elif button_data == "configuration":
            preset_markup = build_preset_keyboard()
            user_data = await load_user_data(user_id)
            wallet = user_data.wallet_address if user_data.wallet_address is not None else '<pre>Disconnected</pre>'
            configuration_message = f"""
                <strong>{PRESETNETWORK} CONFIGURATIONS</strong>
Wallet: {wallet}

Multi-Wallets: {'✅' if user_data.wallet_address != None and user_data.BSC_added or user_data.wallet_address != None and user_data.ARB_added or user_data.wallet_address != None and user_data.BASE_added  else '❌'}

<strong>🛠 {PRESETNETWORK} GENERAL</strong>
-------------------------------------------
Max Gas Price: <strong>Default({round(user_data.max_gas_price, 2) if user_data.max_gas_price > 1 else gas_price} GWEI) + Delta({round(user_data.max_delta)} GWEI)</strong>
Swap Slippage: <strong>Default ({round(user_data.slippage)}%)</strong>
Gas Limit: <strong>{user_data.max_gas if user_data.max_gas > 0.00 else 'Auto'}</strong>
-------------------------------------------
            """
            context.user_data['config_message'] = configuration_message
            message = await query.edit_message_caption(
                caption=configuration_message,
                parse_mode=ParseMode.HTML,
                reply_markup=preset_markup
            )
            
            context.user_data['last_message'] = configuration_message
            context.user_data['last_markup'] = preset_markup
            
            back_variable(message, context, configuration_message, preset_markup, True, False)
            return message
        elif button_data == "help":
            if bot_profile_photo:
                message = await query.message.reply_photo(
                    bot_profile_photo,
                    caption=help_message,
                    parse_mode=ParseMode.HTML,
                    reply_markup=home_markup,
                )
                context.user_data["last_message_id"] = query.message.message_id if query.message.message_id else None
                message
            else:
                message = await query.message.reply_text(
                    help_message, parse_mode=ParseMode.HTML, reply_markup=home_markup
                )

                context.user_data["last_message_id"] = query.message.message_id if query.message.message_id else None
                message
    else:
        await query.message.reply_text("I don't understand that command.")







# ------------------------------------------------------------------------------
# CONFIGURATION BUTTON CALLBACK
# ------------------------------------------------------------------------------
REPLYDELTA = range(1)
async def configuration_next_and_back_callback(update: Update, context: CallbackContext):
    global SELECTED_CHAIN_INDEX
    
    query = update.callback_query
    await query.answer()
    command = query.data
    user_id = str(query.from_user.id)
    user_data = await load_user_data(user_id)
    text = context.user_data['last_message']
    markup = context.user_data['last_markup']
    context.user_data["last_message_id"] = query.message.message_id
    
    wallet = user_data.wallet_address if user_data.wallet_address is not None else '<pre>Disconnected</pre>'
    
    gas_price = await get_default_gas_price_gwei()

    match = re.match(r"^presets_(\w+)", command)
    if match:
        button_data = match.group(1)
        
        if button_data == "left":
            SELECTED_CHAIN_INDEX = (SELECTED_CHAIN_INDEX - 1) % len(NETWORK_CHAINS)
            # Update the keyboard markup with the new selected chain
            new_markup = build_preset_keyboard()

            # Edit the message to display the updated keyboard markup
            configuration_message = f"""
                <strong>{PRESETNETWORK} CONFIGURATIONS</strong>
Wallet: {wallet}

Multi-Wallets: {'✅' if user_data.wallet_address != None and user_data.BSC_added or user_data.wallet_address != None and user_data.ARB_added or user_data.wallet_address != None and user_data.BASE_added  else '❌'}

<strong>🛠 {PRESETNETWORK} GENERAL</strong>
-------------------------------------------
Max Gas Price: <strong>Default({round(user_data.max_gas_price, 2) if user_data.max_gas_price > 1 else gas_price} GWEI) + Delta({round(user_data.max_delta)} GWEI)</strong>
Swap Slippage: <strong>Default ({Decimal(user_data.slippage)}%)</strong>
Gas Limit: <strong>{user_data.max_gas if user_data.max_gas > 0.00 else 'Auto'}</strong>
-------------------------------------------
    """
            context.user_data['config_message'] = configuration_message
    
            message = await query.edit_message_caption(caption=configuration_message, parse_mode=ParseMode.HTML, reply_markup=new_markup)
            back_variable(message, context, text, new_markup, False, True)
        elif button_data == "right":
            SELECTED_CHAIN_INDEX = (SELECTED_CHAIN_INDEX + 1) % len(NETWORK_CHAINS)
            # Update the keyboard markup with the new selected chain
            new_markup = build_preset_keyboard()
            
            configuration_message = f"""
                <strong>{PRESETNETWORK} CONFIGURATIONS</strong>
Wallet: {wallet}

Multi-Wallets: {'✅' if user_data.wallet_address != None else '❌'}

<strong>🛠 {PRESETNETWORK} GENERAL</strong>
-------------------------------------------
Max Gas Price: <strong>Default({round(user_data.max_gas_price, 2) if user_data.max_gas_price > 1 else gas_price} GWEI) + Delta({round(user_data.max_delta)} GWEI)</strong>
Swap Slippage: <strong>Default ({round(Decimal(user_data.slippage))}%)</strong>
Gas Limit: <strong>{user_data.max_gas if user_data.max_gas > 0.00 else 'Auto'}</strong>
-------------------------------------------
    """
            context.user_data['config_message'] = configuration_message

            # Edit the message to display the updated keyboard markup
            message = await query.edit_message_caption(caption=configuration_message, parse_mode=ParseMode.HTML, reply_markup=new_markup)
            back_variable(message, context, text, new_markup, False, True)
        elif button_data == "buy":
            configuration_message = context.user_data['config_message']
            caption = f"""
            <strong>{PRESETNETWORK} CONFIGURATIONS</strong>
Wallet: {wallet}

Multi-Wallets: {'✅' if user_data.wallet_address != None and user_data.BSC_added or user_data.wallet_address != None and user_data.ARB_added or user_data.wallet_address != None and user_data.BASE_added  else '❌'}

<strong>🛠 {PRESETNETWORK} Buy</strong>
-------------------------------------------
Auto Buy: {'✅' if user_data.auto_buy else '❌'}
Buy Gas Price: <strong>Default({user_data.max_gas_price if user_data.max_gas_price > 1 else gas_price} GWEI) + Delta({round(user_data.max_delta)} GWEI)</strong>
Max Buy Tax: {user_data.buy_tax if user_data.buy_tax > 0.00 else 'Disabled'}
Max Sell Tax: {user_data.sell_tax if user_data.sell_tax > 0.00 else 'Disabled'}
-------------------------------------------            
            """
            context.user_data['buy_message'] = caption
            buy_markup = build_buy_keyboard(user_data)
            message = await query.edit_message_caption(caption=caption, parse_mode=ParseMode.HTML, reply_markup=buy_markup)
            back_variable(message, context, configuration_message, markup, False, True)
        elif button_data == "sell":
            caption = f"""
            <strong>{PRESETNETWORK} CONFIGURATIONS</strong>
Wallet: {wallet}

Multi-Wallets: {'✅' if user_data.wallet_address != None and user_data.BSC_added or user_data.wallet_address != None and user_data.ARB_added or user_data.wallet_address != None and user_data.BASE_added  else '❌'}

<strong>🛠 {PRESETNETWORK} Sell</strong>
-------------------------------------------
Auto Sell: {'✅' if user_data.auto_sell else '❌'}
Sell Gas Price: <strong>Default({round(user_data.max_gas_price, 2) if user_data.max_gas_price > 1 else gas_price} GWEI) + Delta({round(user_data.max_delta)} GWEI)</strong>
Auto Sell (high): <strong>{(user_data.sell_hi * 50) if user_data.sell_hi > 0.00 else 'Default(+100%)'}</strong>
Sell Amount (high): <strong>{user_data.sell_hi_amount if user_data.sell_hi_amount > 0.00 else 'Default(100%)'}</strong>
Auto Sell (low): <strong>{(user_data.sell_lo * 50) if user_data.sell_lo > 0.00 else '-50%'}</strong>
Sell Amount (low): <strong>{user_data.sell_lo_amount if user_data.sell_lo_amount > 0.00 else '100%'}</strong>
-------------------------------------------            
            """
            configuration_message = context.user_data['config_message']
            context.user_data['sell_message'] = caption
            sell_markup = build_sell_keyboard(user_data)
            message = await query.edit_message_caption(caption=caption, parse_mode=ParseMode.HTML, reply_markup=sell_markup)
            back_variable(message, context, configuration_message, markup, False, True)
        elif button_data == "approve":
            caption = f"""
            <strong>{PRESETNETWORK} CONFIGURATIONS</strong>
Wallet: {wallet}

Multi-Wallets: {'✅' if user_data.wallet_address != None and user_data.BSC_added or user_data.wallet_address != None and user_data.ARB_added or user_data.wallet_address != None and user_data.BASE_added  else '❌'}

<strong>{'✅' if user_data.auto_approve else '❌'} {PRESETNETWORK} Sell</strong>
-------------------------------------------
Auto Approve: {'✅' if user_data.auto_approve else '❌'}
Approve Gas Price: <strong>Default({round(user_data.max_gas_price, 2) if user_data.max_gas_price > 1 else gas_price} GWEI) + Delta({round(user_data.max_delta)} GWEI)</strong>
-------------------------------------------            
            """
            configuration_message = context.user_data['config_message']
            context.user_data['approve_message'] = caption
            
            approve_markup = build_approve_keyboard(user_data)


            message = await query.edit_message_caption(caption=caption, parse_mode=ParseMode.HTML, reply_markup=approve_markup)
            back_variable(message, context, configuration_message, markup, False, True)
        elif button_data == "delgas":
            await update_user_data(user_id, {'max_gas':round(Decimal(0.00), 2)})
            message = await query.message.reply_text(text="❌ Custom gas limit has been deleted!")
            back_variable(message, context, text, markup, False, False)
            context.user_data['msg_id'] = message.message_id
            context.user_data['preset'] = "delgas"
        elif button_data == "deldelta":
            await update_user_data(user_id, {'max_delta':round(Decimal(0.00), 2)})
            message = await query.message.reply_text(text="❌ Max gas delta has been deleted!")
            back_variable(message, context, text, markup, False, False)
            context.user_data['msg_id'] = message.message_id
            context.user_data['preset'] = "deldelta"
        elif button_data == "delslippage":
            await update_user_data(user_id, {'slippage':round(Decimal(100.00), 2)})
            message = await query.message.reply_text(text="❌ Custom slippage has been deleted!")
            back_variable(message, context, text, markup, False, False)
            context.user_data['msg_id'] = message.message_id
            context.user_data['preset'] = "delslippage"
        elif button_data == "delbuytax":
            await update_user_data(user_id, {'buy_tax':round(Decimal(0.00), 2)})
            message = await query.message.reply_text(text="❌ Max buy tax threshold has been deleted!")
            back_variable(message, context, text, markup, False, False)
            context.user_data['msg_id'] = message.message_id
            context.user_data['preset'] = "delbuytax"
        elif button_data == "delselltax":
            await update_user_data(user_id, {'sell_tax':round(Decimal(0.00), 2)})
            message = await query.message.reply_text(text="❌ Max sell tax threshold has been deleted!")
            back_variable(message, context, text, markup, False, False)
            context.user_data['msg_id'] = message.message_id
            context.user_data['preset'] = "delselltax"
        elif button_data == "delautoapprove":
            variable = user_data.auto_approve
            variable = not variable
            LOGGER.info(variable)
            await update_user_data(user_id, {'auto_approve':variable})
            user_data = await load_user_data(user_id)
            approve_markup = build_approve_keyboard(user_data)
            message = await query.edit_message_caption(caption=f"""
            <strong>{PRESETNETWORK} CONFIGURATIONS</strong>
Wallet: {wallet}

Multi-Wallets: {'✅' if user_data.wallet_address != None and user_data.BSC_added or user_data.wallet_address != None and user_data.ARB_added or user_data.wallet_address != None and user_data.BASE_added  else '❌'}

<strong>{'✅' if variable else '❌'} {PRESETNETWORK} Sell</strong>
-------------------------------------------
Auto Approve: {'✅' if variable else '❌'}
Approve Gas Price: <strong>Default({round(user_data.max_gas_price, 2) if user_data.max_gas_price > 1 else gas_price} GWEI) + Delta({round(user_data.max_delta)} GWEI)</strong>
-------------------------------------------            
            """, parse_mode=ParseMode.HTML, reply_markup=approve_markup)
            back_variable(message, context, text, markup, True, False)
            context.user_data['msg_id'] = message.message_id
            context.user_data['preset'] = "delautoapprove"
        elif button_data == "deldupebuy":
            variable = user_data.dupe_buy
            variable = not variable
            await update_user_data(user_id, {'dupe_buy':variable})
            user_data = await load_user_data(user_id)
            buy_markup = build_buy_keyboard(user_data)
            caption = f"""
            <strong>{PRESETNETWORK} CONFIGURATIONS</strong>
Wallet: {wallet}

Multi-Wallets: {'✅' if user_data.wallet_address != None and user_data.BSC_added or user_data.wallet_address != None and user_data.ARB_added or user_data.wallet_address != None and user_data.BASE_added  else '❌'}

<strong>🛠 {PRESETNETWORK} Buy</strong>
-------------------------------------------
Auto Buy: {'✅' if user_data.auto_buy else '❌'}
Buy Gas Price: <strong>Default({user_data.max_gas_price if user_data.max_gas_price > 1 else gas_price} GWEI) + Delta({round(user_data.max_delta)} GWEI)</strong>
Max Buy Tax: {user_data.buy_tax if user_data.buy_tax > 0.00 else 'Disabled'}
Max Sell Tax: {user_data.sell_tax if user_data.sell_tax > 0.00 else 'Disabled'}
-------------------------------------------            
            """
            message = await query.edit_message_caption(caption=caption, parse_mode=ParseMode.HTML, reply_markup=buy_markup)
            back_variable(message, context, text, markup, True, False)
            context.user_data['msg_id'] = message.message_id
            context.user_data['preset'] = "deldupebuy"
        elif button_data == "delautobuy":
            variable = user_data.auto_buy
            variable = not variable
            await update_user_data(user_id, {'auto_buy':variable})
            user_data = await load_user_data(user_id)
            buy_markup = build_buy_keyboard(user_data)
            caption = f"""
            <strong>{PRESETNETWORK} CONFIGURATIONS</strong>
Wallet: {wallet}

Multi-Wallets: {'✅' if user_data.wallet_address != None and user_data.BSC_added or user_data.wallet_address != None and user_data.ARB_added or user_data.wallet_address != None and user_data.BASE_added  else '❌'}

<strong>🛠 {PRESETNETWORK} Buy</strong>
-------------------------------------------
Auto Buy: {'✅' if user_data.auto_buy else '❌'}
Buy Gas Price: <strong>Default({user_data.max_gas_price if user_data.max_gas_price > 1 else gas_price} GWEI) + Delta({round(user_data.max_delta)} GWEI)</strong>
Max Buy Tax: {user_data.buy_tax if user_data.buy_tax > 0.00 else 'Disabled'}
Max Sell Tax: {user_data.sell_tax if user_data.sell_tax > 0.00 else 'Disabled'}
-------------------------------------------            
            """
            message = await query.edit_message_caption(caption=caption, parse_mode=ParseMode.HTML, reply_markup=buy_markup)
            back_variable(message, context, text, markup, True, False)
            context.user_data['msg_id'] = message.message_id
            context.user_data['preset'] = "delautobuy"
        elif button_data == "delautosell":
            variable = user_data.auto_sell
            variable = not variable
            await update_user_data(user_id, {'auto_sell':variable})
            user_data = await load_user_data(user_id)
            caption = f"""
            <strong>{PRESETNETWORK} CONFIGURATIONS</strong>
Wallet: {wallet}

Multi-Wallets: {'✅' if user_data.wallet_address != None and user_data.BSC_added or user_data.wallet_address != None and user_data.ARB_added or user_data.wallet_address != None and user_data.BASE_added  else '❌'}

<strong>🛠 {PRESETNETWORK} Sell</strong>
-------------------------------------------
Auto Sell: {'✅' if user_data.auto_sell else '❌'}
Sell Gas Price: <strong>Default({round(user_data.max_gas_price, 2) if user_data.max_gas_price > 1 else gas_price} GWEI) + Delta({round(user_data.max_delta)} GWEI)</strong>
Auto Sell (high): <strong>{(user_data.sell_hi * 50) if user_data.sell_hi > 0.00 else 'Default(+100%)'}</strong>
Sell Amount (high): <strong>{user_data.sell_hi_amount if user_data.sell_hi_amount > 0.00 else 'Default(100%)'}</strong>
Auto Sell (low): <strong>{(user_data.sell_lo * 50) if user_data.sell_lo > 0.00 else '-50%'}</strong>
Sell Amount (low): <strong>{user_data.sell_lo_amount if user_data.sell_lo_amount > 0.00 else '100%'}</strong>
-------------------------------------------            
            """
            sell_markup = build_sell_keyboard(user_data)            
            message = await query.edit_message_caption(caption=caption, parse_mode=ParseMode.HTML, reply_markup=sell_markup)
            back_variable(message, context, text, markup, True, False)
            context.user_data['msg_id'] = message.message_id
            context.user_data['preset'] = "delautosell"
        elif button_data == "delsellhi":
            # multiplied by 50
            await update_user_data(user_id, {'sell_hi':round(Decimal(2.00), 2)})
            user_data = await load_user_data(user_id)
            caption = f"""
            <strong>{PRESETNETWORK} CONFIGURATIONS</strong>
Wallet: {wallet}

Multi-Wallets: {'✅' if user_data.wallet_address != None and user_data.BSC_added or user_data.wallet_address != None and user_data.ARB_added or user_data.wallet_address != None and user_data.BASE_added  else '❌'}

<strong>🛠 {PRESETNETWORK} Sell</strong>
-------------------------------------------
Auto Sell: {'✅' if user_data.auto_sell else '❌'}
Sell Gas Price: <strong>Default({round(user_data.max_gas_price, 2) if user_data.max_gas_price > 1 else gas_price} GWEI) + Delta({round(user_data.max_delta)} GWEI)</strong>
Auto Sell (high): <strong>{(user_data.sell_hi * 50) if user_data.sell_hi > 0.00 else 'Default(+100%)'}</strong>
Sell Amount (high): <strong>{user_data.sell_hi_amount if user_data.sell_hi_amount > 0.00 else 'Default(100%)'}</strong>
Auto Sell (low): <strong>{(user_data.sell_lo * 50) if user_data.sell_lo > 0.00 else '-50%'}</strong>
Sell Amount (low): <strong>{user_data.sell_lo_amount if user_data.sell_lo_amount > 0.00 else '100%'}</strong>
-------------------------------------------            
            """
            sell_markup = build_sell_keyboard(user_data)            
            message = await query.message.reply_text(text="""❌ Auto sell (high) % has been deleted!""")
            await query.edit_message_caption(caption=caption, parse_mode=ParseMode.HTML, reply_markup=sell_markup)
            back_variable(message, context, text, markup, False, False)
            context.user_data['msg_id'] = message.message_id
            context.user_data['preset'] = "delsellhi"
        elif button_data == "delselllo":
            # Multiplied by 50
            await update_user_data(user_id, {'sell_lo':round(Decimal(0.50), 2)})
            user_data = await load_user_data(user_id)
            caption = f"""
            <strong>{PRESETNETWORK} CONFIGURATIONS</strong>
Wallet: {wallet}

Multi-Wallets: {'✅' if user_data.wallet_address != None and user_data.BSC_added or user_data.wallet_address != None and user_data.ARB_added or user_data.wallet_address != None and user_data.BASE_added  else '❌'}

<strong>🛠 {PRESETNETWORK} Sell</strong>
-------------------------------------------
Auto Sell: {'✅' if user_data.auto_sell else '❌'}
Sell Gas Price: <strong>Default({round(user_data.max_gas_price, 2) if user_data.max_gas_price > 1 else gas_price} GWEI) + Delta({round(user_data.max_delta)} GWEI)</strong>
Auto Sell (high): <strong>{(user_data.sell_hi * 50) if user_data.sell_hi > 0.00 else 'Default(+100%)'}</strong>
Sell Amount (high): <strong>{user_data.sell_hi_amount if user_data.sell_hi_amount > 0.00 else 'Default(100%)'}</strong>
Auto Sell (low): <strong>{(user_data.sell_lo * 50) if user_data.sell_lo > 0.00 else '-50%'}</strong>
Sell Amount (low): <strong>{user_data.sell_lo_amount if user_data.sell_lo_amount > 0.00 else '100%'}</strong>
-------------------------------------------            
            """
            sell_markup = build_sell_keyboard(user_data)            
            message = await query.message.reply_text(text="""❌ Auto sell (low) % has been deleted!""")
            await query.edit_message_caption(caption=caption, parse_mode=ParseMode.HTML, reply_markup=sell_markup)
            back_variable(message, context, text, markup, False, False)
            context.user_data['msg_id'] = message.message_id
            context.user_data['preset'] = "delselllo"
        elif button_data == "delsellhiamount":
            # 50 for half the token owned ie: 50/100
            await update_user_data(user_id, {'sell_hi_amount':round(Decimal(100.00), 2)})
            user_data = await load_user_data(user_id)
            caption = f"""
            <strong>{PRESETNETWORK} CONFIGURATIONS</strong>
Wallet: {wallet}

Multi-Wallets: {'✅' if user_data.wallet_address != None and user_data.BSC_added or user_data.wallet_address != None and user_data.ARB_added or user_data.wallet_address != None and user_data.BASE_added  else '❌'}

<strong>🛠 {PRESETNETWORK} Sell</strong>
-------------------------------------------
Auto Sell: {'✅' if user_data.auto_sell else '❌'}
Sell Gas Price: <strong>Default({round(user_data.max_gas_price, 2) if user_data.max_gas_price > 1 else gas_price} GWEI) + Delta({round(user_data.max_delta)} GWEI)</strong>
Auto Sell (high): <strong>{(user_data.sell_hi * 50) if user_data.sell_hi > 0.00 else 'Default(+100%)'}</strong>
Sell Amount (high): <strong>{user_data.sell_hi_amount if user_data.sell_hi_amount > 0.00 else 'Default(100%)'}</strong>
Auto Sell (low): <strong>{(user_data.sell_lo * 50) if user_data.sell_lo > 0.00 else '-50%'}</strong>
Sell Amount (low): <strong>{user_data.sell_lo_amount if user_data.sell_lo_amount > 0.00 else '100%'}</strong>
-------------------------------------------            
            """
            sell_markup = build_sell_keyboard(user_data)            
            message = await query.message.reply_text(text="""❌ Auto sell (high-amount) % has been deleted!""")
            await query.edit_message_caption(caption=caption, parse_mode=ParseMode.HTML, reply_markup=sell_markup)
            back_variable(message, context, text, markup, False, False)
            context.user_data['msg_id'] = message.message_id
            context.user_data['preset'] = "delsellhiamount"
        elif button_data == "delsellloamount":
            # 50 for half the token owned ie: 50/100
            await update_user_data(user_id, {'sell_lo_amount':round(Decimal(50.00), 2)})
            user_data = await load_user_data(user_id)
            caption = f"""
            <strong>{PRESETNETWORK} CONFIGURATIONS</strong>
Wallet: {wallet}

Multi-Wallets: {'✅' if user_data.wallet_address != None and user_data.BSC_added or user_data.wallet_address != None and user_data.ARB_added or user_data.wallet_address != None and user_data.BASE_added  else '❌'}

<strong>🛠 {PRESETNETWORK} Sell</strong>
-------------------------------------------
Auto Sell: {'✅' if user_data.auto_sell else '❌'}
Sell Gas Price: <strong>Default({round(user_data.max_gas_price, 2) if user_data.max_gas_price > 1 else gas_price} GWEI) + Delta({round(user_data.max_delta)} GWEI)</strong>
Auto Sell (high): <strong>{(user_data.sell_hi * 50) if user_data.sell_hi > 0.00 else 'Default(+100%)'}</strong>
Sell Amount (high): <strong>{user_data.sell_hi_amount if user_data.sell_hi_amount > 0.00 else 'Default(100%)'}</strong>
Auto Sell (low): <strong>{(user_data.sell_lo * 50) if user_data.sell_lo > 0.00 else '-50%'}</strong>
Sell Amount (low): <strong>{user_data.sell_lo_amount if user_data.sell_lo_amount > 0.00 else '100%'}</strong>
-------------------------------------------            
            """
            sell_markup = build_sell_keyboard(user_data)                     
            message = await query.message.reply_text(text="""❌ Auto sell (low-amount) % has been deleted!""")
            await query.edit_message_caption(caption=caption, parse_mode=ParseMode.HTML, reply_markup=sell_markup)
            back_variable(message, context, text, markup, False, False)
            context.user_data['msg_id'] = message.message_id
            context.user_data['preset'] = "delsellloamount"






async def configuration_button_callback(update: Update, context: CallbackContext):
    global SELECTED_CHAIN_INDEX
    
    query = update.callback_query
    await query.answer()
    command = query.data
    user_id = str(query.from_user.id)
    user_data = await load_user_data(user_id)
    text = context.user_data['last_message']
    markup = context.user_data['last_markup']
    context.user_data["last_message_id"] = query.message.message_id
    wallet = user_data.wallet_address if user_data.wallet_address is not None else '<pre>Disconnected</pre>'
    
    gas_price = await get_default_gas_price_gwei()
    

    match = re.match(r"^config_(\w+)", command)
    if match:
        button_data = match.group(1)
        
        if button_data == "maxdelta":
            message = await query.message.reply_text(text="Reply to this message with your desired maximum gas delta (in GWEI). 1 GWEI = 10 ^ 9 wei. Minimum is 0 GWEI!")
            back_variable(message, context, text, markup, False, True)
            context.user_data['msg_id'] = message.message_id
            context.user_data['preset'] = "delta"
            return REPLYDELTA
        elif button_data == "slippage":
            message = await query.message.reply_text(text="Reply to this message with your desired slippage percentage. Minimum is 0.1%. Max is 100%!")
            back_variable(message, context, text, markup, False, True)
            context.user_data['msg_id'] = message.message_id
            context.user_data['preset'] = "slippage"
            return REPLYDELTA
        elif button_data == "maxgas":
            message = await query.message.reply_text(text="Reply to this message with your desired maximum gas limit. Minimum is 1m, Maximum is 10m!")
            back_variable(message, context, text, markup, False, True)
            context.user_data['msg_id'] = message.message_id
            context.user_data['preset'] = "gas"
            return REPLYDELTA
# ----------------------------------------
        elif button_data == "maxbuytax":
            msg = """
Reply to this message with your desired buy tax threshold!

⚠️ If the token's buy tax is higher than your set amount, auto buy will not be triggered.            
            """
            message = await query.message.reply_text(text=msg)
            back_variable(message, context, text, markup, False, True)
            context.user_data['msg_id'] = message.message_id
            context.user_data['preset'] = "maxbuytax"
            return REPLYDELTA
        elif button_data == "maxselltax":
            msg = """
Reply to this message with your desired sell tax threshold!

⚠️ If the token's sell tax is higher than your set amount, auto buy will not be triggered.
"""
            message = await query.message.reply_text(text=msg)
            back_variable(message, context, text, markup, False, True)
            context.user_data['msg_id'] = message.message_id
            context.user_data['preset'] = "maxselltax"
            return REPLYDELTA
        elif button_data == "sellhi":
            msg = """
Reply to this message with your desired sell percentage. This is the HIGH threshold at which you'll auto sell for profits.

Example: 2x would be 100.
"""
            message = await query.message.reply_text(text=msg)
            back_variable(message, context, text, markup, False, True)
            context.user_data['msg_id'] = message.message_id
            context.user_data['preset'] = "sellhi"
            return REPLYDELTA
        elif button_data == "selllo":
            msg = """
Reply to this message with your desired sell tax threshold!

⚠️ If the token's sell tax is higher than your set amount, auto buy will not be triggered.
"""
            message = await query.message.reply_text(text=msg)
            back_variable(message, context, text, markup, False, True)
            context.user_data['msg_id'] = message.message_id
            context.user_data['preset'] = "selllo"
            return REPLYDELTA
        elif button_data == "sellhiamount":
            msg = """
Reply to this message with your desired sell amount %. This represents how much of your holdings you want to sell when sell-high is triggered.

Example: If you want to sell half of your bag, type 50.
"""
            message = await query.message.reply_text(text=msg)
            back_variable(message, context, text, markup, False, True)
            context.user_data['msg_id'] = message.message_id
            context.user_data['preset'] = "sellhiamount"
            return REPLYDELTA
        elif button_data == "sellloamount":
            msg = """
Reply to this message with your desired sell amount %. This represents how much of your holdings you want to sell when sell-low is triggered.

Example: If you want to sell half of your bag, type 50.
"""
            message = await query.message.reply_text(text=msg)
            back_variable(message, context, text, markup, False, True)
            context.user_data['msg_id'] = message.message_id
            context.user_data['preset'] = "sellloamount"
            return REPLYDELTA



async def reply_preset_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = context.user_data.get('user_id')   
    preset = context.user_data.get('preset')
    text = update.message.text
    caption = context.user_data['config_message'] 
    
    wallet = user_data.wallet_address if user_data.wallet_address is not None else '<pre>Disconnected</pre>'
    
    gas_price = await get_default_gas_price_gwei()
    
    if preset == "delta":
        f_text = Decimal(text.replace(' GWEI', '')) if 'GWEI' in text else Decimal(text)
        text = f"""
        ✅ Max gas delta set to {round(Decimal(f_text))} GWEI. By setting your Max Gas Delta to {round(Decimal(f_text))} GWEI, the bot will no longer frontrun rugs or copytrade transactions that require more than {round(Decimal(f_text))} GWEI in delta.
        """
        await update_user_data(user_id, {'max_delta':f_text})
        user_data = await load_user_data(user_id)
        new_markup = build_preset_keyboard()
        await update.message.edit_caption(caption=caption, parse_mode=ParseMode.HTML, reply_markup=new_markup)
    elif preset == "slippage":
        f_text = text.replace('%', '') if '%' in text else Decimal(text)
        text = f"""
        ✅ Slippage percentage set to {f_text}%!        
        """
        await update_user_data(user_id, {'slippage':Decimal(f_text)})
        user_data = await load_user_data(user_id)
        new_markup = build_preset_keyboard()
        await update.message.edit_caption(caption=caption, parse_mode=ParseMode.HTML, reply_markup=new_markup)
    elif preset == "gas":
        f_text = int(text.replace('m', '')) if 'm' in text else int(text) * 1000000
        text = f"""
        ✅ Max gas limit set to {round(f_text)}!
        """
        await update_user_data(user_id, {'max_gas':round(Decimal(f_text), 2)})
        user_data = await load_user_data(user_id)
        new_markup = build_preset_keyboard()
        await update.message.edit_caption(caption=caption, parse_mode=ParseMode.HTML, reply_markup=new_markup)
# --------------------------------------------------------------------------------
    elif preset == "maxbuytax":
        f_text = int(text.replace('x', '')) if 'x' in text else int(text)
        text = f"""
        ✅ Max Buy Tax set to {round(f_text)}!
        """
        user_data = await load_user_data(user_id)
        await update_user_data(user_id, {'buy_tax':round(Decimal(f_text), 2)})
        buy_markup = build_buy_keyboard(user_data)
        await update.message.edit_caption(caption=context.user_data['buy_message'], parse_mode=ParseMode.HTML, reply_markup=buy_markup)
    elif preset == "maxselltax":
        f_text = int(text.replace('x', '')) if 'x' in text else int(text)
        text = f"""
        ✅ Max Sell Tax set to {round(f_text)}!
        """
        await update_user_data(user_id, {'sell_tax':round(Decimal(f_text), 2)})
        user_data = await load_user_data(user_id)
        buy_markup = build_buy_keyboard(user_data)
        await update.message.edit_caption(caption=context.user_data['buy_message'], parse_mode=ParseMode.HTML, reply_markup=buy_markup)
    elif preset == "sellhi":
        f_text = int(text.replace('x', '')) if 'x' in text else Decimal(text)
        text = f"""
        ✅ Sell-Hi set to {round(f_text)}!
        """
        await update_user_data(user_id, {'sell_hi':round(Decimal(f_text), 2)})
        user_data = await load_user_data(user_id)
        sell_markup = build_sell_keyboard(user_data)
        caption = f"""
            <strong>{PRESETNETWORK} CONFIGURATIONS</strong>
Wallet: {wallet}

Multi-Wallets: {'✅' if user_data.wallet_address != None and user_data.BSC_added or user_data.wallet_address != None and user_data.ARB_added or user_data.wallet_address != None and user_data.BASE_added  else '❌'}

<strong>🛠 {PRESETNETWORK} Sell</strong>
-------------------------------------------
Auto Sell: {'✅' if user_data.auto_sell else '❌'}
Sell Gas Price: <strong>Default({round(user_data.max_gas_price, 2) if user_data.max_gas_price > 1 else gas_price} GWEI) + Delta({round(user_data.max_delta)} GWEI)</strong>
Auto Sell (high): <strong>{(user_data.sell_hi * 50) if user_data.sell_hi > 0.00 else 'Default(+100%)'}</strong>
Sell Amount (high): <strong>{user_data.sell_hi_amount if user_data.sell_hi_amount > 0.00 else 'Default(100%)'}</strong>
Auto Sell (low): <strong>{(user_data.sell_lo * 50) if user_data.sell_lo > 0.00 else '-50%'}</strong>
Sell Amount (low): <strong>{user_data.sell_lo_amount if user_data.sell_lo_amount > 0.00 else '100%'}</strong>
-------------------------------------------            
            """
        await update.message.edit_caption(caption=caption, parse_mode=ParseMode.HTML, reply_markup=sell_markup)
    elif preset == "selllo":
        f_text = int(text.replace('x', '')) if 'x' in text else Decimal(text)
        text = f"""
        ✅ Sell-Lo set to {round(f_text)}!
        """
        await update_user_data(user_id, {'sell_lo':round(Decimal(f_text), 2)})
        user_data = await load_user_data(user_id)
        sell_markup = build_sell_keyboard(user_data)
        caption = f"""
            <strong>{PRESETNETWORK} CONFIGURATIONS</strong>
Wallet: {wallet}

Multi-Wallets: {'✅' if user_data.wallet_address != None and user_data.BSC_added or user_data.wallet_address != None and user_data.ARB_added or user_data.wallet_address != None and user_data.BASE_added  else '❌'}

<strong>🛠 {PRESETNETWORK} Sell</strong>
-------------------------------------------
Auto Sell: {'✅' if user_data.auto_sell else '❌'}
Sell Gas Price: <strong>Default({round(user_data.max_gas_price, 2) if user_data.max_gas_price > 1 else gas_price} GWEI) + Delta({round(user_data.max_delta)} GWEI)</strong>
Auto Sell (high): <strong>{(user_data.sell_hi * 50) if user_data.sell_hi > 0.00 else 'Default(+100%)'}</strong>
Sell Amount (high): <strong>{user_data.sell_hi_amount if user_data.sell_hi_amount > 0.00 else 'Default(100%)'}</strong>
Auto Sell (low): <strong>{(user_data.sell_lo * 50) if user_data.sell_lo > 0.00 else '-50%'}</strong>
Sell Amount (low): <strong>{user_data.sell_lo_amount if user_data.sell_lo_amount > 0.00 else '100%'}</strong>
-------------------------------------------            
            """
        await update.message.edit_caption(caption=caption, parse_mode=ParseMode.HTML, reply_markup=sell_markup)
    elif preset == "sellhiamount":
        f_text = int(text.replace('m', '')) if 'm' in text else int(text)
        text = f"""
        ✅ Sell-Hi Amount set to {round(f_text)}!
        """
        await update_user_data(user_id, {'sell_hi_amount':round(Decimal(f_text), 2)})
        user_data = await load_user_data(user_id)
        sell_markup = build_sell_keyboard(user_data)
        caption = f"""
            <strong>{PRESETNETWORK} CONFIGURATIONS</strong>
Wallet: {wallet}

Multi-Wallets: {'✅' if user_data.wallet_address != None and user_data.BSC_added or user_data.wallet_address != None and user_data.ARB_added or user_data.wallet_address != None and user_data.BASE_added  else '❌'}

<strong>🛠 {PRESETNETWORK} Sell</strong>
-------------------------------------------
Auto Sell: {'✅' if user_data.auto_sell else '❌'}
Sell Gas Price: <strong>Default({round(user_data.max_gas_price, 2) if user_data.max_gas_price > 1 else gas_price} GWEI) + Delta({round(user_data.max_delta)} GWEI)</strong>
Auto Sell (high): <strong>{(user_data.sell_hi * 50) if user_data.sell_hi > 0.00 else 'Default(+100%)'}</strong>
Sell Amount (high): <strong>{user_data.sell_hi_amount if user_data.sell_hi_amount > 0.00 else 'Default(100%)'}</strong>
Auto Sell (low): <strong>{(user_data.sell_lo * 50) if user_data.sell_lo > 0.00 else '-50%'}</strong>
Sell Amount (low): <strong>{user_data.sell_lo_amount if user_data.sell_lo_amount > 0.00 else '100%'}</strong>
-------------------------------------------            
            """
        await update.message.edit_caption(caption=caption, parse_mode=ParseMode.HTML, reply_markup=sell_markup)
        
    elif preset == "sellloamount":
        f_text = int(text.replace('m', '')) if 'm' in text else int(text)
        text = f"""
        ✅ Sell-Lo Amount set to {round(f_text)}!
        """
        await update_user_data(user_id, {'sell_lo_amount':round(Decimal(f_text), 2)})
        user_data = await load_user_data(user_id)
        sell_markup = build_sell_keyboard(user_data)
        caption = f"""
            <strong>{PRESETNETWORK} CONFIGURATIONS</strong>
Wallet: {wallet}

Multi-Wallets: {'✅' if user_data.wallet_address != None and user_data.BSC_added or user_data.wallet_address != None and user_data.ARB_added or user_data.wallet_address != None and user_data.BASE_added  else '❌'}

<strong>🛠 {PRESETNETWORK} Sell</strong>
-------------------------------------------
Auto Sell: {'✅' if user_data.auto_sell else '❌'}
Sell Gas Price: <strong>Default({round(user_data.max_gas_price, 2) if user_data.max_gas_price > 1 else gas_price} GWEI) + Delta({round(user_data.max_delta)} GWEI)</strong>
Auto Sell (high): <strong>{(user_data.sell_hi * 50) if user_data.sell_hi > 0.00 else 'Default(+100%)'}</strong>
Sell Amount (high): <strong>{user_data.sell_hi_amount if user_data.sell_hi_amount > 0.00 else 'Default(100%)'}</strong>
Auto Sell (low): <strong>{(user_data.sell_lo * 50) if user_data.sell_lo > 0.00 else '-50%'}</strong>
Sell Amount (low): <strong>{user_data.sell_lo_amount if user_data.sell_lo_amount > 0.00 else '100%'}</strong>
-------------------------------------------            
            """
        await update.message.edit_caption(caption=caption, parse_mode=ParseMode.HTML, reply_markup=sell_markup)



        
        

    # Reply to the user and highlight the last sent message
    last_message_id = context.user_data.get('msg_id')
    if last_message_id:
        await update.message.reply_text(
            text=text,
            reply_to_message_id=last_message_id,  # Highlight the last sent message
        )

    return ConversationHandler.END

async def cancel_preset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop('msg_id', None)
    context.user_data.pop('preset', None)
    await update.message.reply_text("Preset Cancelled.")
    return ConversationHandler.END








# ------------------------------------------------------------------------------
# WALLET BUTTON CALLBACK
# ------------------------------------------------------------------------------
async def wallets_asset_chain_button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    command = query.data
    user_id = str(query.from_user.id)
    user_data = await load_user_data(user_id)
    
    context.user_data["last_message_id"] = query.message.message_id

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
        
        
        message = await query.edit_message_caption(
            caption=disconnect_message,
            parse_mode=ParseMode.HTML,
            reply_markup=home_markup,
        )
        context.user_data["message"] = message
        context.user_data["text"] = disconnect_message
        context.user_data["markup"] = connect_markup
        back_variable(message, context, disconnect_message, home_markup, True, False)
        return message
    else:
        await query.message.reply_text("I don't understand that command.")

async def wallets_chain_button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    command = query.data
    user_id = str(query.from_user.id)
    user_data = await load_user_data(user_id)
    
    context.user_data["last_message_id"] = query.message.message_id

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

<strong>🛠 GENERAL</strong>
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

<strong>🛠 {NETWORK} GENERAL</strong>
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
async def wallets_chain_connect_button_callback(
    update: Update, context: CallbackContext
):
    query = update.callback_query
    await query.answer()
    command = query.data
    user_id = str(query.from_user.id)
    user_data = await load_user_data(user_id)
    context.user_data["last_message_id"] = query.message.message_id

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


<strong>🛠 {NETWORK} GENERAL</strong>
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

<strong>🛠 GENERAL</strong>
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

<strong>🛠 {NETWORK} GENERAL</strong>
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

        
async def wallets_chain_attach_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    command = query.data
    user_data = await load_user_data(user_id)
    
    context.user_data["last_message_id"] = query.message.message_id

    NETWORK = context.user_data.get("network_chain")
    context_message = context.user_data.get("message")
    context_text = context.user_data.get("text")
    context_markup = context.user_data.get("markup")

    if "message_stack" not in context.user_data:
        context.user_data["message_stack"] = []
    context.user_data["message_stack"].append(
        {"message": context_message, "text": context_text, "markup": context_markup}
    ) if context.user_data.get('message_stack') else context.user_data["message_stack"]

    match = re.match(r'^connect_(\w+)', command)
    if match:
        button_data = match.group(1)

        status = user_data.agreed_to_terms

        if not status:
            message = await query.edit_message_text(
                text=terms_message, parse_mode=ParseMode.HTML, reply_markup=home_markup
            )
            return message
        
        if button_data == "attach":
            reply_message = """
What's the private key of this wallet? You may also use a 12-word mnemonic phrase.            
            """
            context.user_data['private_reply'] = query.message.message_id
            await query.edit_message_text(text=reply_message, reply_markup=home_markup)
            return PRIVATEKEY



async def reply_wallet_attach(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_id = context.user_data['private_reply']
    text = update.message.text
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    NETWORK = context.user_data.get("network_chain")
    
    LOGGER.info(message_id)
    LOGGER.info(update.message.message_id)
    
    if message_id and update.message.message_id > message_id:
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

async def cancel_attachment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Investment Cancelled.")
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
# BACK BUTTON CALLBACK
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
            if last_message['caption']:
                await query.edit_message_caption(
                    caption=last_message["text"],
                    parse_mode=ParseMode.HTML,
                    reply_markup=last_message["markup"],
                )
            elif not last_message['caption'] and not last_message['markup_reply']:
                await query.edit_message_text(
                    text=last_message["text"],
                    parse_mode=ParseMode.HTML,
                    reply_markup=last_message["markup"],
                )
            elif last_message['markup_reply']:
                await query.edit_message_reply_markup(
                    reply_markup=last_message["markup"],
                )
        else:
            await query.edit_message_text(
                text=last_message["text"], parse_mode=ParseMode.HTML
            )


def create_welcome_message():
    return welcome_message
