import pandas as pd
import os

def csv_to_excel():
    """Converte o arquivo CSV consolidado para Excel."""
    
    # Caminhos dos arquivos
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(base_dir, '..', 'projetos_consolidado.csv')
    excel_file = os.path.join(base_dir, '..', 'projetos_consolidado.xlsx')
    
    try:
        # Ler o arquivo CSV
        print(f"Lendo arquivo CSV: {csv_file}")
        df = pd.read_csv(csv_file, encoding='utf-8-sig')
        
        print(f"Total de linhas: {len(df)}")
        print(f"Total de colunas: {len(df.columns)}")
        print(f"Colunas: {list(df.columns)}")
        
        # Criar arquivo Excel com formatação
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Projetos Consolidados', index=False)
            
            # Ajustar largura das colunas
            worksheet = writer.sheets['Projetos Consolidados']
            
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                adjusted_width = min(max_length + 2, 50)  # Limitar largura máxima
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"✅ Arquivo Excel salvo com sucesso: {excel_file}")
        print(f"📊 Tamanho do arquivo: {os.path.getsize(excel_file) / 1024:.1f} KB")
        
        # Estatísticas finais
        print("\n📈 Estatísticas do arquivo Excel:")
        print(f"   - Total de projetos: {len(df)}")
        print(f"   - Total de colunas: {len(df.columns)}")
        
        # Contar valores não nulos por coluna
        print("\n📋 Preenchimento por coluna:")
        for col in df.columns:
            non_null = df[col].notna().sum()
            percentage = (non_null / len(df)) * 100
            print(f"   - {col}: {non_null}/{len(df)} ({percentage:.1f}%)")
        
        return excel_file
        
    except Exception as e:
        print(f"❌ Erro ao converter CSV para Excel: {e}")
        return None

if __name__ == "__main__":
    csv_to_excel()
