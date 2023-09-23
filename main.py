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
    terms_button_callback,
    language_button_callback,
    home_button_callback,
    back_button_callback,
    
    configuration_next_and_back_callback,
    configuration_button_callback,
    reply_preset_response,
    cancel_preset,
    
    copy_trade_next_and_back_callback,
    copy_trade_rename,
    answer_rename,
    cancel_rename,
    copy_trade_start_callback,
    target_token_address_reply,
    submit_copy_reply,
    cancel_copy,
    
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
    cancel_attachment,
    
    delete_sniper_callback,
    add_sniper_address,
    sniper_gas_delta_reply,
    sniper_slippage_reply,
    sniper_token_amount_reply,
    sniper_eth_amount_reply,
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


PRIVATEKEY = range(1)
REPLYDELTA = range(1)
TOKENADDRESS, TOADDRESS, AMOUNT = range(3)
TRADEWALLETNAME, TARGETWALLET = range(2)
RENAME = range(1)
SNIPERADDRESS = range(1)
EDITGASDELTA = range(1)
EDITETHAMOUNT = range(1)
EDITTOKENAMOUNT = range(1)
EDITSLIPPAGE = range(1)

def main() -> None:
    LOGGER.info(TOKEN)
    LOGGER.info(USERNAME)
    LOGGER.info("Starting the YangTrading Bot")
    app = Application.builder().token(TOKEN).build()
    LOGGER.info("App initialized")

    LOGGER.info("Commands Ready")
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
    
    # Copy Trading callback
    app.add_handler(CallbackQueryHandler(copy_trade_next_and_back_callback, pattern=r"^copy_*"))
    
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

    # CONVERSATION HANDLERS
    attach_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(wallets_chain_attach_callback, pattern=r"^connect_attach")
        ],
        states={
            PRIVATEKEY: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_attachment$")), reply_wallet_attach)],
        },
        fallbacks=[CommandHandler("cancel_attachment", cancel_attachment)]
    )
    app.add_handler(attach_conv_handler)
    
    # SNIPER CONVERSATION HANDLERS
    sniper_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(delete_sniper_callback, pattern=r"^sniper_snipe$")
        ],
        states={
            SNIPERADDRESS: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_sniper$")), add_sniper_address)],
        },
        fallbacks=[CommandHandler("cancel_sniper", cancel_sniper)]
    )
    app.add_handler(sniper_conv_handler)
    
    edit_sniper_gasdelta_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(delete_sniper_callback, pattern=r"^sniper_gasdelta$")
        ],
        states={
            EDITGASDELTA: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_sniper$")), sniper_gas_delta_reply)],
        },
        fallbacks=[CommandHandler("cancel_sniper", cancel_sniper)]
    )
    app.add_handler(edit_sniper_gasdelta_conv_handler)

    edit_sniper_ethamount_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(delete_sniper_callback, pattern=r"^sniper_eth$")
        ],
        states={
            EDITETHAMOUNT: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_sniper$")), sniper_eth_amount_reply)],
        },
        fallbacks=[CommandHandler("cancel_sniper", cancel_sniper)]
    )
    app.add_handler(edit_sniper_ethamount_conv_handler)

    edit_sniper_tokenamount_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(delete_sniper_callback, pattern=r"^sniper_token$")
        ],
        states={
            EDITTOKENAMOUNT: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_sniper$")), sniper_token_amount_reply)],
        },
        fallbacks=[CommandHandler("cancel_sniper", cancel_sniper)]
    )
    app.add_handler(edit_sniper_tokenamount_conv_handler)

    edit_sniper_slippage_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(delete_sniper_callback, pattern=r"^sniper_slippage$")
        ],
        states={
            EDITSLIPPAGE: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_sniper$")), sniper_slippage_reply)],
        },
        fallbacks=[CommandHandler("cancel_sniper", cancel_sniper)]
    )
    app.add_handler(edit_sniper_slippage_conv_handler)
    
    

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
            TOKENADDRESS: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_transfer$")), token_address_reply)],
            TOADDRESS: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_transfer$")), to_address_reply)],
            AMOUNT: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel_transfer$")), token_amount_reply)],
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
