import pandas as pd
import json
import os
import glob

def load_json_file(filepath):
    """Carrega arquivo JSON."""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Erro ao carregar arquivo {filepath}: {e}")
        return None

def extract_guid_from_filename(filename):
    """Extrai GUID do nome do arquivo JSON."""
    # Padrões possíveis de nome de arquivo:
    # response_44cd4078-42b0-4a83-8955-efa31cdb2130_project_info.json
    # response_44cd4078_42b0_4a83_8955_efa31cdb2130_project_info.json
    
    # Extrair GUID entre "response_" e "_project_info"
    if "response_" in filename and "_project_info" in filename:
        guid_part = filename.replace("response_", "").replace("_project_info.json", "")
        
        # Se tiver underscores, converter para hífens
        if '_' in guid_part and guid_part.count('_') >= 4:  # Formato com underscores
            guid = guid_part.replace('_', '-')
        else:
            guid = guid_part
            
        # Verificar se tem 36 caracteres (GUID válido)
        if len(guid) == 36:
            return guid
    
    return None

def extract_project_info(data):
    """Extrai informações básicas do projeto."""
    if not data:
        return {}
    
    info = {}
    
    # Nome do projeto
    info['nome_completo'] = data.get('Name', '')
    
    # Descrição (limpando HTML)
    description = data.get('Description', '')
    if description:
        # Remover entidades HTML
        description = description.replace('&#231;', 'ç').replace('&#227;', 'ã').replace('&#225;', 'á').replace('&#234;', 'ê').replace('&#243;', 'ó').replace('&#237;', 'í')
        description = description.replace('&#225;', 'á').replace('&#233;', 'é').replace('&#237;', 'í').replace('&#243;', 'ó').replace('&#250;', 'ú')
        description = description.replace('&#226;', 'â').replace('&#234;', 'ê').replace('&#244;', 'ô').replace('&#226;', 'â')
        description = description.replace('&#201;', 'É').replace('&#233;', 'é').replace('&#205;', 'Í').replace('&#211;', 'Ó').replace('&#218;', 'Ú')
        description = description.replace('&#193;', 'Á').replace('&#195;', 'Ã').replace('&#199;', 'Ç').replace('&#213;', 'Õ')
        description = description.replace('&#34;', '"').replace('&#39;', "'").replace('&#38;', '&')
        info['descricao_curta'] = description
    else:
        info['descricao_curta'] = ''
    
    # Setor
    sector = data.get('Sector', {})
    info['setor'] = sector.get('Value', '') if sector else ''
    
    # Subsetor
    subsector = data.get('SubSector', {})
    info['subsetor'] = subsector.get('Value', '') if subsector else ''
    
    # Organização responsável
    orgs = data.get('ProjectOrganizations', [])
    info['organizacao'] = orgs[0].get('Value', '') if orgs else ''
    
    # Localizações
    locations = data.get('Locations', [])
    if locations:
        # Pegar a primeira localização ou concatenar todas
        if len(locations) == 1:
            info['localizacoes'] = locations[0]
        else:
            info['localizacoes'] = '; '.join(locations)
    else:
        info['localizacoes'] = ''
    
    # Coordenadas GPS
    gps_coords = data.get('GPSCoordinates', [])
    if gps_coords and len(gps_coords) >= 2:
        info['latitude'] = gps_coords[0] if gps_coords[0] else ''
        info['longitude'] = gps_coords[1] if gps_coords[1] else ''
    else:
        info['latitude'] = ''
        info['longitude'] = ''
    
    # Endereço principal (da primeira localização)
    if locations and len(locations) > 0:
        info['endereco_principal'] = locations[0]
    else:
        info['endereco_principal'] = ''
    
    # Custo estimado
    cost = data.get('EstimatedCapitalCost', 0)
    info['custo_estimado'] = float(cost) if cost else 0
    
    # Moeda original
    currency = data.get('OriginalCurrency', {})
    info['moeda'] = currency.get('Value', '') if currency else ''
    
    # Custo original (com moeda)
    if cost and info['moeda']:
        info['custo_original'] = f"{cost} {info['moeda']}"
    else:
        info['custo_original'] = ''
    
    # Status da atividade
    status = data.get('CurrentProjectStatus', {})
    info['status_atividade'] = status.get('Value', '') if status else ''
    
    # É PPP
    info['eh_ppp'] = data.get('IsPPP', False)
    
    # Tipo de projeto
    proj_types = data.get('TypeOfProject', [])
    if proj_types:
        info['tipo_projeto'] = '; '.join([t.get('Value', str(t)) if isinstance(t, dict) else str(t) for t in proj_types])
    else:
        info['tipo_projeto'] = ''
    
    # Arranjo contratual
    legal_framework = data.get('LegalFramework', {})
    info['arranjo_contratual'] = legal_framework.get('Value', '') if legal_framework else ''
    
    # Processo licitação
    tender_process = data.get('TenderProcess', {})
    info['processo_licitacao'] = tender_process.get('Value', '') if tender_process else ''
    
    # Outros campos (se existirem)
    info['outro_arranjo_contratual'] = data.get('OtherLegalFramework', '')
    info['outro_processo_licitacao'] = data.get('OtherTenderProcess', '')
    
    return info

def main():
    # Diretório dos JSONs de project info
    project_info_dir = os.path.join(os.path.dirname(__file__), 'responses_project_info')
    
    if not os.path.exists(project_info_dir):
        print(f"ERRO: Diretório {project_info_dir} não encontrado!")
        return
    
    # Listar todos os arquivos JSON de project info
    json_files = glob.glob(os.path.join(project_info_dir, '*_project_info.json'))
    print(f"Encontrados {len(json_files)} arquivos JSON de project info")
    
    # Criar DataFrame vazio
    df = pd.DataFrame()
    
    # Processar cada arquivo JSON
    processed_guids = []
    for json_file in json_files:
        filename = os.path.basename(json_file)
        guid = extract_guid_from_filename(filename)
        
        if not guid:
            print(f"Não foi possível extrair GUID do arquivo: {filename}")
            continue
        
        # Evitar duplicatas
        if guid in processed_guids:
            print(f"GUID duplicado ignorado: {guid}")
            continue
            
        processed_guids.append(guid)
        
        # Carregar dados do JSON
        data = load_json_file(json_file)
        if not data:
            print(f"Erro ao carregar dados do GUID: {guid}")
            continue
        
        # Extrair informações
        project_info = extract_project_info(data)
        project_info['GUID'] = guid
        
        # Adicionar ao DataFrame
        df = pd.concat([df, pd.DataFrame([project_info])], ignore_index=True)
        
        if len(processed_guids) % 50 == 0:
            print(f"Processados: {len(processed_guids)} projetos")
    
    print(f"Total de projetos processados: {len(df)}")
    
    if len(df) == 0:
        print("ERRO: Nenhum projeto foi processado!")
        return
    
    # Salvar CSV
    output_csv = os.path.join(os.path.dirname(__file__), '..', 'projetos_from_project_info.csv')
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"CSV salvo em: {output_csv}")
    
    # Salvar Excel
    output_excel = os.path.join(os.path.dirname(__file__), '..', 'projetos_from_project_info.xlsx')
    df.to_excel(output_excel, index=False, engine='openpyxl')
    print(f"Excel salvo em: {output_excel}")
    
    # Estatísticas
    print(f"\n📊 Estatísticas:")
    print(f"   - Total de projetos: {len(df)}")
    print(f"   - Total de colunas: {len(df.columns)}")
    print(f"   - Projetos com coordenadas: {df['latitude'].notna().sum()}")
    print(f"   - Projetos com custo: {df['custo_estimado'].notna().sum()}")
    print(f"   - Projetos PPP: {df['eh_ppp'].sum()}")
    
    # Listar colunas
    print(f"\n📋 Colunas criadas:")
    for col in df.columns:
        non_null = df[col].notna().sum()
        percentage = (non_null / len(df)) * 100
        print(f"   - {col}: {non_null}/{len(df)} ({percentage:.1f}%)")

if __name__ == "__main__":
    main()
