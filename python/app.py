# libs
from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS
from ipfs import PinataIpfs
from algo import PurestakeAlgorand
import math
# app init
app = Flask(__name__)
CORS(app)
api = Api(app)
# global
pinataIpfs = PinataIpfs()
purestakeAlgorand = PurestakeAlgorand()
# class to manage the entry point for generating the file hash
class PinFileToIPFS(Resource):
    def post(self):
        response = { }
        try:
            file = request.files['static_file']
            if(file.filename != ''):
                # get hash from upload file
                hash = pinataIpfs.pinFileToIPFS(file)
                response["hash"] = hash
            else:
                response["errore"] = "no_file"
        except:
            response["exception"] = "exception"
        return response
    pass
# class to manage the entry point for generating the metadata json file and hash
class CreateMetadataJson(Resource):
    def post(self):
        response = { }
        try:
            file = request.files['static_file']
            if(file.filename != ''):
                # get hash from upload file
                response = pinataIpfs.pinFileToIPFS(file)
                if(response["hash"] is not None):
                    asset_name = request.form['asset_name']
                    total = request.form['total']
                    if(total == '1'):
                        decimals = 0
                    else:
                        decimals = math.log10(int(total))
                    description = request.form['description']
                    # get metadata json and create file
                    response["metadata"] = purestakeAlgorand.createMetadataJson(asset_name, decimals, description, response["hash"], file)
                    if(response["metadata"]["created"]):
                        response["metadata"]["hash"] = pinataIpfs.pinFileToIPFS(response["metadata"]["file"])
            else:
                response["error"] = "no_file"
        except:
            response["exception"] = "exception in CreateMetadataJson"
        return response
    pass
# class to manage the creation of an NFT asset according to the arc3 convention
class CreateAssetNFT(Resource):
    def post(self):
        response = { }
        try:
            file = request.files['static_file']
            if(file.filename != ''):
                # get hash from upload file
                response = pinataIpfs.pinFileToIPFS(file)
                if(response["hash"] is not None):
                    asset_name = request.form['asset_name']
                    total = request.form['total']
                    if(total == '1'):
                        decimals = 0
                    else:
                        decimals = math.log10(int(total))
                    description = request.form['description']
                    # get metadata json and create file
                    response["metadata"] = purestakeAlgorand.createMetadataJson(asset_name, decimals, description, response["hash"], file)
                    if(response["metadata"]["created"]):
                        response["metadata"]["hash"] = pinataIpfs.pinFileToIPFS(response["metadata"]["file"])
                        if(response["metadata"]["hash"] is not None):
                            unit_name = request.form['unit_name']
                            metadata_uri = "ipfs://" + response["metadata"]["hash"]["hash"]
                            metadata_file = response["metadata"]["file"]
                            response["asset"] = purestakeAlgorand.createAssetNFT("", unit_name, asset_name, total, decimals, metadata_uri, metadata_file)
            else:
                response["error"] = "no_file"
        except:
            response["exception"] = "exception in CreateAssetNFT"
        return response
    pass
#
class OptInAssetNFT(Resource):
    def post(self):
        response = { }
        try:
            asset_id = request.form['asset_id']
            response = purestakeAlgorand.optInAssetNFT(asset_id)
        except:
            response["exception"] = "exception"
        return response
    pass
# entry point for generating the file hash
api.add_resource(PinFileToIPFS, '/pinFileToIPFS')
# entry point for generating the metadata json
api.add_resource(CreateMetadataJson, '/createMetadataJson')
# entry point for generating the asset nft
api.add_resource(CreateAssetNFT, '/createAssetNFT')
#
api.add_resource(OptInAssetNFT, "/optInAssetNFT");
# run app
if __name__ == '__main__':
    app.run()