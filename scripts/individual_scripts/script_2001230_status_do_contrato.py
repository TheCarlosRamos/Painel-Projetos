import csv
import requests
import os
import json
import time
from urllib.parse import quote
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def read_guids(file_path):
    """Lê os GUIDs do arquivo CSV."""
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        # Pular o cabeçalho se existir
        next(reader, None)
        return [row[0].strip() for row in reader if row and row[0].strip()]

def create_session():
    """Cria uma sessão com configurações de retry e headers."""
    session = requests.Session()
    
    # Configuração de retry mais tolerante
    retry_strategy = Retry(
        total=2,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
        respect_retry_after_header=True
    )
    
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=10,
        pool_maxsize=10
    )
    
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    
    # Headers atualizados
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Referer': 'https://www.sif-source.org/',
        'Origin': 'https://www.sif-source.org',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"'
    })
    
    return session

def make_api_call(session, guid, url_code):
    """Faz a chamada da API para um GUID específico."""
    
    # Construir URL
    base_url = "https://api.sif-source.org"
    endpoint = f"/projects/{guid}/questions/search/{url_code}"
    
    # Parâmetros da URL
    params = {
        'SPHostUrl': 'https://www.sif-source.org',
        'SPLanguage': 'pt-BR',
        'SPClientTag': '0',
        'SPProductNumber': '15.0.5023.1183',
        '_t': int(time.time() * 1000)
    }
    
    # Construir URL completa
    url = f"{base_url}{endpoint}"
    
    # Autenticação
    auth = ('adminppi.source@presidencia.gov.br', 'PPI#source147')
    
    try:
        response = session.get(url, params=params, auth=auth, timeout=30)
        
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except requests.exceptions.RequestException as e:
        return None, f"Erro de requisição: {str(e)}"
    except json.JSONDecodeError as e:
        return None, f"Erro ao decodificar JSON: {str(e)}"
    except Exception as e:
        return None, f"Erro inesperado: {str(e)}"

def save_response(guid, url_code, response_data, output_dir):
    """Salva a resposta JSON em um arquivo."""
    
    # Criar diretório de saída se não existir
    os.makedirs(output_dir, exist_ok=True)
    
    # Nome do arquivo
    filename = f"response_{guid}_{url_code}_status_do_contrato.json"
    filepath = os.path.join(output_dir, filename)
    
    # Salvar arquivo
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(response_data, file, ensure_ascii=False, indent=2)
    
    return filepath

def log_execution(guid, url_code, success, error_message, log_file):
    """Registra o resultado da execução."""
    
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    
    with open(log_file, 'a', encoding='utf-8') as file:
        if success:
            file.write(f"{timestamp} - GUID: {guid} - SUCESSO\n")
        else:
            file.write(f"{timestamp} - GUID: {guid} - FALHA: {error_message}\n")

def main():
    """Função principal."""
    
    # Configurações
    url_code = "2001230"
    url_title = "status do contrato"
    
    # Caminhos dos arquivos
    guids_file = "../projects.csv"
    output_dir = f"../responses_{url_code}"
    log_file = f"../error_logs/execution_log_{url_code}.txt"
    
    # Criar diretório de logs se não existir
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    print(f"Processando URL {url_code} ({url_title})")
    print(f"Arquivo de GUIDs: {guids_file}")
    print(f"Diretório de saída: {output_dir}")
    print(f"Arquivo de log: {log_file}")
    print("=" * 50)
    
    # Ler GUIDs
    try:
        guids = read_guids(guids_file)
        print(f"Total de GUIDs lidos: {len(guids)}")
    except Exception as e:
        print(f"Erro ao ler GUIDs: {e}")
        return
    
    # Criar sessão HTTP
    session = create_session()
    
    # Contadores
    total_requests = len(guids)
    processed_requests = 0
    success_count = 0
    failure_count = 0
    
    # Iniciar log
    start_time = time.strftime('%Y-%m-%d %H:%M:%S')
    with open(log_file, 'w', encoding='utf-8') as file:
        file.write(f"==================================================\n")
        file.write(f"Início da execução - URL {url_code} ({url_title}): {start_time}\n")
        file.write(f"Total de requisições: {total_requests}\n")
    
    # Processar cada GUID
    for i, guid in enumerate(guids, 1):
        print(f"\n[{'='*50}]")
        print(f"Processando GUID {i}/{len(guids)}")
        print(f"GUID: {guid}")
        
        # Fazer chamada da API
        response_data, error = make_api_call(session, guid, url_code)
        
        if response_data:
            # Salvar resposta
            try:
                filepath = save_response(guid, url_code, response_data, output_dir)
                print(f"✅ Resposta salva com sucesso: {filepath}")
                success_count += 1
                log_execution(guid, url_code, True, None, log_file)
            except Exception as e:
                print(f"❌ Erro ao salvar resposta: {e}")
                failure_count += 1
                log_execution(guid, url_code, False, f"Erro ao salvar: {e}", log_file)
        else:
            print(f"❌ Erro na chamada da API: {error}")
            failure_count += 1
            log_execution(guid, url_code, False, error, log_file)
        
        processed_requests += 1
        
        # Pequena pausa para não sobrecarregar a API
        time.sleep(0.1)
    
    # Finalizar log
    end_time = time.strftime('%Y-%m-%d %H:%M:%S')
    with open(log_file, 'a', encoding='utf-8') as file:
        file.write(f"\n==================================================\n")
        file.write(f"Término da execução: {end_time}\n")
        file.write(f"Total de requisições: {total_requests}\n")
        file.write(f"Requisições processadas: {processed_requests}\n")
        file.write(f"Sucessos: {success_count}\n")
        file.write(f"Falhas: {failure_count}\n")
    
    # Resumo final
    print(f"\n{'='*50}")
    print("RESUMO DA EXECUÇÃO")
    print(f"{'='*50}")
    print(f"URL: {url_code} - {url_title}")
    print(f"Início: {start_time}")
    print(f"Término: {end_time}")
    print(f"Total de requisições: {total_requests}")
    print(f"Requisições processadas: {processed_requests}")
    print(f"Sucessos: {success_count}")
    print(f"Falhas: {failure_count}")
    print(f"\nLog detalhado salvo em: {os.path.abspath(log_file)}")

if __name__ == "__main__":
    main()
