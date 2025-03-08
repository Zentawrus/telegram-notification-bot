from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os

load_dotenv()

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host='postgres'
    )

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome to the bot!")

def help_command(update: Update, context: CallbackContext):
    update.message.reply_text("Here are the available commands: /start, /help, /register, /status")


def register(update: Update, context: CallbackContext):
    user = update.message.from_user
    telegram_id = user.id
    username = user.username

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
       
        insert_query = sql.SQL("""
            INSERT INTO users (telegram_id, username)
            VALUES (%s, %s)
            ON CONFLICT (telegram_id) DO NOTHING;
        """)
        cursor.execute(insert_query, (telegram_id, username))
        connection.commit()
        update.message.reply_text("You have been registered successfully!")
    except Exception as e:
        update.message.reply_text(f"An error occurred: {e}")
    finally:
        cursor.close()
        connection.close()


def status(update: Update, context: CallbackContext):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT count(*) FROM users;")
    user_count = cursor.fetchone()[0]
    cursor.close()
    connection.close()

    update.message.reply_text(f"Total users in the database: {user_count}")


def main():
    updater = Updater(os.getenv('TELEGRAM_TOKEN'), use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("register", register))
    dp.add_handler(CommandHandler("status", status))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
