import nest_asyncio
nest_asyncio.apply()

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, CallbackQueryHandler, filters
import requests
import asyncio
import logging
import json

# # Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(name)

# Constants
API_URL = "https://valley-zu-reservation-starts.trycloudflare.com"
HUMAN_EXPERT_TGID = "@vdyshlyuk"
YOUR_TOKEN = "6649231948:AAHwFKlsJKO6jYrYMpXE141I6ISTyJbnyl0"
EXPERT_CHAT_ID = "1058344593"

YES_NO_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("Yes", callback_data='yes'), InlineKeyboardButton("No", callback_data='no')]
])

async def start(update: Update, context: CallbackContext) -> None:
    """Sends a welcome message and asks the user to ask a question."""
    await update.message.reply_text(
        "Hello! I am your assistant. Please ask your question by typing it directly into this chat."
    )

async def ask_question(update: Update, context: CallbackContext) -> None:
    """Sends the user's question to the API and handles the response."""
    question = update.message.text
    context.user_data['question'] = question

    response = requests.get(f"{API_URL}/ask?query={question}")
    data = response.json()
    answer = data.get('answer_text', 'No answer found.')

    await update.message.reply_text(answer)
    await update.message.reply_text("Did this answer help you?", reply_markup=YES_NO_KEYBOARD)

async def handle_callback(update: Update, context: CallbackContext) -> None:
    """Handles Yes/No callback from Inline Keyboard."""
    query = update.callback_query
    await query.answer()

    if query.data == 'yes':
        await query.edit_message_text(text="Happy to help! Feel free to ask another question.", reply_markup=None)
    elif query.data == 'no':
        question = context.user_data.get('question')
        response = requests.get(f"{API_URL}/clarify?question={question}")
        data = response.json()
        similar_questions = json.loads(data)
        keyboard = [[InlineKeyboardButton(str(index+1), callback_data=str(index))] for index in range(len(similar_questions))]
        keyboard.append([InlineKeyboardButton("None of these", callback_data='none')])

        message_text = "Choose the question most similar to yours:\n" + \
                       '\n'.join(f"{idx+1}. {q}" for idx, q in enumerate(similar_questions))
        await query.edit_message_text(text=message_text, reply_markup=InlineKeyboardMarkup(keyboard))


async def handle_question_selection(update: Update, context: CallbackContext) -> None:
    """Handles the selection of similar questions."""
    query = update.callback_query
    await query.answer()

    if query.data == 'none':
        # Collect user information
        user = update.effective_user  # This is the user who initiated the update
        user_first_name = user.first_name if user.first_name else 'Unknown First Name'
        user_last_name = user.last_name if user.last_name else 'Unknown Last Name'
        user_id = user.id if user.id else 'Unknown ID'
        full_name = f"{user_first_name} {user_last_name}"
        user_username = f"@{user.username}" if user.username else 'Username not set'

        # Notify the user that an expert will be contacted
        await query.edit_message_text(
            text=f"Here is the TG ID of a human expert {HUMAN_EXPERT_TGID}. "
                 "I have informed them about your query. They will contact you as soon "
                 "as possible or you can contact them by yourself. Feel free to ask other questions.", reply_markup=None
                
        )

        # Send message to the expert about the user's question
        expert_chat_id = EXPERT_CHAT_ID  # Replace this with your expert's actual chat_id
        user_question = context.user_data.get('question', 'No specific question recorded.')
        message_for_expert = (
            f"A user has requested assistance:\n\n"
            f"Name: {full_name}\n"
            f"Telegram ID: {user_id}\n"
            f"Question: {user_question}\n\n"
            f"Username: {user_username}\n\n"
            "Please respond to the user soon."
        )
        await context.bot.send_message(
            chat_id=expert_chat_id,
            text=message_for_expert
        )

    else:
        num_quest = int(query.data)
        response = requests.get(f"{API_URL}/clarify?question={context.user_data['question']}").json()
        question = json.loads(response)[num_quest]
        print(question)
        answer =requests.get(f"{API_URL}/ask?query={question}").json()['answer_text']
        await query.edit_message_text(answer)
        await query.message.reply_text("Did this answer help you?", reply_markup=YES_NO_KEYBOARD)

async def main():
    """Start the bot."""
    application = Application.builder().token(YOUR_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ask_question))
    application.add_handler(CallbackQueryHandler(handle_callback, pattern='^(yes|no)$'))
    application.add_handler(CallbackQueryHandler(handle_question_selection, pattern=r'^\d+|none$'))

    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())