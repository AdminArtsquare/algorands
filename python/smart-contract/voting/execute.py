from asq import *
from app import *
from escrow import *
from app_function import *

def setup():

    _algo_client = algod.AlgodClient(PURESTAKE_API_KEY, ALGO_SERVER, PURESTAKE_HEADERS)

    asa_id = get_asq()
    print("Asset Index: " + str(asa_id))

    # configuration of the registration and voting period
    status = _algo_client.status()
    regBegin = status["last-round"] + 15
    regEnd = regBegin + 10
    voteBegin = regEnd + 1
    voteEnd = voteBegin + 10

    print(f"Registration rounds: {regBegin} to {regEnd}")
    print(f"Vote rounds: {voteBegin} to {voteEnd}")

    app_args = [
        intToBytes(regBegin),
        intToBytes(regEnd),
        intToBytes(voteBegin),
        intToBytes(voteEnd),
    ]

    app_id = get_app(app_args)
    print("Application Index: " + str(app_id))

    read_global_state(app_id)

    escrowAddress = get_escrow(asa_id, app_id)
    print("Escrow Address: " + escrowAddress)

    activateEscrow(escrowAddress)
    print("ActivateEscrow complete")

    optInEscrow(asa_id, app_id, escrowAddress)
    print("OptInEscrow complete")

    vote_setup(asa_id, app_id, escrowAddress)
    print("VoteSetup complete")

    return [ asa_id, app_id, escrowAddress, regBegin, voteBegin, voteEnd]

if __name__ == "__main__":

    _algo_client = algod.AlgodClient(PURESTAKE_API_KEY, ALGO_SERVER, PURESTAKE_HEADERS)

    params = setup()

    print("Wait for registration begin")
    wait_for_round(_algo_client, params[3])

    # opt-in user to app 
    register(params[1])

    read_local_state(params[1])

    print("Wait for vote begin")
    wait_for_round(_algo_client, params[4])

    vote(params[0], params[1], params[2])

    read_local_state(params[1])

    print("Wait for vote end")
    wait_for_round(_algo_client, params[5])

    read_global_state(params[1])

    withdraw(params[0], params[1], params[2])

    delete(params[1])