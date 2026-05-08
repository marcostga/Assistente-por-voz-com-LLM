import websocket
import json
import sys

def send_vts_command(command, data=None):
    ws = websocket.WebSocket()
    try:
        ws.connect("ws://localhost:8001")
        payload = {"apiName": "VTubeStudioPublicAPI", "apiVersion": "1.0", "requestID": "1", "messageType": command, "data": data or {}}
        ws.send(json.dumps(payload))
        result = ws.recv()
        ws.close()
        return result
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "APIStateRequest"
    print(send_vts_command(cmd))
