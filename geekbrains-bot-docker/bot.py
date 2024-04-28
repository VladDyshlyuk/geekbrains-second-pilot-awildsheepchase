from dotenv import load_dotenv
load_dotenv()

import nest_asyncio
nest_asyncio.apply()
import os
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
API_URL = os.getenv('API_URL')
HUMAN_EXPERT_USERNAME = os.getenv('USERNAME_EXPERT')
YOUR_TOKEN = os.getenv('BOT_TOKEN')
EXPERT_CHAT_ID = os.getenv('CHAT_ID_EXPERT')



YES_NO_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("Да", callback_data='yes'), InlineKeyboardButton("Нет", callback_data='no')]
])

async def start(update: Update, context: CallbackContext) -> None:
    
    await update.message.reply_text(
        "Привет! 👋 \n"
    "Я — ваш личный помощник от GeekBrains. Я здесь, чтобы помочь вам с навигацией по курсам, ответить на ваши вопросы о занятиях и "
    "предоставить необходимую информацию об обучении.\n\n"
    "Чем могу помочь сегодня? Вы можете спросить меня о расписании занятий, деталях курсов "
    "и многом другом. Просто введите свой вопрос, и я постараюсь помочь вам как можно скорее!\n\n"
    "Если хотите начать напишите свой вопрос. 📚🖊️"
    )

async def ask_question(update: Update, context: CallbackContext) -> None:
    
    question = update.message.text
    context.user_data['question'] = question

    response = requests.get(f"{API_URL}/ask?query={question}")
    data = response.json()
    answer = data.get('answer_text', 'Прошу прощения, ответ не был найден.')

    await update.message.reply_text(answer)
    await update.message.reply_text("Это то, что вас интересовало?", reply_markup=YES_NO_KEYBOARD)

async def handle_callback(update: Update, context: CallbackContext) -> None:

    query = update.callback_query
    await query.answer()

    if query.data == 'yes':
        await query.edit_message_text(text="Рад был помочь! Если у вас есть ещё вопросы, не стесняйтесь задавать их. 👍", reply_markup=None)
    elif query.data == 'no':

        question = context.user_data.get('question')
        response = requests.get(f"{API_URL}/clarify?question={question}")
        data = response.json()
        similar_questions = json.loads(data)
        keyboard = [[InlineKeyboardButton(str(index+1), callback_data=str(index))] for index in range(len(similar_questions))]
        keyboard.append([InlineKeyboardButton("Никакой не подходит", callback_data='none')])

        message_text = "Пожалуйста, выберите вопрос, наиболее схожий с вашим:\n" + \
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
            text=f"Вот Telegram ID нашего эксперта: {HUMAN_EXPERT_USERNAME}. Я уже сообщил им о вашем вопросе, и они свяжутся с вами в ближайшее время. Вы также можете написать им самостоятельно. Если у вас есть другие вопросы, не стесняйтесь задавать их – я здесь, чтобы помочь!", reply_markup=None
                
        )

        # Send message to the expert about the user's question
        expert_chat_id = EXPERT_CHAT_ID  # Replace this with your expert's actual chat_id
        user_question = context.user_data.get('question', 'Неизвестный вопрос.')
        message_for_expert = (
           f"Пользователь запросил помощь:\n\n"
            f"Имя: {full_name}\n"
            f"Телеграм-логин: {user_id}\n"
            f"Вопрос: {user_question}\n\n"
            f"Пожалуйста, ответьте пользователю в ближайшее время."
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
        await query.message.reply_text("Это то, что вас интересовало?", reply_markup=YES_NO_KEYBOARD)

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