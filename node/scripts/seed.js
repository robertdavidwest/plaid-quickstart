"use strict";

require('dotenv').config();
const {
  db,
  models: { User, AccessToken, Item, TransactionCursor},
} = require("../db");

/**
 * seed - this function clears the database, updates tables to
 *      match the models, and populates the database.
 */
async function seed() {
  await db.sync({ force: true }); // clears db and matches models to tables
  console.log("db synced!");

  const telegramHandle = process.env.EXAMPLE_TELEGRAM_HANDLE === undefined ? "example" : process.env.EXAMPLE_TELEGRAM_HANDLE;

  const user = await User.create({
    firstName: "robert",
    lastName: "west",
    email: "robert@robert.com",
    password: "123",
    telegramHandle
  });

  if (
    (process.env.SAMPLE_SANDBOX_ACCESS_TOKEN !== undefined)
    && (process.env.SAMPLE_SANDBOX_ITEM_ID !== undefined)
  ) {
    const access_token = await AccessToken.create({
      userId: user.id,
      access_token: process.env.SAMPLE_SANDBOX_ACCESS_TOKEN,
    });

    await Item.create({
      accessTokenId: access_token.id,
      item_id: process.env.SAMPLE_SANDBOX_ITEM_ID
    })

    await TransactionCursor.create({
      accessTokenId: access_token.id,
      cursor: ""
    })

  }

  //await Transaction.create({ userId: 1, amount: 100 }); 
  console.log("seeded database");
}

/*
 We've separated the `seed` function from the `runSeed` function.
 This way we can isolate the error handling and exit trapping.
 The `seed` function is concerned only with modifying the database.
*/
async function runSeed() {
  console.log("seeding...");
  try {
    await seed();
  } catch (err) {
    console.error(err);
    process.exitCode = 1;
  } finally {
    console.log("closing db connection");
    await db.close();
    console.log("db connection closed");
  }
}

/*
  Execute the `seed` function, IF we ran this module directly (`node seed`).
  `Async` functions always return a promise, so we can use `catch` to handle
  any errors that might occur inside of `seed`.
*/
if (module === require.main) {
  runSeed();
}

// we export the seed function for testing purposes (see `./seed.spec.js`)
module.exports = seed;
