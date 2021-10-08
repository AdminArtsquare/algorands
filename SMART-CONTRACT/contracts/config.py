from base import *
from algosdk.v2client import algod

debug = True
if debug:
    server = "testnet"
else:
    server = "mainnet"
algod_token = "DWv7SI71H29Gscwc6IeBW92OnxLHLIDW86jpgZWM"
algod_address = "https://"+server+"-algorand.api.purestake.io/ps2"
creator_mnemonic = "slam wait frequent tragic trial energy lecture album flavor april power blast palm machine renew bachelor tumble antique swing party guide imitate general abandon shallow"
# initialize an algodClient
algod_client = algod.AlgodClient(algod_token, algod_address, headers={'X-API-KEY': algod_token})

creator_private_key = get_private_key_from_mnemonic(creator_mnemonic)