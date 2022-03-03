from conf import *
from deploy import *

asset_details = {
	"asset_name": "ArtSquare Coin", #Name of the asset
	"unit_name": "ASQ", #Individual Unit Name
	"total": 100000, #Total number of assets created at configuration
	"decimals": 0, #Decimal places in the total
	"default_frozen": False, 
	"manager": CREATOR_ADDRESS, 
	"reserve": CREATOR_ADDRESS, 
	"freeze": CREATOR_ADDRESS, 
	"clawback": CREATOR_ADDRESS, 
	"url": "https://artsquare.io", 
}

def get_asq():

    _algo_client = algod.AlgodClient(PURESTAKE_API_KEY, ALGO_SERVER, PURESTAKE_HEADERS)

    params = _algo_client.suggested_params() 

    txn = transaction.AssetConfigTxn(CREATOR_ADDRESS, params, **asset_details)

    private_key = get_private_key_from_mnemonic(CREATOR_MNEMONIC)
    
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()
    
    _algo_client.send_transaction(signed_txn)
    
    wait_for_confirmation(_algo_client, tx_id)
    
    transaction_response = _algo_client.pending_transaction_info(tx_id)
    asa_id = transaction_response['asset-index']
    print("Asset Index: " + str(asa_id)) 
    return asa_id

if __name__ == "__main__":
    get_asq()
