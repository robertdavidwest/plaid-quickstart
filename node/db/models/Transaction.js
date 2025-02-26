const Sequelize = require("sequelize");
const db = require("../db");

const Transaction = db.define("transaction", {
  amount: {
    type: Sequelize.DECIMAL,
    allowNull: false
  },
  date: {
    type: Sequelize.DATE,
    allowNull: false
  },
  name: {
    type: Sequelize.STRING,
    allowNull: false
  },
  merchant_name: {
    type: Sequelize.STRING,
    allowNull: true
  },
  primary_category: {
    type: Sequelize.STRING,
    allowNull: true
  },
  detailed_category: {
    type: Sequelize.STRING,
    allowNull: true
  },
  transaction_id: {
    type: Sequelize.STRING,
    allowNull: false
  },
});

module.exports = Transaction;
