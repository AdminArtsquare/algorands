from algosdk.future import transaction
from algosdk import account
from pyteal import *

from base import * # library that implements all the basic functions
from config import * # configuration library

# declare application state storage (immutable)
local_ints = 0
local_bytes = 0
global_ints = 3
global_bytes = 3
global_schema = transaction.StateSchema(global_ints, global_bytes)
local_schema = transaction.StateSchema(local_ints, local_bytes)
# base program for smart contract
def approval_program():
    # first function called once at creation
    handle_creation = Seq([
        # set asset name
        App.globalPut(Bytes("AssetName"), Bytes("AST")),
        App.globalPut(Bytes("NftAddress"), Bytes("qua_ci_andra_indirizzo_nft")),
        App.globalPut(Bytes("TotalShares"), Int(100)),
        App.globalPut(Bytes("AvailableShares"), Int(100)),
        App.globalPut(Bytes("SoldShares"), Int(0)),


        App.globalPut(Bytes("Admin"), Txn.sender()),
        Return(Int(1))
    ])
    # function to check if sender is admin or app creator
    is_admin = App.globalGet(Bytes("Admin")) == Txn.sender()
    # buy share
    buy_share = Seq([
        Assert(Global.group_size() == Int(1)),
        Assert(is_admin),
        # decr available add sold
        App.globalPut(Bytes("AvailableShares"), App.globalGet(Bytes("AvailableShares")) - Int(1)),
        App.globalPut(Bytes("SoldShares"), App.globalGet(Bytes("SoldShares")) + Int(1)),
        Return(Int(1))
    ]) 
    # sold share
    sold_share = Seq([
        Assert(Global.group_size() == Int(1)),
        Assert(is_admin),
        # decr sold add available
        App.globalPut(Bytes("AvailableShares"), App.globalGet(Bytes("AvailableShares")) + Int(1)),
        App.globalPut(Bytes("SoldShares"), App.globalGet(Bytes("SoldShares")) - Int(1)),
        Return(Int(1))
    ]) 
    
    # program core
    program = Cond(
        # transaction to delete application, int(0) cancels the ability to delete it
        [Txn.on_completion() == OnComplete.DeleteApplication, Return(Int(0))],
        # transaction to update TEAL program for a contract, int(0) cancels the ability to update it
        [Txn.on_completion() == OnComplete.UpdateApplication, Return(Int(0))],
        # transaction to exit from the contract
        [Txn.on_completion() == OnComplete.CloseOut, Return(Int(0))],
        # transaction to opt in the contract
        [Txn.on_completion() == OnComplete.OptIn, Return(Int(0))],
        [Txn.application_id() == Int(0), handle_creation],
        [Txn.application_args[0] == Bytes("buy_share"), buy_share],
        [Txn.application_args[0] == Bytes("sold_share"), sold_share]
    )
    # Mode.Application specifies that this is a smart contract
    return compileTeal(program, Mode.Application, version=5)

# base state program for smart contract
def clear_state_program():
   program = Return(Int(1))
   # Mode.Application specifies that this is a smart contract
   return compileTeal(program, Mode.Application, version=5)

# compile program to TEAL assembly
with open("./SMART-CONTRACT/teal/approval.teal", "w") as f:
    approval_program_teal = approval_program()
    f.write(approval_program_teal)

with open("./SMART-CONTRACT/teal/clear.teal", "w") as f:
    clear_state_program_teal = clear_state_program()
    f.write(clear_state_program_teal)

approval_program_compiled = compile_program(algod_client, approval_program_teal)

clear_state_program_compiled = compile_program(algod_client, clear_state_program_teal)

app_id = create_app(algod_client, creator_private_key, approval_program_compiled, clear_state_program_compiled, global_schema, local_schema)

# read global state of application
print("Global state:", read_global_state(algod_client, account.address_from_private_key(creator_private_key), app_id))

# buy share
app_args = ["buy_share"]
call_app(algod_client, creator_private_key, app_id, app_args)

print("Global state:", read_global_state(algod_client, account.address_from_private_key(creator_private_key), app_id))

# buy share
app_args = ["buy_share"]
call_app(algod_client, creator_private_key, app_id, app_args)

print("Global state:", read_global_state(algod_client, account.address_from_private_key(creator_private_key), app_id))

# sold share
app_args = ["sold_share"]
call_app(algod_client, creator_private_key, app_id, app_args)

print("Global state:", read_global_state(algod_client, account.address_from_private_key(creator_private_key), app_id))
