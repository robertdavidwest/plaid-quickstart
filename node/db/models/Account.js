const Sequelize = require("sequelize");
const db = require("../db");

const Account = db.define("account", {
  account_id: {
    type: Sequelize.STRING,
    allowNull: false
  },
  name: {
    type: Sequelize.STRING,
    allowNull: false
  },
  official_name: {
    type: Sequelize.STRING,
    allowNull: false
  },
});

module.exports = Account;
