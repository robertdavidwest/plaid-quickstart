# Spirit Cat

A simple, no thrills app to help users track their finances

Built from Plaid's [quickstart repo](https://github.com/plaid/quickstart).

You will need a plaid development account to run this app in local development: https://dashboard.plaid.com/signin/

## Spirit Cat App - Local Development 

### 1. Clone the repository

```bash
git clone git@github.com:robertdavidwest/spirit-cat.git
cd spirit-cat
```

### 2. Set up your environment variables

```bash
cp .env.example .env
```

Copy `.env.example` to a new file called `.env` and fill out the environment variables inside.

* Server Environment Variables:
    * `DATABASE_URL` only needed in production. In Local dev will default to: `DATABASE_URL=postgres://localhost:5432/spirit_cat`
    * `JWT` - A secret key for JWT token generation for authentication

* Local Dev only Environment Variables:
    * `SEED` - If `SEED=true` then `node/scripts/seed.js` will run on app startup. 
    * `SAMPLE_SANDBOX_ACCESS_TOKEN` - A Plaid Sandbox Access token (You can generate this by using the app in local dev)
    * `SAMPLE_SANDBOX_ITEM_ID` - A Plaid Sandbox Access token (You can generate this by using the app in local dev)
    > Do not set any of these variables in production!

* Plaid Environment variables:
    * At minimum `PLAID_CLIENT_ID` and `PLAID_SECRET` must be filled out. Get your Client ID and secrets from
the dashboard: [https://dashboard.plaid.com/developers/keys](https://dashboard.plaid.com/developers/keys)
    * Only use the Sandbox credentials in local development, most banks will only work in production after being requested

> NOTE: `.env` files are a convenient local development tool. Never run a production application
> using an environment file with secrets in it.

### 3. Pre-requisites

- [npm](https://www.npmjs.com/get-npm)
- node >= 14,
- Your environment variables populated in `.env`
- postgresql local server

### 4. Create the database

On your local postgresql database server create the database `spirit_cat`:

```sql
postgres=# CREATE DATABASE spirit_cat;
```

### 4. Running the Api Server

Once started the api will be running on http://localhost:8000. 

```bash
$ cd ./node
$ npm install
$ ./start.sh
```

> The database will automatically be created from the sequelize schema and seeded by `script/seed.js`
 community-supported implementation of the Plaid Quickstart using the [Going.Plaid](https://github.com/viceroypenguin/Going.Plaid) client library can be found at [PlaidQuickstartBlazor](https://github.com/jcoliz/PlaidQuickstartBlazor). Note that Plaid does not provide first-party support for .NET client libraries and that this Quickstart and client library are not created, reviewed, or supported by Plaid. 

### 5. Running the frontend

```bash
$ cd ./frontend
$ npm ci
$ npm start
```

The frontend which will run on http://localhost:3000.

#### Logging in with Test credentials

In Sandbox, you can log in to any supported institution (except Capital One) using `user_good` as the username and `pass_good` as the password. If prompted to enter a 2-factor authentication code, enter `1234`.

In Production, use real-life credentials.

## Spirit Cat Telegram Bot 

You will need to create a telegram bot, find instructions online. 

Your users must manually opt in by messaging your bot on telegram

Define the env var `TELEGRAM_BOT_TOKEN` in your `.env` 

### Python Jobs `/python_jobs`

#### Local dev

You can create a python virtual environment for local dev, then install 
the requirements found in `python_jobs/requirements.txt`. 
Run any of the jobs locally using sandbox plaid data.

#### Scheduling 

You will need to decide for yourself what platform you want to use to deploy
and schedule these jobs. ([https://pythonanywhere.com](pythonanywhere.com) has 
a nice simple free scheduling service, 
and [https://www.render.com/](render.com/) allows you to create free cron jobs.

1. Schedule the job `get_telegram_chat_ids.py` to run at least once a day. 
   When new users sign up, they will need to manually message your bot in Telegram 
   (this prevents spam). Once they have done so, this script will pick up the
   chat id, then going forward you will be able to message the user from
   the telegram API.

2. Schedule the job `send_all_user_balances.py`. Users will receive balance
   statements for all linked accounts (if they have messaged your bot and the
   script in step 1 has been run after.
