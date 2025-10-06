import asyncio
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, ContextTypes, CommandHandler,
    MessageHandler, CallbackQueryHandler, filters
)

# === Bot Configuration ===
TOKEN = "8252936732:AAHVgIDlVwAlWi4HSywj7nVO6sIJWB_v0NM"
IMAGE_PATH = "Wishing Birthday.png"          # must be in same folder
TRIGGER_MESSAGE = "10/10/2002"
ADMIN_CHAT_ID = 1299129410
START_TIME = time.time()


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
    text = update.message.text.strip().lower()

    if text == TRIGGER_MESSAGE.lower():
        loading_message = await update.message.reply_text("Preparing your card... Please wait 💫")
        await asyncio.sleep(2.5)

        await loading_message.delete()
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

    else:
        await update.message.reply_text("I only respond to the specific trigger message.")
        await update.message.reply_text("You can check out more details below 👇", reply_markup=get_main_menu())


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

    # Helper for universal back button
    back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back_to_menu")]])

    # Calculate uptime
    uptime_seconds = int(time.time() - START_TIME)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{hours}h {minutes}m {seconds}s"

    # --- Individual Button Logic ---
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
        # Submenu for socials (with website link added)
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
    app.add_handler(CallbackQueryHandler(handle_rating, pattern="^rating_"))
    app.add_handler(CallbackQueryHandler(handle_info_buttons))

    print("Bot is running...")
    app.run_polling()
