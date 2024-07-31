import asyncio
import websockets
import json
from rich import print

async def subscribe_to_logs(websocket):
    subscription_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "logsSubscribe",
        "params": [
            {"mentions": ["TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"]}
        ]
    }
    await websocket.send(json.dumps(subscription_request))

async def handle_log_message(data):
    if "method" in data and data["method"] == "logsNotification":
        log_message = data["params"]["result"]
        logs = log_message.get("value", {}).get("logs", [])
        relevant_log = False

        # Check for the specific sequence in logs
        required_logs = [
            'Instruction: MintTo'
        ]

        for log in logs:
            if any(req_log in log for req_log in required_logs):
                relevant_log = True

        if relevant_log:
            # Write to file
            with open("current.txt", "a") as f:
                f.write(f"{log_message}\n")
            # print(log_message)

async def monitor_new_tokens():
    uri = "wss://api.mainnet-beta.solana.com/"
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                await subscribe_to_logs(websocket)
                while True:
                    response = await websocket.recv()
                    data = json.loads(response)
                    await handle_log_message(data)
        except (websockets.ConnectionClosedError, websockets.ConnectionClosedOK) as e:
            print(f"Connection closed, reconnecting: {e}")
            await asyncio.sleep(1)  # Wait before reconnecting
        except Exception as e:
            print(f"Unexpected error: {e}")
            await asyncio.sleep(5)  # Wait longer before reconnecting in case of an unexpected error

asyncio.get_event_loop().run_until_complete(monitor_new_tokens())
