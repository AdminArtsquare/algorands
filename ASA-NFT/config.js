//TODO: The generation of the ipfs hash will have to be moved to the backend, it is not correct for the client to handle it.
const debug = true;
/** PINATA **/
// PINATA URL
const url_base_pinata_api = "https://api.pinata.cloud/";
const url_base_pinata_gateway = "https://gateway.pinata.cloud/ipfs/";
// PINATA KEY
const pinata_api_key = "8e6f31a8da7c9949f400";
const pinata_secret_api_key = "8782d21e40028375dd7451c4b0053c6609919657502a6421a9b4cefbe08e2ea3";
// CONF
const pinata_headers = {
    pinata_api_key: pinata_api_key,
    pinata_secret_api_key: pinata_secret_api_key
};
/** PURESTAKE  **/
const purestake_api_key = "DWv7SI71H29Gscwc6IeBW92OnxLHLIDW86jpgZWM";
const purestake_token = {
    "X-API-KEY": purestake_api_key
};
const port = "";
var server = debug ? "testnet" : "mainnet";
const algo_server = "https://"+server+"-algorand.api.purestake.io/ps2";
const algo_indexer = "https://"+server+"-algorand.api.purestake.io/idx2";
const ledger_network = debug ? 'TestNet' : 'MainNet';