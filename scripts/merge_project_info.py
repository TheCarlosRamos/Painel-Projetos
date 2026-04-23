import pandas as pd
import json
import os
import csv
from collections import defaultdict

def load_project_info(guid):
    """Carrega informações do projeto do arquivo JSON."""
    filename = f"responses_project_info/response_{guid.replace('-', '_')}_project_info.json"
    
    if not os.path.exists(filename):
        return {}
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extrair informações relevantes
        project_info = {}
        
        # Informações básicas
        project_info['Nome do Projeto'] = data.get('Name', '')
        project_info['Descrição'] = data.get('Description', '')
        
        # Setor e Subsetor
        sector = data.get('Sector', {})
        project_info['Setor'] = sector.get('Value', '') if isinstance(sector, dict) else str(sector)
        
        subsector = data.get('SubSector', {})
        project_info['Subsetor'] = subsector.get('Value', '') if isinstance(subsector, dict) else str(subsector)
        
        # Localização
        locations = data.get('Locations', [])
        if locations and len(locations) > 0:
            project_info['Localização'] = ', '.join(str(loc) for loc in locations)
        else:
            project_info['Localização'] = ''
        
        # Coordenadas (se disponível)
        gps_coordinates = data.get('GPSCoordinates', [])
        if gps_coordinates and len(gps_coordinates) > 0:
            coord = gps_coordinates[0]
            location = coord.get('location', {})
            x = location.get('x', '')
            y = location.get('y', '')
            project_info['Coordenada X'] = str(x)
            project_info['Coordenada Y'] = str(y)
            
            # Endereço detalhado
            attributes = coord.get('attributes', {})
            project_info['Estado'] = attributes.get('Region', '')
            project_info['Cidade'] = attributes.get('City', '')
            project_info['Endereço'] = attributes.get('Place_addr', '')
        else:
            project_info['Coordenada X'] = ''
            project_info['Coordenada Y'] = ''
            project_info['Estado'] = ''
            project_info['Cidade'] = ''
            project_info['Endereço'] = ''
        
        # Status do projeto
        status = data.get('CurrentProjectStatus', {})
        project_info['Status Atual'] = status.get('Value', '') if isinstance(status, dict) else str(status)
        
        # Tipo de projeto
        type_of_project = data.get('TypeOfProject', [])
        if type_of_project and len(type_of_project) > 0:
            project_info['Tipo de Projeto'] = ', '.join(str(t) for t in type_of_project)
        else:
            project_info['Tipo de Projeto'] = ''
        
        # É PPP?
        project_info['É PPP'] = 'Sim' if data.get('IsPPP', False) else 'Não'
        project_info['É Não Solicitado'] = 'Sim' if data.get('IsUnsolicited', False) else 'Não'
        
        # Custo estimado
        project_info['Custo Estimado (BRL)'] = data.get('EstimatedCapitalCost', 0)
        project_info['Custo Estimado (Original)'] = data.get('OriginalCurrencyEstimatedCapitalCost', 0)
        
        # Moeda original
        original_currency = data.get('OriginalCurrency', {})
        project_info['Moeda Original'] = original_currency.get('Value', '') if isinstance(original_currency, dict) else str(original_currency)
        
        # Organização responsável
        owner_org = data.get('OwnerOrganisation', {})
        project_info['Organização Responsável'] = owner_org.get('Value', '') if isinstance(owner_org, dict) else str(owner_org)
        
        # Data de criação e modificação
        project_info['Data de Criação'] = data.get('Created', '')
        project_info['Data de Modificação'] = data.get('Modified', '')
        project_info['Data Prevista de Conclusão'] = data.get('ProjectEstimatedDueDate', '')
        
        # Percentual de conclusão
        project_info['Percentual de Conclusão'] = f"{data.get('Completion', 0) * 100:.1f}%"
        
        # Framework legal
        legal_framework = data.get('LegalFramework', {})
        project_info['Framework Legal'] = legal_framework.get('Title', '') if isinstance(legal_framework, dict) else str(legal_framework)
        
        # Suporte técnico
        tech_support = data.get('TechnicalSupport', {})
        project_info['Suporte Técnico'] = tech_support.get('Title', '') if isinstance(tech_support, dict) else str(tech_support)
        
        # Territórios
        territories = data.get('Territories', [])
        if territories and len(territories) > 0:
            project_info['Territórios'] = ', '.join(str(t.get('Value', t)) for t in territories)
        else:
            project_info['Territórios'] = ''
        
        return project_info
        
    except Exception as e:
        print(f"Erro ao carregar project info para {guid}: {e}")
        return {}

def main():
    print("🔍 Iniciando merge de informações básicas dos projetos...")
    
    # Carregar planilha existente
    excel_file = "consolidado_projetos_atualizado.xlsx"
    if not os.path.exists(excel_file):
        print(f"❌ Arquivo {excel_file} não encontrado!")
        return
    
    print(f"📊 Carregando planilha existente: {excel_file}")
    df = pd.read_excel(excel_file)
    
    print(f"📋 Planilha carregada: {len(df)} linhas e {len(df.columns)} colunas")
    
    # Lista de GUIDs na planilha
    planilha_guids = set(df['GUID'].astype(str))
    print(f"🎯 Encontrados {len(planilha_guids)} GUIDs na planilha")
    
    # Carregar GUIDs do projects.csv para garantir que usamos apenas os projetos corretos
    projects_guids = set()
    try:
        with open('projects.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # Pular cabeçalho
            for row in reader:
                if row and row[0].strip():
                    projects_guids.add(row[0].strip())
        print(f"📋 {len(projects_guids)} GUIDs no projects.csv")
    except Exception as e:
        print(f"Erro ao ler projects.csv: {e}")
        return
    
    # Verificar arquivos de project info disponíveis apenas para GUIDs do projects.csv
    project_info_files = [f for f in os.listdir('responses_project_info') if f.endswith('_project_info.json')]
    available_guids = set()
    
    for filename in project_info_files:
        # Extrair GUID do nome do arquivo
        guid_part = filename.replace('response_', '').replace('_project_info.json', '').replace('_', '-')
        # Adicionar apenas se estiver no projects.csv
        if guid_part in projects_guids:
            available_guids.add(guid_part)
    
    print(f"📁 Encontrados {len(available_guids)} arquivos de project info válidos (do projects.csv)")
    
    # Encontrar GUIDs que têm project info mas não estão na planilha
    missing_guids = available_guids - planilha_guids
    if missing_guids:
        print(f"⚠️ {len(missing_guids)} GUIDs têm project info mas não estão na planilha")
        print("   Esses projetos serão adicionados como novas linhas")
    
    # Preparar novas colunas
    new_columns = [
        'Nome do Projeto', 'Descrição', 'Setor', 'Subsetor', 'Localização',
        'Coordenada X', 'Coordenada Y', 'Estado', 'Cidade', 'Endereço',
        'Status Atual', 'Tipo de Projeto', 'É PPP', 'É Não Solicitado',
        'Custo Estimado (BRL)', 'Custo Estimado (Original)', 'Moeda Original',
        'Organização Responsável', 'Data de Criação', 'Data de Modificação',
        'Data Prevista de Conclusão', 'Percentual de Conclusão',
        'Framework Legal', 'Suporte Técnico', 'Territórios'
    ]
    
    # Adicionar novas colunas vazias à planilha
    for col in new_columns:
        if col not in df.columns:
            df[col] = ''
    
    # Processar cada GUID que tem project info
    updated_count = 0
    for guid in available_guids:
        if guid in planilha_guids:
            # Atualizar linha existente
            project_info = load_project_info(guid)
            
            # Encontrar índice da linha
            mask = df['GUID'].astype(str) == guid
            if mask.any():
                idx = df[mask].index[0]
                
                # Atualizar colunas
                for col, value in project_info.items():
                    if col in df.columns:
                        df.at[idx, col] = value
                
                updated_count += 1
        
        else:
            # Adicionar nova linha
            project_info = load_project_info(guid)
            
            # Criar nova linha
            new_row = {'GUID': guid}
            
            # Preencher todas as colunas existentes com vazio
            for col in df.columns:
                if col != 'GUID':
                    new_row[col] = ''
            
            # Adicionar informações do project info
            for col, value in project_info.items():
                new_row[col] = value
            
            # Adicionar nova linha ao DataFrame
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            updated_count += 1
    
    print(f"✅ {updated_count} projetos atualizados com informações básicas")
    
    # Reordenar colunas (GUID primeiro, depois as novas)
    column_order = ['GUID'] + new_columns + [col for col in df.columns if col not in ['GUID'] + new_columns]
    df = df[column_order]
    
    # Salvar planilha atualizada
    output_file = "consolidado_projetos_completo_corrigido.xlsx"
    print(f"💾 Salvando planilha atualizada: {output_file}")
    
    try:
        df.to_excel(output_file, index=False, engine='openpyxl')
        print(f"✅ Planilha salva com sucesso!")
        print(f"📊 {len(df)} linhas e {len(df.columns)} colunas")
        
        # Estatísticas
        filled_new_cols = 0
        for col in new_columns:
            if col in df.columns:
                filled_count = df[col].astype(str).str.strip().ne('').sum()
                filled_new_cols += filled_count
                print(f"   📋 {col}: {filled_count} valores preenchidos")
        
        total_new_cells = len(df) * len(new_columns)
        fill_rate = (filled_new_cols / total_new_cells) * 100 if total_new_cells > 0 else 0
        print(f"\n📈 Estatísticas das novas colunas:")
        print(f"   • Total de células novas: {total_new_cells:,}")
        print(f"   • Células preenchidas: {filled_new_cols:,}")
        print(f"   • Taxa de preenchimento: {fill_rate:.1f}%")
        
    except Exception as e:
        print(f"❌ Erro ao salvar planilha: {e}")
        return
    
    print(f"\n🎉 Planilha completa salva em: {os.path.abspath(output_file)}")

if __name__ == "__main__":
    main()
