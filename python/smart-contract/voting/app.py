from pyteal import *
from conf import *
from deploy import *

# ApprovalProgram
def approval_program():
    # method called upon creation and initialization of the contract
    on_creation = Seq(
        [
            App.globalPut(Bytes("Creator"), Txn.sender()),
            Assert(Txn.application_args.length() == Int(4)),
            App.globalPut(Bytes("RegBegin"), Btoi(Txn.application_args[0])),
            App.globalPut(Bytes("RegEnd"), Btoi(Txn.application_args[1])),
            App.globalPut(Bytes("VoteBegin"), Btoi(Txn.application_args[2])),
            App.globalPut(Bytes("VoteEnd"), Btoi(Txn.application_args[3])),
            Return(Int(1)),
        ]
    )
    # support control variable to check that the caller is the creator
    is_creator = Txn.sender() == App.globalGet(Bytes("Creator")) 
    # method called when deleting the registration
    on_closeout = Return(Int(1)) 
    # method called upon opt-in in the contract
    on_register = Seq(
        [
            Assert(
                And(
                    Global.round() >= App.globalGet(Bytes("RegBegin")),
                    Global.round() <= App.globalGet(Bytes("RegEnd")),
                )
            ),
            App.localPut(Int(0), Bytes("registered"), Int(1)),
            Return(Int(1))
        ]
    )
    # support variable for the recovery of the vote from the second parameter of the first transaction
    vote = Gtxn[0].application_args[1]
    # the weight of the vote corresponds to the number of assets transferred
    weight_vote = Gtxn[1].asset_amount()
    # number of votes for the key
    vote_tally = App.globalGet(vote)
    # method called up in the app setup
    vote_setup = Seq(
        [
            Assert(
                And(
                    Global.round() < App.globalGet(Bytes("RegBegin")),
                    Gtxn[0].type_enum() == TxnType.ApplicationCall,
                    Gtxn[1].type_enum() == TxnType.AssetTransfer, 
                    Txn.rekey_to() == Global.zero_address(),
                    Txn.asset_close_to() == Global.zero_address(),
                )
            ),
            App.globalPut(Bytes("AssetEscrow"), Gtxn[1].asset_receiver()),
            App.globalPut(Bytes("AssetID"), Gtxn[1].xfer_asset()),
            Return(Int(1))
        ]
    )
    #
    is_registered = App.localGetEx(Int(0), App.id(), Bytes("registered"))
    # method called up in the app vote
    voting = Seq(
        [
            Assert(
                And(
                    # only registered user can vote
                    # the voting period must have started
                    Global.round() >= App.globalGet(Bytes("VoteBegin")),
                    Global.round() <= App.globalGet(Bytes("VoteEnd")),
                    Gtxn[1].type_enum() == TxnType.AssetTransfer,
                    Gtxn[1].xfer_asset() == App.globalGet(Bytes("AssetID")),
                    Gtxn[1].sender() == Gtxn[0].sender(),
                    Gtxn[1].asset_receiver() == App.globalGet(Bytes("AssetEscrow")),
                    Gtxn[1].asset_amount() > Int(0)
                )
            ),
            is_registered,
            If(is_registered.hasValue(), Return(Int(1))),
            App.globalPut(vote, vote_tally + weight_vote),
            Return(Int(1)),
        ]
    )
    # method called up in the app withdraw
    withdraw = Seq(
        [
            Assert(
                And(
                    Global.round() > App.globalGet(Bytes("VoteEnd")),
                    Gtxn[1].type_enum() == TxnType.AssetTransfer,
                    Gtxn[1].xfer_asset() == App.globalGet(Bytes("AssetID")),
                    Gtxn[1].sender() == App.globalGet(Bytes("AssetEscrow")),
                    Gtxn[1].asset_receiver() == App.globalGet(Bytes("Creator")),
                )
            ),
            Return(Int(1)),
        ]
    )
    # methods accepted by the app
    handle_noop = Cond(
        [And(
            Global.group_size() == Int(2), 
            Gtxn[0].application_args.length() == Int(0),
            App.globalGet(Bytes("Creator")) == Gtxn[0].sender(), 
        ), vote_setup],
        [And(
            Global.group_size() == Int(2),
            Gtxn[0].application_args[0] == Bytes("Vote")
        ), voting],
        [And(
            Global.group_size() == Int(2),
            Gtxn[0].application_args[0] == Bytes("Withdraw")
        ), withdraw]
    )
    # definition of the program
    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        # only the creator can delete the app
        [Txn.on_completion() == OnComplete.DeleteApplication, Return(is_creator)],
        # only the creator can update the app
        [Txn.on_completion() == OnComplete.UpdateApplication, Return(is_creator)],
        # defines the method called upon close-out to the contract
        [Txn.on_completion() == OnComplete.CloseOut, on_closeout],
        # defines the method called upon opt-in to the contract
        [Txn.on_completion() == OnComplete.OptIn, on_register],
        # defines the methods accepted by the app
        [Txn.on_completion() == OnComplete.NoOp, handle_noop]
    )
    return program
# ClearStateProgram
def clear_state_program():
    return Int(1)
    
def get_app(app_args):

    _algo_client = algod.AlgodClient(PURESTAKE_API_KEY, ALGO_SERVER, PURESTAKE_HEADERS)

    private_key = get_private_key_from_mnemonic(CREATOR_MNEMONIC)

    local_ints = 0
    local_bytes = 1
    global_ints = 25 # 5 defined for the creations, 20 free for possible votes
    global_bytes = 3
    global_schema = transaction.StateSchema(global_ints, global_bytes)
    local_schema = transaction.StateSchema(local_ints, local_bytes)

    approval_program_ast = approval_program()
    approval_program_teal = compileTeal(approval_program_ast, mode=Mode.Application, version=2)
    approval_program_compiled = compile_program(_algo_client, approval_program_teal)

    clear_state_program_ast = clear_state_program()
    clear_state_program_teal = compileTeal(clear_state_program_ast, mode=Mode.Application, version=2)
    clear_state_program_compiled = compile_program(_algo_client, clear_state_program_teal)

    app_id = create_app(
        _algo_client,
        private_key,
        approval_program_compiled,
        clear_state_program_compiled,
        global_schema,
        local_schema,
        app_args,
    )

    return app_id