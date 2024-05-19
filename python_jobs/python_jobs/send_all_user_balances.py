import os
from dotenv import load_dotenv, find_dotenv

import plaid
from plaid.api import plaid_api
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest

from lib.postgres import PostgresManager
from lib.telegram import send_message

load_dotenv(find_dotenv())


PLAID_ENV = os.environ['PLAID_ENV']
PLAID_CLIENT_ID = os.environ['PLAID_CLIENT_ID']
PLAID_SECRET = os.environ['PLAID_SECRET']

if PLAID_ENV == 'sandbox':
    host = plaid.Environment.Sandbox

if PLAID_ENV == 'development':
    host = plaid.Environment.Development

if PLAID_ENV == 'production':
    host = plaid.Environment.Production


configuration = plaid.Configuration(
    host=host,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
        'plaidVersion': '2020-09-14'
    }
)


def accounts_balance_get_request(client, access_token):
    request = AccountsBalanceGetRequest(access_token=access_token)
    response = client.accounts_balance_get(request)
    accounts = response['accounts']
    return accounts


def get_user_access_tokens(db, user_id):
    query = f"""
                SELECT access_token 
                FROM access_tokens
                WHERE "userId" = {user_id}
            """
    results = db.select(query)
    access_tokens = [x["access_token"] for x in results]
    return access_tokens


def get_all_users(db):
    query = """SELECT "firstName", "id", "telegramChatId" from users"""
    users = db.select(query)
    return users


def get_user_accounts(db, client, user_id):
    access_tokens = get_user_access_tokens(db, user_id)
    
    all_accounts = []
    for token in access_tokens:
        accounts = accounts_balance_get_request(client, token)
        all_accounts.extend(accounts)
    return all_accounts


def create_message(all_accounts):
    messages = []
    for account in all_accounts:
        name = account['name']
        balance = account['balances']['current']
        msg = "{} Balance: ${:,.2f}".format(name, balance)
        messages.append(msg)

    total = sum([account['balances']['current'] for account in all_accounts])
    messages.append("---------")
    messages.append("Total Net Balance: ${:,.2f}".format(total))
    return "\n".join(messages)


def attempt_send_user_balance(db, client, user):
    try:
        user_id = user['id']
        chat_id = user['telegramChatId']
        if not chat_id:
            print(f"user {user_id} has no chat id, skipping")
            return
        
        all_accounts = get_user_accounts(db, client, user_id)
        msg = create_message(all_accounts)
        send_message(chat_id, msg)
    except Exception as e:
        if os.environ['PYTHON_JOBS_DEBUG'] == 'true':
            raise e
        print(f"Error: {e}")


def main():
    db = PostgresManager(os.environ['DATABASE_URL'])
    api_client = plaid.ApiClient(configuration)
    client = plaid_api.PlaidApi(api_client)
    users = get_all_users(db)
    for user in users:
        attempt_send_user_balance(db, client, user)
    
    db.close()


if __name__ == '__main__':
    main()
