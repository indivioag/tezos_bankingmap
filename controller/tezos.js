const tezosService = require("../service/tezos");

exports.test = async function (req, res, next) {
  try {
    // + " ꜩ"
    const result = await tezosService.test();
    res.json({ success: true, res: result });
  } catch (e) {
    next(e);
  }
};

exports.getTokenSupply = async function (req, res, next) {
  try {
    const result = await tezosService.getTokenSupply();
    res.json({ success: true, supply: result });
  } catch (e) {
    next(e);
  }
};

exports.getBalance = async function (req, res, next) {
  try {
    const address = req.query.walletAddress;
    const result = await tezosService.getBalance(address);
    res.json({ success: true, balance: result });
  } catch (e) {
    next(e);
  }
};

exports.performReward = async function (req, res, next) {
  try {
    //tbd calculate TODO
    const walletAddress = req.body.walletAddress;
    const amount = 2300;
    const result = await tezosService.performReward(walletAddress, amount);
    res.json({ success: true, newBalance: result });
  } catch (e) {
    next(e);
  }
};

exports.creditAmount = async function (req, res, next) {
  try {
    const walletAddress = req.body.walletAddress;
    const amount = req.body.amount;
    const result = await tezosService.performReward(walletAddress, amount);
    res.json({ success: true, newBalance: result });
  } catch (e) {
    next(e);
  }
};

exports.spendTokens = async function (req, res, next) {
  try {
    const walletAddress = req.body.walletAddress;
    const amount = 200; //TODO
    const result = await tezosService.spendTokens(walletAddress, amount);
    res.json({ success: true, newBalance: result });
  } catch (e) {
    next(e);
  }
};

exports.debitAmount = async function (req, res, next) {
  try {
    const walletAddress = req.body.walletAddress;
    const amount = req.body.amount;
    const result = await tezosService.spendTokens(walletAddress, amount);
    res.json({ success: true, newBalance: result });
  } catch (e) {
    next(e);
  }
};
