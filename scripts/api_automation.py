import csv
import requests
import os
import json
import time
from urllib.parse import quote
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def read_guids(file_path):
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        # Pular o cabeçalho se existir
        next(reader, None)
        return [row[0].strip() for row in reader if row and row[0].strip()]

def create_session():
    """Cria uma sessão com configurações de retry e headers."""
    session = requests.Session()
    
    # Configuração de retry mais tolerante
    retry_strategy = Retry(
        total=2,  # Reduzindo o número de tentativas para evitar espera longa
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
        'Sec-Fetch-Site': 'same-site',
    })
    
    return session

def make_api_call(guid, question_number, session=None):
    base_url = "https://api.sif-source.org"
    endpoint = f"/projects/{guid}/questions/search/{question_number}"
    
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
        print(f"\nFazendo requisição para: {url}")
        print(f"Headers: {dict(use_session.headers)}")
        
        start_time = time.time()
        response = use_session.get(
            url,
            auth=auth,
            timeout=30,  # 30 segundos de timeout
            verify=True  # Verificar certificado SSL
        )
        
        # Log da resposta
        duration = time.time() - start_time
        print(f"Resposta em {duration:.2f}s - Status: {response.status_code}")
        
        # Debug: Mostrar headers da resposta
        print(f"Headers da resposta: {dict(response.headers)}")
        
        # Se a resposta for bem-sucedida, retorna o JSON
        if response.status_code == 200:
            try:
                json_data = response.json()
                print(f"Resposta JSON recebida com sucesso (tamanho: {len(str(json_data))} caracteres)")
                return json_data
            except json.JSONDecodeError as e:
                print(f"Erro ao decodificar JSON: {e}")
                print(f"Conteúdo da resposta: {response.text[:500]}...")
                return None
            
        # Se houver erro, salva a resposta para depuração
        error_data = {
            'status_code': response.status_code,
            'reason': response.reason,
            'url': response.url,
            'request_headers': dict(use_session.headers),
            'response_headers': dict(response.headers),
            'text': response.text[:2000]  # Aumentado para 2000 caracteres
        }
        
        print(f"\n=== ERRO NA REQUISIÇÃO ===")
        print(f"URL: {response.url}")
        print(f"Status: {response.status_code} - {response.reason}")
        print(f"Headers da Resposta: {dict(response.headers)}")
        print(f"Início da Resposta: {response.text[:500]}...")
        
        # Salva o erro em um arquivo para análise
        error_dir = "error_logs"
        if not os.path.exists(error_dir):
            os.makedirs(error_dir)
            
        error_file = os.path.join(error_dir, f"error_{guid}_{question_number}.json")
        with open(error_file, 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=2)
            
        return None
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Erro ao acessar a API para GUID {guid} e questão {question_number}: {str(e)}"
        print(error_msg)
        
        # Log detalhado do erro
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status code: {e.response.status_code}")
            print(f"Resposta: {e.response.text[:500]}...")
            
        return None
    except Exception as e:
        print(f"Erro inesperado: {str(e)}")
        return None

def save_response(guid, question_number, data, output_dir="responses"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Criar um nome de arquivo seguro a partir do GUID e da questão
    safe_guid = guid.replace('-', '_')
    safe_question = question_number
    filename = f"{output_dir}/response_{safe_guid}_{safe_question}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    # Caminhos dos arquivos
    projects_file = "projects.csv"
    questions_file = "chamadas.csv"
    
    # Criar diretório de logs de erro
    error_dir = "error_logs"
    if not os.path.exists(error_dir):
        os.makedirs(error_dir)
    
    # Criar sessão HTTP compartilhada
    session = create_session()
    
    # Contadores para estatísticas
    success_count = 0
    error_count = 0
    
    # Ler os GUIDs dos projetos
    try:
        guids = read_guids(projects_file)
        print(f"Encontrados {len(guids)} GUIDs no arquivo {projects_file}")
    except Exception as e:
        print(f"Erro ao ler o arquivo {projects_file}: {e}")
        return

    # Verificar se o arquivo de questões existe e tem conteúdo
    if not os.path.exists(questions_file) or os.path.getsize(questions_file) == 0:
        print(f"ATENÇÃO: O arquivo {questions_file} está vazio ou não existe.")
        print("Por favor, adicione as questões que deseja consultar, uma por linha.")
        return

    # Ler as questões
    try:
        with open(questions_file, 'r') as file:
            # Pular o cabeçalho (primeira linha) e pegar apenas linhas que contêm números
            questions = [line.strip() for line in file.readlines()[1:] if line.strip().isdigit()]
        print(f"Encontradas {len(questions)} questões no arquivo {questions_file}")
        if not questions:
            print("Nenhuma questão numérica encontrada no arquivo.")
            return
    except Exception as e:
        print(f"Erro ao ler o arquivo {questions_file}: {e}")
        return

    # Fazer as chamadas à API para cada combinação de GUID e questão
    total_requests = len(guids) * len(questions)
    print(f"Total de chamadas a serem feitas: {total_requests}")
    print("Pressione Ctrl+C para interromper a qualquer momento\n")
    
    # Criar arquivo de log
    log_file = os.path.join(error_dir, "execution_log.txt")
    start_time = time.strftime("%Y-%m-%d %H:%M:%S")
    
    with open(log_file, 'a', encoding='utf-8') as log:
        log.write(f"\n{'='*50}\n")
        log.write(f"Início da execução: {start_time}\n")
        log.write(f"Total de requisições: {total_requests}\n")
    
    try:
        for i, guid in enumerate(guids, 1):
            for j, question in enumerate(questions, 1):
                print(f"\n[{'='*50}]")
                print(f"Processando GUID {i}/{len(guids)}, Questão {j}/{len(questions)}")
                print(f"GUID: {guid}")
                print(f"Questão: {question}")
                
                # Fazer a chamada à API
                response_data = make_api_call(guid, question, session)
                
                # Registrar no log
                log_entry = f"{time.strftime('%Y-%m-%d %H:%M:%S')} - GUID: {guid}, Questão: {question}"
                
                if response_data is not None:
                    save_response(guid, question, response_data)
                    print(f"✅ Resposta salva com sucesso")
                    log_entry += " - SUCESSO\n"
                    success_count += 1
                else:
                    print(f"❌ Falha ao obter resposta")
                    log_entry += " - FALHA\n"
                    error_count += 1
                
                # Escrever no log
                with open(log_file, 'a', encoding='utf-8') as log:
                    log.write(log_entry)
                
                # Pequena pausa para evitar sobrecarga
                time.sleep(0.5)
                
    except KeyboardInterrupt:
        print("\n\nExecução interrompida pelo usuário.")
    except Exception as e:
        print(f"\nErro inesperado: {str(e)}")
    finally:
        # Fechar a sessão
        session.close()
        
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
        
        # Atualizar o log com as estatísticas finais
        with open(log_file, 'a', encoding='utf-8') as log:
            log.write("\n" + "="*50 + "\n")
            log.write(f"Término da execução: {end_time}\n")
            log.write(f"Total de requisições: {total_requests}\n")
            log.write(f"Requisições processadas: {total_processed}\n")
            log.write(f"Sucessos: {success_count}\n")
            log.write(f"Falhas: {error_count}\n")
            
        print(f"\nLog detalhado salvo em: {os.path.abspath(log_file)}")

if __name__ == "__main__":
    main()