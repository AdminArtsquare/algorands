from pyteal import *
from conf import *
from deploy import *
from escrow import *

def vote_setup(asa_id, app_id, escrowAddress):

    _algod_client = algod.AlgodClient(PURESTAKE_API_KEY, ALGO_SERVER, PURESTAKE_HEADERS)

    private_key = get_private_key_from_mnemonic(CREATOR_MNEMONIC)
    
    # atomic transfer ( 1 => ApplicationNoOpTxn, 2 => AssetTransferTxn )
    
    params = _algod_client.suggested_params()
    
    txn_1 = transaction.ApplicationNoOpTxn(CREATOR_ADDRESS, params, app_id)
    
    txn_2 = transaction.AssetTransferTxn(CREATOR_ADDRESS, params, escrowAddress, 10, asa_id)

    grouped_atomic = atomic_transfer(txn_1, txn_2, private_key, private_key)

    txs_id = _algod_client.send_transactions(grouped_atomic)

    wait_for_confirmation(_algod_client, txs_id)

    return

def register(app_id):

    _algod_client = algod.AlgodClient(PURESTAKE_API_KEY, ALGO_SERVER, PURESTAKE_HEADERS)

    private_key = get_private_key_from_mnemonic(TEST_MNEMONIC)

    opt_in_app(_algod_client, private_key, app_id)

def vote(asa_id, app_id, escrowAddress):

    _algod_client = algod.AlgodClient(PURESTAKE_API_KEY, ALGO_SERVER, PURESTAKE_HEADERS)

    private_key = get_private_key_from_mnemonic(TEST_MNEMONIC)
    
    # atomic transfer ( 1 => ApplicationNoOpTxn, 2 => AssetTransferTxn )
    
    params = _algod_client.suggested_params()
    
    txn_1 = transaction.ApplicationNoOpTxn(TEST_ADDRESS, params, app_id, ["Vote","Instagram"])
    
    txn_2 = transaction.AssetTransferTxn(TEST_ADDRESS, params, escrowAddress, 10, asa_id)
    
    grouped_atomic = atomic_transfer(txn_1, txn_2, private_key, private_key)

    txs_id = _algod_client.send_transactions(grouped_atomic)

    wait_for_confirmation(_algod_client, txs_id)

    return

def withdraw(asa_id, app_id, escrowAddress):

    _algod_client = algod.AlgodClient(PURESTAKE_API_KEY, ALGO_SERVER, PURESTAKE_HEADERS)

    private_key = get_private_key_from_mnemonic(CREATOR_MNEMONIC)
    
    # atomic transfer ( 1 => ApplicationNoOpTxn, 2 => AssetTransferTxn )
    
    params = _algod_client.suggested_params()
    
    txn_1 = transaction.ApplicationNoOpTxn(CREATOR_ADDRESS, params, app_id, ["Withdraw"])

    escrow_account_ast = escrow_account(app_id, asa_id)
    escrow_account_teal = compileTeal(escrow_account_ast, mode=Mode.Signature, version=4)
    compile_response = _algod_client.compile(escrow_account_teal)
    approval_program_compiled = base64.b64decode(compile_response["result"])

    lsig = transaction.LogicSigAccount(approval_program_compiled) 
    
    txn_2 = transaction.AssetTransferTxn(escrowAddress, params, CREATOR_ADDRESS, 10, asa_id)

    gid = transaction.calculate_group_id([txn_1, txn_2])
    
    txn_1.group = gid
    txn_2.group = gid

    stxn_1 = txn_1.sign(private_key)
    lstx = transaction.LogicSigTransaction(txn_2, lsig)

    txs_id = _algod_client.send_transactions([stxn_1, lstx])

    wait_for_confirmation(_algod_client, txs_id)

    return

def delete(app_id):

    _algod_client = algod.AlgodClient(PURESTAKE_API_KEY, ALGO_SERVER, PURESTAKE_HEADERS)

    private_key = get_private_key_from_mnemonic(CREATOR_MNEMONIC)

    delete_app(_algod_client, private_key, app_id)

def read_global_state(app_id):

    _algod_client = algod.AlgodClient(PURESTAKE_API_KEY, ALGO_SERVER, PURESTAKE_HEADERS)

    read_global_state = read_global_state(_algod_client, CREATOR_ADDRESS, app_id)

    print(read_global_state)

def read_local_state(app_id):

    _algod_client = algod.AlgodClient(PURESTAKE_API_KEY, ALGO_SERVER, PURESTAKE_HEADERS)

    read_local_state = read_local_state(_algod_client, CREATOR_ADDRESS, app_id)

    print(read_local_state)