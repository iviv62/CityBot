import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import time
import threading

# Replace with your actual bot token and the predefined user ID
TOKEN = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX' # Replace with your Telegram bot token
ADMIN_USER_ID = "XXXXXXX" # Replace with your Telegram admin user ID
TARGET_USER_ID = "XXXXXXXX" # Replace with the target user ID

conversation_mode = {}  
typing_status = {} 


def send_typing_indicator(context, chat_id, duration=2):
    """Send typing indicator for specified duration"""
    try:
        # Start typing indicator
        context.bot.send_chat_action(chat_id=chat_id, action="typing")
        # Keep it active for the specified duration
        time.sleep(duration)
    except Exception as e:
        print(f"Error sending typing indicator: {e}")

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! I'm your bot.")

def handle_message(update, context):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if chat_id in conversation_mode:
        # Conversation mode is active
        target_user_id = conversation_mode[chat_id]
        if user_id == ADMIN_USER_ID:
            sender_prefix = ""
        else:
            sender_prefix = ""

        # Handle text messages
        if update.message.text:
            # Show typing indicator before sending message
            send_typing_indicator(context, target_user_id)
            
            context.bot.send_message(
                chat_id=target_user_id,
                text=f"{sender_prefix}{update.message.text}"
            )
        
        # Handle photos
        if update.message.photo:
            # Show upload photo indicator
            context.bot.send_chat_action(chat_id=target_user_id, action="upload_photo")
            time.sleep(2)
            
            photo = update.message.photo[-1]
            caption = update.message.caption if update.message.caption else ""
            context.bot.send_photo(
                chat_id=target_user_id,
                photo=photo.file_id,
                caption=f"{sender_prefix}{caption}" if caption else sender_prefix.strip()
            )

    else:
        # Start conversation mode
        if user_id == ADMIN_USER_ID:
            conversation_mode[chat_id] = TARGET_USER_ID
            conversation_mode[TARGET_USER_ID] = chat_id
            send_typing_indicator(context, ADMIN_USER_ID)
            context.bot.send_message(chat_id=ADMIN_USER_ID, text=f"Conversation started with {TARGET_USER_ID}. Type messages to send.")
            send_typing_indicator(context, TARGET_USER_ID)
            context.bot.send_message(chat_id=TARGET_USER_ID, text="Conversation started. Please type your messages.")
        elif user_id == TARGET_USER_ID:
            conversation_mode[chat_id] = ADMIN_USER_ID
            conversation_mode[ADMIN_USER_ID] = chat_id
            send_typing_indicator(context, ADMIN_USER_ID)
            context.bot.send_message(chat_id=ADMIN_USER_ID, text=f"Conversation started with {TARGET_USER_ID}. Type messages to send.")
            send_typing_indicator(context, chat_id)
            context.bot.send_message(chat_id=chat_id, text="Hello! I'm your City Assistant. How can I assist you today?")

def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(
        (Filters.text | Filters.photo) & (~Filters.command),
        handle_message
    )

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(message_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()