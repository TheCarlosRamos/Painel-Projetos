import requests
import json
import time
import uuid
import ssl
from datetime import datetime
from collections import Counter
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://api.sif-source.org"
AUTH = ("adminppi.source@presidencia.gov.br", "PPI#source147")
TIMEOUT = 20
SERIAL_TESTS = 8

def create_session():
    session = requests.Session()

    adapter = HTTPAdapter(
        max_retries=Retry(total=0),
        pool_connections=5,
        pool_maxsize=5
    )
    session.mount("https://", adapter)

    session.headers.update({
        "User-Agent": "API-Forensic-Probe/2.0",
        "Accept": "*/*",
        "Connection": "close"  # força nova conexão
    })

    return session

def forensic_call(session, guid, question, tag):
    start = time.time()
    result = {
        "id": str(uuid.uuid4()),
        "tag": tag,
        "timestamp": datetime.utcnow().isoformat(),
        "guid": guid,
        "question": question,
        "elapsed_sec": None,
        "status": "no_response",
        "status_code": None,
        "headers": {},
        "error": None,
    }

    try:
        response = session.get(
            f"{BASE_URL}/projects/{guid}/questions/search/{question}",
            params={
                "SPHostUrl": "https://www.sif-source.org",
                "SPLanguage": "pt-BR",
                "SPClientTag": "0",
                "SPProductNumber": "15.0.5023.1183"
            },
            auth=AUTH,
            timeout=TIMEOUT,
        )

        result["elapsed_sec"] = round(time.time() - start, 3)

        if response is not None:
            result["status"] = "http_response"
            result["status_code"] = response.status_code
            result["headers"] = dict(response.headers)

    except requests.exceptions.SSLError as e:
        result["status"] = "ssl_error"
        result["error"] = str(e)

    except requests.exceptions.ConnectionError as e:
        result["status"] = "connection_aborted"
        result["error"] = str(e)

    except Exception as e:
        result["status"] = "unknown_exception"
        result["error"] = str(e)

    return result

def run_forensic_tests():
    session = create_session()
    results = []

    base_guid = "e87345f1-cd99-4071-a2e9-74ad1eb36787"
    base_question = "2000720"

    for i in range(SERIAL_TESTS):
        results.append(
            forensic_call(session, base_guid, base_question, f"probe_{i+1}")
        )
        time.sleep(1)

    return results

def analyze(results):
    statuses = Counter(r["status"] for r in results)
    status_codes = Counter(r["status_code"] for r in results if r["status_code"])
    servers = Counter(
        r["headers"].get("Server", "None") 
        for r in results if r["headers"]
    )

    root_cause = "Indeterminado"

    if "connection_aborted" in statuses:
        root_cause = "Conexão encerrada pela infraestrutura (proxy / LB / firewall)"

    elif statuses == {"http_response"} and status_codes == {503}:
        root_cause = "Serviço indisponível (application pool / backend)"

    return {
        "statuses": dict(statuses),
        "status_codes": dict(status_codes),
        "servers": dict(servers),
        "root_cause": root_cause
    }

def main():
    results = run_forensic_tests()
    analysis = analyze(results)

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    with open(f"api_forensic_{ts}.json", "w", encoding="utf-8") as f:
        json.dump(
            {"analysis": analysis, "results": results},
            f, indent=2, ensure_ascii=False
        )

    print("\n✅ LAUDO FORENSE CONCLUÍDO")
    print(json.dumps(analysis, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()