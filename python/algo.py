# library
import hashlib
import json
from algosdk.future.transaction import AssetTransferTxn
from algosdk.v2client import algod
from algosdk import transaction, mnemonic
from conf import *
from algo_lib import *
# class for Purestake algorand
class PurestakeAlgorand:
    # constructor
    def __init__(self) -> None:
        self._algod_client = algod.AlgodClient(PURESTAKE_API_KEY, ALGO_SERVER, PURESTAKE_HEADERS)
        self._algod_indexer = algod.AlgodClient(PURESTAKE_API_KEY, ALGO_INDEXER, PURESTAKE_HEADERS)
    # method to generate the metadata json file
    def createMetadataJson(self, name, decimals, description, hash, file):
        response = { }
        try:
            # init sha256 hash lib
            sha256_hash = hashlib.sha256()
            # get sha256 file digest
            for byte_block in iter(lambda: file.read(4096),b""):
                sha256_hash.update(byte_block)
            image_integrity = sha256_hash.hexdigest()
            # ipfs file uri
            image = "ipfs://" + hash
            # file mimetype
            image_mimetype = file.mimetype
            # create metadata structure
            metadata = {
                "name" : name,
                "decimals" : decimals,
                "description" : description,
                "image" : image,
                "image_integrity" : image_integrity,
                "image_mimetype" : image_mimetype
                # the amount of metadata can be extended
                # https://github.com/algorandfoundation/ARCs/blob/main/ARCs/arc-0003.md
            }
            # create metadata file
            with open('./python/metadata/metadata.json', 'w') as outfile:
                json.dump(metadata, outfile)
            response["created"] = True
            response["file"] = './python/metadata/metadata.json'
        except:
            response["exception"] = "exception in createMetadataJson"
        return response
    # method for creating nft asset
    def createAssetNFT(self, sender, unit_name, asset_name, total, decimals, metadata_uri, metadata_file):
        try:
            # get metadata file hash
            metadata_hash = getFileHash(metadata_file)

            # get suggested params
            params = self._algod_client.suggested_params()

            # set the creation address and the mnemonic in a fixed way
            ########################################################
            sender = CREATOR_ADDRESS
            private_key  = mnemonic.to_private_key(CREATOR_MNEMONIC)
            ########################################################
            # who owns the asset
            address = sender 
            # create asset config transaction
            txn = transaction.AssetConfigTxn(

                address,
                fee=params.fee,
                first=params.first,
                last=params.last,
                gh=params.gh,

                total=int(total),
                decimals=int(decimals),

                manager=address,
                reserve=None,
                freeze=None,
                clawback=None,
                
                unit_name=unit_name,
                asset_name=asset_name,
                url=metadata_uri,
                metadata_hash=metadata_hash,
                default_frozen=False,
                strict_empty_address_check=False
            )
            # sign transaction with private key(sender's private key)
            signedTxn = txn.sign(private_key)
            # send the transaction and get the id
            txId = self._algod_client.send_transaction(signedTxn)
            # wait for transaction confirmation
            wait_for_tx_confirmation(self._algod_client, txId)
            # from the transaction retrieve the index of the asset
            ptx = self._algod_client.pending_transaction_info(txId)
            return ptx['asset-index']
        except Exception as e:
            print(e)

        return "error"
    #
    def optInAssetNFT(self,asset_id):
        try:
            # get suggested params
            params = self._algod_client.suggested_params()

            ########################################################
            sender = CREATOR_ADDRESS
            private_key  = mnemonic.to_private_key(CREATOR_MNEMONIC)
            ########################################################

            address = sender 
            
            # check that we are not already in possession of the asset
            account_info = self._algod_client.account_info(address)
            holding = None
            idx = 0
            for my_account_info in account_info['assets']:
                scrutinized_asset = account_info['assets'][idx]
                idx = idx + 1    
                if (scrutinized_asset['asset-id'] == int(asset_id)):
                    holding = True
                    break

            if not holding:
                txn = AssetTransferTxn(
                    address,
                    params,
                    address,
                    0,
                    asset_id
                )

                # sign transaction with private key(sender's private key)
                signedTxn = txn.sign(private_key)
                # send the transaction and get the id
                txId = self._algod_client.send_transaction(signedTxn)
                # wait for transaction confirmation
                wait_for_tx_confirmation(self._algod_client, txId)

                return True

            return False
        except Exception as e:
            print(e)

        return False