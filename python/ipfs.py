# library
import requests
import json

from werkzeug.datastructures import FileStorage
from conf import *
# class for Pinata ipfs
class PinataIpfs: 
    # constructor
    def __init__(self) -> None:
        self._auth_headers: Headers = {
            "pinata_api_key": PINATA_API_KEY,
            "pinata_secret_api_key": PINATA_SECRET_API_KEY,
        }
    # method to check that the pinata node and server is accessible
    def pinataAuth(self):
        url: str = API_ENDPOINT + "data/testAuthentication"
        headers: Headers = self._auth_headers
        response: requests.Response = requests.get(url = url, headers = headers)
        return response.ok
    # method to generate ipfs hashes from file
    def pinFileToIPFS(self, file):
        resp = { }
        url: str = API_ENDPOINT + "pinning/pinFileToIPFS"
        headers: Headers = self._auth_headers

        try:
            file.seek(0)
            sendFile = {"file": (file.filename, file.stream, file.mimetype)}
        except:
            # it is used to manage the upload of the metadata file in json
            fp = open(file, 'rb')
            file = FileStorage(fp)
            file.seek(0)
            sendFile = {"file": ('metadata.json', file.stream, 'application/json')}
        
        data = { 
            "pinataOptions" :
                { 
                    "cidVersion" : 1,
                    "wrapWithDirectory" : False,
                    "customPinPolicy" :
                        { 
                            "regions" : 
                            [ 
                                { "id": "FRA1", "desiredReplicationCount" : 2 },
                                { "id": "NYC1", "desiredReplicationCount" : 2 }
                            ] 
                        } 
                }
            }
        data = json.dumps(data, separators=(',', ':'))
        response: requests.Response = requests.post(url = url, files = sendFile, headers = headers, json = data)
        if(response.status_code == requests.codes.ok):
            json_data = json.loads(response.text)
            hash = json_data["IpfsHash"]
            resp["hash"] = hash
        else:
            resp["error"] = "error"
        try:
            # only in case of uploading the metadata file in json
            fp.close()
        finally:
            return resp