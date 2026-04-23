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
        total=1,  # Reduzido para 1 tentativa para maior velocidade
        backoff_factor=0.1,  # Reduzido backoff
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
        respect_retry_after_header=False  # Ignorar retry-after para velocidade
    )
    
    # Aumentado pool para processamento paralelo
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=20,  # Aumentado de 10 para 20
        pool_maxsize=20       # Aumentado de 10 para 20
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
    """Faz chamada à API para informações básicas do projeto."""
    base_url = "https://api.sif-source.org"
    endpoint = f"/projects/{guid}"
    
    # Parâmetros como parte da URL para evitar problemas de codificação
    params = [
        ("SPHostUrl", "https://www.sif-source.org"),
        ("SPLanguage", "pt-BR"),
        ("SPClientTag", "0"),
        ("SPProductNumber", "15.0.5023.1005"),
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
            timeout=10,  # Reduzido para 10 segundos para maior velocidade
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
        error_dir = "project_info_error_logs"
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

def make_question_call(guid, url_code, session=None):
    """Faz chamada à API para perguntas específicas do projeto."""
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
            timeout=10,  # Reduzido para 10 segundos para maior velocidade
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
        error_dir = "project_info_error_logs"
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

def save_project_info(guid, data, output_dir="project_info_responses"):
    """Salva a resposta de informações do projeto em um arquivo JSON."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Criar um nome de arquivo seguro a partir do GUID
    safe_guid = guid.replace('-', '_')
    filename = f"{output_dir}/project_info_{safe_guid}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return filename

def save_question_response(guid, url_code, url_title, data, output_dir="project_info_responses"):
    """Salva a resposta da pergunta em um arquivo JSON com nome descritivo."""
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

def process_project_info(guid, session, stats_lock, log_file):
    """Processa informações básicas do projeto em paralelo."""
    try:
        # Fazer a chamada à API para informações do projeto
        response_data = make_project_info_call(guid, session)
        
        # Registrar no log
        log_entry = f"{time.strftime('%Y-%m-%d %H:%M:%S')} - GUID: {guid} - PROJECT_INFO"
        
        success = False
        if response_data is not None:
            filename = save_project_info(guid, response_data)
            print(f"✅ [{threading.current_thread().name}] {guid[:8]}... PROJECT_INFO: SUCESSO")
            log_entry += " - SUCESSO\n"
            success = True
        else:
            print(f"❌ [{threading.current_thread().name}] {guid[:8]}... PROJECT_INFO: FALHA")
            log_entry += " - FALHA\n"
        
        # Escrever no log com thread safety
        with stats_lock:
            with open(log_file, 'a', encoding='utf-8') as log:
                log.write(log_entry)
        
        return success
        
    except Exception as e:
        print(f"❌ [{threading.current_thread().name}] Erro em {guid[:8]}... PROJECT_INFO: {str(e)}")
        return False

def process_question(guid, url_code, url_title, session, stats_lock, log_file):
    """Processa uma única requisição de pergunta em paralelo."""
    try:
        # Fazer a chamada à API
        response_data = make_question_call(guid, url_code, session)
        
        # Registrar no log
        log_entry = f"{time.strftime('%Y-%m-%d %H:%M:%S')} - GUID: {guid}, URL: {url_code} ({url_title})"
        
        success = False
        if response_data is not None:
            filename = save_question_response(guid, url_code, url_title, response_data)
            print(f"✅ [{threading.current_thread().name}] {guid[:8]}... {url_code}: SUCESSO")
            log_entry += " - SUCESSO\n"
            success = True
        else:
            print(f"❌ [{threading.current_thread().name}] {guid[:8]}... {url_code}: FALHA")
            log_entry += " - FALHA\n"
        
        # Escrever no log com thread safety
        with stats_lock:
            with open(log_file, 'a', encoding='utf-8') as log:
                log.write(log_entry)
        
        return success
        
    except Exception as e:
        print(f"❌ [{threading.current_thread().name}] Erro em {guid[:8]}... {url_code}: {str(e)}")
        return False

def main():
    # Caminho do arquivo de GUIDs
    projects_file = "projects.csv"
    
    # URLs específicas para informações do projeto
    project_urls = {
        "2000720": "subsecretaria",
        "2000726": "status_atual_do_projeto", 
        "2000727": "questoes_chaves",
        "2000728": "proximas_etapas_do_projeto",
        "2001218": "status_dos_estudos",
        "2001221": "status_consulta_publica",
        "2001224": "status_do_TCU",
        "2001226": "status_do_edital",
        "2001229": "status_do_leilao",
        "2001230": "status_do_contrato",
        "2001232": "descricao_do_projeto"
    }
    
    # Criar diretório de logs de erro
    error_dir = "project_info_error_logs"
    if not os.path.exists(error_dir):
        os.makedirs(error_dir)
    
    # Ler os GUIDs dos projetos
    try:
        guids = read_guids(projects_file)
        print(f"Encontrados {len(guids)} GUIDs no arquivo {projects_file}")
    except Exception as e:
        print(f"Erro ao ler o arquivo {projects_file}: {e}")
        return

    # Preparar todas as combinações de requisições
    all_requests = []
    
    # Adicionar requisições para informações básicas do projeto
    for guid in guids:
        all_requests.append(("project_info", guid, None, "PROJECT_INFO"))
    
    # Adicionar requisições para as perguntas específicas
    for guid in guids:
        for url_code, url_title in project_urls.items():
            all_requests.append(("question", guid, url_code, url_title))
    
    total_requests = len(all_requests)
    print(f"Total de chamadas a serem feitas: {total_requests}")
    print("Processamento paralelo otimizado iniciado...")
    print("Pressione Ctrl+C para interromper a qualquer momento\n")
    
    # Criar arquivo de log
    log_file = os.path.join(error_dir, "execution_log.txt")
    start_time = time.strftime("%Y-%m-%d %H:%M:%S")
    
    with open(log_file, 'a', encoding='utf-8') as log:
        log.write(f"\n{'='*50}\n")
        log.write(f"Início da execução PROJECT INFO: {start_time}\n")
        log.write(f"Total de requisições: {total_requests}\n")
        log.write(f"Threads simultâneas: 15\n")
    
    # Configuração do processamento paralelo
    max_workers = 15  # Número ótimo de threads
    stats_lock = Lock()
    success_count = 0
    error_count = 0
    
    try:
        # Criar múltiplas sessões para melhor performance
        sessions = [create_session() for _ in range(max_workers)]
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submeter todas as tarefas
            futures = []
            for i, (request_type, guid, url_code, url_title) in enumerate(all_requests):
                session = sessions[i % max_workers]  # Round-robin de sessões
                
                if request_type == "project_info":
                    future = executor.submit(
                        process_project_info, 
                        guid, session, stats_lock, log_file
                    )
                else:
                    future = executor.submit(
                        process_question, 
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
                
                # Progresso a cada 100 requisições
                if completed % 100 == 0:
                    progress = (completed / total_requests) * 100
                    print(f"\n📊 Progresso: {completed}/{total_requests} ({progress:.1f}%) - ✅{success_count} ❌{error_count}")
                
                # Pausa mínima entre batches
                if completed % 50 == 0:
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
        print("RESUMO DA EXECUÇÃO PROJECT INFO")
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
        print(f"Respostas salvas em: {os.path.abspath('project_info_responses')}")

if __name__ == "__main__":
    main()
