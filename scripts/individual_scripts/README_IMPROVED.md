# Scripts Individuais de Automação - Versão Melhorada

Este diretório contém scripts individuais para cada URL da API SIF, com um executor robusto que evita problemas de codificação.

## Scripts Criados

1. `script_2000720_subsecretaria.py` - Subsecretaria responsável
2. `script_2000726_status_atual_do_projeto.py` - Status atual do projeto
3. `script_2000727_questões_chaves.py` - Questões chaves
4. `script_2000728_proximas_etapas_do_projeto.py` - Próximas etapas do projeto
5. `script_2001216_2001216.py` - URL 2001216
6. `script_2001218_status_dos_estudos.py` - Status dos estudos
7. `script_2001221_status_consulta_publica.py` - Status consulta pública
8. `script_2001224_status_do_tcu.py` - Status do TCU
9. `script_2001226_status_do_edital.py` - Status do edital
10. `script_2001229_status_do_leilao.py` - Status do leilão
11. `script_2001232_descricao_do_projeto.py` - Descrição do projeto

## Executor Melhorado

Use `run_scripts_improved.py` para executar os scripts de forma segura e flexível.

### Opções Disponíveis

#### 1. Listar todos os scripts:
```bash
python run_scripts_improved.py --list
```

#### 2. Executar um script específico:
```bash
python run_scripts_improved.py --script script_2000720_subsecretaria.py
```

#### 3. Executar um script específico com limite de GUIDs (para teste):
```bash
python run_scripts_improved.py --script script_2000720_subsecretaria.py --max-guids 5
```

#### 4. Executar todos os scripts:
```bash
python run_scripts_improved.py
```

#### 5. Executar todos os scripts com limite de GUIDs (para teste):
```bash
python run_scripts_improved.py --max-guids 10
```

## Vantagens do Executor Melhorado

- ✅ **Sem problemas de codificação**: Executa os scripts diretamente, sem subprocess
- ✅ **Modo de teste**: Permite limitar o número de GUIDs para testes rápidos
- ✅ **Execução seletiva**: Permite executar apenas scripts específicos
- ✅ **Recuperação automática**: Continua executando mesmo se um script falhar
- ✅ **Logs detalhados**: Mantém todos os logs individuais

## Estrutura de Saída

### Respostas
Cada script cria seu próprio diretório:
- `responses_2000720/` - Dados da subsecretaria
- `responses_2000726/` - Dados do status atual do projeto
- `responses_2000727/` - Dados das questões chaves
- ... e assim por diante

### Logs
Logs de erro em `error_logs/`:
- `execution_log_2000720.txt`
- `execution_log_2000726.txt`
- ... etc

### Formato dos Arquivos
```
response_{guid}_{url_code}_{titulo}.json
```

Exemplos:
- `response_ecd74fa2_d64d_42ca_bb9a_a6dbe4dbfef5_2000720_subsecretaria.json`
- `response_ecd74fa2_d64d_42ca_bb9a_a6dbe4dbfef5_2000726_status_atual_do_projeto.json`

## Exemplos de Uso

### Para testar rapidamente um script:
```bash
# Testar com apenas 3 GUIDs
python run_scripts_improved.py --script script_2000720_subsecretaria.py --max-guids 3
```

### Para executar todos os scripts em modo de teste:
```bash
# Executar todos com 10 GUIDs cada
python run_scripts_improved.py --max-guids 10
```

### Para executar produção completa:
```bash
# Executar todos os scripts com todos os GUIDs
python run_scripts_improved.py
```

## Resolução de Problemas

### Se um script falhar:
1. Verifique o log correspondente em `error_logs/execution_log_{url_code}.txt`
2. Execute o script individualmente para depurar:
   ```bash
   python run_scripts_improved.py --script script_problematico.py --max-guids 1
   ```

### Se houver problemas de codificação:
O executor melhorado já resolve esses problemas executando os scripts diretamente.

## URLs Disponíveis

| Código | Título |
|--------|--------|
| 2000720 | subsecretaria |
| 2000726 | status atual do projeto |
| 2000727 | questões chaves |
| 2000728 | proximas etapas do projeto |
| 2001216 | 2001216 |
| 2001218 | status dos estudos |
| 2001221 | status consulta publica |
| 2001224 | status do TCU |
| 2001226 | status do edital |
| 2001229 | status do leilão |
| 2001232 | descrição do projeto |

## Estatísticas

- **Total de scripts**: 11
- **Total de GUIDs**: 211
- **Total de requisições (completo)**: 2.321
- **Tempo estimado (completo)**: ~40-50 minutos
