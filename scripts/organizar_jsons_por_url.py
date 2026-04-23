import os
import json
import shutil
from collections import defaultdict
import re

def extract_url_code_from_filename(filename):
    """Extrai o código URL do nome do arquivo."""
    match = re.search(r'_(\d+)_', filename)
    return match.group(1) if match else None

def load_url_titles():
    """Carrega os títulos das URLs do arquivo lista_de_urls.txt."""
    url_titles = {}
    try:
        with open('lista_de_urls.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if '->' in line:
                    parts = line.split('->')
                    if len(parts) == 2:
                        url_code = parts[0].strip()
                        title = parts[1].strip()
                        url_titles[url_code] = title
    except Exception as e:
        print(f"Erro ao carregar títulos: {e}")
    return url_titles

def main():
    print("🗂️ Organizando JSONs por URL...")
    
    # Carregar títulos das URLs
    url_titles = load_url_titles()
    print(f"📋 {len(url_titles)} títulos de URLs carregados")
    
    # Diretório de origem
    source_dir = "responses"
    if not os.path.exists(source_dir):
        print(f"❌ Diretório {source_dir} não encontrado!")
        return
    
    # Listar todos os arquivos JSON
    json_files = [f for f in os.listdir(source_dir) if f.endswith('.json')]
    print(f"📁 {len(json_files)} arquivos JSON encontrados")
    
    # Agrupar arquivos por URL
    url_groups = defaultdict(list)
    processed = 0
    
    for filename in json_files:
        url_code = extract_url_code_from_filename(filename)
        if url_code:
            url_groups[url_code].append(filename)
            processed += 1
    
    print(f"✅ {processed} arquivos processados")
    print(f"📊 {len(url_groups)} URLs únicas encontradas")
    
    # Criar diretórios e mover arquivos
    moved_files = 0
    for url_code, files in url_groups.items():
        # Obter título da URL
        title = url_titles.get(url_code, url_code)
        
        # Criar nome seguro para o diretório
        safe_title = title.replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '').replace(':', '').replace('-', '_').lower()
        dir_name = f"responses_{url_code}_{safe_title}"
        
        # Criar diretório
        target_dir = os.path.join(source_dir, dir_name)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            print(f"📁 Criado diretório: {dir_name}")
        
        # Mover arquivos
        for filename in files:
            source_path = os.path.join(source_dir, filename)
            target_path = os.path.join(target_dir, filename)
            
            try:
                shutil.move(source_path, target_path)
                moved_files += 1
            except Exception as e:
                print(f"❌ Erro ao mover {filename}: {e}")
    
    print(f"\n✅ Organização concluída!")
    print(f"📊 {moved_files} arquivos movidos")
    print(f"📁 {len(url_groups)} diretórios criados")
    
    # Estatísticas por diretório
    print(f"\n📈 Estatísticas por diretório:")
    for url_code, files in sorted(url_groups.items(), key=lambda x: x[0]):
        title = url_titles.get(url_code, url_code)
        safe_title = title.replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '').replace(':', '').replace('-', '_').lower()
        dir_name = f"responses_{url_code}_{safe_title}"
        print(f"   📁 {dir_name}: {len(files)} arquivos")

if __name__ == "__main__":
    main()
