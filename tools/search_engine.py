import os
import argparse

def search_in_files(query, directory):
    results = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Focando em arquivos de texto/código comuns
            if file.endswith(('.py', '.txt', '.md', '.env', '.json', '.yml', '.yaml')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            if query in line:
                                results.append(f"{file_path}:{line_num}: {line.strip()}")
                except Exception:
                    continue 
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Busca texto dentro de arquivos.")
    parser.add_argument("query", help="O texto a ser buscado.")
    parser.add_argument("directory", help="O diretório onde a busca será realizada.")
    args = parser.parse_args()

    matches = search_in_files(args.query, args.directory)
    if matches:
        print("\n".join(matches))
    else:
        print("Nenhuma correspondência encontrada.")
