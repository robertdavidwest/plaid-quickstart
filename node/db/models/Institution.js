const Sequelize = require("sequelize");
const db = require("../db");

const Institution = db.define("institution", {
  name: {
    type: Sequelize.STRING,
    unique: true,
    allowNull: false,
  },
  instituion_id: {
    type: Sequelize.STRING,
  }
});

module.exports = Institution;
