import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

from send_all_user_summary import main


if __name__ == '__main__':
    telegram_api_token = os.environ["TELEGRAM_MONTHLY_BOT_TOKEN"]
    add_details = True
    num_months_ago = 1
    full_month = True
    telegramChatidFieldName = "telegramMonthlyChatId"
    main(telegram_api_token,
         add_details,
         num_months_ago,
         full_month,
         telegramChatidFieldName)

