import csv
import requests
import os
import json
import time
from urllib.parse import quote
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import threading

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
        pool_connections=15,  # Aumentado para paralelismo
        pool_maxsize=15       # Aumentado para paralelismo
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
    })
    
    return session

def make_api_call(guid, url_code, session=None):
    """Faz uma chamada à API para um GUID e URL específicos."""
    base_url = "https://api.sif-source.org"
    endpoint = f"/projects/{guid}/questions/search/{url_code}"
    
    # Parâmetros como parte da URL para evitar problemas de codificação
    params = [
        ("SPHostUrl", "https://www.sif-source.org"),
        ("SPLanguage", "pt-BR"),
        ("SPClientTag", "0"),
        ("SPProductNumber", "15.0.5023.1183"),
        ("_t", str(int(time.time() * 1000)))  # Adiciona timestamp para evitar cache
    ]
    
    # Construir a URL manualmente para garantir a formatação correta
    query_string = "&".join([f"{k}={requests.utils.quote(str(v))}" for k, v in params])
    url = f"{base_url}{endpoint}?{query_string}"
    
    # Credenciais de autenticação
    auth = ('adminppi.source@presidencia.gov.br', 'PPI#source147')
    
    # Usar a sessão fornecida ou criar uma nova
    use_session = session if session else create_session()
    
    try:
        start_time = time.time()
        response = use_session.get(
            url,
            auth=auth,
            timeout=15,  # Timeout razoável
            verify=True  # Verificar certificado SSL
        )
        
        # Se a resposta for bem-sucedida, retorna o JSON
        if response.status_code == 200:
            try:
                json_data = response.json()
                return json_data
            except json.JSONDecodeError:
                return None
            
        # Se houver erro, salva apenas informações essenciais
        error_dir = "error_logs"
        if not os.path.exists(error_dir):
            os.makedirs(error_dir)
            
        error_file = os.path.join(error_dir, f"error_{guid}_{url_code}.json")
        error_data = {
            'status_code': response.status_code,
            'reason': response.reason,
            'url': response.url,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(error_file, 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=2)
            
        return None
        
    except requests.exceptions.RequestException:
        return None
    except Exception:
        return None

def save_response(guid, url_code, url_title, data, output_dir="responses_2000711"):
    """Salva a resposta em um arquivo JSON com nome descritivo."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Criar um nome de arquivo seguro a partir do GUID e URL
    safe_guid = guid.replace('-', '_')
    safe_url_code = url_code.replace('/', '_')
    safe_title = url_title.replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '').lower()
    filename = f"{output_dir}/response_{safe_guid}_{safe_url_code}_{safe_title}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return filename

def process_request(guid, url_code, url_title, session, stats_lock, log_file):
    """Processa uma única requisição em paralelo."""
    try:
        # Fazer a chamada à API
        response_data = make_api_call(guid, url_code, session)
        
        # Registrar no log
        log_entry = f"{time.strftime('%Y-%m-%d %H:%M:%S')} - GUID: {guid}, URL: {url_code} ({url_title})"
        
        success = False
        if response_data is not None:
            filename = save_response(guid, url_code, url_title, response_data)
            print(f"Thread-{threading.current_thread().name} {guid[:8]}... {url_code}: SUCESSO")
            log_entry += " - SUCESSO\n"
            success = True
        else:
            print(f"Thread-{threading.current_thread().name} {guid[:8]}... {url_code}: FALHA")
            log_entry += " - FALHA\n"
        
        # Escrever no log com thread safety
        with stats_lock:
            with open(log_file, 'a', encoding='utf-8') as log:
                log.write(log_entry)
        
        return success
        
    except Exception as e:
        print(f"Thread-{threading.current_thread().name} Erro em {guid[:8]}... {url_code}: {str(e)}")
        return False

def main():
    # Caminhos dos arquivos
    projects_file = "projects.csv"
    url_code = "2000711"
    url_title = "setor_do_projeto_ppi"
    
    # Criar diretório de logs de erro
    error_dir = "error_logs"
    if not os.path.exists(error_dir):
        os.makedirs(error_dir)
    
    # Ler os GUIDs dos projetos
    try:
        guids = read_guids(projects_file)
        print(f"Encontrados {len(guids)} GUIDs no arquivo {projects_file}")
    except Exception as e:
        print(f"Erro ao ler o arquivo {projects_file}: {e}")
        return

    # Preparar todas as requisições
    all_requests = [(guid, url_code, url_title) for guid in guids]
    
    total_requests = len(all_requests)
    print(f"Total de chamadas a serem feitas: {total_requests}")
    print("Processamento paralelo iniciado...")
    print("Pressione Ctrl+C para interromper a qualquer momento\n")
    
    # Criar arquivo de log
    log_file = os.path.join(error_dir, f"execution_log_{url_code}.txt")
    start_time = time.strftime("%Y-%m-%d %H:%M:%S")
    
    with open(log_file, 'a', encoding='utf-8') as log:
        log.write(f"\n{'='*50}\n")
        log.write(f"Início da execução: {start_time}\n")
        log.write(f"Total de requisições: {total_requests}\n")
        log.write(f"URL: {url_code} - {url_title}\n")
        log.write(f"Threads simultâneas: 10\n")
    
    # Configuração do processamento paralelo
    max_workers = 10  # Número de threads para paralelismo
    stats_lock = Lock()
    success_count = 0
    error_count = 0
    
    try:
        # Criar múltiplas sessões para melhor performance
        sessions = [create_session() for _ in range(max_workers)]
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submeter todas as tarefas
            futures = []
            for i, (guid, url_code, url_title) in enumerate(all_requests):
                session = sessions[i % max_workers]  # Round-robin de sessões
                future = executor.submit(
                    process_request, 
                    guid, url_code, url_title, session, stats_lock, log_file
                )
                futures.append(future)
            
            # Processar resultados conforme são completados
            completed = 0
            for future in as_completed(futures):
                completed += 1
                if future.result():
                    success_count += 1
                else:
                    error_count += 1
                
                # Progresso a cada 50 requisições
                if completed % 50 == 0:
                    progress = (completed / total_requests) * 100
                    print(f"\nProgresso: {completed}/{total_requests} ({progress:.1f}%) - Sucessos: {success_count} Falhas: {error_count}")
                
                # Pausa mínima entre batches para não sobrecarregar
                if completed % 25 == 0:
                    time.sleep(0.2)
        
        # Fechar todas as sessões
        for session in sessions:
            session.close()
            
    except KeyboardInterrupt:
        print("\n\nExecução interrompida pelo usuário.")
    except Exception as e:
        print(f"\nErro inesperado: {str(e)}")
    finally:
        # Estatísticas finais
        end_time = time.strftime("%Y-%m-%d %H:%M:%S")
        total_processed = success_count + error_count
        
        print("\n" + "="*50)
        print("RESUMO DA EXECUÇÃO")
        print("="*50)
        print(f"Início: {start_time}")
        print(f"Término: {end_time}")
        print(f"Total de requisições: {total_requests}")
        print(f"Requisições processadas: {total_processed}")
        print(f"Sucessos: {success_count}")
        print(f"Falhas: {error_count}")
        
        if total_processed > 0:
            success_rate = (success_count / total_processed) * 100
            print(f"Taxa de sucesso: {success_rate:.1f}%")
        
        # Atualizar o log com as estatísticas finais
        with open(log_file, 'a', encoding='utf-8') as log:
            log.write("\n" + "="*50 + "\n")
            log.write(f"Término da execução: {end_time}\n")
            log.write(f"Total de requisições: {total_requests}\n")
            log.write(f"Requisições processadas: {total_processed}\n")
            log.write(f"Sucessos: {success_count}\n")
            log.write(f"Falhas: {error_count}\n")
            
        print(f"\nLog detalhado salvo em: {os.path.abspath(log_file)}")
        print(f"Diretório de saída: responses_2000711")

if __name__ == "__main__":
    main()
