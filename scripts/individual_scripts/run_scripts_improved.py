import os
import sys
import importlib.util
import time
import argparse

def run_script_directly(script_name, max_guids=None):
    """Executa um script individual diretamente, sem subprocess."""
    print(f"\n{'='*60}")
    print(f"EXECUTANDO: {script_name}")
    print(f"{'='*60}")
    
    try:
        # Carregar o script como módulo
        script_path = os.path.join(os.getcwd(), script_name)
        spec = importlib.util.spec_from_file_location(script_name.replace('.py', ''), script_path)
        module = importlib.util.module_from_spec(spec)
        
        # Adicionar o diretório atual ao path para garantir que os imports funcionem
        original_path = sys.path[:]
        sys.path.insert(0, os.getcwd())
        
        try:
            # Se foi especificado um limite de GUIDs, modificar o script para limitar
            if max_guids:
                # Patch temporário para limitar o número de GUIDs processados
                original_read_guids = None
                
                def limited_read_guids(file_path):
                    import csv
                    with open(file_path, 'r', encoding='utf-8') as file:
                        reader = csv.reader(file)
                        next(reader, None)  # Pular cabeçalho
                        guids = [row[0].strip() for row in reader if row and row[0].strip()]
                        return guids[:max_guids]  # Limitar ao número especificado
                
                # Substituir a função read_guids no módulo
                if hasattr(module, 'read_guids'):
                    original_read_guids = module.read_guids
                    module.read_guids = limited_read_guids
            
            # Executar o script
            spec.loader.exec_module(module)
            print(f"\n✅ Script {script_name} concluído com sucesso")
            return True
        except SystemExit as e:
            if e.code == 0:
                print(f"\n✅ Script {script_name} concluído com sucesso")
                return True
            else:
                print(f"\n❌ Script {script_name} falhou com código {e.code}")
                return False
        except KeyboardInterrupt:
            print(f"\n⚠️ Script {script_name} interrompido pelo usuário")
            return False
        except Exception as e:
            print(f"\n❌ Erro ao executar {script_name}: {str(e)}")
            return False
        finally:
            # Restaurar o path original
            sys.path = original_path
            
    except Exception as e:
        print(f"❌ Erro ao carregar {script_name}: {str(e)}")
        return False

def get_available_scripts():
    """Retorna a lista de scripts disponíveis."""
    all_files = os.listdir('.')
    scripts = [f for f in all_files if f.startswith('script_') and f.endswith('.py')]
    scripts.sort()
    return scripts

def main():
    """Executa scripts individuais em sequência."""
    parser = argparse.ArgumentParser(description='Executor de scripts individuais da API SIF')
    parser.add_argument('--script', help='Executar um script específico')
    parser.add_argument('--max-guids', type=int, help='Limitar o número de GUIDs por script (para teste)')
    parser.add_argument('--list', action='store_true', help='Listar scripts disponíveis')
    
    args = parser.parse_args()
    
    scripts = get_available_scripts()
    
    if args.list:
        print("Scripts disponíveis:")
        for i, script in enumerate(scripts, 1):
            print(f"  {i}. {script}")
        return
    
    if args.script:
        # Executar um script específico
        if args.script not in scripts:
            print(f"❌ Script '{args.script}' não encontrado.")
            print("Scripts disponíveis:")
            for script in scripts:
                print(f"  - {script}")
            return
        
        print("EXECUTOR DE SCRIPT INDIVIDUAL (MODO DIRETO)")
        print("=" * 60)
        print(f"Executando: {args.script}")
        if args.max_guids:
            print(f"Limitado a {args.max_guids} GUIDs (modo teste)")
        print("Pressione Ctrl+C para interromper.\n")
        
        success = run_script_directly(args.script, args.max_guids)
        
        if success:
            print(f"\n✅ Script concluído com sucesso!")
        else:
            print(f"\n❌ Script falhou!")
        return
    
    # Executar todos os scripts
    print("EXECUTOR DE SCRIPTS INDIVIDUAIS (MODO DIRETO)")
    print("=" * 60)
    print(f"Total de scripts a executar: {len(scripts)}")
    if args.max_guids:
        print(f"Cada script será limitado a {args.max_guids} GUIDs (modo teste)")
    print("\nOs scripts serão executados em sequência.")
    print("Pressione Ctrl+C para interromper a qualquer momento.\n")
    
    success_count = 0
    error_count = 0
    
    start_time = time.time()
    
    try:
        for i, script in enumerate(scripts, 1):
            print(f"\n[{i}/{len(scripts)}] Iniciando execução de {script}")
            
            if run_script_directly(script, args.max_guids):
                success_count += 1
            else:
                error_count += 1
            
            # Pausa entre scripts para não sobrecarregar
            if i < len(scripts):
                print(f"\nPausando 2 segundos antes do próximo script...")
                time.sleep(2)
                
    except KeyboardInterrupt:
        print("\n\nExecução interrompida pelo usuário.")
    except Exception as e:
        print(f"\nErro inesperado: {str(e)}")
    finally:
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "="*60)
        print("RESUMO DA EXECUÇÃO")
        print("="*60)
        print(f"Total de scripts: {len(scripts)}")
        print(f"Sucessos: {success_count}")
        print(f"Falhas: {error_count}")
        print(f"Duração total: {duration/60:.1f} minutos")
        
        if error_count > 0:
            print(f"\n⚠️  {error_count} script(s) falharam. Verifique os logs individuais.")
        
        # Listar scripts que falharam
        if error_count > 0:
            print("\nScripts que podem ter falhado:")
            for script in scripts:
                url_code = script.split('_')[1]
                log_file = f"../error_logs/execution_log_{url_code}.txt"
                if os.path.exists(log_file):
                    print(f"  - {script} (verifique: {log_file})")

if __name__ == "__main__":
    main()
