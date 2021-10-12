$(document).ready(function() {
    $( "#btn_nft" ).click(async function( event ) {
        event.preventDefault();
        var unitName = $("#unit_name").val();
        var assetName = $("#asset_name").val();
        var hash = $("#img_hash").text();
        var shortName = $("#short_name").val();
        var shortDesc = $("#short_descr").val();
        await createNftASA(shortName, shortDesc, unitName, assetName, hash, 1, 0);
    });
    $( "#btn_nft_fract" ).click(async function( event ) {
        event.preventDefault();
        var unitName = $("#unit_name").val();
        var assetName = $("#asset_name").val();
        var hash = $("#img_hash").text();
        var shortName = $("#short_name").val();
        var shortDesc = $("#short_descr").val();
        await createNftASA(shortName, shortDesc, unitName, assetName, hash, 10, 1);
    });
    $( "#btn_swap" ).click(async function( event ) {
        event.preventDefault();
        var assetId = $("#asset_id").val();
        var toAddress = $("#to_address").val();
        var amount = 1;
        await swapNftASA(assetId, toAddress, amount);
    });
});
// function to initialize the necessary basic components
async function baseInit(){
    // check that the algosigner plugin is present (if the mnemonic is present this is not necessary, because it only serves to recover the account from the wallet)
    checkAlgoSigner();
    // connection to the algosigner wallet
    await connectAlgoSigner();
    // retrieve the client for connections to the node (via purestake)
    var client = await getClient();
    return client;
}
// function for creating an ASA NFT
async function createNftASA(shortName, shortDesc, unitName, assetName, hash, total, decimals){
    //
    var client = await baseInit();
    // retrieve the accounts present in the wallet
    var accounts = await getAccounts();
    // retrieve the basic parameters for creating a transaction from the network
    var params = await getParams(client);
    // create the transaction to create the asa nft and convert it to base 64
    var txn_b64 = await createAssetTxnNFT(accounts[0]["address"], shortName, shortDesc, unitName, assetName, hash, total, decimals, params);
    // transaction is signed via the wallet
    var signedTxn = await signTxn(txn_b64);
    // send the transaction
    await sendTxn(signedTxn);
}
// function for swap an ASA NFT
async function swapNftASA(assetId, toAddress, amount){
    // init the necessary basic components
    var client = await baseInit();
    // retrieve the accounts present in the wallet
    var accounts = await getAccounts();
    // recover the asa asset
    var asset = await getAssetById(assetId);
    // check that the asset actually belongs to one of the wallet accounts
    var permission = false;
    for(let account of accounts){
        if(account["address"] == asset["params"]["creator"]){
            permission = true;
            break;
        }
    }
    if(permission){
        // retrieve the basic parameters for creating a transaction from the network
        var params = await getParams(client);
        var txn_b64 = await createAssetTxnOptIn(asset["params"]["creator"], toAddress, asset["index"], amount, params);
        // transaction is signed via the wallet
        var signedTxn = await signTxn(txn_b64);
        // send the transaction
        await sendTxn(signedTxn);
    }else{
        addLog("you have no permissions on this asset");
    }
}
// function that checks that the AlgoSigner wallet is present. True if present.
function checkAlgoSigner(){
    if (typeof AlgoSigner !== 'undefined') {
        addLog("AlgoSigner is installed.");
        return true;
      } else {
        addLog("AlgoSigner is NOT installed.");
        return false;
      };
}
// function for the connection to the wallet for the recovery of the account
async function connectAlgoSigner(){
    try{
        await AlgoSigner.connect();
        addLog("AlgoSigner connected.");
        return true;
    }catch(error){
        addLog(error);
        return false;
    }
}
// function for retrieving the client to connect to the node
async function getClient(){
    var client = new algosdk.Algodv2(purestake_token, algo_server, port);
    try{
        await client.healthCheck();
        addLog("Algorand client setup ok.");
        return client;
    }catch(error){
        addLog(error);
    }
    return null;
}
// function for recovering the accounts present in the walletnt
async function getAccounts(){
    var accounts = null;
    try{
        accounts = await AlgoSigner.accounts({ledger: ledger_network});
        addLog("Algorand get account ok.");
    }catch(error){
        addLog(error);
    }
    return accounts;
}
// function for retrieving the basic parameters for creating a transaction via the network
async function getParams(client){
    var params = null;
    try{
        params = await client.getTransactionParams().do();
        addLog("Algorand get params ok.");
        //addLog(JSON.stringify(params));
    }catch(error){
        addLog(error);
    }
    return params;
}
// function for creating a transaction (specific for the creation of a nft) and converting to base 64
async function createAssetTxnNFT(address, shortName, shortDesc, unitName, assetName, hash, total, decimals, params){
    var txn_b64 = null;
    try{
        
        var addr = address;
        /** The CID generated by IPFS (hash) is larger than 32 bytes, so we save the metadata in the notes field, we have space up to 1000byte !! **/
        var note = algosdk.encodeObj(JSON.stringify({
            name: shortName,
            description: shortDesc,
            ipfs_cid: "ipfs://" + hash 
        })); 

        //var total = 1; // 1 only asset total defines "NON FUNGIBLE ASSETS"
        //var decimals = 0;
        var defaultFrozen = false;
        var manager = address;
        var reserve = address;
        var freeze = undefined; // address of account used to freeze holdings of this asset, it must be empty, otherwise no one would buy it
        var clawback = undefined; // Address of account used to clawback holdings of this assef, it must be empty, otherwise no one would buy it
        var assetURL = undefined;
        var assetMetadataHash = undefined;

        var suggestedParams = {...params};

        let txn = algosdk.makeAssetCreateTxnWithSuggestedParams(addr, note,
            total, decimals, defaultFrozen, manager, reserve, freeze,
            clawback, unitName, assetName, assetURL, assetMetadataHash, suggestedParams);
        // transform the transaction into base64
        txn_b64 = AlgoSigner.encoding.msgpackToBase64(txn.toByte());
        addLog("Algorand txn creation ok.");
    }catch(error){
        addLog(error);
    }
    return txn_b64;
}
// function for signing the transaction through the wallet
async function signTxn(txn_b64){
    var signedTxn = null;
    try{
        signedTxn = await AlgoSigner.signTxn([{txn: txn_b64}]);
        addLog("Algorand sign txn ok.");
    }catch(error){
        addLog(error);
    }
    return signedTxn;
}
// function for sending the transaction
async function sendTxn(signedTxn){
    try{
        AlgoSigner.send({
            ledger: ledger_network,
            tx: signedTxn[0].blob
          })
          .then((d) => {
            tx = d;
            addLog(tx["txId"]);
            $("#hash_txn").append(tx["txId"]);
          })
          .catch((error) => {
            addLog(error);
          });
    }catch(error){
        addLog(error);
    }
}
// function for recovering an asa via id
async function getAssetById(assetId){
    var assets = null;
    try{
        // parameters /v2/assets https://developer.purestake.io/apis/8d1bfrh5b9/prod
        assets = await AlgoSigner.indexer({ ledger: ledger_network, path: `/v2/assets?asset-id=${assetId}` });
    }catch(error){
        addLog(error);
    }
    return assets["assets"][0];
}
// function for creating a transaction opt in (specific for the swap of a nft) and converting to base 64
async function createAssetTxnOptIn(from, to, assetIndex, amount, params){
    var txn_b64 = null;
    try{
        let txn = algosdk.makeAssetTransferTxnWithSuggestedParamsFromObject({
            from: from,
            to: to,
            assetIndex: assetIndex,
            amount: amount,
            suggestedParams: {...params}
        });
        // transform the transaction into base64
        txn_b64 = AlgoSigner.encoding.msgpackToBase64(txn.toByte());
        addLog("Algorand asa txn opt-in creation ok.");
    }catch(error){
        addLog(error);
    }
    return txn_b64;
}