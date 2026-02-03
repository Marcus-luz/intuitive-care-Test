import pandas as pd
import mysql.connector
import os

def import_all_to_mysql():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, '..', '..', 'data')
    
    # AJUSTE PARA DOCKER: Lê do ambiente ou usa padrão local
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASS = os.getenv("DB_PASS", "Marcusluz1!") # Sua senha atual como padrão
    DB_NAME = os.getenv("DB_NAME", "intuitive_care")

    conn = mysql.connector.connect(
        host=DB_HOST, 
        user=DB_USER, 
        password=DB_PASS, 
        database=DB_NAME, 
        charset='utf8mb4'
    )
    cursor = conn.cursor()

    try:
        # 1. CARREGAR TABELA AGREGADA (Lista Principal)
        path_agg = os.path.join(data_dir, 'despesas_agregadas.csv')
        if os.path.exists(path_agg):
            print("Carregando despesas agregadas...")
            df_agg = pd.read_csv(path_agg, encoding='utf-8-sig')
            cursor.execute("TRUNCATE TABLE despesas_agregadas")
            
            sql_agg = """
                INSERT INTO despesas_agregadas 
                (cnpj, razao_social, uf, total_despesas, media_trimestral, desvio_padrao) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            for _, r in df_agg.iterrows():
                cursor.execute(sql_agg, (
                    str(r['CNPJ']), r['RazaoSocial'], r['UF'], 
                    float(r['Total_Despesas']), float(r['Media_Trimestral']), float(r['Desvio_Padrao'])
                ))
        
        # 2. CARREGAR TABELA DE HISTÓRICO (Consolidadas)
        path_hist = os.path.join(data_dir, 'historico_final.csv')
        if os.path.exists(path_hist):
            print("Carregando histórico detalhado para os gráficos...")
            df_hist = pd.read_csv(path_hist, encoding='utf-8-sig')
            
            # --- SANEAMENTO DE DADOS ---
            df_hist['ValorDespesas'] = pd.to_numeric(df_hist['ValorDespesas'], errors='coerce').fillna(0)
            df_hist['Trimestre'] = df_hist['Trimestre'].astype(str).str.extract(r'(\d+)').fillna(0).astype(int)
            df_hist['RazaoSocial'] = df_hist['RazaoSocial'].astype(str).str.strip()
            df_hist['CNPJ'] = df_hist['CNPJ'].astype(str).str.strip() 

            cursor.execute("TRUNCATE TABLE despesas_consolidadas")
            
            sql_hist = """
                INSERT INTO despesas_consolidadas 
                (cnpj, razao_social, trimestre, ano, valor_despesa) 
                VALUES (%s, %s, %s, %s, %s)
            """
            
            for _, r in df_hist.iterrows():
                cursor.execute(sql_hist, (
                    r['CNPJ'],
                    r['RazaoSocial'], 
                    int(r['Trimestre']), 
                    int(r['Ano']), 
                    float(r['ValorDespesas'])
                ))

        # 3. CARREGAR CADASTRO DE OPERADORAS (Para Query 2 - UF)
        path_ops = os.path.join(data_dir, 'operadoras_ativas.csv')
        if os.path.exists(path_ops):
            print("Carregando cadastro de operadoras (Master Data)...")
            
            # Lendo o CSV com o separador correto e encoding padrão da ANS
            df_ops = pd.read_csv(path_ops, sep=';', encoding='latin1', dtype=str)
            
            # Limpeza: Converte valores nulos do Pandas (NaN) para None (NULL no MySQL)
            df_ops = df_ops.where(pd.notnull(df_ops), None)

            cursor.execute("TRUNCATE TABLE operadoras_ativas")
            
            sql_ops = """
                INSERT IGNORE INTO operadoras_ativas 
                (registro_ans, cnpj, razao_social, nome_fantasia, uf) 
                VALUES (%s, %s, %s, %s, %s)
            """
            
            # MAPEAMENTO CORRIGIDO DE ACORDO COM OS CABEÇALHOS DO SEU CSV
            for _, r in df_ops.iterrows():
                cursor.execute(sql_ops, (
                    r['REGISTRO_OPERADORA'], 
                    r['CNPJ'],
                    r['Razao_Social'],       
                    r['Nome_Fantasia'],      
                    r['UF']
                ))

        conn.commit()
        print("✅ Sucesso: Todas as tabelas (Agregada, Histórico e Operadoras) atualizadas!")

    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    import_all_to_mysql()