import json
import os
import pandas as pd
from collections import defaultdict
import re

def extract_url_code_from_filename(filename):
    """Extrai o código URL do nome do arquivo."""
    # Padrão: response_<guid>_<id>_<title>.json
    match = re.search(r'_(\d+)_', filename)
    return match.group(1) if match else None

def extract_guid_from_filename(filename):
    """Extrai o GUID do nome do arquivo de forma flexível."""
    # Tentar capturar o padrão hexadecimal de um GUID (8-4-4-4-12) usando underscores ou hifens
    guid_pattern = r'([a-f0-9]{8}[-_][a-f0-9]{4}[-_][a-f0-9]{4}[-_][a-f0-9]{4}[-_][a-f0-9]{12})'
    match = re.search(guid_pattern, filename, re.IGNORECASE)
    if match:
        return match.group(1).replace('_', '-').lower()
    
    # Fallback: pegar tudo entre response_ e o próximo underscore que precede um ID ou o fim
    match = re.search(r'response_([^_]+(?:_[^_]+){0,4})', filename)
    if match:
        return match.group(1).replace('_', '-').lower()
        
    return None

def load_url_titles():
    """Carrega os títulos das URLs do arquivo lista_de_urls.txt."""
    url_titles = {}
    try:
        # Procurar o arquivo no diretório atual
        filename = 'lista_de_urls.txt'
        if not os.path.exists(filename):
            # Tentar um nível acima se não encontrar
            filename = os.path.join('..', filename)
            
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    # Formatos comuns: "2000720 -> subsecretaria" ou "2000725 → Data de qualificação"
                    if '->' in line or '→' in line:
                        separator = '->' if '->' in line else '→'
                        parts = line.split(separator)
                        if len(parts) >= 2:
                            url_code = parts[0].strip()
                            title = parts[1].strip()
                            # Remover caracteres estranhos no final se houver
                            title = title.rstrip(':').strip()
                            url_titles[url_code] = title
    except Exception as e:
        print(f"⚠️ Erro ao carregar títulos de lista_de_urls.txt: {e}")
    return url_titles

def process_json_file(filepath):
    """Processa um arquivo JSON e extrai o título, valor e GUID interno."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, dict):
            return None, None, None

        # 0. Tentar extrair o GUID de dentro do JSON (fonte da verdade)
        guid_inside = data.get('Guid') or data.get('guid')
        if guid_inside:
            guid_inside = str(guid_inside).lower()

        # 1. Extrair o título da coluna (Field -> Title)
        column_title = data.get('Field', {}).get('Title')
        
        # 2. Extrair o valor do campo (FieldValue -> Value)
        cell_value = None
        field_value_obj = data.get('FieldValue', {})
        
        if isinstance(field_value_obj, dict):
            val = field_value_obj.get('Value')
            field_type = field_value_obj.get('Type')
            
            # Tratar ChoiceSingle
            if field_type == "ChoiceSingle" and isinstance(val, dict):
                cell_value = val.get('Value')
            
            # Tratar ChoiceMultiple
            elif field_type == "ChoiceMultiple" and isinstance(val, list):
                extracted = []
                for item in val:
                    if isinstance(item, dict) and 'Value' in item:
                        extracted.append(str(item['Value']))
                    else:
                        extracted.append(str(item))
                cell_value = ", ".join(extracted)
            
            # Tratar outros tipos (Numerical, Text, Date)
            else:
                cell_value = val
        
        # Especial para project_info: pegar o Nome se não houver Title
        if not column_title and 'Name' in data and 'ProjectActivityStatus' in data:
            column_title = "Nome do Projeto"
            cell_value = data.get('Name')

        # Fallbacks se FieldValue.Value não funcionar
        if cell_value is None:
            for key in ['Value', 'value', 'response', 'data']:
                if key in data:
                    cell_value = data[key]
                    break
        
        # Formatação final para string amigável
        if cell_value is not None:
            if isinstance(cell_value, dict):
                cell_value = cell_value.get('Value', str(cell_value))
            elif isinstance(cell_value, list):
                cell_value = ", ".join(str(i) for i in cell_value)
            elif isinstance(cell_value, bool):
                cell_value = "Sim" if cell_value else "Não"
            else:
                cell_value = str(cell_value)
        
        return column_title, cell_value, guid_inside
        
    except Exception as e:
        print(f"⚠️ Erro ao processar {filepath}: {e}")
        return None, None, None

def main():
    print("Iniciando consolidacao inteligente de dados para Excel...")
    
    # 1. Carregar títulos das URLs (Preferência para Português)
    url_titles_pt = load_url_titles()
    print(f"--- {len(url_titles_pt)} titulos em portugues carregados de lista_de_urls.txt")
    
    # 2. Localizar todas as pastas de respostas
    base_dir = "."
    response_dirs = [d for d in os.listdir(base_dir) if os.path.isdir(d) and d.startswith("responses")]
    
    if not response_dirs:
        print("!!! Nenhuma pasta 'responses*' encontrada no diretorio atual.")
        return
    
    print(f"Pastas de origem encontradas: {', '.join(response_dirs)}")
    
    # 3. Coletar todos os arquivos JSON
    json_files = []
    for rdir in response_dirs:
        for root, _, files in os.walk(rdir):
            for file in files:
                if file.endswith('.json'):
                    json_files.append(os.path.join(root, file))
    
    print(f"--- {len(json_files)} arquivos JSON encontrados no total")
    
    # 4. Estrutura de dados: { GUID: { URL_CODE: VALUE } }
    projects_data = defaultdict(dict)
    
    # Mapeamento de fallback (títulos do JSON)
    column_titles_json = {}
    
    # Processar cada arquivo
    processed_count = 0
    for filepath in json_files:
        filename = os.path.basename(filepath)
        
        guid_from_file = extract_guid_from_filename(filename)
        url_code = extract_url_code_from_filename(filename)
        
        # Se for project_info, damos um código especial
        if "project_info" in filename:
            url_code = "PROJECT_NAME"
        
        if not guid_from_file and not "project_info" in filename:
            continue
        
        title_from_json, cell_value, guid_inside = process_json_file(filepath)
        
        # Priorizar GUID de dentro do JSON
        final_guid = guid_inside if guid_inside else guid_from_file
        
        if not final_guid:
            continue

        # Salvar o título do JSON caso não tenhamos o de Portugal
        if title_from_json and url_code not in column_titles_json:
            column_titles_json[url_code] = title_from_json
            
        if cell_value is not None:
            # Armazenar o valor (se houver duplicatas para o mesmo GUID/ID, o último vence)
            projects_data[final_guid][url_code] = cell_value
            processed_count += 1
    
    print(f"--- {processed_count} campos extraidos de {len(projects_data)} projetos")
    
    # 5. Preparar o DataFrame
    # Obter todos os códigos de URL encontrados
    all_codes = set()
    for p_data in projects_data.values():
        all_codes.update(p_data.keys())
    
    # Ordenar códigos numericamente (mantendo códigos especiais como PROJECT_NAME no início)
    sorted_codes = sorted(list(all_codes), key=lambda x: (0 if x == "PROJECT_NAME" else 1, int(x) if x.isdigit() else 999999))
    
    final_rows = []
    for guid, p_fields in projects_data.items():
        row = {'GUID': guid}
        for code in sorted_codes:
            # Prioridade de título: 1. Lista TXT (PT), 2. JSON (EN), 3. Código ID
            col_name = url_titles_pt.get(code)
            if not col_name:
                col_name = column_titles_json.get(code, f"Campo_{code}")
            
            # Limitar tamanho para o Excel não reclamar e ficar legível
            if len(col_name) > 100:
                col_name = col_name[:97] + "..."
                
            row[col_name] = p_fields.get(code, "")
        final_rows.append(row)
    
    df = pd.DataFrame(final_rows)
    
    # Garantir que GUID seja a primeira coluna
    cols = ['GUID'] + [c for c in df.columns if c != 'GUID']
    df = df[cols]
    
    # 6. Salvar em Excel
    output_file = "consolidado_projetos_COMPLETO_FINAL.xlsx"
    print(f"Gerando planilha: {output_file}")
    
    try:
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Projetos')
            
            # Ajuste de layout básico
            worksheet = writer.sheets['Projetos']
            for idx, col in enumerate(df.columns):
                max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.column_dimensions[chr(65 + idx % 26) if idx < 26 else 'A' + chr(65 + (idx-26) % 26)].width = min(max_len, 60)
        
        print(f"Sucesso! Planilha salva em: {os.path.abspath(output_file)}")
        print(f"Dimensoes: {df.shape[0]} projetos x {df.shape[1]} colunas")
        
        # Calcular estatísticas de preenchimento
        total_cells = df.shape[0] * (df.shape[1] - 1)  # Exclui GUID
        filled_cells = df.iloc[:, 1:].notna().sum().sum()
        fill_rate = (filled_cells / total_cells) * 100 if total_cells > 0 else 0
        
        print("\nEstatisticas de Preenchimento:")
        print(f"  - Total de campos possiveis (colunas x linhas): {total_cells:,}")
        print(f"  - Campos preenchidos: {filled_cells:,}")
        print(f"  - Taxa de preenchimento: {fill_rate:.2f}%")
        
    except Exception as e:
        print(f"Erro ao salvar Excel: {e}")
        # Fallback simples
        df.to_excel(output_file.replace(".xlsx", ".csv"), index=False)
        print(f"Salvo como CSV devido ao erro: {output_file.replace('.xlsx', '.csv')}")


if __name__ == "__main__":
    main()

