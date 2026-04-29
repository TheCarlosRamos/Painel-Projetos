# Painel-Projetos

## 📋 Descrição

Painel de visualização de projetos do Programa de Parcerias e Investimentos (PPI) do Governo Federal. Este projeto consiste em uma aplicação web para exibir informações detalhadas sobre projetos de infraestrutura em andamento no Brasil.

## 🏗️ Estrutura do Projeto

```
Painel-Projetos/
├── page/                           # Aplicação web principal
│   ├── ppi_landing_site_v2/       # Site de visualização
│   │   ├── data/                  # Dados dos projetos
│   │   │   └── projects_full.json # Base de dados principal
│   │   ├── index.html             # Página principal
│   │   └── assets/                # CSS, JS e imagens
│   └── ppi_landing_site_v2.pdf    # Versão PDF
├── scripts/                        # Scripts de processamento de dados
│   ├── api_automation_urls.py     # Script de referência da API
│   ├── project_info_api.py        # Coleta de informações básicas
│   ├── consolidate_project_data.py # Consolidação de dados
│   ├── update_all_complete.py     # Script unificado principal
│   ├── projects.csv               # Lista de todos os projetos (278 GUIDs)
│   ├── project_guids.csv          # Lista reduzida (3 GUIDs)
│   └── project_info_responses/    # Respostas da API
├── mapas/                         # Arquivos de mapas
├── Qcode/                         # Notebooks e análises
└── README.md                      # Este arquivo
```

## 🚀 Funcionalidades

### Aplicação Web
- **Visualização interativa** de projetos de infraestrutura
- **Filtros** por setor, subsetor, organização e status
- **Mapas interativos** com localização dos projetos
- **Timeline** de status dos projetos
- **Cards detalhados** com informações completas

### Scripts de Processamento
- **Coleta automática** de dados da API SIF-Source
- **Processamento paralelo** para otimização de performance
- **Consolidação** de múltiplas fontes de dados
- **Atualização automática** do `projects_full.json`

## 🛠️ Tecnologias Utilizadas

### Frontend
- **HTML5** e **CSS3**
- **JavaScript** vanilla
- **Bootstrap** para UI responsiva
- **Chart.js** para gráficos
- **Leaflet** para mapas interativos

### Backend/Scripts
- **Python 3.8+**
- **Requests** para chamadas HTTP
- **Pandas** para manipulação de dados
- **JSON** para armazenamento de dados

## 📦 Instalação e Configuração

### Pré-requisitos
```bash
# Python 3.8+
python --version

# Instalar dependências
pip install requests pandas
```

### Configuração da API
As credenciais da API estão configuradas nos scripts:
```python
AUTH = ('adminppi.source@presidencia.gov.br', 'PPI#source147')
```

## 🔄 Como Usar

### 1. Atualizar Dados dos Projetos

Para atualizar todos os projetos (278 projetos):
```bash
cd scripts
python update_all_complete.py
```

Este script:
- Lê todos os GUIDs do `projects.csv`
- Faz chamadas à API em paralelo
- Consolida os dados
- Atualiza o `projects_full.json`

### 2. Executar Aplicação Web Local

```bash
# Servir os arquivos estáticos
cd page/ppi_landing_site_v2
python -m http.server 8000
```

Acesse: `http://localhost:8000`

### 3. Deploy

O projeto está configurado para deploy na Vercel através do `vercel.json`.

## 📊 Fonte de Dados

### API Principal
- **URL Base**: `https://api.sif-source.org`
- **Endpoint Projects**: `/projects`
- **Endpoint Questions**: `/projects/{guid}/questions/{question_id}`

### Estrutura dos Dados
```json
{
  "guid": "uuid",
  "nome_projeto": "string",
  "descricao_curta": "string",
  "setor": "string",
  "subsetor": "string",
  "organizacao": "string",
  "localizacoes": "string",
  "latitude": number,
  "longitude": number,
  "status_atual_do_projeto": "string",
  "questoes_chaves": "string",
  "status_dos_estudos": "string",
  "status_consulta_publica": "string",
  "status_do_tcu": "string",
  "status_do_edital": "string",
  "status_do_leilao": "string",
  "status_do_contrato": "string"
}
```

## 🔧 Scripts Detalhados

### update_all_complete.py
Script unificado que combina:
- Coleta de informações básicas dos projetos
- Coleta de dados específicos por questão
- Consolidação dos dados
- Atualização do arquivo final

### api_automation_urls.py
Script de referência com:
- Autenticação funcional
- Processamento em paralelo
- Tratamento de erros

### project_info_api.py
Script para coletar informações básicas:
- Dados gerais dos projetos
- Coordenadas GPS
- Informações organizacionais

### consolidate_project_data.py
Script para consolidar múltiplas fontes:
- Merge de dados da API
- Formatação para aplicação
- Validação de estrutura

## 🚨 Considerações Importantes

### Segurança
- As credenciais da API estão hardcoded nos scripts
- Recomenda-se mover para variáveis de ambiente
- Considerar uso de `.env` file

### Performance
- Processamento paralelo com `ThreadPoolExecutor`
- Timeout configurado para chamadas API
- Tratamento de erros 500 da API

### Manutenção
- Scripts individuais foram removidos para simplificação
- Apenas o script unificado `update_all_complete.py` é mantido
- Dados consolidados em `projects_full.json`

## 📈 Estatísticas Atuais

- **Total de projetos**: 278
- **Setores**: Transport, Energy, Urban Services, Water & Waste
- **Organizações**: SEPPI, SIEC, SIPE
- **Status**: Multiple (Completed, Not Started, Scheduled, etc.)

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📝 Licença

Este projeto é propriedade do Governo Federal do Brasil.

## 📞 Contato

- **Repositório**: https://github.com/TheCarlosRamos/Painel-Projetos
- **Email**: adminppi.source@presidencia.gov.br

---

**Última atualização**: Abril 2026
