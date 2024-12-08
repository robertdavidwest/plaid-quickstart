import os
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
import pandas as pd 
import numpy as np

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


def filter_transactions(df):
    df = df[
            df.detailed_category != 'LOAN_PAYMENTS_CREDIT_CARD_PAYMENT'
    ]
    return df


def get_transactions(db, access_token, start_date, end_date):
    query = f"""
        WITH 
            trans as (
                    select *,
                    (date AT TIME ZONE 'UTC' AT TIME ZONE 'America/New_York')::date as date_et
                    from transactions
            )

        SELECT amount, t.name, date_et, a.type as account_type,
            primary_category, detailed_category
        FROM trans t
        JOIN accounts a ON t."accountId" = a.id
        JOIN items i ON a."itemId" = i.id
        JOIN access_tokens at ON i."accessTokenId" = at.id

        WHERE date_et BETWEEN '{start_date}' AND '{end_date}'
        AND
          at.access_token = '{access_token}'
    """
    results = db.select(query)
    df = pd.DataFrame(results)
    columns = ['amount', 'name', 'date_et', 'account_type', 
        'primary_category', 'detailed_category']
    if len(df) == 0:
        return pd.DataFrame(columns=columns)
    df.columns = columns
    df = filter_transactions(df)
    df['amount'] = - df['amount']
    return df 


def get_pending_transactions(db, access_token):
    query = f"""
        WITH 
            pending as (
                    select *,
                    (date AT TIME ZONE 'UTC' AT TIME ZONE 'America/New_York')::date as date_et
                    from pending_transactions
            )

        SELECT amount, p.name, date_et, a.type as account_type,
            primary_category, detailed_category
        FROM pending p
        JOIN accounts a ON p."accountId" = a.id
        JOIN items i ON a."itemId" = i.id
        JOIN access_tokens at ON i."accessTokenId" = at.id

        WHERE at.access_token = '{access_token}'
    """
    results = db.select(query)
    df = pd.DataFrame(results)
    columns = ['amount', 'name', 'date_et', 'account_type', 
        'primary_category', 'detailed_category']
    if len(df) == 0:
        return pd.DataFrame(columns=columns)
    df.columns = columns
    df = filter_transactions(df)
    df['amount'] = - df['amount']
    return df


def get_all_users(db):
    query = """SELECT "firstName", "id", "telegramChatId", "telegramMonthlyChatId" from users"""
    users = db.select(query)
    return users


def get_all_account_transactions(db, user_id, start_date, end_date):
    access_tokens = get_user_access_tokens(db, user_id)
    all = [
        get_transactions(db, token, start_date, end_date)
        for token in access_tokens
    ]
    df = pd.concat(all, ignore_index=True)
    return df


def get_all_account_pending_transactions(db, user_id):
    access_tokens = get_user_access_tokens(db, user_id)
    all = [
        get_pending_transactions(db, token)
        for token in access_tokens
    ]
    df = pd.concat(all, ignore_index=True)
    return df


def category_summary(df):
    df['label'] = df['name']
    df['label'] = df['label'].apply(lambda x: 'amazon+food' if
                                    'amazon' in x.lower() else x)
    # df['label'] = np.where(df.amount.abs() < 100,
                           # df['detailed_category'], df['label'])
    df['label'] = np.where(df.amount.abs() < 100,   
                           "Items < $100", df['label'])
    df['label'] = df.label.str[:15]
    
    income = df[df.amount > 0 ].groupby(by='label', as_index=False)['amount'].sum()
    income = income.sort_values(by='amount', ascending=False)
    percent = income['amount']/income['amount'].sum()
    income['percent'] = percent.cumsum()

    expense = df[df.amount < 0 ].groupby(by='label', as_index=False)['amount'].sum()
    expense = expense.sort_values(by='amount', ascending=True)
    expense['amount'] = - expense['amount']
    percent = expense['amount']/expense['amount'].sum()
    expense['percent'] = percent.cumsum()
    
    income = income.reset_index(drop=True)
    expense = expense.reset_index(drop=True)

    return income, expense


def get_totals(df):
    total_earned = df[df['amount'] > 0]['amount'].sum()
    total_spent = df[df['amount'] < 0]['amount'].sum()
    net = total_earned + total_spent 
    return total_earned, total_spent, net


def attempt_send_user_summary(db, user, add_details,
                              start_date, end_date,
                              telegram_api_token,
                              telegramChatidFieldName):
    try:
        user_id = user['id']
        chat_id = user[telegramChatidFieldName]
        if not chat_id:
            print(f"user {user_id} has no chat id, skipping")
            return


        all_accounts_df = get_all_account_transactions(
            db, user_id, start_date, end_date
        )
        
        pending_df = get_all_account_pending_transactions(db, user_id)

        if len(all_accounts_df) == 0 and len(pending_df) == 0:
            print(f"user {user_id} has no transactions this month so far, "
                  "skipping")
            return
        

        date_range_str = f"{start_date} to {end_date}"
        msg = "Transaction Summary \n"
        msg += f"({date_range_str})\n"
        len_ = len(msg)
        msg += "-" * len_ + "\n"
        msg += "\n"

        if len(pending_df) > 0:
            msg += "Pending Transactions:\n"
            for i, row in pending_df.iterrows():
                msg += f"{row['name']}: ${row['amount']:,.2f}\n"
            msg += "\n"

        if len(all_accounts_df) > 0:
            earned, spent, net = get_totals(all_accounts_df)

            msg += f"Earned this month: ${earned:,.2f}\n"
            if spent < 0:
                msg += f"Spent this month: -${-spent:,.2f}\n"
            else:
                msg += f"Spent: ${spent:,.2f}\n"

        if len(pending_df) > 0:
            # total pending
            total_pending = pending_df['amount'].sum()
            msg += f"Total Pending: ${total_pending:,.2f}\n"
            
            net += total_pending
        
        if len(all_accounts_df) > 0:
            if net < 0:
                msg += f"Net: -${-net:,.2f}\n"
            else:
                msg += f"Net: ${net:,.2f}\n"
            msg += "\n\n"
        
        if add_details: 
            income_details, expense_details = category_summary(all_accounts_df)

            msg += "\n\n"
            msg += "Income Details\n"
            msg += "-" * len_ + "\n"
            for i, row in income_details.iterrows():
                msg += f"{row['label']}: ${row['amount']:,.2f} ({row['percent']:.0%})\n"
                msg += "\n"

            msg += "\n\n"
            msg += "Expense Details\n"
            msg += "-" * len_ + "\n"
            for i, row in expense_details.iterrows():
                msg += f"{row['label']}: ${row['amount']:,.2f} ({row['percent']:.0%})\n"
                msg += "\n"

        send_message(chat_id, msg, telegram_api_token)
    except Exception as e:
        if os.environ['PYTHON_JOBS_DEBUG'] == 'true':
            raise e
        print(f"Error: {e}")


def get_month_start_end_dates(num_months_ago, full_month):
    today = datetime.today() 
    day_num_months_ago = today - pd.DateOffset(months=num_months_ago)
    start_date = day_num_months_ago.replace(day=1).strftime("%Y-%m-%d")
    if full_month:
        end_date = (
                day_num_months_ago.replace(day=1) +
                pd.DateOffset(months=1) -
                pd.DateOffset(days=1)
                ).strftime("%Y-%m-%d")
    else:
        end_date = day_num_months_ago.strftime("%Y-%m-%d")
    return start_date, end_date


def main(telegram_api_token, add_details,
         num_months_ago, full_month,
         telegramChatidFieldName):
    start_date, end_date = get_month_start_end_dates(num_months_ago,
                                                     full_month)
    print(f"Sending user summary for {start_date} to {end_date}")
    print(f"Adding details: {add_details}")
    db = PostgresManager(os.environ['DATABASE_URL'])
    users = get_all_users(db)
    any_errors = False
    for user in users:
        error = attempt_send_user_summary(
                db, user, add_details,
                start_date, end_date, telegram_api_token,
                telegramChatidFieldName)
        if error:
            any_errors = True 
    if any_errors:
        raise Exception("There were errors sending user balances")

    db.close()


if __name__ == '__main__':
    telegram_api_token = os.environ["TELEGRAM_BOT_TOKEN"]
    add_details = False
    num_months_ago = 0
    full_month = False
    telegramChatidFieldName = "telegramChatId"
    main(telegram_api_token,
         add_details,
         num_months_ago,
         full_month,
         telegramChatidFieldName)
        
