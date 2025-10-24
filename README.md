# 🏛️ Consulta de Licitações PNCP

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-senior-brightgreen.svg)](https://github.com/jhonne/PNCP)
[![UV](https://img.shields.io/badge/package%20manager-uv-blueviolet.svg)](https://github.com/astral-sh/uv)

Aplicação otimizada para consultar licitações publicadas no Portal Nacional de Compras Públicas (PNCP), com busca automática de pregões eletrônicos por estado e data de publicação.

> ⚡ **GERENCIAMENTO COM UV**: Este projeto utiliza `uv` para gerenciamento rápido de dependências e execução Python.

## 📋 Sobre

Esta aplicação em Python consulta a API oficial do PNCP para buscar pregões eletrônicos, filtrá-los por palavras-chave de interesse e exportar os resultados para Excel. Desenvolvida para atender à **Lei de Licitações 14.133/2021**, que exige centralização das informações de contratações públicas.

**Características da implementação:**

- ✅ Padrões Senior Python 3.11
- ✅ Type hints completos
- ✅ Docstrings Google Style
- ✅ Logging estruturado
- ✅ Requisições paralelas otimizadas
- ✅ Gerenciamento com UV

## ✨ Funcionalidades

- 🔍 **Busca Automática**: Consulta pregões eletrônicos em múltiplos estados simultaneamente
- ⚡ **Requisições Paralelas**: Até 10x mais rápido com processamento concorrente
- 🎯 **Filtragem Inteligente**: Filtra licitações por palavras-chave no objeto
- 📊 **Exportação Excel**: Salva resultados em arquivo Excel com 2 abas (completo e filtrado)
- 📅 **Datas Dinâmicas**: Busca automática dos últimos 7 dias
- 🔄 **Retry Automático**: Retenta requisições falhas automaticamente
- 📈 **Barra de Progresso**: Acompanhe o progresso em tempo real
- 🛡️ **Tratamento de Erros**: Timeout e validações robustas

## 🚀 Performance

### Otimizações Implementadas

| Recurso | Descrição | Benefício |
|---------|-----------|-----------|
| **ThreadPoolExecutor** | Requisições HTTP paralelas (até 10 simultâneas) | ~10x mais rápido |
| **Session Pooling** | Reutilização de conexões HTTP | Reduz overhead |
| **Retry com Backoff** | 3 tentativas automáticas (0.5s, 1s, 2s) | Maior confiabilidade |
| **Timeout Inteligente** | Limite de 10s por requisição | Evita travamentos |
| **Barra de Progresso** | Feedback visual em tempo real | Melhor UX |

### Tempo de Execução

- **Antes**: ~5-8 minutos (150 requisições sequenciais)
- **Agora**: ~30-60 segundos (10 requisições paralelas)

## 📦 Instalação

### Método 1: Usando UV (Recomendado) ⚡

O UV é 10-100x mais rápido que pip e gerencia o ambiente automaticamente:

```powershell
# Instalar UV (se ainda não tiver)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Clonar repositório
git clone https://github.com/jhonne/PNCP.git
cd PNCP

# UV cria ambiente e instala dependências automaticamente
uv sync
```

### Método 2: Usando pip tradicional

```powershell
# Clone o repositório
git clone https://github.com/jhonne/PNCP.git
cd PNCP

# Crie ambiente virtual
python -m venv .venv
.venv\Scripts\Activate.ps1

# Instale dependências
pip install -r requirements.txt
```

### 📚 Dependências

- `pandas` - Manipulação de dados e DataFrames
- `requests` - Requisições HTTP para API
- `python-dateutil` - Manipulação de datas
- `openpyxl` - Exportação para Excel
- `urllib3` - Retry e pooling de conexões HTTP

## 🎯 Como Usar

### ⚡ Execução com UV (Recomendado)

```powershell
# Executar script principal
uv run python consulta_publicacoes_pncp.py

# Verificar versão Python
uv run python --version
```

### 🐍 Execução Tradicional

```powershell
# Ativar ambiente virtual
.venv\Scripts\Activate.ps1

# Executar script
python consulta_publicacoes_pncp.py
```

### 📝 Sobre o Script Único

O projeto agora possui **uma única versão otimizada**: `consulta_publicacoes_pncp.py`

**Características:**

- ✅ Padrões Senior Python 3.11
- ✅ Type hints completos
- ✅ Docstrings Google Style
- ✅ Logging estruturado
- ✅ Validação de inputs robusta
- ✅ Funções especializadas com responsabilidade única
- ✅ API pública para uso programático
- ✅ Dataclasses para configuração

### ⚙️ Configuração Personalizada

#### Opção 1: Editar constantes no script

Edite a seção `if __name__ == "__main__"` em `consulta_publicacoes_pncp.py`:

```python
if __name__ == "__main__":
    # Configuração personalizada
    DIAS_BUSCA = 7  # Alterar para 30, 60, 90 dias
    ESTADOS_CONSULTA = ESTADOS_PADRAO  # Ou ['PE', 'BA', 'RN']
    PALAVRAS_FILTRO = ['alimentício', 'alimento']  # Suas palavras-chave
    DIRETORIO_SAIDA = Path.cwd()  # Ou Path('C:/resultados')
```

#### Opção 2: Uso programático (importar como módulo)

```python
from pathlib import Path
from consulta_publicacoes_pncp import executar_consulta_licitacoes

# Busca customizada
df_completo, df_filtrado, arquivo = executar_consulta_licitacoes(
    dias_anteriores=30,
    estados=['PE', 'BA', 'CE'],
    palavras_chave=['notebook', 'computador'],
    diretorio_saida=Path('C:/meus_resultados')
)

print(f"Encontradas {len(df_completo)} licitações")
print(f"Filtradas {len(df_filtrado)} licitações")
print(f"Arquivo salvo em: {arquivo}")
```

#### Opção 3: Ajustar constantes globais

No topo do script, você pode modificar:

```python
# Configurações de performance
MAX_WORKERS: Final[int] = 10  # Requisições paralelas
TIMEOUT_SEGUNDOS: Final[int] = 10  # Timeout por requisição

# Configurações de busca
TAMANHO_PAGINA: Final[int] = 50  # Registros por página
NUMERO_PAGINAS: Final[int] = 10  # Páginas por estado

# Modalidade padrão
MODALIDADE_PREGAO_ELETRONICO: Final[int] = 6
```

### Saída

O arquivo Excel gerado (`licitacoes_DD_MM_YYYY.xlsx`) contém:

- **Aba "Todos"**: Todas as licitações encontradas
- **Aba "Filtrados"**: Apenas licitações com palavras-chave no objeto

### Colunas do Excel

| Coluna | Descrição |
|--------|-----------|
| sequencial | ID sequencial da compra |
| orgao | Razão social do órgão |
| uf | Estado |
| inclusao | Data de inclusão |
| amparo_legal | Descrição do amparo legal |
| abertura | Data de abertura das propostas |
| encerramento | Data de encerramento |
| n_processo | Número do processo |
| objeto | Descrição do objeto da licitação |
| link | Link para o sistema de origem |
| valor_estimado | Valor total estimado |
| valor_homologado | Valor total homologado |
| disputa | Modo de disputa |
| plataforma | Nome do usuário/plataforma |
| situacao | Situação da compra |
| srp | Sistema de Registro de Preços (True/False) |

## 📊 Abrangência

### Estados Consultados

- **Nordeste**: PE, PB, AL, SE, BA, RN, CE, PI, MA (9 estados)
- **Norte**: TO, PA, AP, RR, AM, AC (6 estados)
- **Total**: 15 estados × 10 páginas = **150 consultas paralelas**

### Modalidades Suportadas

- **6**: Pregão Eletrônico (padrão)
- Outras modalidades podem ser configuradas

## 🔧 Estrutura do Projeto

```
PNCP/
├── 📄 consulta_publicacoes_pncp.py                   # Script principal (refatorado) ⭐
├── 📋 requirements.txt                               # Dependências Python
├── 📘 README.md                                      # Documentação principal
├── 🚀 QUICKSTART.md                                  # Guia rápido de início
├── 📁 docs/
│   └── 📖 manual-api-compras.md                      # Manual completo da API PNCP
├── 📁 pdf/                                           # Documentos em PDF
├── 📁 vendor/
│   └── 📦 awesome-copilot/                           # Recursos do GitHub Copilot
├── 📁 .github/
│   └── 📝 copilot-instructions.md                    # Instruções para o Copilot
├── 📊 licitacoes_*.xlsx                              # Arquivos Excel gerados
└── 🔒 .gitignore                                     # Arquivos ignorados no Git
```

### 📂 Arquivos Principais

- **`consulta_publicacoes_pncp.py`**: Script principal com código refatorado
- **`requirements.txt`**: Lista de dependências do projeto
- **`README.md`**: Documentação completa (este arquivo)
- **`QUICKSTART.md`**: Guia rápido para começar
- **`docs/manual-api-compras.md`**: Manual detalhado da API PNCP
- **`.github/copilot-instructions.md`**: Instruções para desenvolvimento com Copilot

## 🌐 API Utilizada

**Portal Nacional de Compras Públicas (PNCP)**

- Endpoint: `https://dadosabertos.compras.gov.br/modulo-contratacoes/1_consultarContratacoes_PNCP_14133`
- Versão: API v3
- Documentação: Lei 14.133/2021

### Parâmetros da API

- `dataPublicacaoPncpInicial`: Data inicial (YYYY-MM-DD)
- `dataPublicacaoPncpFinal`: Data final (YYYY-MM-DD)
- `codigoModalidade`: Código da modalidade (6 = pregão eletrônico)
- `unidadeOrgaoUfSigla`: Sigla do estado (PE, PB, etc.)
- `tamanhoPagina`: Registros por página (50)
- `pagina`: Número da página (1-10)

## 🐛 Solução de Problemas

### Arquivo Excel vazio ou sem dados?

1. ✅ Verifique se há licitações no período selecionado
2. ✅ Aumente o intervalo de datas (ex: últimos 30 dias)
3. ✅ Teste outros estados
4. ✅ Verifique conectividade com a API

### Requisições muito lentas?

1. ✅ Aumente `max_workers` (linha 124) para 15-20
2. ✅ Verifique sua conexão de internet
3. ✅ API pode estar sobrecarregada em horários de pico

### Erros de timeout?

1. ✅ Aumente o timeout (linha 109): `timeout=20`
2. ✅ Reduza `max_workers` para evitar sobrecarga

## 📈 Exemplos de Uso

### Exemplo 1: Uso Básico (Padrão)

```powershell
# Com UV (recomendado)
uv run python consulta_publicacoes_pncp.py

# Tradicional
python consulta_publicacoes_pncp.py
```

### Exemplo 2: Busca em Todos os Estados (30 dias)

```python
from pathlib import Path
from consulta_publicacoes_pncp import executar_consulta_licitacoes

# Todos os estados do Brasil
estados_brasil = [
    'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 
    'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 
    'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
]

df_completo, df_filtrado, arquivo = executar_consulta_licitacoes(
    dias_anteriores=30,
    estados=estados_brasil,
    palavras_chave=['alimentício', 'alimento', 'merenda']
)
```

### Exemplo 3: Busca Específica por Setor

```python
# Setor de Tecnologia
executar_consulta_licitacoes(
    dias_anteriores=15,
    estados=['SP', 'RJ', 'MG'],
    palavras_chave=['software', 'sistema', 'tecnologia', 'computador']
)

# Setor de Saúde
executar_consulta_licitacoes(
    dias_anteriores=15,
    estados=['PE', 'BA', 'CE'],
    palavras_chave=['medicamento', 'hospitalar', 'equipamento médico']
)
```

### Exemplo 4: Análise de Dados

```python
import pandas as pd

df_completo, df_filtrado, _ = executar_consulta_licitacoes()

# Estatísticas por estado
print(df_completo['uf'].value_counts())

# Análise de valores
print(f"Valor total: R$ {df_completo['valor_estimado'].sum():,.2f}")
print(f"Valor médio: R$ {df_completo['valor_estimado'].mean():,.2f}")

# Top 10 órgãos
print(df_completo['orgao'].value_counts().head(10))
```

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para:

1. 🍴 Fork o projeto
2. 🔧 Criar uma branch (`git checkout -b feature/MinhaFeature`)
3. 💾 Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. 📤 Push para a branch (`git push origin feature/MinhaFeature`)
5. 🎉 Abrir um Pull Request

## 📝 Changelog

### v2.0 (23 Outubro 2025) 🎉 **ATUAL**

**Versão Refatorada - Padrão Senior Python 3.11**

#### 🚀 Melhorias de Código

- ✅ **Type Hints**: Todos os parâmetros e retornos tipados
- ✅ **Docstrings Google Style**: Documentação completa de todas as funções
- ✅ **Logging Estruturado**: Substituição de `print()` por `logging`
- ✅ **Dataclasses**: `ConfiguracaoBusca` e `ResultadoRequisicao`
- ✅ **Constantes**: Todas em UPPER_CASE com `Final`
- ✅ **Pathlib**: Manipulação de arquivos com `Path`
- ✅ **Código Limpo**: Remoção de código morto e imports não utilizados

#### ⚡ Performance

- ⚡ Requisições paralelas com `ThreadPoolExecutor` (10x mais rápido)
- 🔄 Retry automático com backoff exponencial (3 tentativas)
- ⏱️ Timeout de 10s por requisição
- 🎯 Pool de conexões HTTP reutilizáveis (20 conexões)
- 📊 Barra de progresso visual em tempo real

#### 🛡️ Robustez

- ✅ Validação de inputs com mensagens claras
- ✅ Funções especializadas com responsabilidade única
- ✅ Tratamento de erros com logging detalhado
- ✅ Fail-fast para erros críticos

#### 📚 Documentação

- ✅ README.md atualizado e expandido
- ✅ QUICKSTART.md para início rápido
- ✅ Manual completo da API PNCP
- ✅ Instruções detalhadas para GitHub Copilot

#### � Gerenciamento

- ✅ Suporte a UV para gerenciamento rápido
- ✅ Requirements.txt simplificado
- ✅ API pública: `executar_consulta_licitacoes()`
- ✅ Configuração flexível via parâmetros

### v1.0 (Junho 2024)

- 🎉 Versão inicial
- 🔍 Busca sequencial por estados
- 📊 Exportação para Excel
- 🎯 Filtro por palavras-chave
- 📅 Busca por período de datas

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👨‍💻 Autor

**Jhonne**

- GitHub: [@jhonne](https://github.com/jhonne)

---

⭐ **Dica**: Estrele este repositório se ele foi útil para você!

💼 **Objetivo**: Facilitar o trabalho de profissionais que buscam oportunidades de negócios em licitações públicas, oferecendo uma solução automatizada e eficiente para consulta e análise de pregões eletrônicos.
