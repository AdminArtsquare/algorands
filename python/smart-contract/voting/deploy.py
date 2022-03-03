import base64

from algosdk.v2client import algod
from algosdk.future import transaction
from algosdk import account, mnemonic

from conf import *

# helper for compiling teal sources
def compile_program(client, source_code):
    compile_response = client.compile(source_code)
    return base64.b64decode(compile_response["result"])
# helper method for recovering the private key using mnemonic
def get_private_key_from_mnemonic(mn):
    private_key = mnemonic.to_private_key(mn)
    return private_key
# helper method that waits for the network to confirm a transaction
def wait_for_confirmation(client, txid):
    last_round = client.status().get("last-round")
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get("confirmed-round") and txinfo.get("confirmed-round") > 0):
        print("Waiting for confirmation...")
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
    print(
        "Transaction {} confirmed in round {}.".format(
            txid, txinfo.get("confirmed-round")
        )
    )
    return txinfo
# helper method that waits for a specific round in the network
def wait_for_round(client, round):
    last_round = client.status().get("last-round")
    print(f"Waiting for round {round}")
    while last_round < round:
        last_round += 1
        client.status_after_block(last_round)
        print(f"Round {last_round}")
# helper method for creating the app ApprovalProgram
def create_app(
    client,
    private_key,
    approval_program,
    clear_program,
    global_schema,
    local_schema,
    app_args,
):
    sender = account.address_from_private_key(private_key)
    on_complete = transaction.OnComplete.NoOpOC.real
    params = client.suggested_params()
    
    txn = transaction.ApplicationCreateTxn(
        sender,
        params,
        on_complete,
        approval_program,
        clear_program,
        global_schema,
        local_schema,
        app_args,
    )
    
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()
    
    client.send_transaction(signed_txn)
    
    wait_for_confirmation(client, tx_id)
    
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response["application-index"]

    return app_id
# method for opt-in with the app
def opt_in_app(client, private_key, index):
    
    sender = account.address_from_private_key(private_key)
    params = client.suggested_params()
    
    txn = transaction.ApplicationOptInTxn(sender, params, index)
    
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()
    
    client.send_transaction(signed_txn)
    
    wait_for_confirmation(client, tx_id)

    return tx_id
# method to invoke a method defined in the app
def call_app(client, private_key, index, app_args):
    
    sender = account.address_from_private_key(private_key)
    params = client.suggested_params()
    
    txn = transaction.ApplicationNoOpTxn(sender, params, index, app_args)
    
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()
    
    client.send_transaction(signed_txn)
    
    wait_for_confirmation(client, tx_id)

    return tx_id
# method to format the data in the app
# todo: to be modified for printing the results of the votes
def format_state(state):
    formatted = {}
    for item in state:
        key = item["key"]
        value = item["value"]
        formatted_key = base64.b64decode(key).decode("utf-8")
        if value["type"] == 1:
            # byte string
            if formatted_key == "voted":
                formatted_value = base64.b64decode(value["bytes"]).decode("utf-8")
            else:
                formatted_value = value["bytes"]
            formatted[formatted_key] = formatted_value
        else:
            # integer
            formatted[formatted_key] = value["uint"]
    return formatted
# method for retrieving local data user in the app
def read_local_state(client, addr, app_id):
    results = client.account_info(addr)
    for local_state in results["apps-local-state"]:
        if local_state["id"] == app_id:
            if "key-value" not in local_state:
                return {}
            return format_state(local_state["key-value"])
    return {}
# method for retrieving global data in the app
def read_global_state(client, addr, app_id):
    results = client.account_info(addr)
    apps_created = results["created-apps"]
    for app in apps_created:
        if app["id"] == app_id:
            return format_state(app["params"]["global-state"])
    return {}
# method for deleting the app
def delete_app(client, private_key, index):
    
    sender = account.address_from_private_key(private_key)
    params = client.suggested_params()
    
    txn = transaction.ApplicationDeleteTxn(sender, params, index)
    
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()
    
    client.send_transaction(signed_txn)
    
    wait_for_confirmation(client, tx_id)
    
    return tx_id
# method for close-out from the app
def close_out_app(client, private_key, index):
    
    sender = account.address_from_private_key(private_key)
    params = client.suggested_params()
    
    txn = transaction.ApplicationCloseOutTxn(sender, params, index)
    
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()
    
    client.send_transaction(signed_txn)
    
    wait_for_confirmation(client, tx_id)
    
    return tx_id
# helper method for creating the app ClearStateProgram
def clear_app(client, private_key, index):
    
    sender = account.address_from_private_key(private_key)
    params = client.suggested_params()
    
    txn = transaction.ApplicationClearStateTxn(sender, params, index)
    
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()
    
    client.send_transaction(signed_txn)
    
    wait_for_confirmation(client, tx_id)
    
    transaction_response = client.pending_transaction_info(tx_id)
    
    cleared_app_id = transaction_response["txn"]["txn"]["apid"]

    return cleared_app_id
# helper method converts int to bytes
def intToBytes(i):
    return i.to_bytes(8, "big")
# atomic transaction helper method
def atomic_transfer(txn_1, txn_2, private_key1, private_key2):

    gid = transaction.calculate_group_id([txn_1, txn_2])
    
    txn_1.group = gid
    txn_2.group = gid

    stxn_1 = txn_1.sign(private_key1)
    stxn_2 = txn_2.sign(private_key2)

    return [stxn_1, stxn_2]