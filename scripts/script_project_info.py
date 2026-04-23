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
    """Cria uma sessão otimizada com configurações de retry e headers."""
    session = requests.Session()
    
    # Configuração de retry otimizada
    retry_strategy = Retry(
        total=1,
        backoff_factor=0.1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
        respect_retry_after_header=False
    )
    
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=20,
        pool_maxsize=20
    )
    
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    
    # Headers otimizados
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Referer': 'https://www.sif-source.org/',
        'Origin': 'https://www.sif-source.org',
    })
    
    return session

def make_project_info_call(guid, session=None):
    """Faz uma chamada à API para obter informações básicas do projeto."""
    base_url = "https://api.sif-source.org"
    endpoint = f"/projects/{guid}"
    
    # Parâmetros como parte da URL
    params = [
        ("SPHostUrl", "https://www.sif-source.org"),
        ("SPLanguage", "pt-BR"),
        ("SPClientTag", "0"),
        ("SPProductNumber", "15.0.5023.1005"),
        ("_t", str(int(time.time() * 1000)))
    ]
    
    # Construir a URL manualmente
    query_string = "&".join([f"{k}={requests.utils.quote(str(v))}" for k, v in params])
    url = f"{base_url}{endpoint}?{query_string}"
    
    # Credenciais de autenticação
    auth = ('adminppi.source@presidencia.gov.br', 'PPI#source147')
    
    # Usar a sessão fornecida ou criar uma nova
    use_session = session if session else create_session()
    
    try:
        response = use_session.get(
            url,
            auth=auth,
            timeout=10,
            verify=True
        )
        
        if response.status_code == 200:
            try:
                json_data = response.json()
                return json_data
            except json.JSONDecodeError:
                return None
        else:
            # Salvar erro
            error_dir = "error_logs"
            if not os.path.exists(error_dir):
                os.makedirs(error_dir)
                
            error_file = os.path.join(error_dir, f"error_project_info_{guid}.json")
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

def save_response(guid, data, output_dir="responses_project_info"):
    """Salva a resposta em um arquivo JSON."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Criar um nome de arquivo seguro a partir do GUID
    safe_guid = guid.replace('-', '_')
    filename = f"{output_dir}/response_{safe_guid}_project_info.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return filename

def process_request(guid, session, stats_lock, log_file):
    """Processa uma única requisição em paralelo."""
    try:
        # Fazer a chamada à API
        response_data = make_project_info_call(guid, session)
        
        # Registrar no log
        log_entry = f"{time.strftime('%Y-%m-%d %H:%M:%S')} - GUID: {guid}"
        
        success = False
        if response_data is not None:
            filename = save_response(guid, response_data)
            print(f"✅ [{threading.current_thread().name}] {guid[:8]}...: SUCESSO")
            log_entry += " - SUCESSO\n"
            success = True
        else:
            print(f"❌ [{threading.current_thread().name}] {guid[:8]}...: FALHA")
            log_entry += " - FALHA\n"
        
        # Escrever no log com thread safety
        with stats_lock:
            with open(log_file, 'a', encoding='utf-8') as log:
                log.write(log_entry)
        
        return success
        
    except Exception as e:
        print(f"❌ [{threading.current_thread().name}] Erro em {guid[:8]}...: {str(e)}")
        return False

def main():
    print("🔍 Iniciando coleta de informações básicas dos projetos...")
    
    # Caminho do arquivo
    projects_file = "projects.csv"
    
    # Criar diretório de logs de erro
    error_dir = "error_logs"
    if not os.path.exists(error_dir):
        os.makedirs(error_dir)
    
    # Ler os GUIDs dos projetos
    try:
        guids = read_guids(projects_file)
        print(f"📋 Encontrados {len(guids)} GUIDs no arquivo {projects_file}")
    except Exception as e:
        print(f"Erro ao ler o arquivo {projects_file}: {e}")
        return

    print(f"📊 Total de chamadas a serem feitas: {len(guids)}")
    print("🚀 Processamento paralelo otimizado iniciado...")
    print("Pressione Ctrl+C para interromper a qualquer momento\n")
    
    # Criar arquivo de log
    log_file = os.path.join(error_dir, "execution_log_project_info.txt")
    start_time = time.strftime("%Y-%m-%d %H:%M:%S")
    
    with open(log_file, 'a', encoding='utf-8') as log:
        log.write(f"\n{'='*50}\n")
        log.write(f"Início da execução PROJECT INFO: {start_time}\n")
        log.write(f"Total de requisições: {len(guids)}\n")
        log.write(f"Threads simultâneas: 15\n")
    
    # Configuração do processamento paralelo
    max_workers = 15
    stats_lock = Lock()
    success_count = 0
    error_count = 0
    
    try:
        # Criar múltiplas sessões para melhor performance
        sessions = [create_session() for _ in range(max_workers)]
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submeter todas as tarefas
            futures = []
            for i, guid in enumerate(guids):
                session = sessions[i % max_workers]
                future = executor.submit(
                    process_request, 
                    guid, session, stats_lock, log_file
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
                    progress = (completed / len(guids)) * 100
                    print(f"\n📊 Progresso: {completed}/{len(guids)} ({progress:.1f}%) - ✅{success_count} ❌{error_count}")
                
                # Pausa mínima entre batches
                if completed % 25 == 0:
                    time.sleep(0.1)
        
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
        print("RESUMO DA EXECUÇÃO - PROJECT INFO")
        print("="*50)
        print(f"Início: {start_time}")
        print(f"Término: {end_time}")
        print(f"Total de requisições: {len(guids)}")
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
            log.write(f"Total de requisições: {len(guids)}\n")
            log.write(f"Requisições processadas: {total_processed}\n")
            log.write(f"Sucessos: {success_count}\n")
            log.write(f"Falhas: {error_count}\n")
            
        print(f"\nLog detalhado salvo em: {os.path.abspath(log_file)}")
        print(f"📁 Dados salvos em: responses_project_info/")

if __name__ == "__main__":
    main()
