import pandas as pd
import numpy as np

def merge_duplicated_rows(df):
    """Consolida linhas duplicadas pelo GUID, mesclando os dados."""
    print("🔍 Analisando duplicatas por GUID...")
    
    # Contar duplicatas
    guid_counts = df['GUID'].value_counts()
    duplicated_guids = guid_counts[guid_counts > 1].index.tolist()
    
    print(f"📊 Encontrados {len(duplicated_guids)} GUIDs duplicados:")
    for guid in duplicated_guids[:10]:  # Mostrar apenas os 10 primeiros
        count = guid_counts[guid]
        print(f"   🔄 {guid[:8]}...: {count} ocorrências")
    
    if len(duplicated_guids) > 10:
        print(f"   ... e mais {len(duplicated_guids) - 10} GUIDs")
    
    # Função para mesclar dados de múltiplas linhas
    def merge_row_data(group):
        """Mescla dados de um grupo de linhas com o mesmo GUID."""
        merged = {}
        
        # Para cada coluna, mesclar os dados
        for col in group.columns:
            if col == 'GUID':
                merged[col] = group[col].iloc[0]  # GUID é o mesmo
            else:
                # Obter todos os valores não vazios/não nulos
                values = group[col].dropna().drop_duplicates()
                
                if len(values) == 0:
                    merged[col] = np.nan
                elif len(values) == 1:
                    merged[col] = values.iloc[0]
                else:
                    # Se tiver múltiplos valores diferentes, concatenar
                    non_empty_values = [str(v) for v in values if str(v).strip() and str(v) != 'nan']
                    if non_empty_values:
                        # Remover duplicatas mantendo a ordem
                        unique_values = list(dict.fromkeys(non_empty_values))
                        if len(unique_values) == 1:
                            merged[col] = unique_values[0]
                        else:
                            merged[col] = " | ".join(unique_values)
                    else:
                        merged[col] = np.nan
        
        return pd.Series(merged)
    
    # Agrupar por GUID e mesclar
    print("🔄 Mesclando linhas duplicadas...")
    df_merged = df.groupby('GUID', as_index=False).apply(merge_row_data)
    
    return df_merged

def main():
    print("🔍 Iniciando remoção de duplicatas...")
    
    # Carregar planilha
    input_file = "consolidado_projetos_completo_corrigido.xlsx"
    if not pd.io.common.file_exists(input_file):
        print(f"❌ Arquivo {input_file} não encontrado!")
        return
    
    print(f"📊 Carregando planilha: {input_file}")
    df = pd.read_excel(input_file)
    
    print(f"📋 Planilha original: {len(df)} linhas e {len(df.columns)} colunas")
    
    # Verificar duplicatas
    total_guids = len(df['GUID'].unique())
    total_rows = len(df)
    duplicates_count = total_rows - total_guids
    
    print(f"🎯 GUIDs únicos: {total_guids}")
    print(f"📊 Total de linhas: {total_rows}")
    print(f"🔄 Linhas duplicadas: {duplicates_count}")
    
    if duplicates_count == 0:
        print("✅ Nenhuma duplicata encontrada!")
        return
    
    # Mesclar duplicatas
    df_merged = merge_duplicated_rows(df)
    
    print(f"\n✅ Mesclagem concluída!")
    print(f"📊 Planilha final: {len(df_merged)} linhas e {len(df_merged.columns)} colunas")
    print(f"🎯 GUIDs únicos: {len(df_merged['GUID'].unique())}")
    print(f"📉 Redução de {total_rows - len(df_merged)} linhas")
    
    # Salvar planilha consolidada
    output_file = "consolidado_projetos_final.xlsx"
    print(f"\n💾 Salvando planilha consolidada: {output_file}")
    
    try:
        df_merged.to_excel(output_file, index=False, engine='openpyxl')
        print(f"✅ Planilha salva com sucesso!")
        
        # Estatísticas finais
        print(f"\n📈 Estatísticas finais:")
        print(f"   📋 Linhas: {len(df_merged)}")
        print(f"   🎯 GUIDs únicos: {len(df_merged['GUID'].unique())}")
        print(f"   📊 Colunas: {len(df_merged.columns)}")
        
        # Verificar se ainda há duplicatas
        remaining_guids = len(df_merged['GUID'].unique())
        if remaining_guids == len(df_merged):
            print("   ✅ Nenhuma duplicata restante!")
        else:
            print(f"   ⚠️ Ainda há {len(df_merged) - remaining_guids} duplicatas")
        
        # Contar valores preenchidos nas novas colunas
        new_columns = [
            'Nome do Projeto', 'Descrição', 'Setor', 'Subsetor', 'Localização',
            'Coordenada X', 'Coordenada Y', 'Estado', 'Cidade', 'Endereço',
            'Status Atual', 'Tipo de Projeto', 'É PPP', 'É Não Solicitado',
            'Custo Estimado (BRL)', 'Custo Estimado (Original)', 'Moeda Original',
            'Organização Responsável', 'Data de Criação', 'Data de Modificação',
            'Data Prevista de Conclusão', 'Percentual de Conclusão',
            'Framework Legal', 'Suporte Técnico', 'Territórios'
        ]
        
        print(f"\n📋 Valores preenchidos nas novas colunas:")
        for col in new_columns:
            if col in df_merged.columns:
                filled_count = df_merged[col].astype(str).str.strip().ne('').sum()
                print(f"   📋 {col}: {filled_count} valores")
        
        print(f"\n🎉 Planilha final salva em: {output_file}")
        
    except Exception as e:
        print(f"❌ Erro ao salvar planilha: {e}")
        return

if __name__ == "__main__":
    main()
