import os
from dotenv import load_dotenv, find_dotenv
from datetime import datetime

import plaid
from plaid.api import plaid_api
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.item_get_request import ItemGetRequest
from plaid.model.institutions_get_by_id_request import InstitutionsGetByIdRequest
from plaid.model.country_code import CountryCode

from lib.postgres import PostgresManager
from lib.telegram import send_message

load_dotenv(find_dotenv())

institution_shorthands = {
    "American Express": "Amex",
}


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


def get_item_institution_id(client, access_token):
    request = ItemGetRequest(access_token=access_token)
    response = client.item_get(request)
    institution_id = response['item']['institution_id']
    return institution_id


def get_institution_name(client, access_token):
    institution_id = get_item_institution_id(client, access_token)
    request = InstitutionsGetByIdRequest(
        institution_id=institution_id,
        country_codes=[CountryCode('US')]
    )
    response = client.institutions_get_by_id(request)
    return response['institution']['name']


def accounts_balance_get_request(client, access_token):
    request = TransactionsSyncRequest(
        access_token=access_token,
        cursor='',
    )
    response = client.transactions_sync(request).to_dict()
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
        institution_name = get_institution_name(client, token)
        for account in accounts:
            account['institution_name'] = institution_name
        all_accounts.extend(accounts)
    return all_accounts


def create_message(all_accounts):
    today = datetime.today()
    formatted_date = today.strftime("%m/%d/%Y")

    messages = [
            f"Account Balances ({formatted_date})",
            "------------------------------"
            ]
    for account in all_accounts:
        name = account['institution_name']
        if account.get('official_name'):
            name += " " + account['official_name']
        else:
            name += " " + account['name']
        balance = account['balances']['current']
        if account['type'] == 'credit' and balance > 0:
            msg = "{}: -${:,.2f}".format(name, balance)
            account['balances']['current'] = -balance
        else:
            msg = "{}: ${:,.2f}".format(name, balance)
        messages.append(msg)

    total = sum([account['balances']['current'] for account in all_accounts])
    messages.append("----------------------------------")
    if total < 0:
        messages.append("Total Net Balance: -${:,.2f}".format(-total))
    else:
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
        for insitution in institution_shorthands:
            short = institution_shorthands[insitution]
            msg = msg.replace(insitution, short)
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
    any_errors = False
    for user in users:
        error = attempt_send_user_balance(db, client, user)
        if error:
            any_errors = True 
    if any_errors:
        raise Exception("There were errors sending user balances")

    db.close()


if __name__ == '__main__':
    main()
