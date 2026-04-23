import json
import os
import pandas as pd
from collections import defaultdict
import re

def extract_guid_from_filename(filename):
    """Extrai GUID do nome do arquivo JSON."""
    parts = filename.replace('.json', '').split('_')
    if len(parts) >= 6:
        return f"{parts[1]}-{parts[2]}-{parts[3]}-{parts[4]}-{parts[5]}"
    return None

def extract_url_code_from_filename(filename):
    """Extrai URL code do nome do arquivo JSON."""
    parts = filename.replace('.json', '').split('_')
    for part in parts:
        if part.isdigit() and len(part) >= 6:
            return part
    return None

def get_field_value(data):
    """Extrai valor do campo FieldValue de forma segura."""
    if 'FieldValue' not in data or data['FieldValue'] is None:
        return ''
    
    field_value = data['FieldValue']
    field_type = field_value.get('Type', 'Unknown')
    
    if field_type == 'ChoiceSingle':
        return field_value.get('Value', {}).get('Value', '')
    elif field_type == 'Numerical':
        return field_value.get('Value', '')
    elif field_type == 'Text':
        return field_value.get('Value', '')
    elif field_type == 'TextMulti':
        return field_value.get('Value', '')
    elif field_type == 'Date':
        return field_value.get('Value', '')
    elif field_type == 'ChoiceMulti':
        values = field_value.get('Value', {})
        if isinstance(values, dict):
            return ', '.join([v for v in values.values() if v])
        return str(values)
    else:
        return str(field_value)

def load_project_info():
    """Carrega informações dos projetos do arquivo project_info se disponível."""
    project_info = {}
    
    # Tentar carregar do responses_project_info
    project_info_dir = "responses_project_info"
    if os.path.exists(project_info_dir):
        for filename in os.listdir(project_info_dir):
            if filename.endswith('.json'):
                guid = extract_guid_from_filename(filename)
                if guid:
                    filepath = os.path.join(project_info_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # Extrair informações do projeto
                        info = {}
                        
                        # Nome do projeto
                        if 'Name' in data:
                            info['Nome_Projeto'] = data['Name']
                        elif 'projectName' in data:
                            info['Nome_Projeto'] = data['projectName']
                        elif 'name' in data:
                            info['Nome_Projeto'] = data['name']
                        else:
                            info['Nome_Projeto'] = ''
                        
                        # Setor do projeto
                        if 'Sector' in data and data['Sector']:
                            info['Setor do projeto (de acordo com a classificação da PPI)'] = data['Sector'].get('Value', '')
                        else:
                            info['Setor do projeto (de acordo com a classificação da PPI)'] = ''
                        
                        # Subsetor do projeto
                        if 'SubSector' in data and data['SubSector']:
                            info['Subsetor do projeto (de acordo com a classificação da PPI)'] = data['SubSector'].get('Value', '')
                        else:
                            info['Subsetor do projeto (de acordo com a classificação da PPI)'] = ''
                        
                        project_info[guid] = info
                        
                    except Exception as e:
                        print(f"Erro ao carregar info do projeto {filename}: {e}")
                        continue
    
    return project_info

def process_json_files(responses_dir="responses"):
    """Processa todos os arquivos JSON e cria DataFrame consolidado."""
    
    # Mapeamento de URL codes para títulos descritivos
    url_mapping = {
        "2000720": "Qual Subsecretaria da SEPPI é responsável pelo projeto?",
        "2000726": "Status atual do projeto", 
        "2000727": "Questões chaves",
        "2000728": "Próximas etapas do projeto",
        "2001218": "Status dos estudos",
        "2001221": "Status consulta pública",
        "2001224": "Status do TCU",
        "2001226": "Status do edital",
        "2001229": "Status do leilão",
        "2001230": "Status do contrato",
        "2001232": "Descrição do projeto",
        "2000725": "Data de qualificação em PPI",
        "2000711": "Setor do projeto (de acordo com a classificação da PPI)",
        "2000712": "Subsetor do projeto (de acordo com a classificação da PPI)",
        "400014": "Qual é o custo de capital estimado para o projeto?",
        "400015": "Qual é o custo médio anual estimado de operação e manutenção?",
        "100231": "Quem será a Autoridade Contratante?",
        "1105352": "Qual dos seguintes objetivos melhor justificaria o gasto de fundos públicos para o projeto proposto?",
        "1400095": "Qual a duração prevista para o contrato principal (em anos)?",
        "2000713": "Quem irá estruturar o projeto?",
        "2000714": "Qual é o modelo de PPP?",
        "2000715": "Qual é o setor do projeto?",
        "2000716": "Qual é o subsetor do projeto?",
        "2000717": "Qual é o estágio atual do projeto?",
        "2000718": "Qual é a data prevista para o início da operação?",
        "2000719": "Qual é a data prevista para o término da operação?",
        "2000721": "Qual é o valor total do contrato?",
        "2000722": "Qual é o valor total do investimento?",
        "2000723": "Qual é o valor total da contrapartida do governo?",
        "2000724": "Qual é o valor total da contrapartida do parceiro privado?",
        "2000729": "Qual é o modelo de remuneração?",
        "2000730": "Qual é o período de concessão?",
        "2000731": "Qual é o período de construção?",
        "2000732": "Qual é o período de operação?",
        "2000733": "Qual é o período de manutenção?",
        "2000941": "Qual é o valor total da receita?",
        "2000942": "Qual é o valor total do custo?",
        "2000943": "Qual é o valor total do lucro?",
        "2000944": "Qual é o valor total do ROI?",
        "2000945": "Qual é o valor total do payback?",
        "2000946": "Qual é o valor total do NPV?",
        "2000947": "Qual é o valor total do IRR?",
        "2000948": "Qual é o valor total do break even?",
        "2000949": "Qual é o valor total do sensitivity analysis?",
        "2000950": "Qual é o valor total do scenario analysis?",
        "2000951": "Qual é o valor total do risk analysis?",
        "2000952": "Qual é o valor total do monte carlo?",
        "2001215": "Qual é o valor total do valuation?",
        "2001216": "Qual é o valor total do due diligence?",
        "2001217": "Qual é o valor total do legal opinion?",
        "2001219": "Qual é o valor total do financial model?",
        "2001220": "Qual é o valor total do technical study?",
        "2001222": "Data início - Controle Externo",
        "2001223": "Data fim - Controle Externo",
        "2001225": "Data de publicação - Edital",
        "2001227": "Data início - Licitação",
        "2001228": "Data fim - Licitação",
        "2001231": "Data de assinatura do contrato",
        "03175202": "Quem será a Autoridade Contratante?",
        "03476266": "Quem será a Autoridade Contratante?",
        "42887213": "Quem será a Autoridade Contratante?",
        "52665076": "Quem será a Autoridade Contratante?",
        "73401929": "Quem será a Autoridade Contratante?",
        "83410882": "Quem será a Autoridade Contratante?",
        "84527695": "Quem será a Autoridade Contratante?",
        "91086620": "Quem será a Autoridade Contratante?",
        "839133579224": "Quem será a Autoridade Contratante?"
    }
    
    # Dicionário para armazenar dados por GUID
    projects_data = defaultdict(dict)
    
    print("Processando arquivos JSON...")
    
    # Processar cada arquivo JSON
    total_files = 0
    processed_files = 0
    
    for filename in os.listdir(responses_dir):
        if filename.endswith('.json'):
            total_files += 1
            filepath = os.path.join(responses_dir, filename)
            
            try:
                guid = extract_guid_from_filename(filename)
                url_code = extract_url_code_from_filename(filename)
                
                if not guid or not url_code:
                    continue
                
                # Carregar dados do arquivo
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extrair valor do campo
                value = get_field_value(data)
                
                # Adicionar aos dados do projeto
                friendly_name = url_mapping.get(url_code, url_code)
                projects_data[guid][friendly_name] = value
                projects_data[guid]['GUID'] = guid
                
                processed_files += 1
                
            except Exception as e:
                print(f"Erro ao processar {filename}: {e}")
    
    print(f"Arquivos processados: {processed_files}/{total_files}")
    print(f"Projetos únicos: {len(projects_data)}")
    
    # Carregar informações dos projetos
    project_info_data = load_project_info()
    
    # Converter para DataFrame
    df_data = []
    for guid, data in projects_data.items():
        # Adicionar informações do projeto se disponível
        if guid in project_info_data:
            # Mesclar dados das respostas com info do projeto
            data.update(project_info_data[guid])
        else:
            # Adicionar campos vazios se não tiver info
            data['Nome_Projeto'] = ''
            data['Setor do projeto (de acordo com a classificação da PPI)'] = ''
            data['Subsetor do projeto (de acordo com a classificação da PPI)'] = ''
        
        df_data.append(data)
    
    df = pd.DataFrame(df_data)
    
    # Reordenar colunas
    if 'GUID' in df.columns:
        cols = ['GUID'] + [col for col in df.columns if col != 'GUID']
        df = df[cols]
    
    if 'Nome_Projeto' in df.columns:
        cols = ['GUID', 'Nome_Projeto'] + [col for col in df.columns if col not in ['GUID', 'Nome_Projeto']]
        df = df[cols]
    
    return df

def create_excel_files(df):
    """Cria diferentes arquivos Excel com diferentes visões."""
    
    # 1. Arquivo completo
    df.to_excel("projects_complete_data.xlsx", index=False, engine='openpyxl')
    print("Arquivo completo salvo: projects_complete_data.xlsx")
    
    # 2. Arquivo resumido (campos principais)
    main_columns = ['GUID', 'Nome_Projeto', 'Setor do projeto (de acordo com a classificação da PPI)', 
                   'Subsetor do projeto (de acordo com a classificação da PPI)', 
                   'Qual Subsecretaria da SEPPI é responsável pelo projeto?', 'Status atual do projeto', 
                   'Qual é o custo de capital estimado para o projeto?', 
                   'Qual é o custo médio anual estimado de operação e manutenção?', 'Descrição do projeto']
    
    available_main_cols = [col for col in main_columns if col in df.columns]
    df_summary = df[available_main_cols].copy()
    df_summary.to_excel("projects_summary.xlsx", index=False, engine='openpyxl')
    print("Arquivo resumo salvo: projects_summary.xlsx")
    
    # 3. Arquivo por setor (se disponível)
    sector_col = 'Setor do projeto (de acordo com a classificação da PPI)'
    if sector_col in df.columns:
        sectors = df[sector_col].dropna().unique()
        for sector in sectors:
            if sector:  # Pular valores vazios
                df_sector = df[df[sector_col] == sector].copy()
                filename = f"projects_sector_{re.sub(r'[^a-zA-Z0-9]', '_', str(sector))}.xlsx"
                df_sector.to_excel(filename, index=False, engine='openpyxl')
                print(f"Arquivo do setor '{sector}' salvo: {filename}")
    
    # 4. Estatísticas
    stats = {
        'Total de Projetos': len(df),
        'Colunas': len(df.columns),
        'Arquivos por Setor': len(df['Setor do projeto (de acordo com a classificação da PPI)'].unique()) if 'Setor do projeto (de acordo com a classificação da PPI)' in df.columns else 0,
        'Projetos com Nome': df['Nome_Projeto'].notna().sum() if 'Nome_Projeto' in df.columns else 0,
        'Projetos com Custo Capital': df['Qual é o custo de capital estimado para o projeto?'].notna().sum() if 'Qual é o custo de capital estimado para o projeto?' in df.columns else 0,
        'Projetos com Descrição': df['Descrição do projeto'].notna().sum() if 'Descrição do projeto' in df.columns else 0
    }
    
    with open("processing_stats.txt", "w", encoding='utf-8') as f:
        f.write("ESTATÍSTICAS DE PROCESSAMENTO\n")
        f.write("="*40 + "\n")
        for key, value in stats.items():
            f.write(f"{key}: {value}\n")
    
    print("Estatísticas salvas em: processing_stats.txt")
    
    return stats

if __name__ == "__main__":
    print("Iniciando geração do Excel consolidado...")
    
    # Processar arquivos JSON
    df = process_json_files()
    
    print(f"\nShape do DataFrame: {df.shape}")
    print(f"Colunas: {list(df.columns)}")
    
    # Criar arquivos Excel
    stats = create_excel_files(df)
    
    print("\n" + "="*50)
    print("PROCESSAMENTO CONCLUÍDO!")
    print("="*50)
    print("\nArquivos gerados:")
    print("- projects_complete_data.xlsx (todos os dados)")
    print("- projects_summary.xlsx (resumo)")
    print("- projects_sector_*.xlsx (por setor)")
    print("- processing_stats.txt (estatísticas)")
    
    print(f"\nEstatísticas:")
    for key, value in stats.items():
        print(f"- {key}: {value}")
