import pandas as pd
import csv

def main():
    print("🔍 Verificando GUIDs na planilha vs projects.csv...")
    
    # Carregar GUIDs do projects.csv
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
    
    # Carregar planilha
    df = pd.read_excel("consolidado_projetos_completo_corrigido.xlsx")
    planilha_guids = set(df['GUID'].astype(str))
    print(f"📊 {len(planilha_guids)} GUIDs na planilha")
    
    # Comparar
    only_in_planilha = planilha_guids - projects_guids
    only_in_projects = projects_guids - planilha_guids
    common = planilha_guids & projects_guids
    
    print(f"\n📈 Comparação:")
    print(f"   ✅ Apenas em comum: {len(common)} GUIDs")
    print(f"   ⚠️ Apenas na planilha: {len(only_in_planilha)} GUIDs")
    print(f"   ⚠️ Apenas no projects.csv: {len(only_in_projects)} GUIDs")
    
    if only_in_planilha:
        print(f"\n📋 GUIDs que estão na planilha mas não no projects.csv:")
        for guid in sorted(list(only_in_planilha))[:10]:
            print(f"   🔄 {guid}")
        if len(only_in_planilha) > 10:
            print(f"   ... e mais {len(only_in_planilha) - 10}")
    
    if only_in_projects:
        print(f"\n📋 GUIDs que estão no projects.csv mas não na planilha:")
        for guid in sorted(list(only_in_projects))[:10]:
            print(f"   🔄 {guid}")
        if len(only_in_projects) > 10:
            print(f"   ... e mais {len(only_in_projects) - 10}")
    
    # Criar planilha apenas com GUIDs válidos
    if only_in_planilha:
        print(f"\n🔄 Criando planilha apenas com GUIDs válidos...")
        df_valid = df[df['GUID'].isin(projects_guids)].copy()
        
        output_file = "consolidado_projetos_validos.xlsx"
        df_valid.to_excel(output_file, index=False, engine='openpyxl')
        
        print(f"✅ Planilha válida salva: {output_file}")
        print(f"📊 {len(df_valid)} linhas (apenas GUIDs do projects.csv)")
        print(f"🎯 {len(df_valid['GUID'].unique())} GUIDs únicos")

if __name__ == "__main__":
    main()
