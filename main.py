import os
import html
import json
import traceback

from logger import LOGGER
from decouple import config
from typing import Final

DEBUG: Final = config("DEBUG", default=True)
TOKEN: Final = config("TOKEN")
USERNAME: Final = config("USERNAME")
DEVELOPER_CHAT_ID: Final = config("DEVELOPERCHATID")

from warnings import filterwarnings
from telegram import Update
from telegram.ext import (
    Application,
    ConversationHandler,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    PicklePersistence,
)
from telegram.warnings import PTBUserWarning
from telegram.constants import ParseMode

filterwarnings(
    action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning
)

from constants import about_message, terms_message, help_message

from commands.start.__command import (
    help_command,
    terms_command,
    start_command,
    about_command,
    language_command,
)
from commands.start.__buttons import (
    start_button_callback,
    start_quick_callback,
    terms_button_callback,
    language_button_callback,
    home_button_callback,
    back_button_callback,
    trades_start_callback,
    reply_buysell_address,
    buy_callback,
    sell_callback,
    reply_buysell_amount,
    cancel_buysell,
    trades_next_and_back_callback,
    configuration_next_and_back_callback,
    configuration_button_callback,
    reply_preset_response,
    cancel_preset,
    AskLimitammount,
    AskLimitammount2,
    
    copy_trade_next_and_back_callback,
    copy_trade_rename,
    answer_rename,
    cancel_rename,
    copy_trade_start_callback,
    target_token_address_reply,
    AskAmmount,
    AskAmmount2,
    AskSlippage,
    AskSlippage2,
    AskGas,
    AskGas2,
    submit_copy_reply,
    cancel_copy,
    cancel_ammount,
    submit_trades_reply,
    AskLimit,
    AskLimit2,
    AskLoss2,
    AskLoss,
    AskProfit,
    AskProfit2,
    transfer_callback,
    token_callback,
    token_address_reply,
    to_address_reply,
    token_amount_reply,
    cancel_transfer,
    
    wallets_asset_chain_button_callback,
    wallets_chain_button_callback,
    wallets_chain_connect_button_callback,
    wallets_chain_attach_callback,
    reply_wallet_attach,
    reply_wallet_attach_address,
    cancel_attachment,
    
    delete_sniper_callback,
    delete_conversation_sniper_callback,
    add_sniper_address,
    sniper_gas_delta_reply,
    sniper_slippage_reply,
    sniper_token_amount_reply,
    sniper_eth_amount_reply,
    sniper_blockdelay_reply,
    cancel_sniper,
)


def handle_response(text: str) -> str:
    processed_text = text.lower()

    if any(word in processed_text for word in ["hello", "hi", "who's here"]):
        return "Hello There!"

    if any(
        word in processed_text
        for word in [
            "about yourself",
            "what do you do",
            "who are you",
            "what is RDTrading",
            "about",
        ]
    ):
        return about_message

    if any(word in processed_text for word in ["terms", "conditions"]):
        return terms_message

    if "how are you" in processed_text:
        return "I am doing alright mate. How about you?"

    if any(
        word in processed_text for word in ["assist me", "support", "commands", "help"]
    ):
        return help_message

    return help_message


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = (
        update.message.chat.type
    )  # to determin the chat type private or group
    text: str = update.message.text  # messga ethat will be processed
    LOGGER.debug(f"user: {update.message.chat.id} in {message_type}: '{text}'")

    if message_type == "group":
        if USERNAME in text:
            new_text: str = text.replace(USERNAME, "").strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)

    await update.message.reply_text(response, parse_mode=ParseMode.HTML)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    LOGGER.error("Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.

    update_str = update.to_dict() if isinstance(update, Update) else str(update)

    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    await context.bot.send_message(
        chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML
    )


async def log_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """This logs the error from the bot to the console

    return: error log
    """
    LOGGER.error(f"Update: {update}\n\n caused error {context.error}")

TRADESTOKEN =range(1)
ANSWERBUYAMOUNT = range(1)
PRIVATEKEY, WALLETADDRESS = range(2)
PASTECONTRACTADDRESS = range(1)
REPLYDELTA = range(1)
TRANSFERTOKENADDRESS, TRANSFERTOADDRESS, TRANSFERAMOUNT = range(3)
TRADEWALLETNAME, TARGETWALLET = range(2)
CHATCHIT = range(1)
CHATSLIP = range(1)
CHATAMMOUNT = range(1)
CHATGAS = range(1)
CHATLIMIT =range(1)
CHATPROFIT = range(1)
CHATLOSS = range(1)
RENAME = range(1)
SNIPERADDRESS, EDITGASDELTA, EDITETHAMOUNT, EDITTOKENAMOUNT, EDITSLIPPAGE, EDITBLOCKDELAY = range(6)
def main() -> None:
    LOGGER.info(TOKEN)
    LOGGER.info(USERNAME)
    LOGGER.info("Starting the YangTrading Bot")
    app = Application.builder().token(TOKEN).build()
    LOGGER.info("App initialized")

    LOGGER.info("Commands Ready")
    # Buy and Sell Conversation
    buysel_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_quick_callback, pattern=r"^buysell_quick")
        ],
        states={
            PASTECONTRACTADDRESS: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_attachment$")), reply_buysell_address)],
        },
        fallbacks=[CommandHandler("cancel_buysell", cancel_buysell)]
    )
    app.add_handler(buysel_conv_handler)

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("terms", terms_command))
    app.add_handler(CommandHandler("menu", help_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("language", language_command))

    # TERMS BUTTON CALLBACK
    app.add_handler(CallbackQueryHandler(terms_button_callback, pattern=r"^terms_*"))

    # LANGUAGE BUTTON CALLBACK
    app.add_handler(
        CallbackQueryHandler(language_button_callback, pattern=r"^language_*")
    )

    # CONFIGURATION BUTTON CALLBACK
    app.add_handler(CallbackQueryHandler(configuration_next_and_back_callback, pattern=r"^presets_*"))

    # SNIPER BUTTON CALLBACK
    app.add_handler(CallbackQueryHandler(delete_sniper_callback, pattern=r"^sniper_*"))



    # START BUTTON CALLBACKS
    app.add_handler(CallbackQueryHandler(start_button_callback, pattern=r"^start_*"))
    app.add_handler(CallbackQueryHandler(home_button_callback, pattern=r"^home$"))
    app.add_handler(CallbackQueryHandler(back_button_callback, pattern=r"^direct_left$"))
    
    # TRANSFER TOKEN CALLBACK
    app.add_handler(CallbackQueryHandler(transfer_callback, pattern=r"^transfer_chain_*"))
    

    #
    app.add_handler(CallbackQueryHandler(trades_next_and_back_callback, pattern=r"^trades_*"))

    # Copy Trading callback
    app.add_handler(CallbackQueryHandler(copy_trade_next_and_back_callback, pattern=r"^copy_*"))
    #profit
    Ask_Profit = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(AskProfit2, pattern=r"^ask_Profit$")

        ],
        states={
            CHATPROFIT: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_copy$")), AskProfit)],
        },
        fallbacks=[CommandHandler("cancel_copy", cancel_ammount)]
    )
    app.add_handler(Ask_Profit)
    #loss
    Ask_Loss = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(AskLoss2, pattern=r"^ask_Loss$")

        ],
        states={
            CHATLOSS: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_copy$")), AskLoss)],
        },
        fallbacks=[CommandHandler("cancel_copy", cancel_ammount)]
    )
    app.add_handler(Ask_Loss)
    #limit_Ammout
    Ask_Limit_Ammout = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(AskLimitammount2, pattern=r"^ask_buyammount$")

        ],
        states={
            CHATAMMOUNT: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_copy$")), AskLimitammount)],
        },
        fallbacks=[CommandHandler("cancel_copy", cancel_ammount)]
    )
    app.add_handler(Ask_Limit_Ammout)
    #limit
    Ask_Limit = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(AskLimit2, pattern=r"^ask_Limit$")

        ],
        states={
            CHATLIMIT: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_copy$")), AskLimit)],
        },
        fallbacks=[CommandHandler("cancel_copy", cancel_ammount)]
    )
    app.add_handler(Ask_Limit)
    #gas
    Ask_gas = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(AskGas2, pattern=r"^ask_gasdelta$")

        ],
        states={
            CHATGAS: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_copy$")), AskGas)],
        },
        fallbacks=[CommandHandler("cancel_copy", cancel_ammount)]
    )
    app.add_handler(Ask_gas)

    # Slippage
    Ask_slippage = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(AskSlippage2, pattern=r"^ask_slippage$")

        ],
        states={
            CHATSLIP: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_copy$")), AskSlippage)],
        },
        fallbacks=[CommandHandler("cancel_copy", cancel_ammount)]
    )
    app.add_handler(Ask_slippage)
    # Ammount
    Ask_ammount = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(AskAmmount2, pattern=r"^ask_buyamount$")

        ],
        states={
            CHATCHIT: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_copy$")), AskAmmount)],
        },
        fallbacks=[CommandHandler("cancel_copy", cancel_ammount)]
    )
    app.add_handler(Ask_ammount)
    # TRANSFER HANDLERS
    copytrade_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(copy_trade_start_callback, pattern=r"^trade_address$")
        ],
        states={
            TRADEWALLETNAME: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_copy$")), target_token_address_reply)],
            TARGETWALLET: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_copy$")), submit_copy_reply)],
        },
        fallbacks=[CommandHandler("cancel_copy", cancel_copy)]
    )
    app.add_handler(copytrade_conv_handler)
    #TRADES HANDLERS
    trades_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(trades_start_callback, pattern=r"^asktrade_address$")
        ],
        states={
            TRADESTOKEN: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_copy$")), submit_trades_reply)],
        },
        fallbacks=[CommandHandler("cancel_copy", cancel_copy)]
    )
    app.add_handler(trades_handler)

    # CONVERSATION HANDLERS
    attach_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(wallets_chain_attach_callback, pattern=r"^connect_attach")
        ],
        states={
            PRIVATEKEY: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_attachment$")), reply_wallet_attach)],
            WALLETADDRESS: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_attachment$")), reply_wallet_attach_address)],
        },
        fallbacks=[CommandHandler("cancel_attachment", cancel_attachment)]
    )
    app.add_handler(attach_conv_handler)
    
    # BUY ETH CONVERSATION HANDLERS
    buy_xeth_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(buy_callback, pattern=r"^buy_xeth$")
        ],
        states={
            ANSWERBUYAMOUNT: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_buysell$")), reply_buysell_amount)],
        },
        fallbacks=[CommandHandler("cancel_buysell", cancel_buysell)]
    )
    app.add_handler(buy_xeth_conv_handler)


    token_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(buy_callback, pattern=r"^buy_token$")
        ],
        states={
            ANSWERBUYAMOUNT: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_buysell$")), reply_buysell_amount)],
        },
        fallbacks=[CommandHandler("cancel_buysell", cancel_buysell)]
    )
    app.add_handler(token_conv_handler)


    # SELL ETH CONVERSATION HANDLERS
    sell_xeth_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(sell_callback, pattern=r"^sell_xeth$")
        ],
        states={
            ANSWERBUYAMOUNT: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_buysell$")), reply_buysell_amount)],
        },
        fallbacks=[CommandHandler("cancel_buysell", cancel_buysell)]
    )
    app.add_handler(sell_xeth_conv_handler)

    maxtx_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(sell_callback, pattern=r"^sell_selltoken$")
        ],
        states={
            ANSWERBUYAMOUNT: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_buysell$")), reply_buysell_amount)],
        },
        fallbacks=[CommandHandler("cancel_buysell", cancel_buysell)]
    )
    app.add_handler(maxtx_conv_handler)



    # SNIPER CONVERSATION HANDLERS
    sniper_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(delete_conversation_sniper_callback, pattern=r"^conversation_sniper_*")
        ],
        states={
            SNIPERADDRESS: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_sniper$")), add_sniper_address)],
            EDITGASDELTA: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_sniper$")), sniper_gas_delta_reply)],
            EDITETHAMOUNT: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_sniper$")), sniper_eth_amount_reply)],
            EDITTOKENAMOUNT: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_sniper$")), sniper_token_amount_reply)],
            EDITSLIPPAGE: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_sniper$")), sniper_slippage_reply)],
            EDITBLOCKDELAY: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_sniper$")), sniper_blockdelay_reply)],
        },
        fallbacks=[CommandHandler("cancel_sniper", cancel_sniper)]
    )
    app.add_handler(sniper_conv_handler)
    
    
    # COPY TRADE ADDRESS RENAME HANDLERS
    rename_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(copy_trade_rename, pattern=r'^rename_*')
        ],
        states={
            RENAME: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_rename$")), answer_rename)],
        },
        fallbacks=[CommandHandler("cancel_rename", cancel_rename)]
    )
    app.add_handler(rename_conv_handler)



    # TRANSFER HANDLERS
    transfer_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(token_callback, pattern=r"^transfer_*")
        ],
        states={
            TRANSFERTOKENADDRESS: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_transfer$")), token_address_reply)],
            TRANSFERTOADDRESS: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_transfer$")), to_address_reply)],
            TRANSFERAMOUNT: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_transfer$")), token_amount_reply)],
        },
        fallbacks=[CommandHandler("cancel_transfer", cancel_transfer)]
    )
    app.add_handler(transfer_conv_handler)



    # PRESETS HANDLERS
    preset_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(configuration_button_callback, pattern=r"^config_*")
        ],
        states={
            REPLYDELTA: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_preset$")), reply_preset_response)],
        },
        fallbacks=[CommandHandler("cancel_preset", cancel_preset)]
    )
    app.add_handler(preset_conv_handler)

    
    
    # buy callbacks
    app.add_handler(CallbackQueryHandler(buy_callback, pattern=r"^buy_*"))
    
    # sell callback
    app.add_handler(CallbackQueryHandler(sell_callback, pattern=r"^sell_*"))

    

    # WALLETS CONNECT OR CREATE CALLBACKS
    app.add_handler(CallbackQueryHandler(wallets_asset_chain_button_callback, pattern=r"^asset_chain_*"))
    app.add_handler(
        CallbackQueryHandler(wallets_chain_button_callback, pattern=r"^chain_*")
    )
    app.add_handler(
        CallbackQueryHandler(
            wallets_chain_connect_button_callback, pattern=r"^connect_*"
        )
    )
    
    
    
    

    # handle messages
    LOGGER.info("Message handler initiated")
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # error commands
    app.add_error_handler(log_error)
    app.add_error_handler(error_handler)

    LOGGER.info("Hit Ctrl + C to terminate the server")
    app.run_polling(allowed_updates=Update.ALL_TYPES)



if __name__ == "__main__":
    main()
