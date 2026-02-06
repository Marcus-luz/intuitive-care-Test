import os
import pandas as pd
import logging
import sys
from dotenv import load_dotenv

# Força o Python a encontrar o .env na mesma pasta deste script
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

# 2. Chame a função para carregar as variáveis do arquivo .env
load_dotenv()
print(f"DEBUG: Host do Banco: {os.getenv('DB_HOST')}")
print(f"DEBUG: Senha carregada: {'SIM' if os.getenv('DB_PASS') else 'NÃO'}")

from backend.core.crawler import fetch_ans_files, fetch_operator_registry
from backend.core.processor import DataProcessor
from backend.core.enricher import DataEnricher
from backend.core.aggregator import DataAggregator
from backend.core.loader import import_all_to_mysql 



# Configuração de Logging Profissional
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def check_db_connection():
    try:
        import mysql.connector
        import os
        # preencher no .env ou na .env.example
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASS"), 
            database=os.getenv("DB_NAME", "intuitive_care")
        )
        conn.close()
        logger.info("✅ Conexão com o banco de dados validada.")
        return True
    except Exception as e:
        logger.error(f"❌ Falha de conexão com o banco: {e}. Certifique-se que o MySQL está rodando.")
        return False

def executar_pipeline():
    logger.info("=== INICIANDO PIPELINE DE DADOS ANS ===")

    if not check_db_connection():
        logger.critical("Execução abortada: Banco de dados inacessível.")
        return False

    path_base = os.path.dirname(os.path.abspath(__file__))
    pasta_data_real = os.path.join(path_base, 'data')

    # Passo 1: Extração
    try:
        logger.info("[1/5] Baixando arquivos da ANS (Scraping)...")
        fetch_ans_files()
        fetch_operator_registry()
    except Exception as e:
        logger.error(f"Erro no Scraping: {e}")
        return False

    # Passo 2: Processamento
    try:
        logger.info("[2/5] Processando ZIPs e consolidando dados...")
        processor = DataProcessor(data_dir=pasta_data_real)
        processor.run() 
    except Exception as e:
        logger.error(f"Erro no processamento de arquivos: {e}")
        return False

    # Passo 3: Enriquecimento
    try:
        logger.info("[3/5] Enriquecendo dados e validando registros...")
        path_consolidado = os.path.join(pasta_data_real, 'consolidado_despesas.csv')
        
        if not os.path.exists(path_consolidado):
            raise FileNotFoundError(f"Arquivo {path_consolidado} não foi gerado.")

        df_consolidado = pd.read_csv(path_consolidado)
        enricher = DataEnricher(data_dir=pasta_data_real) 
        df_enriquecido = enricher.enrich(df_consolidado)
        
        if 'UF' not in df_enriquecido.columns:
            raise ValueError("O enriquecimento falhou: Coluna UF não encontrada.")
    except Exception as e:
        logger.error(f"Erro no enriquecimento: {e}")
        return False

    # Passo 4: Agregação
    try:
        logger.info("[4/5] Gerando estatísticas (Média e Desvio Padrão)...")
        aggregator = DataAggregator(data_dir=pasta_data_real)
        df_final = aggregator.aggregate_expenses(df_enriquecido)
        aggregator.save_report(df_final)
    except Exception as e:
        logger.info(f"Erro na agregação: {e}")
        return False

    # Passo 5: Carga Final (Onde seu script antigo parava, mas o novo carrega no SQL)
    try:
        logger.info("[5/5] Carregando dados processados para o MySQL...")
        import_all_to_mysql()
        logger.info("✨ PIPELINE DE DADOS CONCLUÍDO COM SUCESSO! ✨")
        return True
    except Exception as e:
        logger.error(f"Erro na carga do banco de dados: {e}")
        return False

if __name__ == "__main__":
    sucesso = executar_pipeline()
    if not sucesso:
        sys.exit(1)