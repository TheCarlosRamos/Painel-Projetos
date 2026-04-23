import json
import os
import html
from datetime import datetime

def decode_html_entities(text):
    """Decodifica entidades HTML para caracteres normais."""
    if text is None:
        return None
    if not isinstance(text, str):
        return text
    return html.unescape(text)

def extract_field_value(field_data):
    """Extrai o valor de um campo da API formatado."""
    if not field_data:
        return None
    
    # Se for string simples
    if isinstance(field_data, str):
        return decode_html_entities(field_data)
    
    # Se for dicionário com FieldValue
    if isinstance(field_data, dict):
        if 'FieldValue' in field_data:
            field_value = field_data['FieldValue']
            if field_value is None:
                return None
            
            # Se FieldValue for um dicionário com Value
            if isinstance(field_value, dict) and 'Value' in field_value:
                return decode_html_entities(field_value['Value'])
            
            # Se FieldValue for string ou outro tipo
            return decode_html_entities(field_value)
        
        # Se for dicionário com Value direto
        if 'Value' in field_data:
            return decode_html_entities(field_data['Value'])
        
        # Se for dicionário com Answer
        if 'Answer' in field_data:
            return decode_html_entities(field_data['Answer'])
    
    return decode_html_entities(field_data)

def load_consolidated_data():
    """Carrega os dados consolidados do projetos_completos_atualizado.json."""
    try:
        with open('projetos_completos_atualizado.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('projetos', [])
    except Exception as e:
        print(f"Erro ao carregar dados consolidados: {e}")
        return []

def format_project_for_app(project_data):
    """Formata um projeto para o formato esperado pela aplicação."""
    formatted_project = {}
    
    # Mapeamento dos campos
    field_mapping = {
        'guid': 'guid',
        'nome_projeto': 'nome_projeto',
        'subsecretaria': 'subsecretaria',
        'status_atual_do_projeto': 'status_atual_do_projeto',
        'questoes_chaves': 'questoes_chaves',
        'proximas_etapas': 'proximas_etapas',
        'status_dos_estudos': 'status_dos_estudos',
        'status_consulta_publica': 'status_consulta_publica',
        'status_do_tcu': 'status_do_tcu',
        'status_do_edital': 'status_do_edital',
        'status_do_leilao': 'status_do_leilao',
        'status_do_contrato': 'status_do_contrato',
        'descricao_do_projeto': 'descricao_do_projeto',
        'nome_completo': 'nome_completo',
        'descricao_curta': 'descricao_curta',
        'setor': 'setor',
        'subsetor': 'subsetor',
        'organizacao': 'organizacao',
        'localizacoes': 'localizacoes',
        'latitude': 'latitude',
        'longitude': 'longitude',
        'endereco_principal': 'endereco_principal',
        'custo_estimado': 'custo_estimado',
        'moeda': 'moeda',
        'custo_original': 'custo_original',
        'status_atividade': 'status_atividade',
        'eh_ppp': 'eh_ppp',
        'tipo_projeto': 'tipo_projeto',
        'arranjo_contratual': 'arranjo_contratual',
        'processo_licitacao': 'processo_licitacao',
        'outro_arranjo_contratual': 'outro_arranjo_contratual',
        'outro_processo_licitacao': 'outro_processo_licitacao'
    }
    
    # Extrair valores para cada campo
    for app_field, source_field in field_mapping.items():
        if source_field in project_data:
            formatted_project[app_field] = extract_field_value(project_data[source_field])
        else:
            formatted_project[app_field] = None
    
    # Garantir que o nome_projeto tenha um formato consistente
    if formatted_project.get('guid') and not formatted_project.get('nome_projeto'):
        formatted_project['nome_projeto'] = f"Projeto {formatted_project['guid'][:8]}"
    
    return formatted_project

def main():
    """Função principal."""
    print("Atualizando projects_full.json com dados consolidados...")
    
    # Carregar dados consolidados
    consolidated_projects = load_consolidated_data()
    
    if not consolidated_projects:
        print("❌ Nenhum dado consolidado encontrado!")
        return
    
    print(f"📊 Processando {len(consolidated_projects)} projetos...")
    
    # Formatar projetos para a aplicação
    formatted_projects = []
    for i, project in enumerate(consolidated_projects):
        formatted_project = format_project_for_app(project)
        formatted_projects.append(formatted_project)
        
        if (i + 1) % 50 == 0:
            print(f"  Processados {i + 1}/{len(consolidated_projects)} projetos...")
    
    # Ordenar por GUID
    formatted_projects.sort(key=lambda x: x.get('guid', ''))
    
    # Salvar arquivo projects_full.json
    output_path = "../page/ppi_landing_site_v2/data/projects_full.json"
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(formatted_projects, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Arquivo projects_full.json atualizado com sucesso!")
        print(f"📊 Total de projetos: {len(formatted_projects)}")
        print(f"📅 Data de atualização: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 Caminho: {os.path.abspath(output_path)}")
        
        # Estatísticas
        valid_projects = sum(1 for p in formatted_projects if p.get('guid'))
        print(f"📈 Projetos válidos: {valid_projects}/{len(formatted_projects)}")
        
    except Exception as e:
        print(f"❌ Erro ao salvar arquivo: {e}")

if __name__ == "__main__":
    main()
