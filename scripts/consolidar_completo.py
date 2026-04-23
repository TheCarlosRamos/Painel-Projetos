import pandas as pd
import json
import os
import re
from collections import defaultdict

def extract_guid_from_filename(filename):
    """Extrai o GUID completo do nome do arquivo."""
    # Padrão: response_44cd4078_42b0_4a83_8955_efa31cdb2130_2001232_descrição_do_projeto.json
    # ou: response_44cd4078-42b0-4a83-8955-efa31cdb2130_2001232_descrição_do_projeto.json
    
    # Tentar diferentes padrões
    patterns = [
        r'response_([0-9a-fA-F]{8}(?:_[0-9a-fA-F]{4}){3}_[0-9a-fA-F]{12})_(\d+)_',  # com underscores
        r'response_([0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12})_(\d+)_',  # com hífens
        r'response_([^_]+(?:_[^_]+)*?)_(\d+)_',  # fallback genérico
    ]
    
    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            guid_part = match.group(1)
            # Se tiver underscores, converter para hífens
            if '_' in guid_part and len(guid_part) > 20:
                return guid_part.replace('_', '-')
            else:
                return guid_part
    
    return None

def extract_url_code_from_filename(filename):
    """Extrai o código URL do nome do arquivo."""
    match = re.search(r'_(\d+)_', filename)
    return match.group(1) if match else None

def process_json_file(filepath):
    """Processa um arquivo JSON para extrair título e valor."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extrair título do campo Field.Title
        column_title = None
        if 'Field' in data and data['Field']:
            field = data['Field']
            if isinstance(field, dict) and 'Title' in field:
                column_title = field['Title']
        
        # Fallback para outros campos se Field.Title não existir
        if not column_title:
            if 'SourceId' in data:
                column_title = data['SourceId']
            elif 'Id' in data:
                column_title = str(data['Id'])
            else:
                column_title = 'Unknown'
        
        # Extrair valor do campo FieldValue.Value
        cell_value = None
        if 'FieldValue' in data and data['FieldValue']:
            field_value = data['FieldValue']
            
            if isinstance(field_value, dict):
                if 'Value' in field_value:
                    value = field_value['Value']
                    
                    # Se for um dicionário com Key e Value, extrair apenas o Value
                    if isinstance(value, dict) and 'Value' in value:
                        cell_value = str(value['Value'])
                    elif isinstance(value, list):
                        # Se for lista, juntar com vírgulas
                        cell_value = ', '.join(str(v) for v in value if v is not None)
                    else:
                        cell_value = str(value) if value is not None else ''
                else:
                    cell_value = str(field_value) if field_value is not None else ''
            else:
                cell_value = str(field_value) if field_value is not None else ''
        
        return column_title, cell_value
        
    except Exception as e:
        print(f"Erro ao processar {filepath}: {e}")
        return None, None

def main():
    print("🔍 Iniciando consolidação COMPLETA dos dados para Excel...")
    
    # Diretório de respostas
    responses_dir = "responses"
    if not os.path.exists(responses_dir):
        print(f"❌ Diretório {responses_dir} não encontrado!")
        print("📁 Verificando subdiretórios disponíveis...")
        
        # Listar subdiretórios que começam com "responses_"
        subdirs = [d for d in os.listdir('.') if d.startswith('responses_') and os.path.isdir(d)]
        if subdirs:
            print(f"📁 Encontrados {len(subdirs)} subdiretórios:")
            for subdir in subdirs[:5]:
                print(f"   📂 {subdir}")
            if len(subdirs) > 5:
                print(f"   ... e mais {len(subdirs) - 5}")
            
            # Usar o primeiro subdiretório como base
            responses_dir = subdirs[0]
            print(f"🔄 Usando diretório: {responses_dir}")
        else:
            print("❌ Nenhum diretório de respostas encontrado!")
            return
    
    # Listar todos os arquivos JSON em todos os subdiretórios responses_*
    json_files = []
    processed_dirs = []
    
    # Procurar em todos os diretórios que começam com "responses_"
    for item in os.listdir('.'):
        if item.startswith('responses_') and os.path.isdir(item):
            dir_files = []
            for root, dirs, files in os.walk(item):
                for file in files:
                    if file.endswith('.json'):
                        dir_files.append(os.path.join(root, file))
            
            json_files.extend(dir_files)
            processed_dirs.append((item, len(dir_files)))
    
    # Também procurar no responses_project_info
    if os.path.exists('responses_project_info'):
        dir_files = []
        for root, dirs, files in os.walk('responses_project_info'):
            for file in files:
                if file.endswith('.json'):
                    dir_files.append(os.path.join(root, file))
        
        json_files.extend(dir_files)
        processed_dirs.append(('responses_project_info', len(dir_files)))
    
    print(f"📁 {len(json_files)} arquivos JSON encontrados")
    print(f"📂 Diretórios processados:")
    for dirname, count in processed_dirs:
        print(f"   📁 {dirname}: {count} arquivos")
    
    # Estrutura de dados para organizar por GUID
    projects_data = defaultdict(dict)
    
    # Mapeamento de títulos das colunas extraídas dos JSONs
    column_titles = {}
    
    # Processar cada arquivo
    processed = 0
    for filepath in json_files:
        filename = os.path.basename(filepath)
        
        # Extrair informações do nome do arquivo
        guid = extract_guid_from_filename(filename)
        url_code = extract_url_code_from_filename(filename)
        
        if not guid or not url_code:
            continue
        
        # Processar o JSON para extrair título e valor
        column_title, cell_value = process_json_file(filepath)
        
        if column_title and cell_value is not None:
            # Armazenar dados do projeto
            projects_data[guid][column_title] = cell_value
            column_titles[column_title] = url_code
            processed += 1
    
    print(f"✅ {processed} arquivos processados com sucesso")
    
    # Criar DataFrame
    if not projects_data:
        print("❌ Nenhum dado encontrado para processar!")
        return
    
    # Converter para DataFrame
    df_data = []
    for guid, data in projects_data.items():
        row = {'GUID': guid}
        row.update(data)
        df_data.append(row)
    
    df = pd.DataFrame(df_data)
    
    # Reordenar colunas: GUID primeiro, depois as outras em ordem alfabética
    columns = ['GUID'] + sorted([col for col in df.columns if col != 'GUID'])
    df = df[columns]
    
    print(f"📊 {len(df)} projetos únicos encontrados")
    print(f"📋 {len(columns) - 1} títulos de colunas extraídos dos JSONs")
    
    # Salvar planilha
    output_file = "consolidado_projetos_final.xlsx"
    print(f"💾 Salvando planilha em {output_file}...")
    
    try:
        df.to_excel(output_file, index=False, engine='openpyxl')
        print(f"✅ Planilha salva com sucesso!")
        print(f"📊 {len(df)} linhas e {len(df.columns)} colunas")
        print(f"📁 Arquivo: {os.path.abspath(output_file)}")
        
        # Estatísticas
        total_cells = len(df) * (len(df.columns) - 1)  # Excluindo coluna GUID
        filled_cells = 0
        for col in df.columns:
            if col != 'GUID':
                filled_cells += df[col].astype(str).str.strip().ne('').sum()
        
        fill_rate = (filled_cells / total_cells * 100) if total_cells > 0 else 0
        
        print(f"\n📈 Estatísticas:")
        print(f"   • Total de células: {total_cells:,}")
        print(f"   • Células preenchidas: {filled_cells:,}")
        print(f"   • Taxa de preenchimento: {fill_rate:.1f}%")
        
        # Verificar GUIDs
        unique_guids = df['GUID'].nunique()
        print(f"   • GUIDs únicos: {unique_guids}")
        
        # Mostrar alguns exemplos de GUIDs para verificação
        print(f"\n🔍 Exemplos de GUIDs na planilha:")
        for i, guid in enumerate(df['GUID'].head(5)):
            print(f"   {i+1}. {guid}")
        
        # Verificar se há GUIDs truncados
        truncated_guids = df[df['GUID'].str.len() < 36]['GUID'].tolist()
        if truncated_guids:
            print(f"\n⚠️ {len(truncated_guids)} GUIDs parecem truncados:")
            for guid in truncated_guids[:5]:
                print(f"   🔄 {guid}")
        else:
            print(f"\n✅ Todos os GUIDs parecem completos!")
            
    except Exception as e:
        print(f"❌ Erro ao salvar planilha: {e}")
        return

if __name__ == "__main__":
    main()
