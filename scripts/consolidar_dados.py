import csv
import json
import os
import glob
from collections import defaultdict

def load_json_file(filepath):
    """Carrega um arquivo JSON e retorna o conteúdo."""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Erro ao carregar arquivo {filepath}: {e}")
        return None

def extract_field_value(data, url_code):
    """Extrai o valor do campo baseado no código da URL."""
    
    if not data:
        return None
    
    if 'FieldValue' not in data:
        return None
    
    field_value = data['FieldValue']
    
    if field_value is None:
        return None
    
    # 2000720 -> subsecretaria (SIPE, SIEC, SISU)
    if url_code == '2000720':
        if isinstance(field_value, dict) and 'Value' in field_value and 'Value' in field_value['Value']:
            return field_value['Value']['Value']
    
    # 2000726 -> status atual do projeto (texto do FieldValue.Value)
    elif url_code == '2000726':
        if isinstance(field_value, dict) and 'Value' in field_value:
            return field_value['Value']
    
    # 2000727 -> questões chaves (texto do FieldValue)
    elif url_code == '2000727':
        if isinstance(field_value, dict) and 'Value' in field_value:
            return field_value['Value']
    
    # 2000728 -> proximas etapas do projeto (texto do FieldValue)
    elif url_code == '2000728':
        if isinstance(field_value, dict) and 'Value' in field_value:
            return field_value['Value']
    
    # 2001218 -> status dos estudos (Not started, In progress, Completed)
    elif url_code == '2001218':
        if isinstance(field_value, dict) and 'Value' in field_value and 'Value' in field_value['Value']:
            return field_value['Value']['Value'].replace('\r', '')
    
    # 2001221 -> status consulta publica (Not started, In progress, Completed)
    elif url_code == '2001221':
        if isinstance(field_value, dict) and 'Value' in field_value and 'Value' in field_value['Value']:
            return field_value['Value']['Value'].replace('\r', '')
    
    # 2001224 -> status do TCU (Not started, In progress, Completed, Not applicable)
    elif url_code == '2001224':
        if isinstance(field_value, dict) and 'Value' in field_value and 'Value' in field_value['Value']:
            return field_value['Value']['Value'].replace('\r', '')
    
    # 2001226 -> status do edital (Not started, Completed)
    elif url_code == '2001226':
        if isinstance(field_value, dict) and 'Value' in field_value and 'Value' in field_value['Value']:
            return field_value['Value']['Value'].replace('\r', '')
    
    # 2001229 -> status do leilão (Not started, In progress, Completed)
    elif url_code == '2001229':
        if isinstance(field_value, dict) and 'Value' in field_value and 'Value' in field_value['Value']:
            return field_value['Value']['Value'].replace('\r', '')
    
    # 2001230 -> status do contrato (mesma lógica dos outros status)
    elif url_code == '2001230':
        if isinstance(field_value, dict) and 'Value' in field_value and 'Value' in field_value['Value']:
            return field_value['Value']['Value'].replace('\r', '')
        else:
            print(f"  Debug: 2001230 structure unexpected: {type(field_value)}")
    
    # 2001232 -> descrição do projeto (texto do FieldValue)
    elif url_code == '2001232':
        if isinstance(field_value, dict) and 'Value' in field_value:
            return field_value['Value']
    
    # 2001216 -> 2001216 (texto do FieldValue)
    elif url_code == '2001216':
        if isinstance(field_value, dict) and 'Value' in field_value:
            return field_value['Value']
    
    return None

def get_project_name(guid, responses_dir):
    """Tenta obter o nome do projeto a partir da descrição do projeto."""
    description_file = os.path.join(responses_dir, f'response_{guid}_2001232_descrição_do_projeto.json')
    
    if os.path.exists(description_file):
        data = load_json_file(description_file)
        if data and 'FieldValue' in data and data['FieldValue'] and 'Value' in data['FieldValue']:
            description = data['FieldValue']['Value']
            # Extrair as primeiras palavras como nome do projeto
            if description:
                # Pegar as primeiras 50 caracteres ou primeira frase
                if len(description) > 50:
                    first_sentence = description.split('.')[0]
                    if len(first_sentence) > 50:
                        return first_sentence[:47] + '...'
                    return first_sentence
                return description[:50]
    
    return f"Projeto {guid[:8]}"

def consolidate_data():
    """Consolida todos os dados dos arquivos JSON em um CSV."""
    
    # Mapeamento das URLs para títulos das colunas
    url_mapping = {
        '2000720': 'subsecretaria',
        '2000726': 'status_atual_do_projeto',
        '2000727': 'questoes_chaves',
        '2000728': 'proximas_etapas',
        '2001216': '2001216',
        '2001218': 'status_dos_estudos',
        '2001221': 'status_consulta_publica',
        '2001224': 'status_do_tcu',
        '2001226': 'status_do_edital',
        '2001229': 'status_do_leilao',
        '2001230': 'status_do_contrato',
        '2001232': 'descricao_do_projeto'
    }
    
    # Diretório base
    base_dir = os.path.dirname(os.path.abspath(__file__))
    responses_base_dir = base_dir  # Os diretórios responses_* estão diretamente em scripts/
    
    # Coletar todos os GUIDs
    all_guids = set()
    
    # Para cada diretório de respostas
    for url_code in url_mapping.keys():
        response_dir = os.path.join(responses_base_dir, f'responses_{url_code}')
        
        if os.path.exists(response_dir):
            json_files = glob.glob(os.path.join(response_dir, f'response_*_{url_code}_*.json'))
            for file in json_files:
                # Extrair GUID do nome do arquivo
                filename = os.path.basename(file)
                # Formato: response_XXXX_XXXX_XXXX_XXXX_XXXX_XXXX_XXXX_XXXX_XXXX_XXXX_XXXX_2000720_title.json
                parts = filename.split('_')
                if len(parts) >= 10:  # GUID tem 5 partes separadas por _
                    # Reconstruir o GUID completo
                    guid_parts = parts[1:6]  # Pega as 5 primeiras partes após "response_"
                    guid = '-'.join(guid_parts)
                    all_guids.add(guid)
    
    print(f"Total de GUIDs encontrados: {len(all_guids)}")
    
    # Preparar dados para o CSV
    consolidated_data = []
    
    for guid in sorted(all_guids):
        project_name = get_project_name(guid, responses_base_dir)
        
        row = {
            'guid': guid,
            'nome_projeto': project_name
        }
        
        # Para cada URL, extrair o valor correspondente
        for url_code, column_name in url_mapping.items():
            # Converter GUID para o formato usado nos nomes dos arquivos (com underscores)
            guid_underscored = guid.replace('-', '_')
            
            # Construir o nome do arquivo baseado no padrão real
            # response_{guid}_{url_code}_{title}.json
            response_pattern = os.path.join(responses_base_dir, f'responses_{url_code}', f'response_{guid_underscored}_{url_code}_*.json')
            
            # Procurar o arquivo correspondente
            matching_files = glob.glob(response_pattern)
            if matching_files:
                data = load_json_file(matching_files[0])
                value = extract_field_value(data, url_code)
                row[column_name] = value if value is not None else ''
            else:
                row[column_name] = ''
        
        consolidated_data.append(row)
    
    # Salvar CSV
    output_file = os.path.join(base_dir, '..', 'projetos_consolidado.csv')
    
    # Definir ordem das colunas
    fieldnames = ['guid', 'nome_projeto'] + list(url_mapping.values())
    
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(consolidated_data)
    
    print(f"Arquivo CSV consolidado salvo em: {output_file}")
    print(f"Total de projetos: {len(consolidated_data)}")
    
    # Estatísticas
    print("\nEstatísticas por campo:")
    for column_name in url_mapping.values():
        filled_count = sum(1 for row in consolidated_data if row.get(column_name))
        percentage = (filled_count / len(consolidated_data)) * 100 if consolidated_data else 0
        print(f"  {column_name}: {filled_count}/{len(consolidated_data)} ({percentage:.1f}%)")

if __name__ == "__main__":
    consolidate_data()
