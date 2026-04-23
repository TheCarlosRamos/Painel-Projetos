import pandas as pd

def verify_excel_data():
    """Verifica se os dados foram preenchidos corretamente no Excel."""
    
    print("=== VERIFICAÇÃO DOS DADOS DO EXCEL ===")
    
    # Carregar o arquivo completo
    try:
        df = pd.read_excel("projects_complete_data.xlsx")
        print(f"✅ Arquivo carregado com sucesso")
        print(f"Shape: {df.shape}")
        print(f"Colunas: {list(df.columns)}")
        
        # Verificar coluna Nome_Projeto
        if 'Nome_Projeto' in df.columns:
            non_empty_names = df['Nome_Projeto'].notna() & (df['Nome_Projeto'] != '') & (df['Nome_Projeto'] != ' ')
            print(f"\n📊 Nome_Projeto:")
            print(f"  Total de projetos: {len(df)}")
            print(f"  Projetos com nome: {non_empty_names.sum()}")
            print(f"  Projetos sem nome: {(~non_empty_names).sum()}")
            
            # Mostrar exemplos
            print(f"\n📝 Exemplos de nomes:")
            for i, name in enumerate(df['Nome_Projeto'].dropna().head(5)):
                print(f"  {i+1}. {name}")
                
            # Mostrar exemplos vazios
            empty_names = df[~non_empty_names]['Nome_Projeto'].head(3)
            if len(empty_names) > 0:
                print(f"\n❌ Exemplos de nomes vazios:")
                for i, name in enumerate(empty_names):
                    print(f"  {i+1}. '{name}'")
        
        # Verificar colunas de setor
        sector_col = 'Setor do projeto (de acordo com a classificação da PPI)'
        subsetor_col = 'Subsetor do projeto (de acordo com a classificação da PPI)'
        
        if sector_col in df.columns:
            non_empty_sectors = df[sector_col].notna() & (df[sector_col] != '') & (df[sector_col] != ' ')
            print(f"\n🏢 {sector_col}:")
            print(f"  Projetos com setor: {non_empty_sectors.sum()}")
            print(f"  Projetos sem setor: {(~non_empty_sectors).sum()}")
            
            # Mostrar valores únicos
            unique_sectors = df[sector_col].dropna().unique()
            print(f"  Setores únicos: {len(unique_sectors)}")
            for sector in unique_sectors[:5]:
                count = df[df[sector_col] == sector].shape[0]
                print(f"    - {sector}: {count} projetos")
        
        if subsetor_col in df.columns:
            non_empty_subsetores = df[subsetor_col].notna() & (df[subsetor_col] != '') & (df[subsetor_col] != ' ')
            print(f"\n🏢 {subsetor_col}:")
            print(f"  Projetos com subsetor: {non_empty_subsetores.sum()}")
            print(f"  Projetos sem subsetor: {(~non_empty_subsetores).sum()}")
        
        # Verificar primeira linha
        print(f"\n📋 Primeira linha de dados:")
        first_row = df.iloc[0]
        for col in ['GUID', 'Nome_Projeto', sector_col, subsetor_col]:
            if col in df.columns:
                print(f"  {col}: {first_row[col]}")
        
    except Exception as e:
        print(f"❌ Erro ao carregar Excel: {e}")

if __name__ == "__main__":
    verify_excel_data()
