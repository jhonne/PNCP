#!/usr/bin/env python
# coding: utf-8

"""
Aplicação para Consultar Licitações Publicadas no PNCP.

Este módulo realiza buscas de pregões eletrônicos por estado e data de publicação,
filtra licitações por palavras-chave e exporta os resultados para Excel.

A Nova Lei de Licitações 14.133/2021 exige que todos os órgãos da administração
pública centralizem as informações de suas contratações no Portal Nacional de
Compras Públicas (PNCP).

Author: Jhonne Jefferson
Version: 2.0 (Refatorado)
Date: 23/10/2025
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Final

import pandas as pd
import requests
from dateutil.relativedelta import relativedelta
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# =============================================================================
# CONFIGURAÇÃO DE LOGGING
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# =============================================================================
# CONSTANTES
# =============================================================================

# URL Base da API
BASE_URL: Final[str] = 'https://dadosabertos.compras.gov.br/modulo-contratacoes/1_consultarContratacoes_PNCP_14133'

# Configurações de Requisição
TIMEOUT_SEGUNDOS: Final[int] = 10
MAX_WORKERS: Final[int] = 10
MAX_RETRIES: Final[int] = 3
BACKOFF_FACTOR: Final[float] = 0.5
POOL_CONNECTIONS: Final[int] = 20
POOL_MAXSIZE: Final[int] = 20

# Configurações de Paginação
TAMANHO_PAGINA: Final[int] = 50
NUMERO_PAGINAS: Final[int] = 10

# Modalidades
MODALIDADE_PREGAO_ELETRONICO: Final[int] = 6

# Estados do Norte e Nordeste
ESTADOS_PADRAO: Final[list[str]] = [
    'PE', 'PB', 'AL', 'SE', 'BA', 'RN', 'CE', 'PI', 'MA',
    'TO', 'PA', 'AP', 'RR', 'AM', 'AC'
]

# Palavras-chave padrão
PALAVRAS_CHAVE_PADRAO: Final[list[str]] = ['alimentício', 'alimento']

# Status HTTP para retry
STATUS_FORCELIST: Final[list[int]] = [429, 500, 502, 503, 504]

# =============================================================================
# DATACLASSES
# =============================================================================

@dataclass
class ConfiguracaoBusca:
    """Configuração para busca de licitações.
    
    Attributes:
        data_inicial: Data inicial da busca (formato: YYYY-MM-DD)
        data_final: Data final da busca (formato: YYYY-MM-DD)
        codigo_modalidade: Código da modalidade de licitação
        estados: Lista de siglas de estados para buscar
        palavras_chave: Lista de palavras-chave para filtrar resultados
        tamanho_pagina: Número de registros por página
        numero_paginas: Número total de páginas para buscar
    """
    data_inicial: str
    data_final: str
    codigo_modalidade: int
    estados: list[str]
    palavras_chave: list[str]
    tamanho_pagina: int = TAMANHO_PAGINA
    numero_paginas: int = NUMERO_PAGINAS

    def validar(self) -> None:
        """Valida os parâmetros de configuração.
        
        Raises:
            ValueError: Se algum parâmetro for inválido
        """
        try:
            datetime.strptime(self.data_inicial, '%Y-%m-%d')
            datetime.strptime(self.data_final, '%Y-%m-%d')
        except ValueError as e:
            raise ValueError(f"Formato de data inválido. Use YYYY-MM-DD: {e}")
        
        if not self.estados:
            raise ValueError("Lista de estados não pode estar vazia")
        
        if self.tamanho_pagina <= 0 or self.tamanho_pagina > 500:
            raise ValueError("Tamanho de página deve estar entre 1 e 500")
        
        if self.numero_paginas <= 0:
            raise ValueError("Número de páginas deve ser maior que zero")


@dataclass
class ResultadoRequisicao:
    """Resultado de uma requisição à API.
    
    Attributes:
        sucesso: Indica se a requisição foi bem-sucedida
        dados: Lista de dados retornados pela API
        url: URL que foi consultada
        indice: Índice da requisição
        status_code: Código de status HTTP (opcional)
        erro: Mensagem de erro (opcional)
    """
    sucesso: bool
    dados: list[dict[str, Any]]
    url: str
    indice: int
    status_code: int | None = None
    erro: str | None = None


# =============================================================================
# FUNÇÕES DE CONFIGURAÇÃO
# =============================================================================

def obter_configuracao_padrao(dias_anteriores: int = 7) -> ConfiguracaoBusca:
    """Obtém configuração padrão para busca de licitações.
    
    Args:
        dias_anteriores: Número de dias anteriores para buscar (padrão: 7)
        
    Returns:
        Objeto ConfiguracaoBusca com valores padrão
        
    Raises:
        ValueError: Se dias_anteriores for negativo
    """
    if dias_anteriores < 0:
        raise ValueError("dias_anteriores deve ser um número positivo")
    
    data_final_dt = datetime.now()
    data_inicial_dt = data_final_dt - relativedelta(days=dias_anteriores)
    
    return ConfiguracaoBusca(
        data_inicial=data_inicial_dt.strftime('%Y-%m-%d'),
        data_final=data_final_dt.strftime('%Y-%m-%d'),
        codigo_modalidade=MODALIDADE_PREGAO_ELETRONICO,
        estados=ESTADOS_PADRAO,
        palavras_chave=PALAVRAS_CHAVE_PADRAO
    )


# =============================================================================
# FUNÇÕES DE REQUISIÇÃO HTTP
# =============================================================================

def criar_sessao_http() -> requests.Session:
    """Cria sessão HTTP com retry automático e pooling de conexões.
    
    Configura retry automático para falhas temporárias e otimiza
    o pooling de conexões para requisições paralelas.
    
    Returns:
        Sessão HTTP configurada
    """
    sessao = requests.Session()
    
    retry = Retry(
        total=MAX_RETRIES,
        backoff_factor=BACKOFF_FACTOR,
        status_forcelist=STATUS_FORCELIST,
        raise_on_status=False
    )
    
    adapter = HTTPAdapter(
        max_retries=retry,
        pool_connections=POOL_CONNECTIONS,
        pool_maxsize=POOL_MAXSIZE
    )
    
    sessao.mount('http://', adapter)
    sessao.mount('https://', adapter)
    
    return sessao


def construir_urls(config: ConfiguracaoBusca) -> list[str]:
    """Constrói lista de URLs para consulta à API.
    
    Args:
        config: Configuração da busca
        
    Returns:
        Lista de URLs completas para consulta
    """
    urls = []
    
    for pagina in range(1, config.numero_paginas + 1):
        for uf in config.estados:
            url = (
                f'{BASE_URL}'
                f'?dataPublicacaoPncpInicial={config.data_inicial}'
                f'&dataPublicacaoPncpFinal={config.data_final}'
                f'&codigoModalidade={config.codigo_modalidade}'
                f'&unidadeOrgaoUfSigla={uf}'
                f'&tamanhoPagina={config.tamanho_pagina}'
                f'&pagina={pagina}'
            )
            urls.append(url)
    
    return urls


def buscar_url(
    sessao: requests.Session,
    url: str,
    indice: int,
    total: int
) -> ResultadoRequisicao:
    """Faz requisição HTTP para uma URL específica.
    
    Args:
        sessao: Sessão HTTP configurada
        url: URL para consultar
        indice: Índice da requisição (para logging)
        total: Total de requisições (para logging)
        
    Returns:
        Resultado da requisição encapsulado em ResultadoRequisicao
    """
    try:
        response = sessao.get(url, timeout=TIMEOUT_SEGUNDOS)
        
        if response.status_code == 200:
            dados = response.json().get('resultado', [])
            return ResultadoRequisicao(
                sucesso=True,
                dados=dados,
                url=url,
                indice=indice,
                status_code=response.status_code
            )
        else:
            logger.warning(
                f"Requisição {indice}/{total} falhou com status {response.status_code}: {url}"
            )
            return ResultadoRequisicao(
                sucesso=False,
                dados=[],
                url=url,
                indice=indice,
                status_code=response.status_code
            )
            
    except requests.exceptions.Timeout:
        logger.error(f"Timeout na requisição {indice}/{total}: {url}")
        return ResultadoRequisicao(
            sucesso=False,
            dados=[],
            url=url,
            indice=indice,
            erro='Timeout'
        )
        
    except Exception as e:
        logger.exception(f"Erro na requisição {indice}/{total}: {e}")
        return ResultadoRequisicao(
            sucesso=False,
            dados=[],
            url=url,
            indice=indice,
            erro=str(e)
        )


# =============================================================================
# FUNÇÕES DE PROCESSAMENTO DE DADOS
# =============================================================================

def extrair_dados_processo(processo: dict[str, Any]) -> list[Any]:
    """Extrai dados relevantes de um processo de licitação.
    
    Args:
        processo: Dicionário com dados do processo da API
        
    Returns:
        Lista com dados extraídos na ordem correta para o DataFrame
    """
    return [
        processo.get('sequencialCompraPncp', ''),
        processo.get('orgaoEntidadeRazaoSocial', ''),
        processo.get('unidadeOrgaoUfSigla', ''),
        processo.get('dataInclusaoPncp', ''),
        processo.get('amparoLegalNome', ''),
        processo.get('dataAberturaPropostaPncp', ''),
        processo.get('dataEncerramentoPropostaPncp', ''),
        processo.get('numeroCompra', ''),
        processo.get('objetoCompra', ''),
        processo.get('numeroControlePNCP', ''),
        processo.get('valorTotalEstimado', 0),
        processo.get('valorTotalHomologado', 0),
        processo.get('modoDisputaNomePncp', ''),
        processo.get('modalidadeNome', ''),
        processo.get('situacaoCompraNomePncp', ''),
        processo.get('srp', False)
    ]


def buscar_licitacoes_paralelo(config: ConfiguracaoBusca) -> pd.DataFrame:
    """Busca licitações usando requisições paralelas.
    
    Executa múltiplas requisições HTTP em paralelo para otimizar
    o tempo de resposta total.
    
    Args:
        config: Configuração da busca
        
    Returns:
        DataFrame com todas as licitações encontradas
        
    Raises:
        ValueError: Se a configuração for inválida
    """
    config.validar()
    
    urls = construir_urls(config)
    processos = []
    
    logger.info(f"Buscando licitações de {config.data_inicial} até {config.data_final}")
    logger.info(f"Total de URLs para consultar: {len(urls)}")
    logger.info("Iniciando requisições paralelas...")
    
    import time
    inicio = time.time()
    sessao = criar_sessao_http()
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futuros = {
            executor.submit(buscar_url, sessao, url, i, len(urls)): url
            for i, url in enumerate(urls, 1)
        }
        
        completados = 0
        erros = 0
        total_registros = 0
        
        for futuro in as_completed(futuros):
            completados += 1
            resultado = futuro.result()
            
            # Barra de progresso
            percentual = (completados / len(urls)) * 100
            barra = '█' * int(percentual / 2) + '░' * (50 - int(percentual / 2))
            print(f'\r[{barra}] {percentual:.1f}% ({completados}/{len(urls)})', end='', flush=True)
            
            if resultado.sucesso:
                total_registros += len(resultado.dados)
                
                for processo in resultado.dados:
                    processos.append(extrair_dados_processo(processo))
            else:
                erros += 1
    
    print()  # Nova linha após barra de progresso
    tempo_total = time.time() - inicio
    
    logger.info(f"Requisições concluídas em {tempo_total:.2f} segundos")
    logger.info(f"Sucessos: {completados - erros}")
    logger.info(f"Erros: {erros}")
    logger.info(f"Total de registros: {total_registros}")
    
    # Criar DataFrame
    df = pd.DataFrame(processos, columns=[
        'sequencial', 'orgao', 'uf', 'inclusao', 'amparo_legal',
        'abertura', 'encerramento', 'n_processo', 'objeto', 'link',
        'valor_estimado', 'valor_homologado', 'disputa', 'plataforma',
        'situacao', 'srp'
    ])
    
    logger.info(f"Total de processos encontrados: {len(df)}")
    
    if len(df) == 0:
        logger.warning("ATENÇÃO: Nenhum processo foi encontrado!")
        logger.warning("Possíveis causas:")
        logger.warning("  1. Não há licitações no período selecionado")
        logger.warning("  2. A API pode estar fora do ar")
        logger.warning("  3. Os parâmetros de busca podem estar incorretos")
    
    return df


def formatar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Formata colunas do DataFrame com tipos apropriados.
    
    Args:
        df: DataFrame com dados brutos
        
    Returns:
        DataFrame com colunas formatadas
    """
    if len(df) == 0:
        return df
    
    # Converter valores
    df['valor_estimado'] = pd.to_numeric(df['valor_estimado'], errors='coerce')
    df['valor_homologado'] = pd.to_numeric(df['valor_homologado'], errors='coerce')
    
    # Converter datas
    df['abertura'] = pd.to_datetime(df['abertura'], format='%Y-%m-%dT%H:%M:%S', errors='coerce')
    df['inclusao'] = pd.to_datetime(df['inclusao'], format='%Y-%m-%dT%H:%M:%S', errors='coerce')
    df['encerramento'] = pd.to_datetime(df['encerramento'], format='%Y-%m-%dT%H:%M:%S', errors='coerce')
    
    logger.info("DataFrame formatado com sucesso")
    
    return df


def filtrar_por_palavras_chave(
    df: pd.DataFrame,
    palavras_chave: list[str]
) -> pd.DataFrame:
    """Filtra DataFrame por palavras-chave no campo objeto.
    
    Args:
        df: DataFrame com licitações
        palavras_chave: Lista de palavras para filtrar
        
    Returns:
        DataFrame filtrado contendo apenas registros com palavras-chave
    """
    if len(df) == 0:
        logger.warning("DataFrame vazio, retornando DataFrame vazio")
        return pd.DataFrame()
    
    palavras_lower = [palavra.lower() for palavra in palavras_chave]
    filtro = df['objeto'].str.lower().str.contains('|'.join(palavras_lower), na=False)
    df_filtrado = df[filtro].reset_index(drop=True)
    
    logger.info(f"Processos filtrados por palavras-chave: {len(df_filtrado)}")
    logger.info(f"Palavras-chave utilizadas: {', '.join(palavras_chave)}")
    
    return df_filtrado


# =============================================================================
# FUNÇÕES DE EXPORTAÇÃO
# =============================================================================

def exportar_para_excel(
    df_completo: pd.DataFrame,
    df_filtrado: pd.DataFrame,
    diretorio_saida: Path | None = None
) -> Path | None:
    """Exporta DataFrames para arquivo Excel.
    
    Cria arquivo Excel com duas abas: uma com todos os dados e outra
    com dados filtrados por palavras-chave.
    
    Args:
        df_completo: DataFrame com todas as licitações
        df_filtrado: DataFrame com licitações filtradas
        diretorio_saida: Diretório onde salvar o arquivo (padrão: diretório atual)
        
    Returns:
        Path do arquivo criado ou None se não houver dados
    """
    if len(df_completo) == 0:
        logger.warning("Arquivo Excel não foi criado pois não há dados para salvar")
        return None
    
    if diretorio_saida is None:
        diretorio_saida = Path.cwd()
    else:
        diretorio_saida.mkdir(parents=True, exist_ok=True)
    
    data_atual = datetime.now().strftime('%d_%m_%Y')
    nome_arquivo = f'licitacoes_{data_atual}.xlsx'
    caminho_arquivo = diretorio_saida / nome_arquivo
    
    try:
        with pd.ExcelWriter(caminho_arquivo, engine='openpyxl') as writer:
            df_completo.to_excel(writer, sheet_name='Todos', index=False)
            df_filtrado.to_excel(writer, sheet_name='Filtrados', index=False)
        
        logger.info(f"DataFrame salvo com sucesso em {caminho_arquivo}")
        logger.info(f"  - Aba 'Todos': {len(df_completo)} registros")
        logger.info(f"  - Aba 'Filtrados': {len(df_filtrado)} registros")
        
        return caminho_arquivo
        
    except Exception as e:
        logger.exception(f"Erro ao salvar arquivo Excel: {e}")
        return None


# =============================================================================
# FUNÇÃO PRINCIPAL
# =============================================================================

def executar_consulta_licitacoes(
    dias_anteriores: int = 7,
    estados: list[str] | None = None,
    palavras_chave: list[str] | None = None,
    diretorio_saida: Path | None = None
) -> tuple[pd.DataFrame, pd.DataFrame, Path | None]:
    """Executa consulta completa de licitações no PNCP.
    
    Esta é a função principal que orquestra todo o processo:
    1. Configuração da busca
    2. Busca paralela de licitações
    3. Formatação de dados
    4. Filtragem por palavras-chave
    5. Exportação para Excel
    
    Args:
        dias_anteriores: Número de dias anteriores para buscar (padrão: 7)
        estados: Lista de siglas de estados (padrão: estados Norte/Nordeste)
        palavras_chave: Lista de palavras para filtrar (padrão: alimentos)
        diretorio_saida: Diretório para salvar Excel (padrão: diretório atual)
        
    Returns:
        Tupla contendo:
        - DataFrame completo
        - DataFrame filtrado
        - Path do arquivo Excel (ou None se não foi criado)
        
    Raises:
        ValueError: Se parâmetros forem inválidos
        
    Example:
        >>> df_completo, df_filtrado, arquivo = executar_consulta_licitacoes(
        ...     dias_anteriores=7,
        ...     palavras_chave=['alimentício', 'merenda']
        ... )
        >>> print(f"Encontradas {len(df_completo)} licitações")
        >>> print(f"Arquivo salvo em: {arquivo}")
    """
    logger.info("=" * 60)
    logger.info("INICIANDO CONSULTA DE LICITAÇÕES PNCP")
    logger.info("=" * 60)
    
    # Configuração
    config = obter_configuracao_padrao(dias_anteriores)
    
    if estados is not None:
        config.estados = estados
    
    if palavras_chave is not None:
        config.palavras_chave = palavras_chave
    
    # Busca e processamento
    df_completo = buscar_licitacoes_paralelo(config)
    df_completo = formatar_dataframe(df_completo)
    
    # Filtragem
    df_filtrado = filtrar_por_palavras_chave(df_completo, config.palavras_chave)
    
    # Exportação
    arquivo_excel = exportar_para_excel(df_completo, df_filtrado, diretorio_saida)
    
    logger.info("=" * 60)
    logger.info("CONSULTA FINALIZADA COM SUCESSO")
    logger.info("=" * 60)
    
    return df_completo, df_filtrado, arquivo_excel


# =============================================================================
# EXECUÇÃO PRINCIPAL
# =============================================================================

if __name__ == "__main__":
    """Execução principal do script."""
    
    # Configuração personalizada (ajuste conforme necessário)
    DIAS_BUSCA = 7
    ESTADOS_CONSULTA = ESTADOS_PADRAO  # Ou liste estados específicos: ['PE', 'BA']
    PALAVRAS_FILTRO = ['alimentício', 'alimento']  # Ajuste conforme necessário
    DIRETORIO_SAIDA = Path.cwd()  # Salva no diretório atual
    
    try:
        df_completo, df_filtrado, arquivo = executar_consulta_licitacoes(
            dias_anteriores=DIAS_BUSCA,
            estados=ESTADOS_CONSULTA,
            palavras_chave=PALAVRAS_FILTRO,
            diretorio_saida=DIRETORIO_SAIDA
        )
        
        # Exibir primeiras linhas para validação
        if len(df_completo) > 0:
            print("\n" + "=" * 60)
            print("PREVIEW DOS DADOS")
            print("=" * 60)
            print(f"\nPrimeiras linhas do DataFrame completo:")
            print(df_completo.head())
            
            if len(df_filtrado) > 0:
                print(f"\nPrimeiras linhas do DataFrame filtrado:")
                print(df_filtrado.head())
        
    except Exception as e:
        logger.exception(f"Erro fatal na execução: {e}")
        raise
