import requests
import json
import time
import os
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# URLs para coletar exemplos
URLS_TO_SAMPLE = {
    "2000720": "subsecretaria",
    "2000726": "status_atual_do_projeto", 
    "2000727": "questoes_chaves",
    "2000728": "proximas_etapas_do_projeto",
    "2001218": "status_dos_estudos",
    "2001221": "status_consulta_publica",
    "2001224": "status_do_tcu",
    "2001226": "status_do_edital",
    "2001229": "status_do_leilao",
    "2001230": "status_do_contrato",
    "2001232": "descricao_do_projeto",
    "2000725": "data_de_qualificacao_em_ppi",
    "2000711": "setor_do_projeto_ppi",
    "2000712": "subsetor_do_projeto_ppi",
    "400014": "custo_capital_estimado",
    "400015": "custo_medio_anual_operacao"
}

# GUID de exemplo (primeiro da lista)
SAMPLE_GUID = "4aa4c2df-edd5-437f-8cc5-924341d560b3"

def create_session():
    session = requests.Session()
    
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
    
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'pt-BR,pt;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache',
        'Referer': 'https://www.sif-source.org/',
        'Origin': 'https://www.sif-source.org',
    })
    
    return session

def make_api_call(guid, url_code, session):
    base_url = "https://api.sif-source.org"
    endpoint = f"/projects/{guid}/questions/search/{url_code}"
    
    params = [
        ("SPHostUrl", "https://www.sif-source.org"),
        ("SPLanguage", "pt-BR"),
        ("SPClientTag", "0"),
        ("SPProductNumber", "15.0.5023.1183"),
        ("_t", str(int(time.time() * 1000)))
    ]
    
    query_string = "&".join([f"{k}={requests.utils.quote(str(v))}" for k, v in params])
    url = f"{base_url}{endpoint}?{query_string}"
    
    auth = ('adminppi.source@presidencia.gov.br', 'PPI#source147')
    
    try:
        response = session.get(url, auth=auth, timeout=15, verify=True)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erro {response.status_code} para {url_code}: {response.reason}")
            return None
            
    except Exception as e:
        print(f"Exceção para {url_code}: {str(e)}")
        return None

def main():
    print("Coletando exemplos de JSON para cada tipo de chamada...")
    print(f"GUID de exemplo: {SAMPLE_GUID}")
    
    # Criar diretório de saída
    output_dir = "sample_responses"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    session = create_session()
    
    results = {}
    
    for url_code, description in URLS_TO_SAMPLE.items():
        print(f"\nColetando {url_code} - {description}...")
        
        data = make_api_call(SAMPLE_GUID, url_code, session)
        
        if data:
            # Salvar arquivo
            filename = f"{output_dir}/sample_{url_code}_{description.replace(' ', '_')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            results[url_code] = {
                "description": description,
                "success": True,
                "data_type": type(data).__name__,
                "data_size": len(str(data)),
                "keys": list(data.keys()) if isinstance(data, dict) else "N/A"
            }
            print(f"  Salvo: {filename}")
        else:
            results[url_code] = {
                "description": description,
                "success": False,
                "error": "API call failed"
            }
            print(f"  Falha na chamada API")
        
        time.sleep(0.5)  # Pausa entre chamadas
    
    session.close()
    
    # Salvar resumo
    summary_file = f"{output_dir}/collection_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\nResumo salvo em: {summary_file}")
    print(f"Total de chamadas: {len(URLS_TO_SAMPLE)}")
    print(f"Sucessos: {sum(1 for r in results.values() if r.get('success'))}")

if __name__ == "__main__":
    main()
