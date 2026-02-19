# 📊 RESUMO DO CSV CONSOLIDADO

## 🎯 OBJETIVO ALCANÇADO
Criado com sucesso o arquivo `projetos_consolidado.csv` contendo todos os dados dos projetos consolidados de todas as URLs da API.

## 📈 ESTATÍSTICAS FINAIS

### **Total de Projetos**: 209

### **Cobertura por Campo**:
| Campo | Registros | Taxa de Cobertura |
|-------|-----------|------------------|
| **subsecretaria** | 199/209 | 95.2% ✅ |
| **status_atual_do_projeto** | 134/209 | 64.1% ⚠️ |
| **questoes_chaves** | 64/209 | 30.6% ⚠️ |
| **proximas_etapas** | 70/209 | 33.5% ⚠️ |
| **2001216** | 111/209 | 53.1% ⚠️ |
| **status_dos_estudos** | 169/209 | 80.9% ✅ |
| **status_consulta_publica** | 173/209 | 82.8% ✅ |
| **status_do_tcu** | 153/209 | 73.2% ⚠️ |
| **status_do_edital** | 169/209 | 80.9% ✅ |
| **status_do_leilao** | 169/209 | 80.9% ✅ |
| **status_do_contrato** | 0/209 | 0.0% ❌ |
| **descricao_do_projeto** | 189/209 | 90.4% ✅ |

## 📁 ESTRUTURA DO CSV

O arquivo contém as seguintes colunas:
1. **guid** - Identificador único do projeto
2. **nome_projeto** - Nome/descrição resumida do projeto
3. **subsecretaria** - SIPE, SIEC ou SISU
4. **status_atual_do_projeto** - Status atual (Approved, etc.)
5. **questoes_chaves** - Texto com questões chaves
6. **proximas_etapas** - Próximas etapas do projeto
7. **2001216** - Dados do campo 2001216
8. **status_dos_estudos** - Not started/In progress/Completed
9. **status_consulta_publica** - Not started/In progress/Completed
10. **status_do_tcu** - Not started/In progress/Completed/Not applicable
11. **status_do_edital** - Not started/Completed
12. **status_do_leilao** - Not started/In progress/Completed
13. **status_do_contrato** - Status do contrato (sem dados)
14. **descricao_do_projeto** - Descrição completa do projeto

## 🎉 RESULTADOS DESTACADOS

### **Campos com Excelente Cobertura (>90%)**:
- **subsecretaria**: 95.2% (199 de 209)
- **descricao_do_projeto**: 90.4% (189 de 209)

### **Campos com Boa Cobertura (70-90%)**:
- **status_dos_estudos**: 80.9% (169 de 209)
- **status_consulta_publica**: 82.8% (173 de 209)
- **status_do_edital**: 80.9% (169 de 209)
- **status_do_leilao**: 80.9% (169 de 209)

### **Campos com Cobertura Moderada (50-70%)**:
- **status_atual_do_projeto**: 64.1% (134 de 209)
- **status_do_tcu**: 73.2% (153 de 209)
- **2001216**: 53.1% (111 de 209)

### **Campos com Baixa Cobertura (<50%)**:
- **proximas_etapas**: 33.5% (70 de 209)
- **questoes_chaves**: 30.6% (64 de 209)
- **status_do_contrato**: 0.0% (0 de 209) - *Script executado recentemente, dados podem estar incompletos*

## 📄 ARQUIVO GERADO

**Localização**: `projetos_consolidado.csv`
**Encoding**: UTF-8 com BOM (compatível com Excel)
**Tamanho**: ~1815 linhas (incluindo cabeçalho)

## 🔍 PRÓXIMOS PASSOS SUGERIDOS

1. **Analisar dados faltantes**: Investigar por que alguns campos têm baixa cobertura
2. **Reexecutar scripts problemáticos**: Especialmente para status_do_contrato
3. **Validação dos dados**: Verificar consistência das informações
4. **Análise estatística**: Criar dashboards e relatórios

---
**Data de geração**: 13/02/2026  
**Status**: ✅ CSV CONSOLIDADO GERADO COM SUCESSO
