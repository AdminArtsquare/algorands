$(document).ready(function() {
    $( "#form" ).submit(async function( event ) {
        event.preventDefault();
        var input = $('#img').prop('files');
        if(input && input[0]){
            var reader  = new FileReader();
            reader.onload = function(e)  {
                $("#img_pinned").attr("src", e.target.result);
                $("#btn_hash").attr("disabled", false);
             }
             reader.readAsDataURL(input[0]);
        }
    });
    $( "#btn_hash" ).click(async function( event ) {
        event.preventDefault();
        var input = $('#img').prop('files');
        await pinFileToIPFS(input);
    });
});

// https://docs.ipfs.io/how-to/best-practices-for-nft-data/66240
// function for generating the ipfs hash of a file
async function pinFileToIPFS(image){
    // check the validity of the file
    if(image && image[0]){
        // check that the pinata servers are accessible
        var auth = await pinataAuth();
        if(auth){
            var url = url_base_pinata_api + "pinning/pinFileToIPFS";
            // create the request parameters
            var data = new FormData();
            // attach the file
            data.append('file', image[0]);
            // set the settings for the request (optional)
            const pinataOptions = JSON.stringify({
                cidVersion: 1, // indica la versione ipfs
                /*  If wrapWithDirectory is set to true, it puts the file into a directory, which then allows you to recover
                    the file either by hash or by filename; it also generates two hashes, one for the folder and one for the file.
                    If set to false it generates only the hash of the file.
                    https://flyingzumwalt.gitbooks.io/decentralized-web-primer/content/files-on-ipfs/lessons/wrap-directories-around-content.html */
                wrapWithDirectory: false,
                /*  It allows you to replicate content across multiple nodes and regions, theoretically allowing you to retrieve files faster. It can be set globally for everyone or specific.
                    The only ones available are FRA1 (Frankfurt, Germany) and NYC1 (New York, USA); for others you have to contact them. 
                    https://docs.pinata.cloud/regions-and-replications#what-if-i-need-additional-regions-or-replications */
               customPinPolicy: {
                    regions: [
                        {
                            id: 'FRA1',
                            desiredReplicationCount: 2
                        },
                        {
                            id: 'NYC1',
                            desiredReplicationCount: 2
                        }
                    ]
                }
            })
            data.append('pinataOptions', pinataOptions);
            // send the request
            try{
                // POST request
                var result = await $.ajax({
                    url: url,
                    type: 'post',
                    headers: pinata_headers,
                    data: data,
                    processData: false,
                    contentType: false
                });
                // retrieving content hash from the response
                hash = result["IpfsHash"];
                $("#img_hash").append(hash);
                addLog("IPFS CID: " + hash);
                addLog("View your file at the following link https://gateway.pinata.cloud/ipfs/" + hash)
                enableNFT();
                disableHash();

            }catch(error){
                console.error(error);
            }
        }else{
            console.log("pinata connection node unreachable")
        }
    }else{
        console.log("no images uploaded")
    }
}
// function to check that pinata servers and bees are accessible
async function pinataAuth(){
    let auth = false;
    var url = url_base_pinata_api + "data/testAuthentication";
    try{
        await $.ajax({
            url: url,
            type: 'get',
            headers: pinata_headers
        });
        auth = true;
    }catch(error){
        console.error(error);
    }
    return auth;
}
// enable nft buttons
function enableNFT(){
    $("#short_name").attr("disabled", false);
    $("#short_descr").attr("disabled", false);
    $("#asset_name").attr("disabled", false);
    $("#unit_name").attr("disabled", false);
    $("#total").attr("disabled", false);
    $("#btn_nft").attr("disabled", false);
}
// disable hash creation buttons
function disableHash(){
    $("#btn_hash").attr("disabled", true);
    $("#form_submit").attr("disabled", true);
    $("#img").attr("disabled", true);
}