import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters

# Bot configuration
TOKEN = "8252936732:AAGYulWg2cnqnZ2iyd4ypbpskO1v9qHabwY"
IMAGE_PATH = "Wishing Birthday.png"  # make sure this file is uploaded in same folder
TRIGGER_MESSAGE = "10/10/2002"
ADMIN_CHAT_ID = 1299129410  # your own chat ID to receive ratings

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Send the secret word you just copied to get your card! ❤️❤️❤️")

# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()

    if text == TRIGGER_MESSAGE.lower():
        # Step 1: Send loading message
        loading_message = await update.message.reply_text("Preparing your card... Please wait 💫")
        await asyncio.sleep(2.5)  # simulate loading

        # Step 2: Delete loading message and send spoiler image
        await loading_message.delete()
        await update.message.reply_photo(
            photo=open(IMAGE_PATH, "rb"),
            caption="🎁 Your card is ready — Tap to reveal!",
            has_spoiler=True
        )

        # Step 3: Send rating buttons
        keyboard = [
            [
                InlineKeyboardButton("1 ⭐", callback_data="rating_1"),
                InlineKeyboardButton("2 ⭐", callback_data="rating_2"),
                InlineKeyboardButton("3 ⭐", callback_data="rating_3"),
                InlineKeyboardButton("4 ⭐", callback_data="rating_4"),
                InlineKeyboardButton("5 ⭐", callback_data="rating_5"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Please rate your experience:", reply_markup=reply_markup)

    else:
        await update.message.reply_text("I only respond to the specific trigger message.")

# Rating handler
async def handle_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    rating = query.data.split("_")[1]
    username = query.from_user.username or query.from_user.first_name
    user_chat_id = query.message.chat.id

    # Thank the user
    await query.edit_message_text(f"Thank you for your rating of {rating} ⭐!")

    # Send admin a private message with feedback info
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"User @{username} (ID: {user_chat_id}) rated {rating} ⭐"
    )

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(CallbackQueryHandler(handle_rating))

    print("Bot is running...")
    app.run_polling()
