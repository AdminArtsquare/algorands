const debug = true;
/** PINATA **/
// PINATA URL
const url_base_pinata_api = "https://api.pinata.cloud/"; //DO NOT MODIFY
const url_base_pinata_gateway = "https://gateway.pinata.cloud/ipfs/"; //DO NOT MODIFY
// PINATA KEY
const pinata_api_key = "8e6f31a8da7c9949f400"; //PUT YOUR PINATA API KEY HERE
const pinata_secret_api_key = "8782d21e40028375dd7451c4b0053c6609919657502a6421a9b4cefbe08e2ea3"; //PUT YOUR PINATA SECRET API KEY HERE
// CONF
const pinata_headers = { //DO NOT MODIFY
    pinata_api_key: pinata_api_key, //DO NOT MODIFY
    pinata_secret_api_key: pinata_secret_api_key //DO NOT MODIFY
};
/** PURESTAKE  **/
const purestake_api_key = "DWv7SI71H29Gscwc6IeBW92OnxLHLIDW86jpgZWM"; //PUT YOUR PURESTAKE API KEY HERE
const purestake_token = { //DO NOT MODIFY
    "X-API-KEY": purestake_api_key //DO NOT MODIFY
};
const port = ""; //DO NOT MODIFY
var server = debug ? "testnet" : "mainnet";  //DO NOT MODIFY
const algo_server = "https://"+server+"-algorand.api.purestake.io/ps2"; //DO NOT MODIFY
const algo_indexer = "https://"+server+"-algorand.api.purestake.io/idx2"; //DO NOT MODIFY
const ledger_network = debug ? 'TestNet' : 'MainNet'; //DO NOT MODIFY