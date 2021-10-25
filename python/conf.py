# libs
import typing
# custom
Headers = typing.Dict[str, str]
OptionsDict = typing.Dict[str, typing.Any]
# IPFS Pinata configuration
API_ENDPOINT: str = "https://api.pinata.cloud/"
PINATA_GATEWAY: str = "https://gateway.pinata.cloud/ipfs/"
PINATA_API_KEY: str = "8e6f31a8da7c9949f400"
PINATA_SECRET_API_KEY: str = "8782d21e40028375dd7451c4b0053c6609919657502a6421a9b4cefbe08e2ea3"
# Algorand Purestake configuration
PURESTAKE_API_KEY = "DWv7SI71H29Gscwc6IeBW92OnxLHLIDW86jpgZWM"
PURESTAKE_HEADERS = { "X-API-KEY": PURESTAKE_API_KEY }
PORT = ""
DEBUG = True
if DEBUG:
    SERVER = "testnet"
    LEDGER_NETWORK = "TestNet"
else:
    SERVER = "mainnet"
    LEDGER_NETWORK = "MainNet"
ALGO_SERVER = "https://"+SERVER+"-algorand.api.purestake.io/ps2"
ALGO_INDEXER = "https://"+SERVER+"-algorand.api.purestake.io/idx2"
# ONLY FOR TEST
CREATOR_MNEMONIC = "slam wait frequent tragic trial energy lecture album flavor april power blast palm machine renew bachelor tumble antique swing party guide imitate general abandon shallow"
CREATOR_ADDRESS = "DLHQDFU3FBKYDW4XPNGCQ6KSDRE7OZIUQMTZEXVV77ZOMLJNORCCGK664M"
# arch -x86_64 zsh