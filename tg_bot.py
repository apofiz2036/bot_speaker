import logging
import os
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from google.cloud import dialogflow


class TelegramLogsHandler(logging.Handler):
    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Здравствуйте {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Help!')


def get_dialogflow_response(text, session_id, project_id):
    try:
        session_client = dialogflow.SessionsClient()
        session = session_client.session_path(project_id, session_id)

        text_input = dialogflow.TextInput(text=text, language_code="ru")
        query_input = dialogflow.QueryInput(text=text_input)

        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )

        return response.query_result.fulfillment_text
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Ошибка в Dialogflow: {e}")
        return 'Произошла ошибка'


def handle_message(update: Update, context: CallbackContext) -> None:
    try:
        user_text = update.message.text
        user_id = str(update.message.from_user.id)

        project_id = context.bot_data.get('project_id')
        bot_response = get_dialogflow_response(user_text, user_id, project_id)
        update.message.reply_text(bot_response)
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f'Ошибка при обработке сообщения: {e}')
        update.message.reply_text('Произошла ошибка')


def main() -> None:
    load_dotenv()
    TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_TOKEN']
    PROJECT_ID = os.environ['DIALOGFLOW_PROJECT_ID']
    TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.WARNING)

    file_handler = RotatingFileHandler('bot.log', maxBytes=20000, backupCount=2)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

    updater = Updater(TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher

    telegram_handler = TelegramLogsHandler(updater.bot, TELEGRAM_CHAT_ID)
    telegram_handler.setLevel(logging.ERROR)
    logger.addHandler(telegram_handler)
    dispatcher.bot_data['project_id'] = PROJECT_ID

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    try:
        logger.info('Бот запущен')
        updater.start_polling()
        updater.idle()
    except Exception as e:
        logger.error(f"Бот упал с ошибкой: {e}")


if __name__ == '__main__':
    main()
