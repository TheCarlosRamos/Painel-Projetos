import json
import os
import pandas as pd
from collections import defaultdict, Counter

def analyze_json_structure(directory="responses"):
    """Analisa a estrutura dos arquivos JSON para determinar o melhor formato Excel."""
    
    # Mapeamento de URL codes para nomes amigáveis
    url_mapping = {
        "2000720": "subsecretaria",
        "2000726": "status_atual_do_projeto",
        "2000727": "questoes_chaves",
        "2000728": "proximas_etapas_do_projeto",
        "2001218": "status_dos_estudos",
        "2001221": "status_consulta_publica",
        "2001224": "status_do_tcu",
        "2001226": "status_do_edital",
        "2001229": "status_do_leilao",
        "2001230": "status_do_contrato",
        "2001232": "descricao_do_projeto",
        "2000725": "data_de_qualificacao_em_ppi",
        "2000711": "setor_do_projeto_ppi",
        "2000712": "subsetor_do_projeto_ppi",
        "400014": "custo_capital_estimado",
        "400015": "custo_medio_anual_operacao"
    }
    
    # Análise de estrutura
    structure_analysis = defaultdict(lambda: defaultdict(int))
    field_types = defaultdict(Counter)
    sample_data = {}
    
    print("Analisando estrutura dos arquivos JSON...")
    
    # Analisar cada arquivo JSON
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            filepath = os.path.join(directory, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extrair GUID do nome do arquivo
                parts = filename.replace('.json', '').split('_')
                guid = parts[1] + '-' + parts[2] + '-' + parts[3] + '-' + parts[4] + '-' + parts[5]
                
                # Extrair URL code
                url_code = None
                for part in parts:
                    if part.isdigit() and len(part) >= 6:
                        url_code = part
                        break
                
                if not url_code:
                    continue
                
                # Analisar estrutura
                if url_code not in sample_data:
                    sample_data[url_code] = data
                
                # Contar tipos de campos
                if 'FieldValue' in data and data['FieldValue'] is not None:
                    field_type = data['FieldValue'].get('Type', 'Unknown')
                    field_types[url_code][field_type] += 1
                
                # Analisar chaves principais
                for key in data.keys():
                    structure_analysis[url_code][key] += 1
                    
            except Exception as e:
                print(f"Erro ao analisar {filename}: {e}")
    
    # Gerar relatório
    print("\n" + "="*80)
    print("ANÁLISE DE ESTRUTURA DOS DADOS")
    print("="*80)
    
    print(f"\nTotal de URL codes analisados: {len(sample_data)}")
    print(f"URL codes encontrados: {list(sample_data.keys())}")
    
    print("\n" + "-"*60)
    print("TIPOS DE CAMPOS POR URL CODE")
    print("-"*60)
    
    for url_code in sorted(sample_data.keys()):
        friendly_name = url_mapping.get(url_code, url_code)
        print(f"\n{url_code} - {friendly_name}:")
        
        data = sample_data[url_code]
        
        # Informações básicas
        print(f"  Título: {data.get('Field', {}).get('Title', 'N/A')}")
        print(f"  Tipo do campo: {data.get('Field', {}).get('Type', 'N/A')}")
        
        # Valor do campo
        if 'FieldValue' in data and data['FieldValue'] is not None:
            field_value = data['FieldValue']
            field_type = field_value.get('Type', 'Unknown')
            
            if field_type == 'ChoiceSingle':
                value = field_value.get('Value', {}).get('Value', 'N/A')
                print(f"  Valor: {value}")
            elif field_type == 'Numerical':
                value = field_value.get('Value', 'N/A')
                print(f"  Valor: {value}")
            elif field_type == 'Text':
                value = field_value.get('Value', 'N/A')
                print(f"  Valor: {value[:100]}..." if len(str(value)) > 100 else f"  Valor: {value}")
            else:
                print(f"  Valor: {field_value}")
        else:
            print(f"  Valor: N/A (Field não preenchido ou nulo)")
        
        # Status e informações adicionais
        print(f"  Status: {data.get('Status', {}).get('Status', 'N/A')}")
        print(f"  Theme: {data.get('Theme', {}).get('Value', 'N/A')}")
        print(f"  Stage: {data.get('Stage', {}).get('Value', 'N/A')}")
    
    # Recomendações para formato Excel
    print("\n" + "="*80)
    print("RECOMENDAÇÕES PARA FORMATO EXCEL")
    print("="*80)
    
    print("\n1. ESTRUTURA RECOMENDADA:")
    print("   - Coluna A: GUID (identificador único do projeto)")
    print("   - Coluna B: Nome do Projeto (se disponível)")
    print("   - Colunas C-Z: Valores para cada URL code")
    
    print("\n2. COLUNAS SUGERIDAS:")
    columns = ['GUID', 'Nome_Projeto']
    for url_code in sorted(url_mapping.keys()):
        friendly_name = url_mapping[url_code]
        columns.append(friendly_name)
    
    print(f"   Total de colunas: {len(columns)}")
    print(f"   Colunas: {columns}")
    
    print("\n3. TRATAMENTO DE DADOS:")
    print("   - ChoiceSingle: Extrair apenas o valor (Value)")
    print("   - Numerical: Manter como número")
    print("   - Text: Manter como texto")
    print("   - Status: Incluir como coluna separada se necessário")
    print("   - Dados ausentes: Preencher com 'N/A' ou vazio")
    
    print("\n4. ARQUIVOS DE EXCEL SUGERIDOS:")
    print("   - projects_complete_data.xlsx (todos os dados)")
    print("   - projects_summary.xlsx (resumo com campos principais)")
    print("   - projects_by_sector.xlsx (filtrado por setor)")
    
    return sample_data, structure_analysis, field_types

def create_sample_excel(sample_data, url_mapping):
    """Cria uma amostra do Excel com base nos dados analisados."""
    
    # Criar DataFrame de exemplo
    sample_rows = []
    
    # Usar o primeiro GUID como exemplo
    sample_guid = "0132e2be-059a-41e0-b2f4-c1a822c0a5c1"
    
    row = {'GUID': sample_guid}
    
    # Adicionar dados para cada URL code
    for url_code, data in sample_data.items():
        friendly_name = url_mapping.get(url_code, url_code)
        
        # Extrair valor do campo
        if 'FieldValue' in data and data['FieldValue'] is not None:
            field_value = data['FieldValue']
            field_type = field_value.get('Type', 'Unknown')
            
            if field_type == 'ChoiceSingle':
                value = field_value.get('Value', {}).get('Value', '')
            elif field_type == 'Numerical':
                value = field_value.get('Value', '')
            elif field_type == 'Text':
                value = field_value.get('Value', '')
            else:
                value = str(field_value)
            
            row[friendly_name] = value
        else:
            row[friendly_name] = ''
    
    sample_rows.append(row)
    
    # Criar DataFrame
    df = pd.DataFrame(sample_rows)
    
    # Salvar como Excel
    output_file = "sample_structure.xlsx"
    df.to_excel(output_file, index=False, engine='openpyxl')
    
    print(f"\nAmostra de estrutura salva em: {output_file}")
    print(f"Shape do DataFrame: {df.shape}")
    print(f"Colunas: {list(df.columns)}")
    
    return df

if __name__ == "__main__":
    # Analisar estrutura
    sample_data, structure_analysis, field_types = analyze_json_structure()
    
    # Criar amostra Excel
    url_mapping = {
        "2000720": "subsecretaria",
        "2000726": "status_atual_do_projeto",
        "2000727": "questoes_chaves",
        "2000728": "proximas_etapas_do_projeto",
        "2001218": "status_dos_estudos",
        "2001221": "status_consulta_publica",
        "2001224": "status_do_tcu",
        "2001226": "status_do_edital",
        "2001229": "status_do_leilao",
        "2001230": "status_do_contrato",
        "2001232": "descricao_do_projeto",
        "2000725": "data_de_qualificacao_em_ppi",
        "2000711": "setor_do_projeto_ppi",
        "2000712": "subsetor_do_projeto_ppi",
        "400014": "custo_capital_estimado",
        "400015": "custo_medio_anual_operacao"
    }
    
    df = create_sample_excel(sample_data, url_mapping)
    
    print("\n" + "="*80)
    print("ANÁLISE CONCLUÍDA!")
    print("="*80)
    print("\nPróximos passos:")
    print("1. Revise a amostra gerada (sample_structure.xlsx)")
    print("2. Execute o script completo para gerar o Excel final")
    print("3. Ajuste o formato conforme necessário")
