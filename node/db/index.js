const db = require("./db");

const User = require("./models/User");
const AccessToken = require("./models/AccessToken");
const Item = require("./models/Item");
const Institution = require("./models/Institution");
const Transaction = require("./models/Transaction");
const TransactionCursor = require("./models/TransactionCursor");
const Balance = require("./models/Balance");
const Account = require("./models/Account");

User.hasMany(AccessToken);
AccessToken.hasOne(Item);
AccessToken.hasOne(TransactionCursor);
Item.hasMany(Institution);
Item.hasMany(Account);
Account.hasMany(Transaction);
Account.hasMany(Balance);

module.exports = {
  db,
  models: {
    User,
    AccessToken,
    TransactionCursor,
    Item,
    Institution,
    Transaction
  },
};
