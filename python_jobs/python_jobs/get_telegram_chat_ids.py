import os
from dotenv import load_dotenv, find_dotenv

from lib.postgres import PostgresManager
from lib.telegram import get_chat_id

load_dotenv(find_dotenv())



def get_users_with_no_telegram_chat_id(db, field_name):
    query = f"""
        SELECT "telegramHandle", "id" 
        FROM users 
        WHERE "{field_name}" IS NULL
    """
    users = db.select(query)
    return users


def update_chat_id(db, user_id, chat_id, field_name):
    query = f"""
            UPDATE users
            SET "{field_name}" = {chat_id}
            WHERE "id" = {user_id}
        """
    db.update(query)


def attempt_update_chat_id(db, user, telegram_api_token,
                           field_name):
    error = False
    try:
        telegram_handle = user['telegramHandle']
        user_id = user['id']
        chat_id = get_chat_id(telegram_handle,
                              telegram_api_token)
        if chat_id is not None:
            update_chat_id(db, user_id, chat_id, field_name)
            print(f"Updated chat ID for {telegram_handle}")
        else: 
            print(f"Could not find chat ID for {telegram_handle}")
    except Exception as e:
        if os.environ['PYTHON_JOBS_DEBUG'] == 'true':
            raise e
        print(f"Error: {e}")
        error = True

    return error


def get_users_chat_ids_for_this_token(db, telegram_api_token,
                                      field_name):
    users = get_users_with_no_telegram_chat_id(db, field_name)
    print(f"Found {len(users)} users with no chat ID")
    if len(users) != 0:
       print("Attempting to update chat IDs") 
    any_errors = False
    for user in users:
        error = attempt_update_chat_id(db, user,
                                       telegram_api_token,
                                       field_name)
        if error:
            any_errors = True
    
    if any_errors:
        raise Exception("There were errors updating chat IDs")



def main():
    db = PostgresManager(os.environ['DATABASE_URL'])
    telegram_api_tokens = [
        os.environ["TELEGRAM_BOT_TOKEN"],
        os.environ["TELEGRAM_MONTHLY_BOT_TOKEN"]
    ]
    chat_id_field_names = [
        "telegramChatId",
        "telegramMonthlyChatId"
    ]

    for field_name, token in zip(chat_id_field_names,
                                 telegram_api_tokens):
        get_users_chat_ids_for_this_token(db,
                                          token,
                                          field_name)
    db.close()


if __name__ == '__main__':
    main()
