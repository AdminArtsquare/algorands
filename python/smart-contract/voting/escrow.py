from pyteal import *
from conf import *
from deploy import *

def escrow_account(app_id, asa_id):

    fee = Int(1000)

    asa_opt_in = And(
        Txn.type_enum() == TxnType.AssetTransfer,
        Txn.xfer_asset() == Int(asa_id),
        Txn.asset_amount() == Int(0),
        Txn.fee() <= fee,
        Txn.rekey_to() == Global.zero_address(),
        Txn.asset_close_to() == Global.zero_address(),
    )

    asa_withdraw = And(
        Gtxn[0].type_enum() == TxnType.ApplicationCall,
        Gtxn[0].application_id() == Int(app_id),
        Gtxn[0].on_completion() == OnComplete.NoOp,
        Gtxn[1].type_enum() == TxnType.AssetTransfer,
        Gtxn[1].xfer_asset() == Int(asa_id),
        Gtxn[1].fee() <= fee,
        Gtxn[1].asset_close_to() == Global.zero_address(),
        Gtxn[1].rekey_to() == Global.zero_address()
    )

    program = Cond(
        [Global.group_size() == Int(1), asa_opt_in],
        [Global.group_size() == Int(2), asa_withdraw]
    )

    return program

def get_escrow(asa_id, app_id):

    _algo_client = algod.AlgodClient(PURESTAKE_API_KEY, ALGO_SERVER, PURESTAKE_HEADERS)

    private_key = get_private_key_from_mnemonic(CREATOR_MNEMONIC)
    
    escrow_account_ast = escrow_account(app_id, asa_id)
    escrow_account_teal = compileTeal(escrow_account_ast, mode=Mode.Signature, version=4)
    compile_response = _algo_client.compile(escrow_account_teal)
    approval_program_compiled = base64.b64decode(compile_response["result"])

    escrowAddress = compile_response['hash'] # address escrow

    lsig = transaction.LogicSigAccount(approval_program_compiled)

    lsig.sign(private_key)

    params = _algo_client.suggested_params()
    
    txn = transaction.AssetTransferTxn(CREATOR_ADDRESS, params, escrowAddress, 0, asa_id)

    lstx = transaction.LogicSigTransaction(txn, lsig)
    
    tx_id = _algo_client.send_transaction(lstx)
    
    wait_for_confirmation(_algo_client, tx_id)
    
    _algo_client.pending_transaction_info(tx_id)

    return escrowAddress

def activateEscrow(escrowAddress):

    _algo_client = algod.AlgodClient(PURESTAKE_API_KEY, ALGO_SERVER, PURESTAKE_HEADERS)

    private_key = get_private_key_from_mnemonic(CREATOR_MNEMONIC)

    params = _algo_client.suggested_params()

    # after creating escrow, we have to 'activate' it by sending at least 0.1 algo
    txnActivate = transaction.PaymentTxn(CREATOR_ADDRESS, params, escrowAddress, 300000)
    stxn_1 = txnActivate.sign(private_key)

    tx_id = _algo_client.send_transaction(stxn_1)

    wait_for_confirmation(_algo_client, tx_id)

def optInEscrow(asa_id, app_id, escrowAddress):

    _algo_client = algod.AlgodClient(PURESTAKE_API_KEY, ALGO_SERVER, PURESTAKE_HEADERS)

    escrow_account_ast = escrow_account(app_id, asa_id)
    escrow_account_teal = compileTeal(escrow_account_ast, mode=Mode.Signature, version=4)
    compile_response = _algo_client.compile(escrow_account_teal)
    approval_program_compiled = base64.b64decode(compile_response["result"])

    lsig = transaction.LogicSigAccount(approval_program_compiled)

    params = _algo_client.suggested_params()

    txOptIn = transaction.AssetTransferTxn(escrowAddress, params, escrowAddress, 0, asa_id)

    lstx = transaction.LogicSigTransaction(txOptIn, lsig)
    
    tx_id = _algo_client.send_transaction(lstx)
    
    wait_for_confirmation(_algo_client, tx_id)
    
    _algo_client.pending_transaction_info(tx_id)