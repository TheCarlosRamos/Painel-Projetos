import requests
import csv
import json
import os
import time
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('error_logs/execution_log_project_info.txt', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Configurações da API
BASE_URL = "https://api.sif-source.org"
AUTH = ('adminppi.source@presidencia.gov.br', 'PPI#source147')
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Referer': 'https://www.sif-source.org/',
    'Origin': 'https://www.sif-source.org'
}

def make_api_call(guid, session):
    """Faz a chamada da API para obter informações básicas do projeto."""
    
    url = f"https://api.sif-source.org/projects/{guid}?SPHostUrl=https%3A%2F%2Fwww.sif-source.org&SPLanguage=pt-BR&SPClientTag=0&SPProductNumber=15.0.5023.1005"
    
    try:
        response = session.get(url, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            logging.warning(f"Projeto {guid} não encontrado (404)")
            return None
        elif response.status_code == 500:
            logging.error(f"Erro 500 no projeto {guid}")
            return None
        else:
            logging.error(f"Erro {response.status_code} no projeto {guid}: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro de requisição para o projeto {guid}: {e}")
        return None

def save_response(guid, data):
    """Salva a resposta JSON em um arquivo."""
    
    output_dir = "responses_project_info"
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"response_{guid}_project_info.json"
    filepath = os.path.join(output_dir, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logging.error(f"Erro ao salvar arquivo {filename}: {e}")
        return False

def main():
    """Função principal."""
    
    print("Iniciando coleta de informações básicas dos projetos...")
    print(f"Data/hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    # Criar diretório de logs se não existir
    os.makedirs("error_logs", exist_ok=True)
    
    # Ler GUIDs do arquivo CSV
    guids = []
    try:
        with open('projects.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                guids.append(row['guid'])
        print(f"Carregados {len(guids)} GUIDs do arquivo projects.csv")
    except Exception as e:
        logging.error(f"Erro ao ler projects.csv: {e}")
        return
    
    # Criar sessão HTTP
    session = requests.Session()
    session.auth = AUTH
    
    # Estatísticas
    success_count = 0
    error_count = 0
    total_requests = len(guids)
    
    # Processar cada GUID
    for i, guid in enumerate(guids, 1):
        print(f"Processando {i}/{total_requests}: {guid}")
        
        # Fazer chamada da API
        data = make_api_call(guid, session)
        
        if data:
            # Salvar resposta
            if save_response(guid, data):
                success_count += 1
                print(f"  ✅ Sucesso - Salvo em responses_project_info/")
            else:
                error_count += 1
                print(f"  ❌ Erro ao salvar arquivo")
        else:
            error_count += 1
            print(f"  ❌ Falha na requisição")
        
        # Pausa para não sobrecarregar a API
        time.sleep(0.5)
        
        # Progresso a cada 50 requisições
        if i % 50 == 0:
            print(f"\nProgresso: {i}/{total_requests} ({i/total_requests*100:.1f}%)")
            print(f"Sucessos: {success_count}, Erros: {error_count}")
            print("-" * 40)
    
    # Estatísticas finais
    print("\n" + "=" * 60)
    print("ESTATÍSTICAS FINAIS")
    print("=" * 60)
    print(f"Total de requisições: {total_requests}")
    print(f"Sucessos: {success_count}")
    print(f"Erros: {error_count}")
    print(f"Taxa de sucesso: {(success_count/total_requests)*100:.1f}%")
    print(f"Data/hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main()
