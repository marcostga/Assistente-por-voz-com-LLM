import websocket
import json
import sys

def set_expression(expression_file):
    ws = websocket.WebSocket()
    try:
        ws.connect("ws://localhost:8001")
        # Autenticação prévia não é necessária se a sessão estiver ativa, 
        # mas o comando de expressão precisa do nome do arquivo da expressão.
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "set_exp",
            "messageType": "ExpressionActivationRequest",
            "data": {"expressionFile": expression_file}
        }
        ws.send(json.dumps(payload))
        print(ws.recv())
        ws.close()
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    exp = sys.argv[1] if len(sys.argv) > 1 else "default"
    set_expression(exp)
