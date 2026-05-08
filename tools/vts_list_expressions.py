import websocket
import json

def list_expressions():
    ws = websocket.WebSocket()
    try:
        ws.connect("ws://localhost:8001")
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "list_exp",
            "messageType": "ExpressionListRequest"
        }
        ws.send(json.dumps(payload))
        response = json.loads(ws.recv())
        ws.close()
        return response.get("data", {}).get("expressions", [])
    except Exception as e:
        return []

if __name__ == "__main__":
    expressions = list_expressions()
    with open("expressions_list.txt", "w", encoding="utf-8") as f:
        for exp in expressions:
            f.write(f"{exp['file']}\n")
    print(f"Encontradas {len(expressions)} expressões. Lista salva em expressions_list.txt")
