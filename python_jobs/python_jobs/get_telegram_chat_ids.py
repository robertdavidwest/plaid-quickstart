import os
from dotenv import load_dotenv, find_dotenv

from lib.postgres import PostgresManager
from lib.telegram import get_chat_id

load_dotenv(find_dotenv())


def get_users_with_no_telegram_chat_id(db):
    query = """
        SELECT "telegramHandle", "id" 
        FROM users 
        WHERE "telegramChatId" IS NULL
    """
    users = db.select(query)
    return users


def update_chat_id(db, user_id, chat_id):
    query = f"""
            UPDATE users
            SET "telegramChatId" = {chat_id}
            WHERE "id" = {user_id}
        """
    db.update(query)


def attempt_update_chat_id(db, user):
    try:
        telegram_handle = user['telegramHandle']
        user_id = user['id']
        chat_id = get_chat_id(telegram_handle)
        if chat_id is not None:
            update_chat_id(db, user_id, chat_id)
            print(f"Updated chat ID for {telegram_handle}")
        else: 
            print(f"Could not find chat ID for {telegram_handle}")
    except Exception as e:
        if os.environ['PYTHON_JOBS_DEBUG'] == 'true':
            raise e
        print(f"Error: {e}")


def main():
    db = PostgresManager(os.environ['DATABASE_URL'])
    users = get_users_with_no_telegram_chat_id(db)
    print(f"Found {len(users)} users with no chat ID")
    if len(users) != 0:
       print("Attempting to update chat IDs") 
    for user in users:
        attempt_update_chat_id(db, user)

    db.close()


if __name__ == '__main__':
    main()
