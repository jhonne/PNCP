# 🚀 Quick Start - Consulta PNCP

Guia rápido para começar a usar a aplicação de consulta de licitações PNCP.

---

## ⚡ Início Rápido (3 minutos)

### 1️⃣ **Instalar Dependências**

```bash
pip install -r requirements.txt
```

### 2️⃣ **Executar Versão Refatorada (Recomendado)**

```bash
python consulta_publicacoes_pncp_refatorado.py
```

### 3️⃣ **Pronto! ✅**

O arquivo Excel será gerado no diretório atual: `licitacoes_DD_MM_YYYY.xlsx`

---

## 🎯 Configuração Rápida

Edite as constantes no final do arquivo `consulta_publicacoes_pncp_refatorado.py`:

```python
if __name__ == "__main__":
    # Configuração personalizada (ajuste conforme necessário)
    DIAS_BUSCA = 7  # ← Mudar para 30 dias, por exemplo
    ESTADOS_CONSULTA = ESTADOS_PADRAO  # ← Ou ['PE', 'BA', 'RN']
    PALAVRAS_FILTRO = ['alimentício', 'alimento']  # ← Suas palavras-chave
    DIRETORIO_SAIDA = Path.cwd()  # ← Ou Path('C:/meus_resultados')
```

---

## 📚 Exemplos Interativos

Execute o menu de exemplos:

```bash
python exemplos_uso.py
```

Ou execute um exemplo específico:

```bash
python exemplos_uso.py 1  # Uso básico
python exemplos_uso.py 7  # Análise de dados
```

---

## 🔧 Uso Programático

```python
from consulta_publicacoes_pncp_refatorado import executar_consulta_licitacoes

# Simples
df_completo, df_filtrado, arquivo = executar_consulta_licitacoes()

# Customizado
df_completo, df_filtrado, arquivo = executar_consulta_licitacoes(
    dias_anteriores=30,
    estados=['PE', 'BA', 'CE'],
    palavras_chave=['computador', 'software', 'tecnologia']
)
```

---

## 📊 Entendendo os Resultados

### Arquivo Excel Gerado

**Aba "Todos"**: Todas as licitações encontradas
- Colunas principais: `orgao`, `objeto`, `valor_estimado`, `abertura`, `link`
- Use para análise geral e estatísticas

**Aba "Filtrados"**: Apenas licitações com suas palavras-chave
- Mesmo formato da aba "Todos"
- Use para identificar oportunidades específicas

---

## 🎨 Customizações Comuns

### 1. Mudar Período de Busca

```python
# Últimos 30 dias
executar_consulta_licitacoes(dias_anteriores=30)

# Últimos 90 dias
executar_consulta_licitacoes(dias_anteriores=90)
```

### 2. Buscar Estados Específicos

```python
# Apenas Pernambuco
executar_consulta_licitacoes(estados=['PE'])

# Região Sul
executar_consulta_licitacoes(estados=['RS', 'SC', 'PR'])

# Sudeste
executar_consulta_licitacoes(estados=['SP', 'RJ', 'MG', 'ES'])
```

### 3. Mudar Palavras-Chave

```python
# Tecnologia
palavras = ['computador', 'notebook', 'software', 'sistema']
executar_consulta_licitacoes(palavras_chave=palavras)

# Saúde
palavras = ['medicamento', 'hospitalar', 'médico']
executar_consulta_licitacoes(palavras_chave=palavras)

# Construção
palavras = ['obra', 'construção', 'reforma']
executar_consulta_licitacoes(palavras_chave=palavras)
```

### 4. Salvar em Pasta Específica

```python
from pathlib import Path

diretorio = Path('C:/MeusResultados/Licitacoes')
executar_consulta_licitacoes(diretorio_saida=diretorio)
```

---

## ⚠️ Solução Rápida de Problemas

### Problema: "Nenhum processo foi encontrado"

**Solução**: Aumente o período de busca
```python
executar_consulta_licitacoes(dias_anteriores=30)  # ou 60, 90
```

### Problema: "Timeout" ou "Muito lento"

**Solução**: No arquivo refatorado, ajuste as constantes:
```python
TIMEOUT_SEGUNDOS: Final[int] = 20  # Aumentar timeout
MAX_WORKERS: Final[int] = 5  # Reduzir workers paralelos
```

### Problema: "ModuleNotFoundError"

**Solução**: Instale as dependências
```bash
pip install -r requirements.txt
```

### Problema: Excel não abre ou está corrompido

**Solução**: Instale a biblioteca correta
```bash
pip install openpyxl --upgrade
```

---

## 📖 Documentação Completa

- **README.md**: Documentação completa do projeto
- **docs/refactoring/**: Detalhes da refatoração
- **docs/manual-api-compras.md**: Manual da API PNCP
- **exemplos_uso.py**: 8 exemplos práticos

---

## 🆘 Precisa de Ajuda?

1. ✅ Leia o **README.md** completo
2. ✅ Execute os **exemplos interativos**: `python exemplos_uso.py`
3. ✅ Consulte a **documentação da refatoração**
4. ✅ Abra uma **issue** no GitHub

---

## 🎉 Dicas de Ouro

### ⚡ Performance

```python
# Busca rápida (poucos estados, poucos dias)
executar_consulta_licitacoes(
    dias_anteriores=7,
    estados=['PE']
)

# Busca completa (demora mais, mais resultados)
executar_consulta_licitacoes(
    dias_anteriores=30,
    estados=TODOS_OS_ESTADOS
)
```

### 🎯 Precisão

```python
# Palavras-chave específicas = menos ruído
palavras = ['notebook Dell']

# Palavras-chave genéricas = mais resultados
palavras = ['equipamento', 'material']
```

### 📊 Análise

```python
import pandas as pd

# Após executar consulta
df_completo, df_filtrado, arquivo = executar_consulta_licitacoes()

# Análises rápidas
print(df_completo['uf'].value_counts())  # Por estado
print(df_completo['valor_estimado'].describe())  # Estatísticas $
print(df_completo['orgao'].value_counts().head(10))  # Top órgãos
```

---

## 📅 Roadmap

- [ ] Interface Web (Flask/Streamlit)
- [ ] Alertas automáticos (email/telegram)
- [ ] Dashboard interativo
- [ ] Histórico de consultas
- [ ] Machine Learning para recomendações

---

**🚀 Boas consultas e bons negócios!**

---

*Última atualização: 23/10/2025*  
*Versão: 2.1 (Refatorado)*
