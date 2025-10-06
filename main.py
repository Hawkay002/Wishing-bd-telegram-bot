import asyncio
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, ContextTypes, CommandHandler,
    MessageHandler, CallbackQueryHandler, filters
)

# === Bot Configuration ===
TOKEN = "8252936732:AAHVgIDlVwAlWi4HSywj7nVO6sIJWB_v0NM"
IMAGE_PATH = "Wishing Birthday.png"          # must be in same folder
TRIGGER_MESSAGE = "10/10/2002"
AUTHORIZED_NUMBERS = ["+918777072747", "+918777845713","+918276829124"]  # allowed numbers
ADMIN_CHAT_ID = 1299129410
START_TIME = time.time()

# === User states ===
user_states = {}  # user_id -> "awaiting_contact", "awaiting_name", None


# === Helper: Main Info Menu Buttons ===
def get_main_menu():
    keyboard = [
        [
            InlineKeyboardButton("📜 Bot Info", callback_data="info"),
            InlineKeyboardButton("💬 Description", callback_data="description"),
        ],
        [
            InlineKeyboardButton("👤 Master", callback_data="master"),
            InlineKeyboardButton("⏱ Uptime", callback_data="uptime"),
        ],
        [
            InlineKeyboardButton("🌐 Master’s Socials", callback_data="socials"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# === /start Command ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Send the secret word you just copied to get your card! ❤️❤️❤️")


# === Handle Messages ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip().lower()

    # Step 1: If awaiting name confirmation
    if user_states.get(user_id) == "awaiting_name":
        if text == "y":
            await update.message.reply_text("✅ Identity confirmed! Preparing your card... 💫")
            del user_states[user_id]
            await asyncio.sleep(2.5)

            await update.message.reply_photo(
                photo=open(IMAGE_PATH, "rb"),
                caption="🎁 Your card is ready — Tap to reveal!",
                has_spoiler=True
            )

            keyboard = [
                [
                    InlineKeyboardButton("1 ⭐", callback_data="rating_1"),
                    InlineKeyboardButton("2 ⭐", callback_data="rating_2"),
                    InlineKeyboardButton("3 ⭐", callback_data="rating_3"),
                    InlineKeyboardButton("4 ⭐", callback_data="rating_4"),
                    InlineKeyboardButton("5 ⭐", callback_data="rating_5"),
                ]
            ]
            await update.message.reply_text("Please rate your experience:", reply_markup=InlineKeyboardMarkup(keyboard))

        elif text == "n":
            await update.message.reply_text("🚫 Sorry! You're not authorized to perform this action.")
            del user_states[user_id]
        else:
            await update.message.reply_text('Please reply with "Y" for yes or "N" for no.')
        return

    # Step 2: If awaiting contact
    if user_states.get(user_id) == "awaiting_contact":
        await update.message.reply_text('Please use the "Share Contact" button to send your number.')
        return

    # Step 3: Trigger message received
    if text == TRIGGER_MESSAGE.lower():
        # Step 3a: First two database messages
        await update.message.reply_text("🔍 Checking database to find matches...")
        await asyncio.sleep(1.5)
        await update.message.reply_text("⌛ Waiting to receive response...")
        await asyncio.sleep(1.5)

        # Step 3b: Ask user to share phone number
        contact_button = KeyboardButton(text="Share Contact", request_contact=True)
        reply_markup = ReplyKeyboardMarkup([[contact_button]], one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("Please share your phone number to continue:", reply_markup=reply_markup)

        user_states[user_id] = "awaiting_contact"
        return

    # Step 4: Other messages
    await update.message.reply_text("I only respond to the specific trigger message.")
    await update.message.reply_text("You can check out more details below 👇", reply_markup=get_main_menu())


# === Handle Contact ===
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    contact = update.message.contact

    if contact:
        user_number = contact.phone_number
        # Normalize both sides (remove any leading +)
        authorized_normalized = [num.lstrip("+") for num in AUTHORIZED_NUMBERS]
        user_number_normalized = user_number.lstrip("+")
        
        if user_number_normalized in authorized_normalized:
            # Step 3c: Remaining database messages after phone verification
            await update.message.reply_text("📞 Checking back with your number...")
            await asyncio.sleep(1.5)
            await update.message.reply_text("🔐 Authenticating...")
            await asyncio.sleep(1.5)

            # Ask for name confirmation
            await update.message.reply_text(
                'As per matches found in database, are you *Pratik Roy*?\nReply "Y" for yes and "N" for no.',
                parse_mode="Markdown"
            )
            user_states[user_id] = "awaiting_name"
        else:
            await update.message.reply_text("🚫 Sorry! You're not authorized to perform this action.")
            if user_id in user_states:
                del user_states[user_id]


# === Handle Ratings ===
async def handle_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    rating = query.data.split("_")[1]
    username = query.from_user.username or query.from_user.first_name
    user_chat_id = query.message.chat.id

    await query.edit_message_text(f"Thank you for your rating of {rating} ⭐!")

    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"User @{username} (ID: {user_chat_id}) rated {rating} ⭐"
    )


# === Handle Info Buttons ===
async def handle_info_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back_to_menu")]])

    uptime_seconds = int(time.time() - START_TIME)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{hours}h {minutes}m {seconds}s"

    if data == "info":
        text = (
            "🤖 *Bot Info*\n\n"
            "This bot was specially made for sending personalized *birthday wish cards* "
            "to that person who deserves a surprise 🎉🎂."
        )
        await query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=back_markup)

    elif data == "description":
        text = (
            "💬 *Description*\n\n"
            "A fun, interactive bot built to deliver surprise birthday wishes with love 💫"
        )
        await query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=back_markup)

    elif data == "master":
        text = "👤 *Master*\n\nMade by **Shovith (Sid)** ✨"
        await query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=back_markup)

    elif data == "uptime":
        text = f"⏱ *Uptime*\n\nYou've been using this bot for past `{uptime_str}`."
        await query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=back_markup)

    elif data == "socials":
        keyboard = [
            [
                InlineKeyboardButton("WhatsApp", url="https://wa.me/918777845713"),
                InlineKeyboardButton("Telegram", url="https://t.me/X_o_x_o_002"),
            ],
            [
                InlineKeyboardButton("Website", url="https://hawkay002.github.io/Connect/"),
            ],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="*🌐 Master’s Socials*\n\nChoose a platform to connect:",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

    elif data == "back_to_menu":
        await query.edit_message_text(
            text="You can check out more details below 👇",
            reply_markup=get_main_menu()
        )


# === Run Bot ===
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(CallbackQueryHandler(handle_rating, pattern="^rating_"))
    app.add_handler(CallbackQueryHandler(handle_info_buttons))

    print("Bot is running...")
    app.run_polling()
