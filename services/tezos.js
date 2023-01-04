const { TezosToolkit } = require("@taquito/taquito");
const { importKey } = require("@taquito/signer");

var bankingmapWalletData = require(`../contracts/bankingmapWallet_${process.env.NODE_ENV}.json`);
const Tezos = new TezosToolkit(process.env.TEZOS_SERVER);

if (process.env.NODE_ENV === "development" || process.env.NODE_ENV === "test") {
  importKey(Tezos, bankingmapWalletData.email, bankingmapWalletData.password, bankingmapWalletData.mnemonic.join(" "), bankingmapWalletData.activation_code).catch((e) => console.error(e));
} else {
  importKey(Tezos, bankingmapWalletData.privateKey).catch((e) => console.error(e));
}

exports.test = async function () {
  try {
    //code to deploy smart contract
    //return await deployContract({ michelsonCode: `../contracts/michelson_${process.env.NODE_ENV}.json`, michelsonStorage: `../contracts/michelsonStorage_${process.env.NODE_ENV}.json` });
  } catch (e) {
    throw e;
  }
};

exports.getTokenSupply = async function () {
  try {
    const res = await Tezos.contract
      .at(process.env.BANKINGMAP_CONTRACT)
      .then((contract) => {
        return contract.views.getTotalSupply([["Unit"]]).read();
      })
      .then((response) => {
        return response;
      })
      .catch((error) => {
        throw error;
      });

    return res;
  } catch (e) {
    throw e;
  }
};

exports.getBalance = async function (address) {
  try {
    const res = await Tezos.contract
      .at(process.env.BANKINGMAP_CONTRACT)
      .then((contract) => {
        return contract.views.getBalance(address).read();
      })
      .then((response) => {
        return response;
      })
      .catch((error) => {
        throw error;
      });

    return res;
  } catch (e) {
    throw e;
  }
};

exports.performReward = async function (walletAddress, amount) {
  try {
    const res = await Tezos.contract
      .at(process.env.BANKINGMAP_CONTRACT)
      .then((contract) => {
        return contract.methods.performReward(amount, walletAddress).send();
      })
      .then((op) => {
        return op.confirmation(1).then(() => {
          op.hash;
        });
      })
      .then((result) => {
        const bal = this.getBalance(walletAddress);
        return bal;
      })
      .catch((err) => {
        throw err;
      });

    return res;
  } catch (e) {
    throw e;
  }
};

exports.spendTokens = async function (walletAddress, amount) {
  try {
    const res = await Tezos.contract
      .at(process.env.BANKINGMAP_CONTRACT)
      .then((contract) => {
        return contract.methods.spendTokens(amount, walletAddress).send();
      })
      .then((op) => {
        return op.confirmation(1).then(() => {
          op.hash;
        });
      })
      .then(() => {
        const bal = this.getBalance(walletAddress);
        return bal;
      })
      .catch((err) => {
        throw err;
      });

    return res;
  } catch (e) {
    throw e;
  }
};

async function deployContract() {
  try {
    const { hash, contractAddress } = await Tezos.contract.originate({
      code: require("../contracts/michelson.json"),
      init: require("../contracts/michelsonStorage.json"),
    });

    return { hash: hash, contractAddress: contractAddress };
  } catch (e) {
    throw e;
  }
}
