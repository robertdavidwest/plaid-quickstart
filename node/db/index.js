const db = require("./db");

const User = require("./models/User");
const AccessToken = require("./models/AccessToken");
const Item = require("./models/Item");
const Institution = require("./models/Institution");
const Transaction = require("./models/Transaction");
const Balance = require("./models/Balance");
const Account = require("./models/Account");

User.hasMany(AccessToken);
AccessToken.hasOne(Item);
Item.hasMany(Institution);
Item.hasMany(Account);
Account.hasMany(Transaction);
Account.hasMany(Balance);

module.exports = {
  db,
  models: {
    User,
    AccessToken,
    Item,
    Institution,
    Transaction
  },
};
