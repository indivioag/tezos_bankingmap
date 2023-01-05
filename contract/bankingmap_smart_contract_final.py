import smartpy as sp

class BMT_Error:
    def make(s): return ("BMT_" + s)
    InsufficientBalance         = make("InsufficientBalance")
    NotAdmin                    = make("NotAdmin")
    InvalidAccount              = make("InvalidAccount")
    AccountExisting             = make("AccountExisting")
    NonpositiveAmount           = make("NonpositiveAmount")

class BMT_mint_burn():
    def mint(self, companyAddress, amount):
        sp.set_type(companyAddress, sp.TAddress)

        # only positive amounts may be transferred
        sp.verify(amount > 0, BMT_Error.NonpositiveAmount)

        # only admin can transfer
        sp.verify(self.is_administrator(sp.sender), BMT_Error.NotAdmin)
        
        # create account if not already there
        self.addAccountIfNecessary(companyAddress)

        # credit the account
        sp.if ((self.data.balances[companyAddress] + amount) <= 10000):
            self.data.balances[companyAddress] = self.data.balances[companyAddress] + amount
            self.data.totalSupply = (self.data.totalSupply + amount)
        sp.else:
            self.data.totalSupply = self.data.totalSupply + sp.as_nat(10000 - self.data.balances[companyAddress])
            self.data.balances[companyAddress] = self.data.balances[companyAddress] + sp.as_nat(10000 - self.data.balances[companyAddress])
        
    def burn(self, companyAddress, amount):
        sp.set_type(companyAddress, sp.TAddress)

        # only positive amounts may be transferred
        sp.verify(amount > 0, BMT_Error.NonpositiveAmount)

        # only admin can transfer
        sp.verify(self.is_administrator(sp.sender), BMT_Error.NotAdmin)

        # only burn, if balance is sufficient
        sp.verify(self.data.balances[companyAddress] >= amount, BMT_Error.InsufficientBalance)

        # burn coins
        self.data.balances[companyAddress] = sp.as_nat(self.data.balances[companyAddress] - amount)
        self.data.totalSupply = sp.as_nat(self.data.totalSupply - amount)

class BMT_administrator():
    @sp.entry_point
    def setAdministrator(self, params):
        sp.set_type(params, sp.TAddress)

        # only admin may set a new admin
        sp.verify(self.is_administrator(sp.sender), BMT_Error.NotAdmin)
        
        self.data.administrator = params
    
    @sp.utils.view(sp.TAddress)
    def getAdministrator(self, params):
        sp.set_type(params, sp.TUnit)
        sp.result(self.data.administrator)
    
    def is_administrator(self, sender):
        return sender == self.data.administrator

class BMT_account_management:   
    @sp.entry_point
    def deleteAccount(self, companyAddress):
        # only the admin may delete accounts
        sp.verify(self.is_administrator(sp.sender), BMT_Error.NotAdmin)
        
        # only delete account if it exists
        sp.verify(self.data.balances.contains(companyAddress), BMT_Error.InvalidAccount)

        # delete the account
        del self.data.balances[companyAddress]
    
    def addAccountIfNecessary(self, companyAddress):
        sp.if ~ self.data.balances.contains(companyAddress):
            self.data.balances[companyAddress] = 0
    
    @sp.utils.view(sp.TNat)
    def getBalance(self, companyAddress):
        sp.if self.data.balances.contains(companyAddress):
            sp.result(self.data.balances[companyAddress])
        sp.else:
            sp.result(sp.nat(0))

class BMT_reward:
    @sp.entry_point
    def performReward(self, companyAddress, amount):
        sp.set_type(companyAddress, sp.TAddress)

        # only admin can transfer
        sp.verify(self.is_administrator(sp.sender), BMT_Error.NotAdmin)

        # mint amount to company's wallet
        self.mint(companyAddress, amount)

    @sp.entry_point
    def spendTokens(self, companyAddress, amount):
        sp.set_type(companyAddress, sp.TAddress)

        # only admin can transfer
        sp.verify(self.is_administrator(sp.sender), BMT_Error.NotAdmin)

        # burn amount from company's wallet
        self.burn(companyAddress, amount)

class BMT_contract_metadata():
    def generate_tzip16_metadata(self):
        views = []

        def token_metadata(self, token_id):
            sp.set_type(token_id, sp.TNat)
            sp.result(self.data.token_metadata[token_id])

        self.token_metadata = sp.offchain_view(pure = True, doc = "Get Token Metadata")(token_metadata)
        views += [self.token_metadata]

        self.init_metadata("metadata", {
            "TZIP16_Metadata_Base": {
                "name": "Banking Map Token",
                "description": "FA1.2 compliant Banking Map Token",
                "authors": ["Dr. Michael Fischbach <michael.fischbach@indivio.ch>"],
                "homepage": "https://bankingmap.ch",
                "interfaces": ["TZIP-007-2021-04-17","TZIP-016-2021-04-17"],
                "license": "-"
            },
            "views": views
        })
    
    def set_contract_metadata(self, metadata):
        self.update_initial_storage(metadata = sp.big_map(self.normalize_metadata(metadata)))

        def update_metadata(self, key, value):
            sp.verify(self.is_administrator(sp.sender), BMT_Error.NotAdmin)
            self.data.metadata[key] = value
        self.update_metadata = sp.entry_point(update_metadata)

class BMT_token_metadata():
    def set_token_metadata(self, metadata):
        self.update_initial_storage(
            token_metadata = sp.big_map(
                {0: sp.record(token_id = 0, token_info = self.normalize_metadata(metadata))},
                tkey = sp.TNat, tvalue = sp.TRecord(token_id = sp.TNat, token_info = sp.TMap(sp.TString, sp.TBytes))
            )
        )

class BMT(sp.Contract, BMT_mint_burn, BMT_administrator, BMT_account_management, BMT_reward, BMT_contract_metadata, BMT_token_metadata):
    def __init__(self, admin, token_metadata, contract_metadata):
        self.init(
            balances = sp.map(l={}, tkey = sp.TAddress, tvalue = sp.TNat), 
            totalSupply = 0,
            administrator = admin,
            token_metadata = None,
            contract_metadata = None
        )
        self.set_contract_metadata(contract_metadata)
        self.set_token_metadata(token_metadata)
        self.generate_tzip16_metadata()
    
    def normalize_metadata(self, metadata):
        for key in metadata:
            metadata[key] = sp.utils.bytes_of_string(metadata[key])
        return metadata

    @sp.utils.view(sp.TNat)
    def getTotalSupply(self, params):
        sp.set_type(params, sp.TUnit)
        sp.result(self.data.totalSupply)

# Used to test offchain views
class TestOffchainView(sp.Contract):
    def __init__(self, f):
        self.f = f.f
        self.init(result = sp.none)

    @sp.entry_point
    def compute(self, data, params):
        b = sp.bind_block()
        with b:
            self.f(sp.record(data = data), params)
        self.data.result = sp.some(b.value)

class Viewer(sp.Contract):
    def __init__(self, t):
        self.init(last = sp.none)
        self.init_type(sp.TRecord(last = sp.TOption(t)))
    @sp.entry_point
    def target(self, params):
        self.data.last = sp.some(params)

if "templates" not in __name__:
    @sp.add_test(name = "BMT_")
    def test():
        scenario = sp.test_scenario()

        alice = sp.test_account("Alice").address
        bob = sp.test_account("Bob").address
        caesar = sp.test_account("Caesar").address
        administrator = sp.address("tz1a4TSCjtm9STUfqpqeycxzJYKQL9pMgjj5")
        #administrator = sp.test_account("Administrator").address
        
        scenario.h1("BMT - Banking Map Token Contract")
        scenario.table_of_contents()

        scenario.h1("Accounts")
        scenario.show([administrator, alice, bob])

        scenario.h1("Contract")
        c1 = BMT(administrator, { "decimals": "0", "name": "Banking Map Token", "symbol": "BMT"}, {"" : "ipfs://tbd"})
        scenario += c1

        scenario.h1("Offchain view - token_metadata")
        offchainViewTester = TestOffchainView(c1.token_metadata)
        scenario.register(offchainViewTester)
        offchainViewTester.compute(data = c1.data, params = 0)
        scenario.verify_equal(
            offchainViewTester.data.result,
                sp.some(
                    sp.record(
                        token_id = 0,
                        token_info = sp.map({
                            "decimals"    : sp.utils.bytes_of_string("0"),
                            "name"        : sp.utils.bytes_of_string("Banking Map Token"),
                            "symbol"      : sp.utils.bytes_of_string("BMT")
                            })
                    )
                )
            )

        scenario.h1("Attempt to update metadata")
        scenario.verify(c1.data.metadata[""] == sp.utils.bytes_of_string("ipfs://tbd"))
        c1.update_metadata(key = "", value = sp.bytes("0x00")).run(sender = administrator)
        scenario.verify(c1.data.metadata[""] == sp.bytes("0x00"))

        scenario.h1("Entry points")
        scenario.h2("Companies receive BMT tokens")
        c1.performReward(companyAddress=alice, amount=5).run(valid=True, sender = administrator)
        c1.performReward(companyAddress=bob, amount=22000).run(valid=True, sender = administrator)
        c1.performReward(companyAddress=caesar, amount=1).run(valid=True, sender = administrator)

        scenario.h2("Companies spend BMT tokens")
        c1.spendTokens(companyAddress=alice, amount=2).run(valid=True, sender = administrator)
        c1.spendTokens(companyAddress=alice, amount=100).run(valid=False, sender = administrator)
        c1.spendTokens(companyAddress=bob, amount=3).run(valid=True, sender = administrator)
        c1.spendTokens(companyAddress=caesar, amount=1).run(valid=True, sender = administrator)

        scenario.h2("Account deletion")
        c1.deleteAccount(caesar).run(valid=True, sender = administrator)

        scenario.verify(c1.data.balances[alice] == sp.nat(3))
        scenario.verify(c1.data.balances[bob] == sp.nat(9997))
        scenario.verify(c1.data.totalSupply == 10000)

        scenario.h1("Views")
        scenario.h2("Balance")
        view_balance = Viewer(sp.TNat)
        scenario += view_balance
        c1.getBalance((alice, view_balance.typed.target))
        scenario.verify_equal(view_balance.data.last, sp.some(3))

        scenario.h2("Administrator")
        view_administrator = Viewer(sp.TAddress)
        scenario += view_administrator
        c1.getAdministrator((sp.unit, view_administrator.typed.target))
        scenario.verify_equal(view_administrator.data.last, sp.some(administrator))

        scenario.h2("Total Supply")
        view_totalSupply = Viewer(sp.TNat)
        scenario += view_totalSupply
        c1.getTotalSupply((sp.unit, view_totalSupply.typed.target))
        scenario.verify_equal(view_totalSupply.data.last, sp.some(10000))

    sp.add_compilation_target(
        "BMT",
        BMT(
            admin   = sp.address("tz1a4TSCjtm9STUfqpqeycxzJYKQL9pMgjj5"),
            token_metadata = {
                "decimals"    : "0",
                "name"        : "Banking Map Token",
                "symbol"      : "BMT"            },
            contract_metadata = {
                "" : "ipfs://TBD",
            }
        )
    )
