import requests
import json
import time

def test_api():
    """Testa a API com uma única requisição."""
    url = "https://api.sif-source.org/projects/8587a771-a713-4b0d-bdaa-594649c26413/questions/search/2000720"
    params = {
        "SPHostUrl": "https://www.sif-source.org",
        "SPLanguage": "pt-BR",
        "SPClientTag": "0",
        "SPProductNumber": "15.0.5023.1183"
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Referer': 'https://www.sif-source.org/',
        'Origin': 'https://www.sif-source.org'
    }
    
    auth = ('adminppi.source@presidencia.gov.br', 'PPI#source147')
    
    try:
        print("🔍 Testando API...")
        print(f"URL: {url}")
        print(f"Auth: {auth[0]}")
        
        start_time = time.time()
        response = requests.get(
            url,
            params=params,
            headers=headers,
            auth=auth,
            timeout=30,
            verify=True
        )
        
        print(f"⏱️ Tempo: {time.time() - start_time:.2f}s")
        print(f"📊 Status: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Sucesso! Dados: {json.dumps(data, indent=2)[:200]}...")
            except:
                print("❌ Erro ao decodificar JSON")
        else:
            print(f"❌ Erro: {response.status_code} - {response.reason}")
            print(f"📄 Resposta: {response.text[:500]}...")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    test_api()
