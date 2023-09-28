from decimal import Decimal
import os
import pickle
import re
from decouple import config

from web3 import Web3
INFURA_URL = config("INFURA_URL")
web3 = Web3(Web3.HTTPProvider(INFURA_URL))
import django
from logger import LOGGER
from asgiref.sync import sync_to_async

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
    home_message,
    transfer_message,
    welcome_message,
    wallets_message,
    wallets_asset_message,
)
from utils import approve_token, attach_wallet_function, back_variable, check_transaction_status, generate_wallet, get_default_gas_price, get_default_gas_price_gwei, get_token_balance, get_token_full_information, get_token_info, get_wallet_balance, processs_buy_or_sell_only, trasnfer_currency
from utils_data import update_trades_addresses_ammount_limit,update_trades_addresses_profit,update_trades_addresses_loss,update_trades_addresses_limit,change_state_limit,change_state_loss,change_state_profit,load_trades_addresses_once,load_trades_addresses_all,load_trade_address,delete_trades_addresses,load_trades_addresses,load_trade_address_all,save_trade_address,update_copy_trade_addresses_gas,load_copy_trade_address_all,load_copy_trade_all,save_sniper,remove_sniper,load_next_sniper_data,update_snipes,load_previous_sniper_data,load_sniper_data,update_copy_trade_addresses_slippage,update_copy_trade_addresses_ammout,delete_copy_trade_addresses, load_copy_trade_addresses, load_user_data, save_copy_trade_address, save_user_data, update_copy_trade_addresses, update_user_data

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
cback = InlineKeyboardButton("⏪ ", callback_data="copy_left")
cforward = InlineKeyboardButton("⏩ ", callback_data="copy_right")
buy = InlineKeyboardButton("🛠 BUY ", callback_data="presets_buy")
sell = InlineKeyboardButton("🛠 SELL", callback_data="presets_sell")
approve = InlineKeyboardButton("🛠 APPROVE", callback_data="presets_approve")
maxdelta = InlineKeyboardButton("📝  Max Gas Delta", callback_data="config_maxdelta")
deldelta = InlineKeyboardButton("⌫ Remove Delta", callback_data="presets_deldelta")
slippage = InlineKeyboardButton("📝  Slippage", callback_data="config_slippage")
delslippage = InlineKeyboardButton("⌫ Remove Slippage", callback_data="presets_delslippage")
maxgas = InlineKeyboardButton("📝  Max Gas Limit", callback_data="config_maxgas")
delgas = InlineKeyboardButton("⌫ Remove Gas Limit", callback_data="presets_delgas")


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

transfer_eth = InlineKeyboardButton("🎫 ETH", callback_data="transfer_chain_eth")
transfer_bsc = InlineKeyboardButton("🎫 BSC", callback_data="transfer_chain_bsc")
transfer_arb = InlineKeyboardButton("🎫 ARB", callback_data="transfer_chain_arb")
transfer_base = InlineKeyboardButton("🎫 BASE", callback_data="transfer_chain_base")

transfer_chain_keyboard = [
    [home],
    [transfer_eth, transfer_bsc, transfer_arb, transfer_base],
]

transfer_chain_markup = InlineKeyboardMarkup(transfer_chain_keyboard)

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
snipe = InlineKeyboardButton("Snipe", callback_data="start_sniper")
copy_trade = InlineKeyboardButton("Copy Trade", callback_data="start_trade")
quick = InlineKeyboardButton("Buy & Sell", callback_data="buysell_quick")
presets = InlineKeyboardButton("Quick Actions", callback_data="start_presets")
token_transfer = InlineKeyboardButton(
    "Token Transfer", callback_data="start_token_transfer"
)
ads_1 = InlineKeyboardButton("Ads Placement Space", callback_data="ads_placement")
trades = InlineKeyboardButton("Trades", callback_data="start_trades")

start_keyboard = [
    # [about, help],
    [language, quick],
    [wallets_assets, wallets],
    [configuration, copy_trade],
    [snipe, token_transfer],
    [trades],
    [ads_1],
    [terms],
]
start_button_markup = InlineKeyboardMarkup(start_keyboard)
start_keyboard2 = [
    # [about, help],
    [language, quick],
    [wallets_assets, wallets],
    [configuration, copy_trade],
    [snipe, token_transfer],
    [trades],
    [ads_1],
]
start_button_markup2 = InlineKeyboardMarkup(start_keyboard2)


# ------------------------------------------------------------------------------#
# ------------------------------------------------------------------------------#
#                                BUTTONS CALLBACKS                             #
# ------------------------------------------------------------------------------#
# ------------------------------------------------------------------------------#
PRESETNETWORK = 'ETH'
COPYPRESETNETWORK = 'ETH'

NETWORK_CHAINS = ["ETH", "BSC", "ARP", "BASE"]
SELECTED_CHAIN_INDEX = 0

COPYNETWORK_CHAINS = ["ETH", "BSC", "ARP", "BASE"]
COPYSELECTED_CHAIN_INDEX = 0


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
def build_buy_sel_keyboard(buy=True):
    switch_sell = InlineKeyboardButton(f"Buy ↔ Sell", callback_data=f"buy_sell")
    switch_buy = InlineKeyboardButton(f"Sell ↔ Buy", callback_data=f"sell_buy")
    chart = InlineKeyboardButton(f"📉 Chart", callback_data=f"buy_chart", url=f"https://etherscan.io/dex/uniswapv2/{TOKENADDRESS}")
    
    buy001 = InlineKeyboardButton(f"Buy 0.01 ETH", callback_data=f"buy_0_01")
    buy005 = InlineKeyboardButton(f"Buy 0.05 ETH", callback_data=f"buy_0_05")
    buy01 = InlineKeyboardButton(f"Buy 0.1 ETH", callback_data=f"buy_0_1")
    buy02 = InlineKeyboardButton(f"Buy 0.2 ETH", callback_data=f"buy_0_2")
    buy05 = InlineKeyboardButton(f"Buy 0.5 ETH", callback_data=f"buy_0_5")
    buy1 = InlineKeyboardButton(f"Buy 1 ETH", callback_data=f"buy_1")
    buyxeth = InlineKeyboardButton(f"Buy X ETH", callback_data=f"buy_xeth")
    buyyangmax = InlineKeyboardButton(f"Yangbot Max", callback_data=f"buy_yangbot")
    buyxtoken = InlineKeyboardButton(f"Buy X {TOKENNAME}", callback_data=f"buy_{TOKENNAME}")
    
    approve = InlineKeyboardButton(f"Approve", callback_data=f"sell_approve")
    sell = InlineKeyboardButton(f"☣ Sell", callback_data=f"sell_haz")
    sell25 = InlineKeyboardButton(f"Sell 25%", callback_data=f"sell_25")
    sell50 = InlineKeyboardButton(f"Sell 50%", callback_data=f"sell_50")
    sell75 = InlineKeyboardButton(f"Sell 75%", callback_data=f"sell_75")
    sell100 = InlineKeyboardButton(f"Sell 100%", callback_data=f"sell_100")
    sellmax = InlineKeyboardButton(f"Sell Max TX", callback_data=f"sell_maxtx")
    sellxeth = InlineKeyboardButton(f"Sell X ETH", callback_data=f"buy_xeth")
    sellxtoken = InlineKeyboardButton(f"Sell X {TOKENNAME}", callback_data=f"sell_{TOKENNAME}")
    
    preset_keyboard = [
            [home, snipe],
            [chart, switch_buy],
            [approve, sell],
            [sell25, sell50],
            [sell75, sell100],
            [sellmax, sellxeth, sellxtoken]
        ]
    if buy:
        preset_keyboard = [
            [home, snipe],
            [chart, switch_sell],
            [buy001, buy005],
            [buy01, buy02],
            [buy05, buy1],
            [buyxeth, buyyangmax, buyxtoken]
        ]
    
    preset_markup = InlineKeyboardMarkup(preset_keyboard)
    
    return preset_markup  

def build_preset_keyboard():
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

async def build_snipe_comment(sniper, user_data, network='ETH'):
    if sniper:
        token_name, token_symbol, token_decimals, token_lp, balance, contract_add = await get_token_info(sniper.contract_address, network, user_data)
        global TOKENNAME
        TOKENNAME = token_name
        message = f"""
🪙 {token_name} ({token_symbol}) ⚡️ ethereum
CA: <pre> {TOKENNAME} </pre>
LP(UNI-V3): <pre> {token_lp} </pre>
V3 Pooluser_data

💵 Wallet | <pre>Main</pre>
⛽️ Gas Price | <pre>Set in Configuration</pre>    
        """
    else:
        message = "⚠️ No tokens to snipe"
    return message

def build_buy_and_sell_message():
    caption = f"""
                <strong>🪙 {TOKENNAME} ⚡️ ETHEREUM</strong>
CA: {TOKENADDRESS}

🧢 Market Cap | ${round(TOKENMARKETCAP, 8)}
📈 Price | ${TOKENPRICE}

👨‍💻 Owner: {TOKENOWNER if TOKENOWNER != '0x0000000000000000000000000000000000000000' else 'OWNER RENOUNCED'}
🔒 LP: {f'{len(TOKENLPLOCKED)} LP' if len(TOKENLPLOCKED) != 0 else "NO LP LOCKED"}!

💰 Balance | {TOKENBALANCE} {TOKENSYMBOL}
🔻 Decimals | {TOKENDECIMAL}

⛽️ Gas: {GASGWEI} GWEI Ξ ${GASETHER}

🕰 Age: {round(TOKENAGE / 86400 / 365)} Days
-------------------------------------------
⚠️ Market cap includes locked tokens, excluding burned
-------------------------------------------
    """
    return caption
@sync_to_async
def build_trades_caption(matched_trade):
    for i in matched_trade:
           caption = f"""
⚡️ ethereum
Name: {i.token_name.title()}
Address: {i.token_address.title()}
🤷‍♀️ Settings
Limit: {i.limit}
Limit_amount: {i.ammount_limit}
Loss: {i.stop_loss}
Profit: {i.profit}
                """
    return caption
 
@sync_to_async
def build_copy_name_caption(matched_trade):
    caption = f"""
⚡️ ethereum
Name: {matched_trade.name.title()}
Target Wallet: {matched_trade.contract_address}

🤷‍♀️ Auto Buy
Multi: {'❌ Disabled - Wallet Disabled ⚠️' if not matched_trade.multi else '✅ Enabled'}
Auto Buy: {'❌ Disabled - Wallet Disabled ⚠️' if not matched_trade.auto_buy else '✅ Enabled'}
Amount: {'❌ Disabled - Wallet Disabled ⚠️' if not matched_trade.amount > 0.000000 else matched_trade.amount}
Slippage: {'Default (100%)' if matched_trade.slippage >= 100.000000 else matched_trade.slippage} 
Smart Slippage: {'❌ Disabled - Wallet Disabled ⚠️' if not matched_trade.smart_slippage else '✅ Enabled'}
Gas Delta: Default (33.191 GWEI) + Delta ({matched_trade.gas_delta} GWEI)
Max Buy Tax: {'❌ Disabled - Wallet Disabled ⚠️' if not matched_trade.max_buy_tax > 0.00000000 else matched_trade.max_buy_tax}
Max Sell Tax: {'❌ Disabled - Wallet Disabled ⚠️' if not matched_trade.max_sell_tax > 0.00000000 else matched_trade.max_sell_tax}

🤷‍♂️ Sell
Auto Sell: Global (❌ Disabled)
Auto Sell (high): Default (+100%)
Sell Amount (high): Default (100%)
Auto Sell (low): Default(-50%)
Sell Amount (low): Default (100%)            
            """
    return caption
@sync_to_async
def build_trade_keyboard(matched_trade):
    trades_keyboard = []
    for data in matched_trade:
            on1 = InlineKeyboardButton(f"{'🔴 OFF' if not data.check_limit else '🔵 ON'}", callback_data=f"trades_{data.token_address.replace(' ', '_')}_{'off' if not data.check_limit else 'on'}_limit")
            on2 = InlineKeyboardButton(f"{'🔴 OFF' if not data.check_profit else '🔵 ON'}", callback_data=f"trades_{data.token_address.replace(' ', '_')}_{'off' if not data.check_profit else 'on'}_profit")
            on3 = InlineKeyboardButton(f"{'🔴 OFF' if not data.check_stop_loss else '🔵 ON'}", callback_data=f"trades_{data.token_address.replace(' ', '_')}_{'off' if not data.check_stop_loss else 'on'}_loss")
            buyProfit = InlineKeyboardButton(f"Catch Profit", callback_data=f"ask_Profit")
            buyLoss = InlineKeyboardButton(f"Catch Loss", callback_data=f"ask_Loss")
            buyLimit = InlineKeyboardButton(f"Catch Limit", callback_data=f"ask_Limit")
            buyammountlimit= InlineKeyboardButton(f"Buy Amount", callback_data=f"ask_buyammount")
            trades_keyboard = [
                [buyProfit,on2],
                [buyLoss,on3],
                [buyLimit,buyammountlimit,on1],
                [home]
            ]

    
    trades_markup = InlineKeyboardMarkup(trades_keyboard)
    
    return trades_markup
@sync_to_async
def build_copy_name_keyboard(matched_trade):
    multi = InlineKeyboardButton(f"{'❌' if not matched_trade.multi else '✅'} Multi", callback_data=f"copyname_multi")
    copyautobuy = InlineKeyboardButton(f"{'❌' if not matched_trade.auto_buy else '✅'} Auto Buy", callback_data=f"copyname_autobuy")
    copysmartslippage = InlineKeyboardButton(f"{'❌' if not matched_trade.smart_slippage else '✅'} Smart Slippage", callback_data=f"copyname_smartslippage")
    copybuyamount = InlineKeyboardButton(f"📝 Buy Amount", callback_data=f"ask_buyamount")
    copyslippage = InlineKeyboardButton(f"📝 Slippage", callback_data=f"ask_slippage")
    delcopyslippage = InlineKeyboardButton(f"⌫ Slippage", callback_data=f"copyname_delslippage")
    copygasdelta = InlineKeyboardButton(f"📝 Gas Delta", callback_data=f"ask_gasdelta")
    delcopygasdelta = InlineKeyboardButton(f"⌫ Gas Delta", callback_data=f"copyname_delgasdelta")
    copysell = InlineKeyboardButton(f"{'❌' if not matched_trade.copy_sell else '✅'} Copy Sell", callback_data=f"copyname_copysell")
    copysellhi = InlineKeyboardButton(f"📝 Sell-Hi", callback_data=f"copyname_sellhi")
    copyselllo = InlineKeyboardButton(f"📝 Sell-Lo", callback_data=f"copyname_selllo")
    copysellhiamount = InlineKeyboardButton(f"📝 Sell-Hi Amount", callback_data=f"copyname_sellhiamount")
    copysellloamount = InlineKeyboardButton(f"📝 Sell-Lo Amount", callback_data=f"copyname_sellloamount")
    copymaxbuytax = InlineKeyboardButton(f"📝 Max Buy Tax", callback_data=f"copyname_buytax")
    copymaxselltax = InlineKeyboardButton(f"📝 Max Sell Tax", callback_data=f"copyname_selltax")
    delcopysellhi = InlineKeyboardButton(f"⌫ Sell-Hi", callback_data=f"copyname_delsellhi")
    delcopyselllo = InlineKeyboardButton(f"⌫ Sell-Lo", callback_data=f"copyname_delselllo")
    delcopysellhiamount = InlineKeyboardButton(f"⌫ Sell-Hi Amount", callback_data=f"copyname_delsellhiamoun")
    delcopysellloamount = InlineKeyboardButton(f"⌫ Sell-Lo Amount", callback_data=f"copyname_delsellloamount")
    delcopymaxbuytax = InlineKeyboardButton(f"⌫ Max Buy Tax", callback_data=f"copyname_delbuytax")
    delcopymaxselltax = InlineKeyboardButton(f"⌫ Max Sell Tax", callback_data=f"copyname_delselltax")
    copyname_keyboard = [
        [home, back],
        [copybuyamount],
        [copyslippage, copygasdelta],
    ] 
    copyname_markup = InlineKeyboardMarkup(copyname_keyboard)
    
    return copyname_markup 

@sync_to_async
def build_snipping_keyboard(sniper, liq=True, aut=False, met=False):
    snipebutton = InlineKeyboardButton("👁 Snipe", callback_data=f"conversation_sniper_snipe")
    sback = InlineKeyboardButton("⏪ ", callback_data="snipper_left")
    sforward = InlineKeyboardButton("⏩ ", callback_data="snipper_right")
    LOGGER.info(f"Sniper Keyboard Rebuiding: {sniper}")
    if sniper != None:
        multi = InlineKeyboardButton(f"{'❌' if not sniper.multi else '✅'} Multi", callback_data=f"sniper_multi")
        deletetoken = InlineKeyboardButton("❌ Delete", callback_data=f"sniper_{sniper.id}")
        token_name = InlineKeyboardButton(f"{TOKENNAME}", callback_data="snipper_right")
        snipeslippage = InlineKeyboardButton(f"📝 Slippage", callback_data=f"snipper_conversation_slippage")
        delsnipeslippage = InlineKeyboardButton(f"⌫ Slippage", callback_data=f"sniper_delslippage")
        gas_delta = InlineKeyboardButton(f"📝 Gas Delta", callback_data=f"conversation_sniper_gasdelta")
        liquidity = InlineKeyboardButton(f"{'❌' if not sniper.liquidity else '✅'} Liquidity", callback_data=f"sniper_liquidity")
        auto = InlineKeyboardButton(f"{'❌' if not sniper.auto else '✅'} Auto", callback_data=f"sniper_auto")
        method = InlineKeyboardButton(f"{'❌' if not sniper.method else '✅'} Method", callback_data=f"sniper_method")
        eth_amount = InlineKeyboardButton(f"{round(sniper.eth, 6)} ETH", callback_data=f"conversation_sniper_eth")
        token_amount = InlineKeyboardButton(f"{round(sniper.token, 2)} {TOKENNAME.upper()}", callback_data=f"conversation_sniper_token")
        snipeliquidity = InlineKeyboardButton(f"{'❌' if not sniper.liquidity else '✅'} Snipe Liquidity", callback_data=f"sniper_snipeliquidity")
        snipemethod = InlineKeyboardButton(f"{'❌' if not sniper.method else '✅'} Snipe Method", callback_data=f"sniper_snipemethod")
        snipeauto = InlineKeyboardButton(f"{'❌' if not sniper.auto else '✅'} Sell-Lo Amount", callback_data=f"sniper_snipeauto")
        blockdelay = InlineKeyboardButton(f"Block Delay | {round(sniper.block_delay, 1)}", callback_data=f"conversation_sniper_blockdelay")
    
        # liq = True if liq == True or sniper.liquidity else False
        # aut = True if aut == True or sniper.auto else False
        # met = True if met == True or sniper.method else False
    

        if liq: # and not sniper.auto and not sniper.method:
            copyname_keyboard = [
                [home, deletetoken],
                [snipebutton],
                [sback, token_name, sforward],
                [multi, gas_delta],
                [liquidity, method, auto],
                [snipeliquidity, blockdelay],
                [eth_amount, token_amount],
                [snipeslippage, delsnipeslippage],
            ] 
            copyname_markup = InlineKeyboardMarkup(copyname_keyboard)
        
            return copyname_markup 
        elif aut: # and not sniper.liquidity and not sniper.method:
            copyname_keyboard = [
                [home, deletetoken],
                [snipebutton],
                [sback, token_name, sforward],
                [multi, gas_delta],
                [liquidity, method, auto],
                [snipeauto],
                [eth_amount, token_amount],
                [snipeslippage, delsnipeslippage],
            ] 
            copyname_markup = InlineKeyboardMarkup(copyname_keyboard)
        
            return copyname_markup 
        elif met: # and not sniper.liquidity and not sniper.auto:
            copyname_keyboard = [
                [home, deletetoken],
                [snipebutton],
                [sback, token_name, sforward],
                [multi, gas_delta],
                [liquidity, method, auto],
                [snipemethod, blockdelay],
                [eth_amount, token_amount],
                [snipeslippage, delsnipeslippage],
            ] 
            copyname_markup = InlineKeyboardMarkup(copyname_keyboard)
        
            return copyname_markup 
    else:
        copyname_keyboard = [
            [home, snipebutton],
        ] 
        
        copyname_markup = InlineKeyboardMarkup(copyname_keyboard)
        
        return copyname_markup 

@sync_to_async
def build_trades_keyboard(trades):
    COPYPRESETNETWORK = COPYNETWORK_CHAINS[COPYSELECTED_CHAIN_INDEX]
    chain = InlineKeyboardButton(f"🛠 {COPYPRESETNETWORK}", callback_data=f"copy_{COPYPRESETNETWORK}")
    target_wallet = InlineKeyboardButton(f"Contract Address", callback_data=f"asktrade_address")
    tback = InlineKeyboardButton("⏪ ", callback_data="trades_left")
    tforward = InlineKeyboardButton("⏩ ", callback_data="trades_right")
    copy_trade_keyboard = [
        [home],
        [tback, chain, tforward],
        [target_wallet]
    ] 
    
    # # Create buttons for each trade in the trades list
    if trades != None:
        for tr in trades:
            print(tr.token_name)
            buttons = [
                InlineKeyboardButton(f"{tr.token_name.lower()}", callback_data=f"trades_{tr.token_address.replace(' ', '_')}"),
                InlineKeyboardButton("❌", callback_data=f"trades_{tr.token_address.replace(' ', '_')}_delete"),

            ]
            copy_trade_keyboard.append(buttons)
    
        
    copy_trade_markup = InlineKeyboardMarkup(copy_trade_keyboard)
    
    return copy_trade_markup   
    
@sync_to_async
def build_copy_trade_keyboard(trades):
    COPYPRESETNETWORK = COPYNETWORK_CHAINS[COPYSELECTED_CHAIN_INDEX]
    chain = InlineKeyboardButton(f"🛠 {COPYPRESETNETWORK}", callback_data=f"copy_{COPYPRESETNETWORK}")
    target_wallet = InlineKeyboardButton(f"Target Wallet or Contract Address", callback_data=f"trade_address")
    copy_trade_keyboard = [
        [home],
        [cback, chain, cforward],
        [target_wallet]
    ] 
    
    # Create buttons for each trade in the trades list
    if trades != None:
        for tr in trades:
            
            buttons = [
                InlineKeyboardButton(f"{tr.name.lower()}", callback_data=f"copy_{tr.name.replace(' ', '_')}"),
                InlineKeyboardButton(f"Rename", callback_data=f"rename_{tr.id}"),
                # InlineKeyboardButton(f"{'🔴 OFF' if not tr.on else '🔵 ON'}", callback_data=f"copy_{tr.name.replace(' ', '_')}_{'off' if not tr.on else 'on'}"),
                InlineKeyboardButton("❌", callback_data=f"copy_{tr.name.replace(' ', '_')}_delete")
            ]
            copy_trade_keyboard.append(buttons)
    
        
    copy_trade_markup = InlineKeyboardMarkup(copy_trade_keyboard)
    
    return copy_trade_markup  

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

PASTECONTRACTADDRESS = range(1)    
async def start_button_callback(update: Update, context: CallbackContext):
    global CAPTION, TOKENADDRESS, TOKENSYMBOL, TOKENDECIMAL, GASGWEI, GASETHER, TOKENNAME, TOKENMARKETCAP, TOKENPRICE, TOKENOWNER, TOKENLPLOCKED, TOKENBALANCE, TOKENAGE
    query = update.callback_query
    await query.answer()
    command = query.data
    user_id = str(query.from_user.id)
    context.user_data.clear()
    context.user_data["last_message_id"] = query.message.message_id
    gas_price = await get_default_gas_price_gwei()
    
    user_data = await load_user_data(user_id)

    match = re.match(r"^start_(\w+)", command)
    if match:
        button_data = match.group(1)

        LOGGER.info(f"Button Data: {button_data}")
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
        elif button_data == "trade":
            context.user_data['copy_id'] = query.message.message_id
            copy_message = "Add or remove wallets from which you'd like to copy trades!"
            trades = await load_copy_trade_addresses(user_id, COPYPRESETNETWORK)
            copy_trade_markup = await build_copy_trade_keyboard(trades)
            message = await query.edit_message_caption(
                caption=copy_message, 
                parse_mode=ParseMode.HTML, 
                reply_markup=copy_trade_markup
            )
            context.user_data['selected_chain'] = 'ETH'
            context.user_data['last_message'] = copy_message
            context.user_data['last_markup'] = copy_trade_markup
            context.user_data["last_message_id"] = message.message_id
            back_variable(message, context, copy_message, copy_trade_markup, True, False)
        elif button_data == "trades":
            context.user_data['copy_id'] = query.message.message_id
            copy_message = "Add or set up token trade settings!"
            trades = await load_trades_addresses(user_id, COPYPRESETNETWORK)
            copy_trade_markup = await build_trades_keyboard(trades)
            message = await query.edit_message_caption(
                caption=copy_message, 
                parse_mode=ParseMode.HTML, 
                reply_markup=copy_trade_markup
            )
            print("tao")
            print(NETWORK_CHAINS[SELECTED_CHAIN_INDEX])
            context.user_data['selected_chain'] = NETWORK_CHAINS[SELECTED_CHAIN_INDEX]
        elif button_data == "sniper":
            context.user_data['caption_id'] = query.message.message_id
            sniper = await load_sniper_data(user_data)
            copy_message = await build_snipe_comment(sniper, user_data)
            copy_trade_markup = await build_snipping_keyboard(sniper)
                
              
            if CAPTION:
                message = await query.edit_message_caption(
                    caption=copy_message, 
                    parse_mode=ParseMode.HTML, 
                    reply_markup=copy_trade_markup
                )
            else:
                message = await query.message.reply_text(
                    copy_message,
                    parse_mode=ParseMode.HTML, 
                    reply_markup=copy_trade_markup
                )  
            CAPTION = True
            context.user_data['selected_chain'] = 'ETH'
            context.user_data['last_message'] = copy_message
            context.user_data['last_markup'] = copy_trade_markup
            context.user_data["last_message_id"] = message.message_id
            back_variable(message, context, copy_message, copy_trade_markup, True, False)
        elif button_data == "token_transfer":
            message = await query.edit_message_caption(
                caption=transfer_message, 
                parse_mode=ParseMode.HTML, 
                reply_markup=transfer_chain_markup
            )
            back_variable(message, context, transfer_message, transfer_chain_markup, True, False)
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
            context.user_data['caption_id'] = query.message.message_id
            
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

async def start_quick_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    command = query.data
    context.user_data["last_message_id"] = query.message.message_id
    match = re.match(r"^buysell_(\w+)", command)
    if match:
        button_data = match.group(1)

        LOGGER.info(f"Button Data: {button_data}")
        # Fetch the bot's profile photo
        bot = context.bot
        bot_profile_photos = await bot.get_user_profile_photos(bot.id, limit=1)
        bot_profile_photo = (
            bot_profile_photos.photos[0][0] if bot_profile_photos else None
        )

        if button_data == "quick":
            caption = "What is the token contract address to buy or sell?"           
            await query.message.reply_text(
                caption,
                parse_mode=ParseMode.HTML,
            )
            context.user_data['caption_id'] = query.message.message_id
            return PASTECONTRACTADDRESS
    else:
        await query.message.reply_text("I don't understand that command.")





# ------------------------------------------------------------------------------
# BUYSELL BUTTON CALLBACK
# ------------------------------------------------------------------------------
async def reply_buysell_address(update: Update, context: CallbackContext):
    global CAPTION, TOKENADDRESS, TOKENSYMBOL, TOKENDECIMAL, GASGWEI, GASETHER, TOKENNAME, TOKENMARKETCAP, TOKENPRICE, TOKENOWNER, TOKENLPLOCKED, TOKENBALANCE, TOKENAGE
    text = update.message.text.strip()
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    user_data = await load_user_data(user_id)    
    token_balance, symbol, decimal, eth_balance, current_exchange_rate, token_metadata, token_liquidity_positions, owner_address, token_age_seconds, market_cap = await get_token_full_information(text, user_data)
    
    CAPTION = False
    TOKENADDRESS = text
    TOKENSYMBOL = symbol
    TOKENDECIMAL = int(decimal)
    GASGWEI = await get_default_gas_price_gwei()
    GASETHER = await get_default_gas_price()
    TOKENNAME = token_metadata
    TOKENBALANCE = token_balance
    TOKENOWNER = owner_address
    TOKENPRICE = current_exchange_rate
    TOKENAGE = token_age_seconds
    TOKENMARKETCAP = market_cap
    TOKENLPLOCKED = token_liquidity_positions
    
    caption = build_buy_and_sell_message()
    markup = build_buy_sel_keyboard()
    
    await context.bot.send_message(chat_id=chat_id, text=caption, parse_mode=ParseMode.HTML, reply_markup=markup)

async def buy_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    command = query.data
    user_id = str(query.from_user.id)
    chat_id=query.message.chat_id
    context.user_data.clear()
    context.user_data["last_message_id"] = query.message.message_id
    # gas_price = await get_default_gas_price_gwei()
    

    match = re.match(r"^buy_(\w+)", command)
    if match:
        button_data = match.group(1)

        LOGGER.info(f"Buy Button Data: {button_data}")
        # Fetch the bot's profile photo
        bot = context.bot
        bot_profile_photos = await bot.get_user_profile_photos(bot.id, limit=1)
        bot_profile_photo = (
            bot_profile_photos.photos[0][0] if bot_profile_photos else None
        )

        if button_data == "sell":
            markup = build_buy_sel_keyboard(buy=False)
            await query.edit_message_reply_markup(
                reply_markup=markup,
            )
        elif button_data == "0_01":
            user_data = await load_user_data(user_id)
            eth_amount = float(button_data.replace('_', '.'))
            result = await processs_buy_or_sell_only(eth_amount, user_data, TOKENADDRESS, TOKENDECIMAL, token_name=TOKENNAME, buy=True)
            await context.bot.send_message(chat_id=chat_id, text=result)
        elif button_data == "0_05":
            user_data = await load_user_data(user_id)
            eth_amount = float(button_data.replace('_', '.'))
            result = await processs_buy_or_sell_only(eth_amount, user_data, TOKENADDRESS, TOKENDECIMAL, token_name=TOKENNAME, buy=True)
            await context.bot.send_message(chat_id=chat_id, text=result)
        elif button_data == "0_1":
            user_data = await load_user_data(user_id)
            eth_amount = float(button_data.replace('_', '.'))
            result = await processs_buy_or_sell_only(eth_amount, user_data, TOKENADDRESS, TOKENDECIMAL, token_name=TOKENNAME, buy=True)
            await context.bot.send_message(chat_id=chat_id, text=result)
        elif button_data == "0_2":
            user_data = await load_user_data(user_id)
            eth_amount = float(button_data.replace('_', '.'))
            result = await processs_buy_or_sell_only(eth_amount, user_data, TOKENADDRESS, TOKENDECIMAL, token_name=TOKENNAME, buy=True)
            await context.bot.send_message(chat_id=chat_id, text=result)
        elif button_data == "0_5":
            user_data = await load_user_data(user_id)
            eth_amount = float(button_data.replace('_', '.'))
            result = await processs_buy_or_sell_only(eth_amount, user_data, TOKENADDRESS, TOKENDECIMAL, token_name=TOKENNAME, buy=True)
            await context.bot.send_message(chat_id=chat_id, text=result)
        elif button_data == "1":
            user_data = await load_user_data(user_id)
            eth_amount = float(button_data)
            result = await processs_buy_or_sell_only(eth_amount, user_data, TOKENADDRESS, TOKENDECIMAL, token_name=TOKENNAME, buy=True)
            await context.bot.send_message(chat_id=chat_id, text=result)        
    else:
        await query.message.reply_text("I don't understand that command.")

async def sell_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    command = query.data
    user_id = str(query.from_user.id)
    chat_id=query.message.chat_id
    context.user_data.clear()
    context.user_data["last_message_id"] = query.message.message_id
    # gas_price = await get_default_gas_price_gwei()
    
    # user_data = await load_user_data(user_id)

    match = re.match(r"^sell_(\w+)", command)
    if match:
        button_data = match.group(1)

        LOGGER.info(f"Button Data: {button_data}")
        # Fetch the bot's profile photo
        bot = context.bot
        bot_profile_photos = await bot.get_user_profile_photos(bot.id, limit=1)
        bot_profile_photo = (
            bot_profile_photos.photos[0][0] if bot_profile_photos else None
        )

        if button_data == "buy":
            markup = build_buy_sel_keyboard(buy=True)
            await query.edit_message_reply_markup(
                reply_markup=markup,
            )
            context.user_data['caption_id'] = query.message.message_id
        elif button_data == "approve":
            user_data = await load_user_data(user_id)
            result = await approve_token(TOKENADDRESS, user_data, TOKENBALANCE, TOKENDECIMAL)
            await context.bot.send_message(chat_id=chat_id, text=result)
        elif button_data == "haz":
            user_data = await load_user_data(user_id)
            result = await processs_buy_or_sell_only(eth_amount, user_data, TOKENADDRESS, TOKENDECIMAL, token_name=TOKENNAME, buy=False)
            await context.bot.send_message(chat_id=chat_id, text=result)
        elif button_data == "25":
            user_data = await load_user_data(user_id)
            eth_amount = int(button_data) / 100
            LOGGER.info(f"Percentage: {eth_amount}")
            result = await processs_buy_or_sell_only(eth_amount, user_data, TOKENADDRESS, TOKENDECIMAL, token_name=TOKENNAME, balance=TOKENBALANCE, buy=False)
            await context.bot.send_message(chat_id=chat_id, text=result)
        elif button_data == "50":
            user_data = await load_user_data(user_id)
            eth_amount = int(button_data) / 100
            result = await processs_buy_or_sell_only(eth_amount, user_data, TOKENADDRESS, TOKENDECIMAL, token_name=TOKENNAME, balance=TOKENBALANCE, buy=False)
            await context.bot.send_message(chat_id=chat_id, text=result)
        elif button_data == "75":
            user_data = await load_user_data(user_id)
            eth_amount = int(button_data) / 100
            result = await processs_buy_or_sell_only(eth_amount, user_data, TOKENADDRESS, TOKENDECIMAL, token_name=TOKENNAME, balance=TOKENBALANCE, buy=False)
            await context.bot.send_message(chat_id=chat_id, text=result)
        elif button_data == "100":
            user_data = await load_user_data(user_id)
            eth_amount = int(button_data) / 100
            result = await processs_buy_or_sell_only(eth_amount, user_data, TOKENADDRESS, TOKENDECIMAL, token_name=TOKENNAME, balance=TOKENBALANCE, buy=False)
            await context.bot.send_message(chat_id=chat_id, text=result)        
    else:
        await query.message.reply_text("I don't understand that command.")


    
async def cancel_buysell(update: Update, context: CallbackContext):
    await update.message.reply_text("Buy Sell Cancelled.")
    return ConversationHandler.END



# ------------------------------------------------------------------------------
# SNIPER BUTTON CALLBACK
# ------------------------------------------------------------------------------
SNIPERADDRESS, EDITGASDELTA, EDITETHAMOUNT, EDITTOKENAMOUNT, EDITSLIPPAGE, EDITBLOCKDELAY = range(6)
async def delete_conversation_sniper_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    command = query.data
    user_id = str(query.from_user.id)
    chat_id = query.message.chat_id
    caption_id = context.user_data['caption_id']
    user_data = await load_user_data(user_id)    
    
    sniper = await load_sniper_data(user_data)
    context.user_data['sniper'] = sniper
    
    match = re.match(r"^conversation_sniper_(\w+)", command)
    if match:
        button_data = match.group(1)
        
        LOGGER.info(button_data)
        if button_data == "snipe":
            message = await query.message.reply_text("what is the token address to snipe?")
            context.user_data['question_message_id'] = message.message_id
            return SNIPERADDRESS        
        elif button_data == "gasdelta":
            message = await query.message.reply_text(f"Reply to this message with your desired gas price (in GWEI). 1 GWEI = 10 ^ 9 wei. Minimum is {user_data.max_gas_price}!")
            context.user_data['question_message_id'] = message.message_id
            return EDITGASDELTA
        elif button_data == "blockdelay":
            message = await query.message.reply_text(f"Reply to this message with your desired block delay.")
            context.user_data['question_message_id'] = message.message_id
            return EDITBLOCKDELAY
        elif button_data == "eth":
            message = await query.message.reply_text("Reply to this message with your desired buy amount (in ETH) or percentage when liquidity is added.")
            context.user_data['question_message_id'] = message.message_id
            return EDITETHAMOUNT
        elif button_data == "token":
            message = await query.message.reply_text(f"Reply to this message with your desired buy amount (in {TOKENNAME.upper()}) when liquidity is added.")
            context.user_data['question_message_id'] = message.message_id
            return EDITTOKENAMOUNT
        elif button_data == "slippage":
            message = await query.message.reply_text("Reply to this message with your desired slippage percentage.")
            context.user_data['question_message_id'] = message.message_id
            return EDITSLIPPAGE
            
async def delete_sniper_callback(update: Update, context: CallbackContext):   
    query = update.callback_query
    await query.answer()
    command = query.data
    user_id = str(query.from_user.id)
    chat_id = query.message.chat_id
    caption_id = context.user_data['caption_id']
    user_data = await load_user_data(user_id)    
    
    sniper = await load_sniper_data(user_data)
    context.user_data['sniper'] = sniper
    
    
    match = re.match(r"^sniper_(\w+)", command)
    if match:
        button_data = match.group(1)
        
        LOGGER.info(button_data)
        
        if button_data == "right":
            sniper = await load_next_sniper_data(sniper.id)
            context.user_data['sniper'] = sniper
            caption = await build_snipe_comment(sniper, user_data)
            markup = await build_snipping_keyboard(sniper)
            
            message = await query.edit_message_caption(caption=caption, parse_mode=ParseMode.HTML, reply_markup=markup)
            context.user_data['message_id'] = message.message_id
            
        elif button_data == "left":
            sniper = await load_previous_sniper_data(sniper.id)
            context.user_data['sniper'] = sniper
            caption = await build_snipe_comment(sniper, user_data)
            markup = await build_snipping_keyboard(sniper)
            
            message = await query.edit_message_caption(caption=caption, parse_mode=ParseMode.HTML, reply_markup=markup)
            context.user_data['message_id'] = message.message_id
            
        elif button_data == "multi":
            await update_snipes(user_id, sniper.contract_address, {'multi': True if not sniper.multi else False, 'auto': False, 'liquidity': False, 'method': False})
            sniper = await load_sniper_data(user_data)
            markup = await build_snipping_keyboard(sniper)
            
            await query.edit_message_reply_markup(reply_markup=markup)

        elif button_data == "snipeliquidity":
            await update_snipes(user_id, sniper.contract_address, {'multi': False, 'auto': False, 'liquidity': True if not sniper.liquidity else False, 'method': False})
            sniper = await load_sniper_data(user_data)
            markup = await build_snipping_keyboard(sniper)
            
            await query.edit_message_reply_markup(reply_markup=markup)

        elif button_data == "snipeauto":
            await update_snipes(user_id, sniper.contract_address, {'multi': False, 'auto': True if not sniper.auto else False, 'liquidity': False, 'method': False})
            sniper = await load_sniper_data(user_data)
            markup = await build_snipping_keyboard(sniper, liq=False, aut=True)
            
            await query.edit_message_reply_markup(reply_markup=markup)

        elif button_data == "snipemethod":
            await update_snipes(user_id, sniper.contract_address, {'multi': False, 'auto': False, 'liquidity': False, 'method': True if not sniper.method else False})
            sniper = await load_sniper_data(user_data)
            markup = await build_snipping_keyboard(sniper, liq=False, met=True)
            
            await query.edit_message_reply_markup(reply_markup=markup)      
            
        elif button_data == "auto":
            markup = await build_snipping_keyboard(sniper, liq=False, aut=True)
            await query.edit_message_reply_markup(reply_markup=markup)
            
        elif button_data == "liquidity":
            markup = await build_snipping_keyboard(sniper, liq=True)
            await query.edit_message_reply_markup(reply_markup=markup)
            
        elif button_data == "method":
            markup = await build_snipping_keyboard(sniper, liq=False, met=True)
            await query.edit_message_reply_markup(reply_markup=markup)
            
        elif button_data == "delslippage":
            await update_user_data(user_id, {'slippage': 0.00})
            
        elif int(button_data) == sniper.id:
            context.user_data['sniper'] = sniper
            sniper = await remove_sniper(user_data, sniper.id)
            context.user_data['sniper'] = sniper
            caption = await build_snipe_comment(sniper, user_data)
            markup = await build_snipping_keyboard(sniper)
            
            message = await query.edit_message_caption(caption=caption, parse_mode=ParseMode.HTML, reply_markup=markup)
            context.user_data['message_id'] = message.message_id
        
async def add_sniper_address(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    user_data = await load_user_data(user_id)    
    
    sniper = await save_sniper(user_id, text, context.user_data['selected_chain'])
    # Update the keyboard markup with the new selected chain
    caption = await build_snipe_comment(sniper, user_data)
    new_markup = await build_snipping_keyboard(sniper)
    
    message_id_to_edit = context.user_data.get('caption_id')

    await context.bot.edit_message_caption(chat_id=chat_id, message_id=message_id_to_edit, caption=caption, reply_markup=new_markup, parse_mode=ParseMode.HTML)
    return ConversationHandler.END


async def sniper_gas_delta_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = Decimal(update.message.text.strip())
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    user_data = await load_user_data(user_id)    
    question_message_id = context.user_data.get('question_message_id')
    
    sniper = await load_sniper_data(user_data)
    
    await update_user_data(user_id, {'max_delta': text})
    
    user_data = await load_user_data(user_id)    
    sniper = await load_sniper_data(user_data)
    
    # Update the keyboard markup with the new selected chain
    new_markup = await build_snipping_keyboard(sniper)
    
    message_id_to_edit = context.user_data.get('caption_id')

    await context.bot.delete_message(chat_id=chat_id, message_id=question_message_id, parse_mode=ParseMode.HTML)
    # await context.bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id_to_edit, reply_markup=new_markup)
    return ConversationHandler.END

async def sniper_blockdelay_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = Decimal(update.message.text.strip())
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    user_data = await load_user_data(user_id)    
    question_message_id = context.user_data.get('question_message_id')
    sniper = await load_sniper_data(user_data)

    await update_snipes(user_id, sniper.contract_address, {'block_delay': text})
    
    user_data = await load_user_data(user_id)    
    sniper = await load_sniper_data(user_data)
    
    # Update the keyboard markup with the new selected chain
    new_markup = await build_snipping_keyboard(sniper)
    
    message_id_to_edit = context.user_data.get('caption_id')
    await context.bot.delete_message(chat_id=chat_id, message_id=question_message_id)
    await context.bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id_to_edit, reply_markup=new_markup)
    return ConversationHandler.END

async def sniper_slippage_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = Decimal(update.message.text.strip())
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    user_data = await load_user_data(user_id)    
    question_message_id = context.user_data.get('question_message_id')
    sniper = await load_sniper_data(user_data)

    await update_user_data(user_id, {'slippage': text})
    
    user_data = await load_user_data(user_id)    
    sniper = await load_sniper_data(user_data)
    
    # Update the keyboard markup with the new selected chain
    new_markup = await build_snipping_keyboard(sniper)
    
    message_id_to_edit = context.user_data.get('caption_id')

    await context.bot.delete_message(chat_id=chat_id, message_id=question_message_id)
    # await context.bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id_to_edit, reply_markup=new_markup)
    return ConversationHandler.END

async def sniper_token_amount_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = Decimal(update.message.text.strip())
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    user_data = await load_user_data(user_id)    
    question_message_id = context.user_data.get('question_message_id')
    sniper = await load_sniper_data(user_data)

    await update_snipes(user_id, sniper.contract_address, {'token': text})
    
    user_data = await load_user_data(user_id)    
    sniper = await load_sniper_data(user_data)
    
    # Update the keyboard markup with the new selected chain
    new_markup = await build_snipping_keyboard(sniper)
    
    message_id_to_edit = context.user_data.get('caption_id')

    await context.bot.delete_message(chat_id=chat_id, message_id=question_message_id)
    await context.bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id_to_edit, reply_markup=new_markup)
    return ConversationHandler.END

async def sniper_eth_amount_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = Decimal(update.message.text.strip())
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    user_data = await load_user_data(user_id)    
    question_message_id = context.user_data.get('question_message_id')
    sniper = await load_sniper_data(user_data)

    await update_snipes(user_id, sniper.contract_address, {'eth': text})
    
    user_data = await load_user_data(user_id)    
    sniper = await load_sniper_data(user_data)
    
    # Update the keyboard markup with the new selected chain
    new_markup = await build_snipping_keyboard(sniper)
    
    message_id_to_edit = context.user_data.get('caption_id')
    await context.bot.delete_message(chat_id=chat_id, message_id=question_message_id)
    await context.bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id_to_edit, reply_markup=new_markup)
    return ConversationHandler.END
    
async def cancel_sniper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop('sniper', None)
    await update.message.reply_text("Sniper Cancelled.")
    return ConversationHandler.END










# ------------------------------------------------------------------------------
# COPY TRADE BUTTON CALLBACK
# ------------------------------------------------------------------------------
TRADESTOKEN = range(1)
TRADEWALLETNAME, TARGETWALLET = range(2)
RENAME = range(1)
CHATCHIT = range(1)
CHATSLIP = range(1)
CHATLIMIT = range(1)
CHATAMMOUNT = range(1)
CHATLOSS= range(1)
CHATPROFIT = range(1)
CHATGAS = range(1)
async def trades_next_and_back_callback(update: Update, context: CallbackContext):
    global COPYSELECTED_CHAIN_INDEX
    query = update.callback_query
    user_id = str(query.from_user.id)
    await query.answer()
    command = query.data
    print("hdsihaihfiahsifhi")
    print(command)

    match = re.match(r"^trades_(\w+)", command)
    if match:
        button_data = match.group(1)
        print(button_data)
        parts = button_data.split("_")
        result = parts[-1]
        result2 = button_data.replace("_", " ")
        adrress_name =await load_trade_address(user_id)
        if button_data == "left":
            COPYSELECTED_CHAIN_INDEX = (COPYSELECTED_CHAIN_INDEX - 1) % len(COPYNETWORK_CHAINS)
            COPYPRESETNETWORK = COPYNETWORK_CHAINS[COPYSELECTED_CHAIN_INDEX]
            context.user_data['selected_chain'] = COPYPRESETNETWORK
            trades = await load_trades_addresses(user_id, COPYPRESETNETWORK)

            new_markup = await build_trades_keyboard(trades)

            message = await query.edit_message_reply_markup(reply_markup=new_markup)
        elif button_data == "right":
            COPYSELECTED_CHAIN_INDEX = (COPYSELECTED_CHAIN_INDEX - 1) % len(COPYNETWORK_CHAINS)
            COPYPRESETNETWORK = COPYNETWORK_CHAINS[COPYSELECTED_CHAIN_INDEX]
            context.user_data['selected_chain'] = COPYPRESETNETWORK
            trades = await load_trades_addresses(user_id, COPYPRESETNETWORK)

            # Update the keyboard markup with the new selected chain
            new_markup = await build_trades_keyboard(trades)
            
            # Edit the message to display the updated keyboard markup
            message = await query.edit_message_reply_markup(reply_markup=new_markup)
        elif result == "delete":
            name = "_".join(parts[:-1])
            
            name = name.replace("_", " ")
            print(name)
            trades = await delete_trades_addresses(user_id,context.user_data['selected_chain'],name)
            # Update the keyboard markup with the new selected chain
            new_markup = await build_trades_keyboard(trades)
            
            # Edit the message to display the updated keyboard markup
            message = await query.edit_message_reply_markup(reply_markup=new_markup)
        elif result == "profit":
            name = "_".join(parts[:-1])
            name2 = name.split("_")
            state = name2[-1]
            if(state =="on"):
                token_Name ="_".join(name2[:-1])
                token_Name = token_Name.replace("_", " ")
                message = await change_state_profit(user_id,context.user_data['selected_chain'],token_Name,False)
                matched_trade = await load_trades_addresses_once(user_id, context.user_data['selected_chain'],token_Name)
                new_markup = await build_trades_caption(matched_trade)
                message = await query.edit_message_caption(caption="Set up here!!!!!!!!!!", parse_mode=ParseMode.HTML, reply_markup=new_markup)
            if(state =="off"):
                token_Name ="_".join(name2[:-1])
                token_Name = token_Name.replace("_", " ")
                message = await change_state_profit(user_id,context.user_data['selected_chain'],token_Name,True)
                matched_trade = await load_trades_addresses_once(user_id, context.user_data['selected_chain'],token_Name)
                new_markup = await build_trade_keyboard(matched_trade)
                caption =await build_trades_caption(matched_trade)
                message = await query.edit_message_caption(caption=caption, parse_mode=ParseMode.HTML, reply_markup=new_markup)


        elif result == "loss":
            name = "_".join(parts[:-1])
            name2 = name.split("_")
            state = name2[-1]
            if(state =="on"):
                token_Name ="_".join(name2[:-1])
                token_Name = token_Name.replace("_", " ")
                message = await change_state_loss(user_id,context.user_data['selected_chain'],token_Name,False)
                matched_trade = await load_trades_addresses_once(user_id, context.user_data['selected_chain'],token_Name)
                new_markup = await build_trade_keyboard(matched_trade)
                caption =await build_trades_caption(matched_trade)
                message = await query.edit_message_caption(caption=caption, parse_mode=ParseMode.HTML, reply_markup=new_markup)
            if(state =="off"):
                token_Name ="_".join(name2[:-1])
                token_Name = token_Name.replace("_", " ")
                message = await change_state_loss(user_id,context.user_data['selected_chain'],token_Name,True)
                matched_trade = await load_trades_addresses_once(user_id, context.user_data['selected_chain'],token_Name)
                new_markup = await build_trade_keyboard(matched_trade)
                caption =await build_trades_caption(matched_trade)
                message = await query.edit_message_caption(caption=caption, parse_mode=ParseMode.HTML, reply_markup=new_markup)
        elif result == "limit":
            name = "_".join(parts[:-1])
            name2 = name.split("_")
            state = name2[-1]
            if(state =="on"):
                token_Name ="_".join(name2[:-1])
                token_Name = token_Name.replace("_", " ")
                message = await change_state_limit(user_id,context.user_data['selected_chain'],token_Name,False)
                matched_trade = await load_trades_addresses_once(user_id, context.user_data['selected_chain'],token_Name)
                new_markup = await build_trade_keyboard(matched_trade)
                caption =await build_trades_caption(matched_trade)
                message = await query.edit_message_caption(caption=caption, parse_mode=ParseMode.HTML, reply_markup=new_markup)
            if(state =="off"):
                token_Name ="_".join(name2[:-1])
                token_Name = token_Name.replace("_", " ")
                message = await change_state_limit(user_id,context.user_data['selected_chain'],token_Name,True)
                matched_trade = await load_trades_addresses_once(user_id, context.user_data['selected_chain'],token_Name)
                new_markup = await build_trade_keyboard(matched_trade)
                caption =await build_trades_caption(matched_trade)
                message = await query.edit_message_caption(caption=caption, parse_mode=ParseMode.HTML, reply_markup=new_markup)
        elif result2 in adrress_name:
            # Update the keyboard markup with the new selected chain
            matched_trade = await load_trades_addresses_once(user_id, context.user_data['selected_chain'],result2)
            new_markup = await build_trade_keyboard(matched_trade)
                    
            #caption = await build_copy_name_caption(matched_trade)
                    
            # Edit the message to display the updated keyboard markup
            caption =await build_trades_caption(matched_trade)
            message = await query.edit_message_caption(caption=caption, parse_mode=ParseMode.HTML, reply_markup=new_markup)
            context.user_data["id_trades"] =user_id
            context.user_data["name_token"] =result2
            

async def copy_trade_next_and_back_callback(update: Update, context: CallbackContext):    
    global COPYSELECTED_CHAIN_INDEX

    query = update.callback_query
    await query.answer()
    command = query.data
    user_id = str(query.from_user.id)
    user_data = await load_user_data(user_id)
    text = context.user_data['last_message']
    context.user_data['copy_next_id'] = query.message.message_id
    markup = context.user_data['last_markup']
    context.user_data["last_message_id"] = query.message.message_id
    COPYPRESETNETWORK = context.user_data['selected_chain']
    trades = await load_copy_trade_addresses(user_id, COPYPRESETNETWORK)
    
    
    
    if trades is not None:
        # Extract the names from the trade data
        global trade_names
        trade_names = [trade.name for trade in trades]
    else:
        # Handle the case where no trade data was loaded
        pass

    match = re.match(r"^copy_(\w+)", command)
    context.user_data["id_ammount"] =user_data.id
    context.user_data["name_ammount"] =match.group(1)
    if match:
        button_data = match.group(1)
        
        
        if button_data == "left":
            COPYSELECTED_CHAIN_INDEX = (COPYSELECTED_CHAIN_INDEX - 1) % len(COPYNETWORK_CHAINS)
            COPYPRESETNETWORK = COPYNETWORK_CHAINS[COPYSELECTED_CHAIN_INDEX]
            context.user_data['selected_chain'] = COPYPRESETNETWORK
            trades = await load_copy_trade_addresses(user_id, COPYPRESETNETWORK)
            # Update the keyboard markup with the new selected chain
            new_markup = await build_copy_trade_keyboard(trades)

            message = await query.edit_message_reply_markup(reply_markup=new_markup)
            back_variable(message, context, text, markup, False, True)
        elif button_data == "right":
            COPYSELECTED_CHAIN_INDEX = (COPYSELECTED_CHAIN_INDEX - 1) % len(COPYNETWORK_CHAINS)
            COPYPRESETNETWORK = COPYNETWORK_CHAINS[COPYSELECTED_CHAIN_INDEX]
            context.user_data['selected_chain'] = COPYPRESETNETWORK
            trades = await load_copy_trade_addresses(user_id, COPYPRESETNETWORK)
            # Update the keyboard markup with the new selected chain
            new_markup = await build_copy_trade_keyboard(trades)
            
            # Edit the message to display the updated keyboard markup
            message = await query.edit_message_reply_markup(reply_markup=new_markup)
            back_variable(message, context, text, markup, False, True)
        elif any(button_data.startswith(trade_name) for trade_name in trade_names):
            for trade_name in trade_names:
                button_data2 = button_data.split('_')


                if button_data.startswith(trade_name) and '_' not in button_data:
                    index = trade_names.index(trade_name)
                    matched_trade = trades[index]
                
                    # Update the keyboard markup with the new selected chain
                    new_markup = await build_copy_name_keyboard(matched_trade)
                    
                    caption = await build_copy_name_caption(matched_trade)
                    
                    # Edit the message to display the updated keyboard markup
                    message = await query.edit_message_caption(caption=caption, parse_mode=ParseMode.HTML, reply_markup=new_markup)
                    back_variable(message, context, text, markup, True, False)
                elif button_data2[0] ==trade_name and '_off' in button_data:
                    index = trade_names.index(trade_name)
                    matched_trade = trades[index]
                    LOGGER.info(matched_trade.name)
                    await update_copy_trade_addresses(user_id, matched_trade.name, context.user_data['selected_chain'], {'on': True})
                    trades = await load_copy_trade_addresses(user_id, context.user_data['selected_chain'])
                    # Update the keyboard markup with the new selected chain
                    new_markup = await build_copy_trade_keyboard(trades)

                    message = await query.edit_message_reply_markup(reply_markup=new_markup)
                    back_variable(message, context, text, markup, False, True)
                    return message
                elif button_data2[0] ==trade_name and '_on' in button_data:
                    index = trade_names.index(trade_name)
                    matched_trade = trades[index]
                    await update_copy_trade_addresses(user_id, matched_trade.name, context.user_data['selected_chain'], {'on': False})
                    trades = await load_copy_trade_addresses(user_id, context.user_data['selected_chain'])
                    # Update the keyboard markup with the new selected chain
                    new_markup = await build_copy_trade_keyboard(trades)

                    message = await query.edit_message_reply_markup(reply_markup=new_markup)
                    back_variable(message, context, text, markup, False, True)
                    return message
                elif button_data.startswith(trade_name) and '_delete' in button_data:
                    index = trade_names.index(trade_name)
                    matched_trade = trades[index]
                    trades = await delete_copy_trade_addresses(user_id, matched_trade.name, context.user_data['selected_chain'])
                    # Update the keyboard markup with the new selected chain
                    new_markup = await build_copy_trade_keyboard(trades)

                    message = await query.edit_message_reply_markup(reply_markup=new_markup)
                    context.user_data['message_id'] = message.message_id
                    back_variable(message, context, text, markup, False, True)
                    return message

async def copy_trade_rename(update: Update, context: CallbackContext):   
    LOGGER.info("Copy Trade Rename") 

    query = update.callback_query
    await query.answer()
    command = query.data
    user_id = str(query.from_user.id)
    
    context.user_data['copy_next_id'] = query.message.message_id
    context.user_data["last_message_id"] = query.message.message_id
    
    trades = await load_copy_trade_addresses(user_id, context.user_data['selected_chain'])
    
    
    if trades is not None:
        # Extract the names from the trade data
        trade_names = [trade.id for trade in trades]
    else:
        LOGGER.info("No trades")
        # Handle the case where no trade data was loaded
        pass

    match = re.match(r"^rename_(\w+)", command)
    if match:
        button_data = match.group(1)
        
        LOGGER.info(button_data)
        
        if int(button_data) in trade_names:
            index = trade_names.index(int(button_data))
            matched_trade = trades[index]
            LOGGER.info(matched_trade.name)

            context.user_data['trade'] = matched_trade
            message = await query.message.reply_text("what would you like to rename the copy trade wallet?")
            context.user_data['message_id'] = message.message_id
            return RENAME
                

async def answer_rename(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    matched_trade = context.user_data['trade']
    temp = []
    temp = await load_copy_trade_all(user_id)
    if temp:
        if text in temp:
             await update.message.reply_text(f"Your name bot has been used. Please use another name.")
             query = update.message
             bot = context.bot
             bot_profile_photos = await bot.get_user_profile_photos(bot.id, limit=1)
             bot_profile_photo = (
             bot_profile_photos.photos[0][0] if bot_profile_photos else None
                )
             message2 = await query.reply_photo(
                                bot_profile_photo,
                                caption=home_message,
                                parse_mode=ParseMode.HTML,
                                reply_markup=home_markup,
                            )    

             return ConversationHandler.END
    await update_copy_trade_addresses(user_id, matched_trade.name, context.user_data['selected_chain'], {'name': text})
    trades = await load_copy_trade_addresses(user_id, context.user_data['selected_chain'])
    
    # Update the keyboard markup with the new selected chain
    new_markup = await build_copy_trade_keyboard(trades)
    
    message_id_to_edit = context.user_data.get('copy_id')
    rename_message_id = context.user_data['message_id']

    await context.bot.delete_message(chat_id=chat_id, message_id=rename_message_id)
    await context.bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id_to_edit, reply_markup=new_markup)
    return ConversationHandler.END
    
async def cancel_rename(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop('trade', None)
    context.user_data.pop('selected_chain', None)
    context.user_data.pop("copy_id", None)
    context.user_data.pop("message_id", None)
    await update.message.reply_text("Copy Trade Cancelled.")
    return ConversationHandler.END
async def trades_start_callback(update: Update, context: CallbackContext):
    global COPYSELECTED_CHAIN_INDEX
    query = update.callback_query
    await query.answer()
    command = query.data
    user_id = str(query.from_user.id)
    user_data = await load_user_data(user_id)
    context.user_data["last_message_id"] = query.message.message_id
    match = re.match(r"^asktrade_(\w+)", command)
    if match:
        button_data = match.group(1)
        
        if button_data == "address":
            # Edit the message to display the updated keyboard markup
            message = await query.message.reply_text("What s contract you want to ?")
            # back_variable(message, context, text, new_markup, False, False)
            return TRADESTOKEN
async def copy_trade_start_callback(update: Update, context: CallbackContext):
    global COPYSELECTED_CHAIN_INDEX
    query = update.callback_query
    await query.answer()
    command = query.data
    user_id = str(query.from_user.id)
    user_data = await load_user_data(user_id)
    text = context.user_data['last_message']
    markup = context.user_data['last_markup']
    context.user_data["last_message_id"] = query.message.message_id
    
    match = re.match(r"^trade_(\w+)", command)
    if match:
        button_data = match.group(1)
        
        if button_data == "address":
            # Edit the message to display the updated keyboard markup
            message = await query.message.reply_text("What would you like to name this copy trade wallet?")
            # back_variable(message, context, text, new_markup, False, False)
            return TRADEWALLETNAME
async def AskLimitammount2(update: Update, context: CallbackContext):
    query = update.callback_query
    message = await query.message.reply_text("Reply to this message with your ammount limit.")
    return CHATAMMOUNT
async def AskLimitammount(update: Update, context: CallbackContext):
    print(context.user_data["id_trades"])
    print(context.user_data["name_token"])
    print(update.message.text)
    ammount_limit = Decimal(update.message.text)
    result = await update_trades_addresses_ammount_limit(context.user_data["id_trades"], ammount_limit,context.user_data["name_token"],context.user_data['selected_chain'])
    query = update.message
    message = await query.reply_text("Add amount limit Successfully!!!!!!")
    bot = context.bot
    bot_profile_photos = await bot.get_user_profile_photos(bot.id, limit=1)
    bot_profile_photo = (
        bot_profile_photos.photos[0][0] if bot_profile_photos else None
    )
    message = await query.reply_photo(
                    bot_profile_photo,
                    caption=home_message,
                    parse_mode=ParseMode.HTML,
                    reply_markup=home_markup,
                )    

    return ConversationHandler.END
async def AskProfit2(update: Update, context: CallbackContext):
    query = update.callback_query
    message = await query.message.reply_text("Reply to this message with your loss.")

    return CHATPROFIT
async def AskProfit(update: Update, context: CallbackContext):
    print(context.user_data["id_trades"])
    print(context.user_data["name_token"])
    print(update.message.text)
    profit = Decimal(update.message.text)
    result = await update_trades_addresses_profit(context.user_data["id_trades"], profit,context.user_data["name_token"],context.user_data['selected_chain'])
    query = update.message
    message = await query.reply_text("Add profit Successfully!!!!!!")
    bot = context.bot
    bot_profile_photos = await bot.get_user_profile_photos(bot.id, limit=1)
    bot_profile_photo = (
        bot_profile_photos.photos[0][0] if bot_profile_photos else None
    )
    message = await query.reply_photo(
                    bot_profile_photo,
                    caption=home_message,
                    parse_mode=ParseMode.HTML,
                    reply_markup=home_markup,
                )    

    return ConversationHandler.END
async def AskLoss2(update: Update, context: CallbackContext):
    query = update.callback_query
    message = await query.message.reply_text("Reply to this message with your loss.")
    return CHATLOSS
async def AskLoss(update: Update, context: CallbackContext):
    print(context.user_data["id_trades"])
    print(context.user_data["name_token"])
    print(update.message.text)
    loss = Decimal(update.message.text)
    result = await update_trades_addresses_loss(context.user_data["id_trades"], loss,context.user_data["name_token"],context.user_data['selected_chain'])
    query = update.message
    message = await query.reply_text("Add loss Successfully!!!!!!")
    bot = context.bot
    bot_profile_photos = await bot.get_user_profile_photos(bot.id, limit=1)
    bot_profile_photo = (
        bot_profile_photos.photos[0][0] if bot_profile_photos else None
    )
    message = await query.reply_photo(
                    bot_profile_photo,
                    caption=home_message,
                    parse_mode=ParseMode.HTML,
                    reply_markup=home_markup,
                )    

    return ConversationHandler.END
async def AskLimit2(update: Update, context: CallbackContext):
    query = update.callback_query
    message = await query.message.reply_text("Reply to this message with your limit.")

    return CHATLIMIT
async def AskLimit(update: Update, context: CallbackContext):
    print(context.user_data["id_trades"])
    print(context.user_data["name_token"])
    print(update.message.text)
    limit = Decimal(update.message.text)
    result = await update_trades_addresses_limit(context.user_data["id_trades"], limit,context.user_data["name_token"],context.user_data['selected_chain'])
    query = update.message
    message = await query.reply_text("Add limit Successfully!!!!!!")
    bot = context.bot
    bot_profile_photos = await bot.get_user_profile_photos(bot.id, limit=1)
    bot_profile_photo = (
        bot_profile_photos.photos[0][0] if bot_profile_photos else None
    )
    message = await query.reply_photo(
                    bot_profile_photo,
                    caption=home_message,
                    parse_mode=ParseMode.HTML,
                    reply_markup=home_markup,
                )    

    return ConversationHandler.END
async def AskGas2(update: Update, context: CallbackContext):
    query = update.callback_query
    message = await query.message.reply_text("Reply to this message with your gas.")

    return CHATGAS
async def AskGas(update: Update, context: CallbackContext):
    print(context.user_data["id_ammount"])
    print(context.user_data["name_ammount"])
    print(update.message.text)
    slippage = Decimal(update.message.text)
    result = await update_copy_trade_addresses_gas(context.user_data["id_ammount"], slippage,context.user_data["name_ammount"])
    query = update.message
    message = await query.reply_text("Add gas Successfully!!!!!!")
    bot = context.bot
    bot_profile_photos = await bot.get_user_profile_photos(bot.id, limit=1)
    bot_profile_photo = (
        bot_profile_photos.photos[0][0] if bot_profile_photos else None
    )
    message = await query.reply_photo(
                    bot_profile_photo,
                    caption=home_message,
                    parse_mode=ParseMode.HTML,
                    reply_markup=home_markup,
                )    

    return ConversationHandler.END

async def AskSlippage2(update: Update, context: CallbackContext):
    query = update.callback_query
    message = await query.message.reply_text("Reply to this message with your slippage.")

    return CHATSLIP
async def AskSlippage(update: Update, context: CallbackContext):
    print(context.user_data["id_ammount"])
    print(context.user_data["name_ammount"])
    print(update.message.text)
    slippage = Decimal(update.message.text)
    result = await update_copy_trade_addresses_slippage(context.user_data["id_ammount"], slippage,context.user_data["name_ammount"])
    query = update.message
    message = await query.reply_text("Add slippage Successfully!!!!!!")
    bot = context.bot
    bot_profile_photos = await bot.get_user_profile_photos(bot.id, limit=1)
    bot_profile_photo = (
        bot_profile_photos.photos[0][0] if bot_profile_photos else None
    )
    message = await query.reply_photo(
                    bot_profile_photo,
                    caption=home_message,
                    parse_mode=ParseMode.HTML,
                    reply_markup=home_markup,
                )   

    return ConversationHandler.END

async def AskAmmount2(update: Update, context: CallbackContext):
    query = update.callback_query
    message = await query.message.reply_text("Reply to this message with your desired buy ammount.")

    return CHATCHIT
async def AskAmmount(update: Update, context: CallbackContext):
    print(context.user_data["id_ammount"])
    print(context.user_data["name_ammount"])
    print(update.message.text)

    ammout = Decimal(update.message.text)
    result = await update_copy_trade_addresses_ammout(context.user_data["id_ammount"], ammout,context.user_data["name_ammount"])
    query = update.message
    message = await query.reply_text("Add ammount Successfully!!!!!!")
    bot = context.bot
    bot_profile_photos = await bot.get_user_profile_photos(bot.id, limit=1)
    bot_profile_photo = (
        bot_profile_photos.photos[0][0] if bot_profile_photos else None
    )
    message = await query.reply_photo(
                    bot_profile_photo,
                    caption=home_message,
                    parse_mode=ParseMode.HTML,
                    reply_markup=home_markup,
                )   
    return ConversationHandler.END

async def target_token_address_reply(update: Update, context: CallbackContext):
    context.user_data['address'] = update.message.text.replace(' ', '_')
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id

    # This message is a reply to the input message, and we can process the user's input here
    await update.message.reply_text(f"Reply to this message with the desired wallet address you'd like to copy trades from.")
    return TARGETWALLET

async def submit_trades_reply(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    token_address = update.message.text
    token_address =token_address.lower()
    temp= []
    temp = await load_trade_address_all(user_id)
    if temp:
        if token_address in temp:
             await update.message.reply_text(f"This address has been in trade")
             return ConversationHandler.END
    if(token_address.__len__() != 42):
        await update.message.reply_text(f"Please enter a valid address.")
        query = update.message
        bot = context.bot
        bot_profile_photos = await bot.get_user_profile_photos(bot.id, limit=1)
        bot_profile_photo = (
            bot_profile_photos.photos[0][0] if bot_profile_photos else None
        )
        message = await query.reply_photo(
                        bot_profile_photo,
                        caption=home_message,
                        parse_mode=ParseMode.HTML,
                        reply_markup=home_markup,
                    )    
        return ConversationHandler.END
    
    contract_ab=[{"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"address","name":"minter_","type":"address"},{"internalType":"uint256","name":"mintingAllowedAfter_","type":"uint256"}],"payable":False,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"owner","type":"address"},{"indexed":True,"internalType":"address","name":"spender","type":"address"},{"indexed":False,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"delegator","type":"address"},{"indexed":True,"internalType":"address","name":"fromDelegate","type":"address"},{"indexed":True,"internalType":"address","name":"toDelegate","type":"address"}],"name":"DelegateChanged","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"delegate","type":"address"},{"indexed":False,"internalType":"uint256","name":"previousBalance","type":"uint256"},{"indexed":False,"internalType":"uint256","name":"newBalance","type":"uint256"}],"name":"DelegateVotesChanged","type":"event"},{"anonymous":False,"inputs":[{"indexed":False,"internalType":"address","name":"minter","type":"address"},{"indexed":False,"internalType":"address","name":"newMinter","type":"address"}],"name":"MinterChanged","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"from","type":"address"},{"indexed":True,"internalType":"address","name":"to","type":"address"},{"indexed":False,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Transfer","type":"event"},{"constant":True,"inputs":[],"name":"DELEGATION_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"DOMAIN_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"PERMIT_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"rawAmount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"uint32","name":"","type":"uint32"}],"name":"checkpoints","outputs":[{"internalType":"uint32","name":"fromBlock","type":"uint32"},{"internalType":"uint96","name":"votes","type":"uint96"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"delegatee","type":"address"}],"name":"delegate","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"delegatee","type":"address"},{"internalType":"uint256","name":"nonce","type":"uint256"},{"internalType":"uint256","name":"expiry","type":"uint256"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"delegateBySig","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"delegates","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"getCurrentVotes","outputs":[{"internalType":"uint96","name":"","type":"uint96"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"uint256","name":"blockNumber","type":"uint256"}],"name":"getPriorVotes","outputs":[{"internalType":"uint96","name":"","type":"uint96"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"minimumTimeBetweenMints","outputs":[{"internalType":"uint32","name":"","type":"uint32"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"dst","type":"address"},{"internalType":"uint256","name":"rawAmount","type":"uint256"}],"name":"mint","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"mintCap","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"minter","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"mintingAllowedAfter","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"nonces","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"numCheckpoints","outputs":[{"internalType":"uint32","name":"","type":"uint32"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"rawAmount","type":"uint256"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"permit","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"minter_","type":"address"}],"name":"setMinter","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"dst","type":"address"},{"internalType":"uint256","name":"rawAmount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"src","type":"address"},{"internalType":"address","name":"dst","type":"address"},{"internalType":"uint256","name":"rawAmount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"}]
    contract = web3.eth.contract(address=web3.to_checksum_address(token_address), abi=contract_ab)
    print(contract.functions.name().call())
    print(context.user_data['selected_chain'])
    print(token_address)

    data = {
                "user": user_id,      
                'chain':context.user_data['selected_chain'],
                "token_name": contract.functions.name().call(),
                'token_address': token_address,
            }
    message = await save_trade_address(data)
    await update.message.reply_text(f"Trade added token successfully.\nSymbol: ${contract.functions.symbol().call()} \nName : {contract.functions.name().call()} \nAddress : {token_address}\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    query1 = update.message
    bot1 = context.bot
    bot_profile_photos1 = await bot1.get_user_profile_photos(bot1.id, limit=1)
    bot_profile_photo1 = (
        bot_profile_photos1.photos[0][0] if bot_profile_photos1 else None
        )
    message1 = await query1.reply_photo(
                        bot_profile_photo1,
                        caption=home_message,
                        parse_mode=ParseMode.HTML,
                        reply_markup=home_markup,
                    )  
    
    return ConversationHandler.END

async def submit_copy_reply(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    name = context.user_data.get('address')
    temp = []
    temp = await load_copy_trade_all(user_id)
    if temp:
        if name in temp:
             await update.message.reply_text(f"Your name bot has been used. Please use another name.")
             query = update.message
             bot = context.bot
             bot_profile_photos = await bot.get_user_profile_photos(bot.id, limit=1)
             bot_profile_photo = (
             bot_profile_photos.photos[0][0] if bot_profile_photos else None
                )
             message = await query.reply_photo(
                                bot_profile_photo,
                                caption=home_message,
                                parse_mode=ParseMode.HTML,
                                reply_markup=home_markup,
                            )    
             return ConversationHandler.END
    
  
    chain = context.user_data['selected_chain']
    token_address = update.message.text.replace(' ', '')
    token_address = token_address.lower()
    temp2= []
    temp2 = await load_copy_trade_address_all(user_id)

    if temp2:
        if token_address in temp2:
             await update.message.reply_text(f"This address has been copy")
             query = update.message
             bot = context.bot
             bot_profile_photos = await bot.get_user_profile_photos(bot.id, limit=1)
             bot_profile_photo = (
             bot_profile_photos.photos[0][0] if bot_profile_photos else None
                )
             message = await query.reply_photo(
                                bot_profile_photo,
                                caption=home_message,
                                parse_mode=ParseMode.HTML,
                                reply_markup=home_markup,
                            )    
             return ConversationHandler.END
    if(token_address.__len__() != 42):
        await update.message.reply_text(f"Please enter a valid wallet address.")
        query = update.message
        bot = context.bot
        bot_profile_photos = await bot.get_user_profile_photos(bot.id, limit=1)
        bot_profile_photo = (
            bot_profile_photos.photos[0][0] if bot_profile_photos else None
        )
        message = await query.reply_photo(
                        bot_profile_photo,
                        caption=home_message,
                        parse_mode=ParseMode.HTML,
                        reply_markup=home_markup,
                    )    
        return ConversationHandler.END
    chat_id = update.message.chat_id
    #copy_trade_main_id = context.user_data["copy_trade_message_id"]
    token_address = token_address.lower()
    await save_copy_trade_address(user_id, name, token_address, chain, False)

    # This message is a reply to the input message, and we can process the user's input here
    await update.message.reply_text(f"Copy trade added successfully.")
    context.user_data.pop('address', None)
    context.user_data.pop('to_address', None)
    context.user_data.pop("network_chain", None)
    trades = await load_copy_trade_addresses(user_id, chain)
    copy_trade_markup = await build_copy_trade_keyboard(trades)
    copy_message = context.user_data['last_message']
    # message = await update.message.edit_reply_markup(
    #     reply_markup=copy_trade_markup
    # )
    message_id_to_edit = "copy_trade_main_id"
    message = context.bot.edit_message_reply_markup(
        chat_id=update.message.chat_id,  # Replace with the chat ID where the message was sent
        message_id=message_id_to_edit,   # Specify the message ID you want to edit
        reply_markup=copy_trade_markup    # Set the updated markup
    )
    context.user_data.pop("last_message", None)
    back_variable(message, context, copy_message, copy_trade_markup, True, False)
    query = update.message
    bot = context.bot
    bot_profile_photos = await bot.get_user_profile_photos(bot.id, limit=1)
    bot_profile_photo = (
    bot_profile_photos.photos[0][0] if bot_profile_photos else None
                )
    message = await query.reply_photo(
                                bot_profile_photo,
                                caption=home_message,
                                parse_mode=ParseMode.HTML,
                                reply_markup=home_markup,
                            )    
    return ConversationHandler.END

async def cancel_copy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop('address', None)
    context.user_data.pop('to_address', None)
    context.user_data.pop("last_message", None)
    context.user_data.pop("network_chain", None)
    await update.message.reply_text("Copy Trade Cancelled.")
    return ConversationHandler.END


async def cancel_ammount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Copy Trade Cancelled.")
    query = update.message
    bot = context.bot
    bot_profile_photos = await bot.get_user_profile_photos(bot.id, limit=1)
    bot_profile_photo = (
        bot_profile_photos.photos[0][0] if bot_profile_photos else None
    )
    message = await query.reply_photo(
                    bot_profile_photo,
                    caption=home_message,
                    parse_mode=ParseMode.HTML,
                    reply_markup=home_markup,
                )    
    return ConversationHandler.END







# ------------------------------------------------------------------------------
# CONFIGURATION BUTTON CALLBACK
# ------------------------------------------------------------------------------
def build_caption(PRESETNETWORK, user_data, wallet, gas_price):
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
    return caption

def build_buy_caption(wallet, user_data, PRESETNETWORK, gas_price):
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
    return caption

def build_sell_caption(wallet, user_data, PRESETNETWORK, gas_price):
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
    return caption


REPLYDELTA = range(1)
async def configuration_next_and_back_callback(update: Update, context: CallbackContext):
    global SELECTED_CHAIN_INDEX
    
    query = update.callback_query
    await query.answer()
    command = query.data
    user_id = str(query.from_user.id)
    user_data = await load_user_data(user_id)
    text = context.user_data.get('last_message')
    markup = context.user_data.get('last_markup')
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
            back_variable(message, context, text, new_markup, True, False)
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
    user_id = str(update.message.from_user.id)
    chat_id = update.message.chat_id
    preset = context.user_data.get('preset')
    text = update.message.text
    # caption = context.user_data['config_message'] 
    user_data = await load_user_data(user_id)
    

    wallet = user_data.wallet_address if user_data is not None and user_data.wallet_address is not None else '<pre>Disconnected</pre>'
    
    gas_price = await get_default_gas_price_gwei()
    
    if preset == "delta":
        f_text = Decimal(text.replace(' GWEI', '')) if 'GWEI' in text else Decimal(text)
        text = f"""
        ✅ Max gas delta set to {round(Decimal(f_text))} GWEI. By setting your Max Gas Delta to {round(Decimal(f_text))} GWEI, the bot will no longer frontrun rugs or copytrade transactions that require more than {round(Decimal(f_text))} GWEI in delta.
        """
        await update_user_data(user_id, {'max_delta':f_text})
        user_data = await load_user_data(user_id)
        new_markup = build_preset_keyboard()
        caption = build_caption(PRESETNETWORK, user_data, wallet, gas_price)
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        message_id = context.user_data['caption_id']
        await context.bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=new_markup)
    elif preset == "slippage":
        f_text = text.replace('%', '') if '%' in text else Decimal(text)
        text = f"""
        ✅ Slippage percentage set to {f_text}%!        
        """
        await update_user_data(user_id, {'slippage':Decimal(f_text)})
        user_data = await load_user_data(user_id)
        new_markup = build_preset_keyboard()
        caption = build_caption(PRESETNETWORK, user_data, wallet, gas_price)
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        message_id = context.user_data['caption_id']
        await context.bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=new_markup)
    elif preset == "gas":
        f_text = int(text.replace('m', '')) if 'm' in text else int(text) * 1000000
        text = f"""
        ✅ Max gas limit set to {round(f_text)}!
        """
        await update_user_data(user_id, {'max_gas':round(Decimal(f_text), 2)})
        user_data = await load_user_data(user_id)
        new_markup = build_preset_keyboard()
        caption = build_caption(PRESETNETWORK, user_data, wallet, gas_price)
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        message_id = context.user_data['caption_id']
        await context.bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=new_markup)
# --------------------------------------------------------------------------------
    elif preset == "maxbuytax":
        f_text = int(text.replace('x', '')) if 'x' in text else int(text)
        text = f"""
        ✅ Max Buy Tax set to {round(f_text)}!
        """
        user_data = await load_user_data(user_id)
        await update_user_data(user_id, {'buy_tax':round(Decimal(f_text), 2)})
        buy_markup = build_buy_keyboard(user_data)
        caption = build_buy_caption(wallet, user_data, PRESETNETWORK, gas_price)
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        message_id = context.user_data['caption_id']
        await context.bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=buy_markup)        
    elif preset == "maxselltax":
        f_text = int(text.replace('x', '')) if 'x' in text else int(text)
        text = f"""
        ✅ Max Sell Tax set to {round(f_text)}!
        """
        await update_user_data(user_id, {'sell_tax':round(Decimal(f_text), 2)})
        user_data = await load_user_data(user_id)
        buy_markup = build_buy_keyboard(user_data)
        caption = build_buy_caption(wallet, user_data, PRESETNETWORK, gas_price)
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        message_id = context.user_data['caption_id']
        await context.bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=buy_markup)        
    elif preset == "sellhi":
        f_text = int(text.replace('x', '')) if 'x' in text else Decimal(text)
        text = f"""
        ✅ Sell-Hi set to {round(f_text)}!
        """
        await update_user_data(user_id, {'sell_hi':round(Decimal(f_text), 2)})
        user_data = await load_user_data(user_id)
        sell_markup = build_sell_keyboard(user_data)
        caption = build_sell_caption(wallet, user_data, PRESETNETWORK, gas_price)
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        message_id = context.user_data['caption_id']
        await context.bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=sell_markup)        
    elif preset == "selllo":
        f_text = int(text.replace('x', '')) if 'x' in text else Decimal(text)
        text = f"""
        ✅ Sell-Lo set to {round(f_text)}!
        """
        await update_user_data(user_id, {'sell_lo':round(Decimal(f_text), 2)})
        user_data = await load_user_data(user_id)
        sell_markup = build_sell_keyboard(user_data)
        caption = build_sell_caption(wallet, user_data, PRESETNETWORK, gas_price)
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        message_id = context.user_data['caption_id']
        await context.bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=sell_markup)        
    elif preset == "sellhiamount":
        f_text = int(text.replace('m', '')) if 'm' in text else int(text)
        text = f"""
        ✅ Sell-Hi Amount set to {round(f_text)}!
        """
        await update_user_data(user_id, {'sell_hi_amount':round(Decimal(f_text), 2)})
        user_data = await load_user_data(user_id)
        sell_markup = build_sell_keyboard(user_data)
        caption = build_sell_caption(wallet, user_data, PRESETNETWORK, gas_price)
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        message_id = context.user_data['caption_id']
        await context.bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=sell_markup)        
    elif preset == "sellloamount":
        f_text = int(text.replace('m', '')) if 'm' in text else int(text)
        text = f"""
        ✅ Sell-Lo Amount set to {round(f_text)}!
        """
        await update_user_data(user_id, {'sell_lo_amount':round(Decimal(f_text), 2)})
        user_data = await load_user_data(user_id)
        sell_markup = build_sell_keyboard(user_data)
        caption = build_sell_caption(wallet, user_data, PRESETNETWORK, gas_price)
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        message_id = context.user_data['caption_id']
        await context.bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=sell_markup)        



        
        

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
# TRANSFER BUTTON CALLBACK
# ------------------------------------------------------------------------------
async def transfer_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    command = query.data
    user_id = str(query.from_user.id)
    user_data = await load_user_data(user_id)
    
    context.user_data["last_message_id"] = query.message.message_id

    match = re.match(r"^transfer_chain_(\w+)", command)
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
            NETWORKNAME = "Ethereum"
            BALANCE = await get_wallet_balance('eth', user_id)
        elif button_data == "bsc":
            NETWORK = "bsc"
            NETWORKNAME = "Binance"
            BALANCE = await get_wallet_balance('bsc', user_id)
        elif button_data == "arb":
            NETWORK = "arb"
            NETWORKNAME = "Avalance"
            BALANCE = await get_wallet_balance('arb', user_id)
        elif button_data == "base":
            NETWORK = "base"
            NETWORKNAME = "Coinbase"
            BALANCE = await get_wallet_balance('base', user_id)

        # STORE THE USER CHOICE FOR NETWORK
        context.user_data["network_chain"] = NETWORK
        context.user_data["network_name"] = NETWORKNAME

        disconnect_message = f"""
⚡️ Chain: {NETWORKNAME}

✅ Address: {user_data.wallet_address}

You have {BALANCE} {NETWORK}            
            """
        
        networkchain = InlineKeyboardButton(f"💰 {NETWORK.upper()}", callback_data=f"transfer_{NETWORK.lower()}")
        token = InlineKeyboardButton(f"💰 TOKEN", callback_data=f"transfer_token")

        transfer_keyboard = [
            [home], 
            [back],
            [networkchain, token],
        ]
        transfer_built_markup = InlineKeyboardMarkup(transfer_keyboard)

        
        
        message = await query.edit_message_caption(
            caption=disconnect_message,
            parse_mode=ParseMode.HTML,
            reply_markup=transfer_built_markup,
        )
        back_variable(message, context, disconnect_message, asset_chain_markup, True, False)
        context.user_data["message"] = message
        context.user_data["text"] = disconnect_message
        context.user_data["markup"] = connect_markup
        message
    else:
        await query.message.reply_text("I don't understand that command.")


TOKENADDRESS, TOADDRESS, AMOUNT = range(3)
async def token_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    command = query.data
    user_id = str(query.from_user.id)
    user_data = await load_user_data(user_id)
    
    context.user_data["last_message_id"] = query.message.message_id

    match = re.match(r"^transfer_(\w+)", command)
    if match:
        button_data = match.group(1)
        
        if button_data == "token":
            token_message = "What is the token contract address?"
            await query.message.reply_text(token_message, parse_mode=ParseMode.HTML)
            return TOKENADDRESS
        elif button_data == "eth":
            NETWORK = "eth"
            NETWORKNAME = "Ethereum"
            BALANCE = await get_wallet_balance('eth', user_id)
            disconnect_message = f"""
⚡️ Chain: {NETWORKNAME}

✅ Address: {user_data.wallet_address}

You have {BALANCE} {NETWORK}        
------------------------------
What wallet address do you wish to send the token to?    
            """
            message = await query.edit_message_caption(
                caption=disconnect_message,
                parse_mode=ParseMode.HTML,
                reply_markup=home_markup,
            )
            message
            return TOADDRESS
        elif button_data == "bsc":
            NETWORK = "bsc"
            NETWORKNAME = "Binance"
            BALANCE = await get_wallet_balance('bsc', user_id)
            disconnect_message = f"""
⚡️ Chain: {NETWORKNAME}

✅ Address: {user_data.wallet_address}

You have {BALANCE} {NETWORK}        
------------------------------
What wallet address do you wish to send the token to?    
            """
            message = await query.edit_message_caption(
                caption=disconnect_message,
                parse_mode=ParseMode.HTML,
                reply_markup=home_markup,
            )
            message
            return TOADDRESS
        elif button_data == "arb":
            NETWORK = "arb"
            NETWORKNAME = "Avalance"
            BALANCE = await get_wallet_balance('arb', user_id)
            disconnect_message = f"""
⚡️ Chain: {NETWORKNAME}

✅ Address: {user_data.wallet_address}

You have {BALANCE} {NETWORK}        
------------------------------
What wallet address do you wish to send the token to?    
            """
            message = await query.edit_message_caption(
                caption=disconnect_message,
                parse_mode=ParseMode.HTML,
                reply_markup=home_markup,
            )
            message
            return TOADDRESS
        elif button_data == "base":
            NETWORK = "base"
            NETWORKNAME = "Coinbase"
            BALANCE = await get_wallet_balance('base', user_id)
            disconnect_message = f"""
⚡️ Chain: {NETWORKNAME}

✅ Address: {user_data.wallet_address}

You have {BALANCE} {NETWORK}        
------------------------------
What wallet address do you wish to send the token to?    
            """
            message = await query.edit_message_caption(
                caption=disconnect_message,
                parse_mode=ParseMode.HTML,
                reply_markup=home_markup,
            )
            message
            return TOADDRESS

            
async def token_address_reply(update: Update, context: CallbackContext):
    context.user_data['address'] = update.message.text
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    user_data = await load_user_data(str(user_id))
    
    token_name, token_symbol, token_decimals, token_lp, balance, contract_add = await get_token_info(context.user_data['address'], context.user_data["network_chain"], user_data) 
    if not token_name.startswith('An error occurred:'):
        token_info = f"""
        🪙 CA: {contract_add}
        
    Please input wallet address to transfer <strong>{token_name}</strong> to
        """

        # This message is a reply to the input message, and we can process the user's input here
        await update.message.reply_text(token_info, parse_mode=ParseMode.HTML)
        return TOADDRESS
    else:
        await update.message.reply_text(token_name, parse_mode=ParseMode.HTML)
        return ConversationHandler.END

async def to_address_reply(update: Update, context: CallbackContext):
    context.user_data['to_address'] = update.message.text
    user_id = update.message.from_user.id
    user_data = await load_user_data(str(user_id))
    chat_id = update.message.chat_id
    LOGGER.info("Chain check::: ")
    LOGGER.info(context.user_data)
    
    token_name, token_symbol, token_decimals, token_lp, balance, contract_add = await get_token_info(context.user_data['address'], context.user_data["network_chain"], user_data) 

    if not token_name.startswith('An error occurred:'):
        text = f"""
        🪙 CA: {contract_add}
        
    How many token do you want to send?

    If you type 100%, it will transfer the entire balance.

    You currently have <strong>{balance} {token_symbol}    </strong>
        """

        # This message is a reply to the input message, and we can process the user's input here
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        return AMOUNT
    else:
        await update.message.reply_text(token_name, parse_mode=ParseMode.HTML)
        return ConversationHandler.END
    
async def token_amount_reply(update: Update, context: CallbackContext):
    percentage = update.message.text
    user_id = update.message.from_user.id
    address = context.user_data.get('address')
    to_address = context.user_data['to_address']
    chat_id = update.message.chat_id
    NETWORK = context.user_data.get("network_chain")
    user_data = await load_user_data(user_id)
        
    # try:
    tx_hash, amount, symbol, symbol_name = await trasnfer_currency(NETWORK, user_data, percentage, to_address, token_address=address)
    
    if "Insufficient balance" == tx_hash:
        await update.message.reply_text(tx_hash)
        return ConversationHandler.END
    elif "Error Trasferring:" in tx_hash:
        await update.message.reply_text(tx_hash)
        return ConversationHandler.END
    
    receipt = await check_transaction_status(NETWORK, user_data,  tx_hash)
    
    tf_msg = f"""
    You are transferring {amount} {symbol.upper()} from your wallet {user_data.wallet_address}... 
    -----------------------------
    
    TXHASH: <code>{tx_hash}</code>
    -----------------------------
    ETHERSCAN: https://etherscan.io/tx/{tx_hash}
    """
    await update.message.reply_text(tf_msg, parse_mode=ParseMode.HTML)
    return ConversationHandler.END

    # except Exception as e:
    #     LOGGER.error(e)
    #     # Handle the error gracefully
    #     error_msg = f"Error: {e}."
    #     await update.message.reply_text(error_msg, parse_mode=ParseMode.HTML)
    #     return ConversationHandler.END

async def cancel_transfer(update: Update, context: CallbackContext):
    context.user_data.pop('address', None)
    context.user_data.pop('to_address', None)
    context.user_data.pop("network_chain", None)
    await update.message.reply_text("Investment Cancelled.")
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



async def reply_wallet_attach(update: Update, context: CallbackContext):
    message_id = context.user_data['private_reply']
    text = update.message.text
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    NETWORK = context.user_data.get("network_chain")
    
    LOGGER.info(message_id)
    LOGGER.info(update.message.message_id)
    
    if message_id and update.message.message_id > message_id:
        phrase, wallet_address = await attach_wallet_function(NETWORK, user_id, text)
        if phrase != None and wallet_address != None:
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
        
    context.user_data.clear()
    ConversationHandler.END

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
