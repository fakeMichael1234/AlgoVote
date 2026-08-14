from algosdk.v2client import algod

# Algorand TestNet
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""

client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

try:
    status = client.status()
    print("Connected to Algorand TestNet!")
    print("Last round:", status["last-round"])
except Exception as e:
    print("Connection failed:", e)
