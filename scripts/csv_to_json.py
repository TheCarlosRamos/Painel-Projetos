import pandas as pd
import json
import os

def csv_to_json():
    """Converte o arquivo CSV completo para JSON."""
    
    # Caminhos dos arquivos
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(base_dir, '..', 'projetos_completos.csv')
    json_file = os.path.join(base_dir, '..', 'projetos_completos.json')
    
    try:
        # Ler o arquivo CSV
        print(f"Lendo arquivo CSV: {csv_file}")
        df = pd.read_csv(csv_file, encoding='utf-8-sig')
        
        print(f"Total de projetos: {len(df)}")
        print(f"Total de colunas: {len(df.columns)}")
        
        # Converter DataFrame para JSON
        # Opção 1: Lista de dicionários (um por projeto)
        json_data = df.to_dict('records')
        
        # Opção 2: Estrutura aninhada com metadados
        json_structured = {
            "metadados": {
                "total_projetos": len(df),
                "total_colunas": len(df.columns),
                "data_geracao": pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                "colunas": list(df.columns)
            },
            "projetos": json_data
        }
        
        # Salvar JSON formatado
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_structured, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Arquivo JSON salvo com sucesso: {json_file}")
        print(f"📊 Tamanho do arquivo: {os.path.getsize(json_file) / 1024:.1f} KB")
        
        # Estatísticas
        print(f"\n📈 Estatísticas do arquivo JSON:")
        print(f"   - Total de projetos: {len(json_data)}")
        print(f"   - Total de colunas: {len(df.columns)}")
        
        # Mostrar exemplo de um projeto
        if len(json_data) > 0:
            print(f"\n📋 Exemplo de estrutura do primeiro projeto:")
            print(json.dumps(json_data[0], ensure_ascii=False, indent=2)[:500] + "...")
        
        # Contar valores não nulos por campo
        print(f"\n📋 Preenchimento por campo:")
        for col in df.columns:
            non_null = df[col].notna().sum()
            percentage = (non_null / len(df)) * 100
            print(f"   - {col}: {non_null}/{len(df)} ({percentage:.1f}%)")
        
        return json_file
        
    except Exception as e:
        print(f"❌ Erro ao converter CSV para JSON: {e}")
        return None

def csv_to_json_simple():
    """Converte para JSON simples (apenas lista de projetos)."""
    
    # Caminhos dos arquivos
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(base_dir, '..', 'projetos_completos.csv')
    json_file = os.path.join(base_dir, '..', 'projetos_completos_simple.json')
    
    try:
        # Ler o arquivo CSV
        print(f"\nGerando JSON simples...")
        df = pd.read_csv(csv_file, encoding='utf-8-sig')
        
        # Converter para JSON simples
        json_data = df.to_dict('records')
        
        # Salvar JSON simples
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ JSON simples salvo: {json_file}")
        print(f"📊 Tamanho: {os.path.getsize(json_file) / 1024:.1f} KB")
        
        return json_file
        
    except Exception as e:
        print(f"❌ Erro ao gerar JSON simples: {e}")
        return None

if __name__ == "__main__":
    print("🔄 Convertendo CSV para JSON...")
    
    # Gerar JSON estruturado
    json_file = csv_to_json()
    
    # Gerar JSON simples
    json_simple = csv_to_json_simple()
    
    if json_file and json_simple:
        print(f"\n🎉 Arquivos JSON gerados com sucesso!")
        print(f"📁 Estruturado: {os.path.basename(json_file)}")
        print(f"📁 Simples: {os.path.basename(json_simple)}")
    else:
        print(f"\n❌ Erro na conversão para JSON")
