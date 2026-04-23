import json
import os
import glob
from datetime import datetime
import html

def read_json_file(file_path):
    """Lê um arquivo JSON e retorna o conteúdo."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao ler arquivo {file_path}: {e}")
        return None

def decode_html_entities(text):
    """Decodifica entidades HTML para caracteres normais."""
    if text is None:
        return None
    return html.unescape(text)

def extract_value_from_response(response_data, field_name=None):
    """Extrai o valor de uma resposta da API."""
    if not response_data:
        return None
    
    # Se for uma lista, pega o primeiro item
    if isinstance(response_data, list):
        if len(response_data) > 0:
            response_data = response_data[0]
        else:
            return None
    
    # Se for um dicionário
    if isinstance(response_data, dict):
        # Caso 1: FieldValue.Value.Value (estrutura comum da API)
        if 'FieldValue' in response_data:
            field_value = response_data['FieldValue']
            if isinstance(field_value, dict):
                if 'Value' in field_value:
                    value = field_value['Value']
                    if isinstance(value, dict) and 'Value' in value:
                        return decode_html_entities(value['Value'])
                    else:
                        return decode_html_entities(value)
                else:
                    return decode_html_entities(field_value)
        
        # Caso 2: Value direto
        if 'Value' in response_data:
            return decode_html_entities(response_data['Value'])
        
        # Caso 3: Answer
        elif 'Answer' in response_data:
            return decode_html_entities(response_data['Answer'])
        
        # Caso 4: campo específico
        elif field_name and field_name in response_data:
            return decode_html_entities(response_data[field_name])
    
    return decode_html_entities(response_data)

def get_project_info(project_info_file):
    """Extrai informações básicas do projeto do arquivo project_info."""
    if not project_info_file:
        return {}
    
    info = {}
    
    # Campos básicos
    info['guid'] = project_info_file.get('Guid', '')
    info['nome_projeto'] = f"Projeto {info['guid'][:8]}" if info['guid'] else ''
    info['nome_completo'] = decode_html_entities(project_info_file.get('Name', ''))
    info['descricao_curta'] = decode_html_entities(project_info_file.get('Description', ''))
    
    # Setor e subsetor
    sector = project_info_file.get('Sector', {})
    info['setor'] = sector.get('Value', '') if isinstance(sector, dict) else ''
    
    subsector = project_info_file.get('SubSector', {})
    info['subsetor'] = subsector.get('Value', '') if isinstance(subsector, dict) else ''
    
    # Organização
    orgs = project_info_file.get('ProjectOrganizations', [])
    if orgs and len(orgs) > 0:
        info['organizacao'] = orgs[0].get('Value', '') if isinstance(orgs[0], dict) else ''
    else:
        info['organizacao'] = ''
    
    # Status da atividade
    activity_status = project_info_file.get('ProjectActivityStatus', {})
    info['status_atividade'] = activity_status.get('Title', '') if isinstance(activity_status, dict) else ''
    
    # Informações de localização
    territories = project_info_file.get('Territories', [])
    info['localizacoes'] = ', '.join([t.get('Value', '') if isinstance(t, dict) else str(t) for t in territories])
    
    # Coordenadas - usar GPSCoordinates
    gps_coords = project_info_file.get('GPSCoordinates', [])
    if gps_coords and len(gps_coords) > 0:
        coord = gps_coords[0]
        if isinstance(coord, dict):
            location = coord.get('location', {})
            if isinstance(location, dict):
                # Nota: na API, x é longitude e y é latitude
                info['longitude'] = float(location.get('x', None)) if location.get('x') else None
                info['latitude'] = float(location.get('y', None)) if location.get('y') else None
            info['endereco_principal'] = coord.get('address', '')
        else:
            info['latitude'] = None
            info['longitude'] = None
            info['endereco_principal'] = ''
    else:
        info['latitude'] = None
        info['longitude'] = None
        info['endereco_principal'] = ''
    
    # Custo
    cost_info = project_info_file.get('ProjectCostInformation', {})
    if isinstance(cost_info, dict):
        info['custo_estimado'] = cost_info.get('EstimatedCost', None)
        info['moeda'] = cost_info.get('Currency', '')
        info['custo_original'] = cost_info.get('OriginalCost', None)
    else:
        info['custo_estimado'] = None
        info['moeda'] = ''
        info['custo_original'] = None
    
    # Campos adicionais (valores padrão)
    info['eh_ppp'] = None
    info['tipo_projeto'] = None
    info['arranjo_contratual'] = None
    info['processo_licitacao'] = None
    info['outro_arranjo_contratual'] = None
    info['outro_processo_licitacao'] = None
    
    return info

def load_all_project_data():
    """Carrega todos os dados dos projetos dos arquivos JSON."""
    responses_dir = "project_info_responses"
    
    # Mapeamento de URLs para campos
    url_mapping = {
        "2000720": "subsecretaria",
        "2000726": "status_atual_do_projeto", 
        "2000727": "questoes_chaves",
        "2000728": "proximas_etapas",
        "2001218": "status_dos_estudos",
        "2001221": "status_consulta_publica",
        "2001224": "status_do_tcu",
        "2001226": "status_do_edital",
        "2001229": "status_do_leilao",
        "2001230": "status_do_contrato",
        "2001232": "descricao_do_projeto"
    }
    
    # Encontrar todos os arquivos de respostas
    response_files = glob.glob(os.path.join(responses_dir, "response_*.json"))
    project_info_files = glob.glob(os.path.join(responses_dir, "project_info_*.json"))
    
    print(f"Encontrados {len(response_files)} arquivos de resposta e {len(project_info_files)} arquivos de info")
    
    # Agrupar dados por GUID
    projects_data = {}
    
    # Carregar informações básicas dos projetos
    for info_file in project_info_files:
        data = read_json_file(info_file)
        if data and data.get('Guid'):
            guid = data['Guid']
            projects_data[guid] = get_project_info(data)
    
    # Carregar respostas das perguntas
    for response_file in response_files:
        data = read_json_file(response_file)
        if not data:
            continue
            
        # Extrair GUID e URL do nome do arquivo
        filename = os.path.basename(response_file)
        parts = filename.replace('.json', '').split('_')
        
        if len(parts) >= 3:
            guid = parts[1] + '-' + parts[2] + '-' + parts[3] + '-' + parts[4] + '-' + parts[5]
            url_code = parts[6]
            
            # Se o projeto não existe nos dados, criar entrada básica
            if guid not in projects_data:
                projects_data[guid] = {
                    'guid': guid,
                    'nome_projeto': f"Projeto {guid[:8]}",
                    'nome_completo': '',
                    'descricao_curta': '',
                    'setor': '',
                    'subsetor': '',
                    'organizacao': '',
                    'localizacoes': '',
                    'latitude': None,
                    'longitude': None,
                    'endereco_principal': '',
                    'custo_estimado': None,
                    'moeda': '',
                    'custo_original': None,
                    'status_atividade': '',
                    'eh_ppp': None,
                    'tipo_projeto': None,
                    'arranjo_contratual': None,
                    'processo_licitacao': None,
                    'outro_arranjo_contratual': None,
                    'outro_processo_licitacao': None
                }
            
            # Mapear URL para campo correspondente
            field_name = url_mapping.get(url_code)
            if field_name:
                projects_data[guid][field_name] = extract_value_from_response(data)
    
    return projects_data

def create_consolidated_json(projects_data):
    """Cria o JSON consolidado no formato do projetos_completos.json."""
    
    # Definir colunas na ordem correta
    columns = [
        "guid",
        "nome_projeto", 
        "subsecretaria",
        "status_atual_do_projeto",
        "questoes_chaves",
        "proximas_etapas",
        "2001216",
        "status_dos_estudos",
        "status_consulta_publica",
        "status_do_tcu",
        "status_do_edital",
        "status_do_leilao",
        "status_do_contrato",
        "descricao_do_projeto",
        "nome_completo",
        "descricao_curta",
        "setor",
        "subsetor",
        "organizacao",
        "localizacoes",
        "latitude",
        "longitude",
        "endereco_principal",
        "custo_estimado",
        "moeda",
        "custo_original",
        "status_atividade",
        "eh_ppp",
        "tipo_projeto",
        "arranjo_contratual",
        "processo_licitacao",
        "outro_arranjo_contratual",
        "outro_processo_licitacao"
    ]
    
    # Converter dados para lista de projetos
    projects_list = []
    for guid, project_data in projects_data.items():
        # Garantir que todos os campos existam
        project = {}
        for col in columns:
            project[col] = project_data.get(col, None)
        projects_list.append(project)
    
    # Ordenar por GUID
    projects_list.sort(key=lambda x: x.get('guid', ''))
    
    # Criar estrutura final
    consolidated_data = {
        "metadados": {
            "total_projetos": len(projects_list),
            "total_colunas": len(columns),
            "data_geracao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "colunas": columns
        },
        "projetos": projects_list
    }
    
    return consolidated_data

def main():
    """Função principal."""
    print("Iniciando consolidação dos dados dos projetos...")
    
    # Carregar todos os dados
    projects_data = load_all_project_data()
    
    if not projects_data:
        print("Nenhum dado de projeto encontrado!")
        return
    
    print(f"Processados {len(projects_data)} projetos")
    
    # Criar JSON consolidado
    consolidated_data = create_consolidated_json(projects_data)
    
    # Salvar arquivo
    output_file = "projetos_completos_atualizado.json"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(consolidated_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Arquivo consolidado criado com sucesso: {output_file}")
        print(f"📊 Total de projetos: {consolidated_data['metadados']['total_projetos']}")
        print(f"📅 Data de geração: {consolidated_data['metadados']['data_geracao']}")
        print(f"📁 Caminho completo: {os.path.abspath(output_file)}")
        
    except Exception as e:
        print(f"❌ Erro ao salvar arquivo: {e}")

if __name__ == "__main__":
    main()
