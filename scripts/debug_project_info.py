import json
import os

def extract_guid_from_filename(filename):
    """Extrai GUID do nome do arquivo JSON."""
    parts = filename.replace('.json', '').split('_')
    if len(parts) >= 6:
        return f"{parts[1]}-{parts[2]}-{parts[3]}-{parts[4]}-{parts[5]}"
    return None

def debug_project_info():
    """Debug para verificar os dados do project_info."""
    
    project_info_dir = "responses_project_info"
    
    print("=== DEBUG: Verificando arquivos project_info ===")
    print(f"Diretório: {project_info_dir}")
    print(f"Existe: {os.path.exists(project_info_dir)}")
    
    if not os.path.exists(project_info_dir):
        print("Diretório não existe!")
        return
    
    files = [f for f in os.listdir(project_info_dir) if f.endswith('.json')]
    print(f"Total de arquivos JSON: {len(files)}")
    
    # Verificar primeiros 5 arquivos
    for i, filename in enumerate(files[:5]):
        print(f"\n--- Arquivo {i+1}: {filename} ---")
        
        guid = extract_guid_from_filename(filename)
        print(f"GUID extraído: {guid}")
        
        filepath = os.path.join(project_info_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"Chaves disponíveis: {list(data.keys())}")
            
            # Verificar nome do projeto
            if 'projectName' in data:
                print(f"projectName: {data['projectName']}")
            elif 'name' in data:
                print(f"name: {data['name']}")
            else:
                print("Nenhum campo de nome encontrado!")
            
            # Verificar setor
            if 'Sector' in data:
                print(f"Sector: {data['Sector']}")
            else:
                print("Campo Sector não encontrado!")
            
            # Verificar subsetor
            if 'SubSector' in data:
                print(f"SubSector: {data['SubSector']}")
            else:
                print("Campo SubSector não encontrado!")
                
        except Exception as e:
            print(f"Erro ao ler arquivo: {e}")
    
    # Verificar se GUIDs correspondem
    print(f"\n=== Verificando correspondência de GUIDs ===")
    
    # Pegar alguns GUIDs dos responses
    responses_dir = "responses"
    response_files = [f for f in os.listdir(responses_dir) if f.endswith('.json') and '2000720' in f][:10]
    
    print(f"GUIDs encontrados em responses:")
    for filename in response_files:
        guid = extract_guid_from_filename(filename)
        print(f"  {guid}")
        
        # Verificar se existe no project_info
        project_info_files = [f for f in files if guid.replace('-', '_') in f]
        if project_info_files:
            print(f"    ✓ Encontrado: {project_info_files[0]}")
        else:
            print(f"    ✗ Não encontrado no project_info")

if __name__ == "__main__":
    debug_project_info()
