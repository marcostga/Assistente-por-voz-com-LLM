import websocket
import json

def list_animations():
    ws = websocket.WebSocket()
    try:
        ws.connect("ws://localhost:8001")
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "list_anim",
            "messageType": "AnimationListRequest"
        }
        ws.send(json.dumps(payload))
        response = json.loads(ws.recv())
        ws.close()
        return response.get("data", {}).get("animations", [])
    except Exception as e:
        return []

if __name__ == "__main__":
    animations = list_animations()
    with open("animations_list.txt", "w", encoding="utf-8") as f:
        for anim in animations:
            f.write(f"{anim['name']} | {anim['file']}\n")
    print(f"Encontradas {len(animations)} animações. Lista salva em animations_list.txt")
