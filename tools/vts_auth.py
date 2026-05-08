import websocket
import json
import sys

def authenticate():
    ws = websocket.WebSocket()
    try:
        ws.connect("ws://localhost:8001")
        
        # 1. Solicitar Token
        token_req = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "auth_token",
            "messageType": "AuthenticationTokenRequest",
            "data": {"pluginName": "GHOST_AI", "pluginDeveloper": "GHOST", "pluginIcon": ""}
        }
        ws.send(json.dumps(token_req))
        response = json.loads(ws.recv())
        token = response["data"]["authenticationToken"]
        print(f"TOKEN RECEBIDO: {token}")
        print("POR FAVOR, AUTORIZE NO VTUBE STUDIO AGORA.")
        
        # 2. Autenticar
        auth_req = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "auth_login",
            "messageType": "AuthenticationRequest",
            "data": {"pluginName": "GHOST_AI", "pluginDeveloper": "GHOST", "authenticationToken": token}
        }
        ws.send(json.dumps(auth_req))
        print(ws.recv())
        ws.close()
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    authenticate()
