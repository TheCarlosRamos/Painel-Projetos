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
    
    # Localizações (concatenadas)
    locations = data.get('Locations', [])
    info['localizacoes'] = ', '.join(locations) if locations else ''
    
    # Coordenadas GPS (primeira localização)
    gps_coords = data.get('GPSCoordinates', [])
    if gps_coords and len(gps_coords) > 0:
        first_coord = gps_coords[0]
        location = first_coord.get('location')
        if location:
            info['latitude'] = location.get('y', '')
            info['longitude'] = location.get('x', '')
            info['endereco_principal'] = first_coord.get('address', '')
        else:
            info['latitude'] = ''
            info['longitude'] = ''
            info['endereco_principal'] = ''
    else:
        info['latitude'] = ''
        info['longitude'] = ''
        info['endereco_principal'] = ''
    
    # Custo estimado
    info['custo_estimado'] = data.get('EstimatedCapitalCost', 0)
    
    # Moeda original
    currency = data.get('OriginalCurrency', {})
    info['moeda'] = currency.get('Value', '') if currency else ''
    
    # Custo na moeda original
    info['custo_original'] = data.get('OriginalCurrencyEstimatedCapitalCost', 0)
    
    # Status do projeto
    status = data.get('ProjectActivityStatus', {})
    info['status_atividade'] = status.get('Title', '') if status else ''
    
    # É PPP?
    info['eh_ppp'] = data.get('IsPPP', False)
    
    # Tipo de projeto
    project_types = data.get('TypeOfProject', [])
    info['tipo_projeto'] = ', '.join(project_types) if project_types else ''
    
    # Arranjos contratuais
    packages = data.get('Packages', [])
    if packages and len(packages) > 0:
        first_package = packages[0]
        contractual_arrangements = first_package.get('ContractualArrangements', [])
        if contractual_arrangements and len(contractual_arrangements) > 0:
            info['arranjo_contratual'] = contractual_arrangements[0].get('Title', '')
        else:
            info['arranjo_contratual'] = ''
        
        # Processo de licitação
        tender_process = first_package.get('TenderProcess')
        if tender_process:
            info['processo_licitacao'] = tender_process.get('Title', '')
        else:
            info['processo_licitacao'] = ''
        
        # Outro arranjo contratual
        other_contractual = first_package.get('OtherContractualArrangement')
        if other_contractual:
            info['outro_arranjo_contratual'] = other_contractual.get('Title', '')
        else:
            info['outro_arranjo_contratual'] = ''
        
        # Outro processo de licitação
        other_tender = first_package.get('OtherTenderProcess')
        if other_tender:
            info['outro_processo_licitacao'] = other_tender.get('Title', '')
        else:
            info['outro_processo_licitacao'] = ''
    else:
        info['arranjo_contratual'] = ''
        info['processo_licitacao'] = ''
        info['outro_arranjo_contratual'] = ''
        info['outro_processo_licitacao'] = ''
    
    return info

def update_csv_with_project_info():
    """Atualiza o CSV consolidado com informações básicas dos projetos."""
    
    # Carregar CSV existente
    csv_file = os.path.join(os.path.dirname(__file__), '..', 'projetos_consolidado.csv')
    print(f"Carregando CSV existente: {csv_file}")
    
    df = pd.read_csv(csv_file, encoding='utf-8-sig')
    print(f"CSV carregado: {len(df)} projetos")
    
    # Diretório com informações dos projetos
    project_info_dir = os.path.join(os.path.dirname(__file__), 'responses_project_info')
    
    # Processar cada projeto
    updated_count = 0
    for index, row in df.iterrows():
        guid = row['guid']
        
        # Buscar arquivo de informações do projeto
        info_file = os.path.join(project_info_dir, f'response_{guid}_project_info.json')
        
        if os.path.exists(info_file):
            data = load_json_file(info_file)
            project_info = extract_project_info(data)
            
            # Atualizar DataFrame
            for key, value in project_info.items():
                df.at[index, key] = value
            
            updated_count += 1
            if updated_count % 50 == 0:
                print(f"Atualizados: {updated_count}/{len(df)} projetos")
        else:
            print(f"Arquivo não encontrado para GUID: {guid}")
    
    print(f"Total de projetos atualizados: {updated_count}")
    
    # Salvar CSV atualizado
    output_file = os.path.join(os.path.dirname(__file__), '..', 'projetos_completos.csv')
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"✅ CSV atualizado salvo em: {output_file}")
    
    # Estatísticas
    print(f"\n📊 Estatísticas do arquivo atualizado:")
    print(f"   - Total de projetos: {len(df)}")
    print(f"   - Total de colunas: {len(df.columns)}")
    print(f"   - Projetos com coordenadas: {df['latitude'].notna().sum()}")
    print(f"   - Projetos com custo: {df['custo_estimado'].notna().sum()}")
    print(f"   - Projetos PPP: {df['eh_ppp'].sum()}")
    
    # Listar novas colunas
    print(f"\n📋 Novas colunas adicionadas:")
    new_columns = ['nome_completo', 'descricao_curta', 'setor', 'subsetor', 'organizacao', 
                   'localizacoes', 'latitude', 'longitude', 'endereco_principal', 
                   'custo_estimado', 'moeda', 'custo_original', 'status_atividade', 
                   'eh_ppp', 'tipo_projeto', 'arranjo_contratual', 'processo_licitacao',
                   'outro_arranjo_contratual', 'outro_processo_licitacao']
    
    for col in new_columns:
        if col in df.columns:
            non_null = df[col].notna().sum()
            percentage = (non_null / len(df)) * 100
            print(f"   - {col}: {non_null}/{len(df)} ({percentage:.1f}%)")
    
    return output_file

if __name__ == "__main__":
    update_csv_with_project_info()
