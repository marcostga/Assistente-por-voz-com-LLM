import urllib.request
import urllib.error
import argparse
import sys

def make_request(url, method="GET", data=None):
    try:
        if method.upper() == "GET":
            req = urllib.request.Request(url)
        elif method.upper() == "POST":
            if data is None:
                return "Erro: Dados necessários para POST."
            req = urllib.request.Request(url, data=data.encode('utf-8'))
        else:
            return f"Erro: Método {method} não suportado."

        with urllib.request.urlopen(req) as response:
            status = response.getcode()
            body = response.read().decode('utf-8')
            return f"Status: {status}\nBody: {body}"
    except Exception as e:
        return f"Erro na requisição: {str(e)}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cliente HTTP simples para uso via terminal.")
    parser.add_argument("url", help="A URL para a requisição.")
    parser.add_argument("--method", default="GET", help="Método HTTP (GET, POST).")
    parser.add_argument("--data", help="Dados para o corpo do POST.")
    args = parser.parse_args()

    result = make_request(args.url, args.method, args.data)
    print(result)
