import os
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
import pandas as pd 

from lib.postgres import PostgresManager
from lib.telegram import send_message

load_dotenv(find_dotenv())


def get_user_access_tokens(db, user_id):
    query = f"""
                SELECT access_token 
                FROM access_tokens
                WHERE "userId" = {user_id}
            """
    results = db.select(query)
    access_tokens = [x["access_token"] for x in results]
    return access_tokens


def get_this_month_transactions(db, access_token):
    query = f"""
        WITH 
            trans as (
                    select *,
                    (date AT TIME ZONE 'UTC' AT TIME ZONE 'America/New_York')::date as date_et
                    from transactions
            )

        SELECT amount, t.name, date_et, a.type as account_type
        FROM trans t
        JOIN accounts a ON t."accountId" = a.id
        JOIN items i ON a."itemId" = i.id
        JOIN access_tokens at ON i."accessTokenId" = at.id

        WHERE date_et BETWEEN date_trunc('month', current_date )
               AND date_trunc('month', current_date) + interval '1 month' - interval '1 day'
        AND
          at.access_token = '{access_token}'
    """
    results = db.select(query)
    df = pd.DataFrame(results)
    df.columns = ['amount', 'name', 'date_et', 'account_type']
    
    # remove credit card payments from credit accounts
    credit_payment_idx = (
        (df['account_type'] == 'credit') & 
        (df['amount'] < 0) &
        (df['name'].str.lower().str.contains('payment'))
    )
    df = df[~credit_payment_idx]
    
    # remove credit card payments from depository accounts
    depo_payment_idx = (
        (df['account_type'] == 'depository') & 
        (df['amount'] > 0) &
        (df['name'].str.lower().str.contains('payment')) & 
        (df['name'].str.lower().str.contains('card'))
    )
    df = df[~depo_payment_idx]

    # alternative index for credit card payments from depository accounts
    depo_payment_idx2 = (
        (df['account_type'] == 'depository') & 
        (df['amount'] > 0) &
        (df['name'].str.lower().str.contains('credit')) & 
        (df['name'].str.lower().str.contains('crd')) &
        (df['name'].str.lower().str.contains('autopay'))
    )
    df = df[~depo_payment_idx2]

    # remove online transfers between accounts
    online_transfer_idx = (
        (df['name'].str.lower().str.contains('transfer')) &
        (df['name'].str.lower().str.contains('online'))
    )
    df = df[~online_transfer_idx]

    df['amount'] = - df['amount']

    return df 

    
def get_all_users(db):
    query = """SELECT "firstName", "id", "telegramChatId" from users"""
    users = db.select(query)
    return users


def get_all_account_this_month_transactions(db, user_id):
    access_tokens = get_user_access_tokens(db, user_id)
    all = [
        get_this_month_transactions(db, token)
        for token in access_tokens
    ]
    df = pd.concat(all, ignore_index=True)
    return df



def get_totals(df):
    total_earned = df[df['amount'] > 0]['amount'].sum()
    total_spent = df[df['amount'] < 0]['amount'].sum()
    net = total_earned + total_spent 
    return total_earned, total_spent, net



def attempt_send_user_month_summary(db, user):
    try:
        user_id = user['id']
        chat_id = user['telegramChatId']
        if not chat_id:
            print(f"user {user_id} has no chat id, skipping")
            return
        all_accounts_df = get_all_account_this_month_transactions(
            db, user_id
        )
        if len(all_accounts_df) == 0:
            print(f"user {user_id} has no transactions this month so far, "
                  "skipping")
            return

        earned, spent, net = get_totals(all_accounts_df)
        month_date = datetime.now().strftime("%B %Y")
        msg = f"Transaction Summary ({month_date})\n"
        len_ = len(msg)
        msg += "-" * len_ + "\n"
        msg += f"Earned this month: ${earned:,.2f}\n"
        if spent < 0:
            msg += f"Spent this month: -${-spent:,.2f}\n"
        else:
            msg += f"Spent: ${spent:,.2f}\n"
        if net < 0:
            msg += f"Net: -${-net:,.2f}\n"
        else:
            msg += f"Net: ${net:,.2f}\n"
        msg += "\n\n"
        msg += f"As of {datetime.now().strftime('%m/%d/%Y')}"
        send_message(chat_id, msg)
    except Exception as e:
        if os.environ['PYTHON_JOBS_DEBUG'] == 'true':
            raise e
        print(f"Error: {e}")


def main():
    db = PostgresManager(os.environ['DATABASE_URL'])
    users = get_all_users(db)
    any_errors = False
    for user in users:
        error = attempt_send_user_month_summary(db, user)
        if error:
            any_errors = True 
    if any_errors:
        raise Exception("There were errors sending user balances")

    db.close()


if __name__ == '__main__':
    main()
