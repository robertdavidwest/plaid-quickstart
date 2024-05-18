const Sequelize = require("sequelize");
const db = require("../db");

const Balance = db.define("balance", {
  available: {
    type: Sequelize.DECIMAL,
    allowNull: false
  },
  current: {
    type: Sequelize.DECIMAL,
    allowNull: false
  },
  iso_currency_code: {
    type: Sequelize.STRING,
    allowNull: false
  },
  limit: {
    type: Sequelize.DECIMAL,
    allowNull: false
  },
  unofficial_currency_code: {
    type: Sequelize.STRING,
    allowNull: false
  }
});

module.exports = Balance;
