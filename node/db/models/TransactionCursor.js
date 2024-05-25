const Sequelize = require("sequelize");
const db = require("../db");

const TransactionCursor = db.define("transaction_cursor", {
  transaction_cursor: {
    type: Sequelize.STRING,
    allowNull: false,
    defaultValue: "",
  },

});

module.exports = TransactionCursor;
