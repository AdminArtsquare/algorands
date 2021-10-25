import hashlib
import logging
#
def wait_for_tx_confirmation(algod_client, txid):
    """HELP wait_for_tx_confirmation:
        (AlgodClient, obj) - Wait for TX confirmation and displays confirmation
        round.
    """
    last_round = algod_client.status().get('last-round')
    while True:
        txinfo = algod_client.pending_transaction_info(txid)
        if txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0:
            print("Transaction {} confirmed in round {}.".format(
                txid, txinfo.get('confirmed-round')))
            break
        else:
            print("Waiting for confirmation...")
            last_round += 1
            algod_client.status_after_block(last_round)
#
def getFileHash(file):
    try:
        
        sha256_hash = hashlib.sha256()
        with open(file, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
            hash = sha256_hash.digest()

    except Exception as e:
        logging.error('Exception: ' + str(e))

    return hash