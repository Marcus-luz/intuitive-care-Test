from backend.core.crawler import fetch_ans_files, fetch_operator_registry
from backend.core.processor import DataProcessor
from backend.core.enricher import DataEnricher
from backend.core.aggregator import DataAggregator
import os
import pandas as pd

def executar_pipeline():
    print("=== INICIANDO PIPELINE DE DADOS ANS ===\n")

    # Caminho absoluto da raiz do projeto onde está a main.py
    path_base = os.path.dirname(os.path.abspath(__file__))
    pasta_data_real = os.path.join(path_base, 'data')

    # [cite_start]Passo 1: Extração (Item 1.1 e 2.2 do PDF) [cite: 29, 68]
    print("[1/4] Baixando arquivos da ANS...")
    fetch_ans_files()
    fetch_operator_registry()

    # [cite_start]Passo 2: Processamento e Consolidação (Item 1.2 e 1.3) [cite: 32, 40]
    print("\n[2/4] Processando ZIPs e gerando consolidado...")
    processor = DataProcessor(data_dir=pasta_data_real)
    processor.run() 

    # [cite_start]Passo 3: Enriquecimento e Validação (Item 2.1 e 2.2) [cite: 57, 67]
    print("\n[3/4] Enriquecendo dados e validando registros...")
    path_consolidado = os.path.join(pasta_data_real, 'consolidado_despesas.csv')

    if os.path.exists(path_consolidado):
        df_consolidado = pd.read_csv(path_consolidado)
        
        # Injetamos o caminho correto para que o Enricher ache o operadoras_ativas.csv
        enricher = DataEnricher(data_dir=pasta_data_real) 
        df_enriquecido = enricher.enrich(df_consolidado)
        
        # [cite_start]Verificação de segurança: O Join funcionou e trouxe a coluna UF? [cite: 72]
        if 'UF' in df_enriquecido.columns:
            # [cite_start]Passo 4: Agregação (Item 2.3) [cite: 79]
            print("\n[4/4] Gerando estatísticas finais (Média e Desvio Padrão)...")
            aggregator = DataAggregator(data_dir=pasta_data_real)
            df_final = aggregator.aggregate_expenses(df_enriquecido)
            aggregator.save_report(df_final)
            print("\n=== PIPELINE CONCLUÍDO COM SUCESSO! ===")
        else:
            print("[!] ERRO: O enriquecimento falhou. Verifique se o cadastro foi baixado.")
    else:
        print(f"[!] ERRO: Arquivo {path_consolidado} não encontrado.")

if __name__ == "__main__":
    executar_pipeline()