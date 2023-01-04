var express = require("express");
var router = express.Router();
var tezosController = require("../controller/tezos");

/**
 * @api [get] /tezos/test
 * description: "Tezos integration test endpoint."
 * tags: ["tezos"]
 */
router.get("/test", tezosController.test);

/**
 * @api [get] /tezos/tokenSupply
 * description: "Returns the total Banking Map token supply."
 * tags: ["tezos"]
 */
router.get("/tokenSupply", tezosController.getTokenSupply);

/**
 * @api [get] /tezos/balance
 * description: "Returns the Banking Map Token balance for the specified address."
 * tags: ["tezos"]
 */
router.get("/balance", tezosController.getBalance);

/**
 * @api [post] /tezos/performReward
 * description: "Calculates and credits the amount."
 * tags: ["tezos"]
 */
router.post("/performReward", tezosController.performReward);

/**
 * @api [post] /tezos/creditAmount
 * description: "Credits the specified amount."
 * tags: ["tezos"]
 */
router.post("/creditAmount", tezosController.creditAmount);

/**
 * @api [post] /tezos/spendTokens
 * description: "Calculates and debits the amount."
 * tags: ["tezos"]
 */
router.post("/spendTokens", tezosController.spendTokens);

/**
 * @api [post] /tezos/debitAmount
 * description: "Debits the specified amount."
 * tags: ["tezos"]
 */
router.post("/debitAmount", tezosController.debitAmount);

module.exports = router;
