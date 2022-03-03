
To test the contracts, rename the file conf.py.example to conf.py and fill in the required data.

--- SETUP ---

#1) ASQ Asset creation => ASSET_ID
#2) APP Smart contract creation (Stateless) => APP_ID
#3) Escrow Smart contract creation (Stateful) => ESCROW_ADDRESS
#4) Activate Escrow address and opt-in to the app
#5) Set of the escrow address and the id of the asset in the app (only app creator)

--- VOTE ---

#1) User opt-in to the app before registration round start
#2) User send ASQ and the choice of vote to the app during registration round

--- WITHDRAW ---

#1) Only the creator of the app can collect the ASQ present in the escrow contract after vote round end