# Scripts Individuais de Automação

Este diretório contém scripts individuais para cada URL da API SIF.

## Scripts Criados

- script_2000720_subsecretaria.py
- script_2000726_status_atual_do_projeto.py
- script_2000727_questões_chaves.py
- script_2000728_proximas_etapas_do_projeto.py
- script_2001216_2001216.py
- script_2001218_status_dos_estudos.py
- script_2001221_status_consulta_publica.py
- script_2001224_status_do_tcu.py
- script_2001226_status_do_edital.py
- script_2001229_status_do_leilao.py
- script_2001232_descricao_do_projeto.py

## Como Usar

### Executar um script específico:
```bash
python individual_scripts/script_2000720_subsecretaria.py
```

### Executar todos os scripts em sequência:
```bash
python individual_scripts/run_all_scripts.py
```

## Estrutura de Saída

- **Respostas**: Cada script cria seu próprio diretório `responses_{url_code}`
- **Logs**: Logs de erro em `error_logs/execution_log_{url_code}.txt`
- **Formato dos arquivos**: `response_{guid}_{url_code}_{titulo}.json`

## Exemplos de Nomes de Arquivos

- `response_ecd74fa2_d64d_42ca_bb9a_a6dbe4dbfef5_2000720_subsecretaria.json`
- `response_ecd74fa2_d64d_42ca_bb9a_a6dbe4dbfef5_2000726_status_atual_do_projeto.json`

## URLs Disponíveis

- 2000720: subsecretaria
- 2000726: status atual do projeto
- 2000727: questões chaves
- 2000728: proximas etapas do projeto
- 2001216: 2001216
- 2001218: status dos estudos
- 2001221: status consulta publica
- 2001224: status do TCU
- 2001226: status do edital
- 2001229: status do leilão
- 2001232: descrição do projeto
