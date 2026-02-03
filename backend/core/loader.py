import pandas as pd
import mysql.connector
import os
from dotenv import load_dotenv

# Carrega as variáveis definidas no arquivo .env
load_dotenv()

def import_all_to_mysql():
    # Definição de caminhos
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, '..', '..', 'data')
    
    # BUSCA DAS VARIÁVEIS DE AMBIENTE (Sem senhas expostas no código)
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASS = os.getenv("DB_PASS")  # O valor virá do .env
    DB_NAME = os.getenv("DB_NAME", "intuitive_care")
    DB_PORT = os.getenv("DB_PORT", "3306")

    # Validação simples
    if not DB_PASS:
        print("⚠️ Aviso: A variável DB_PASS não foi encontrada no .env ou no sistema.")

    try:
        # Conexão com o Banco de Dados
        conn = mysql.connector.connect(
            host=DB_HOST, 
            port=DB_PORT,
            user=DB_USER, 
            password=DB_PASS, 
            database=DB_NAME, 
            charset='utf8mb4'
        )
        cursor = conn.cursor()

        # 1. CARREGAR TABELA AGREGADA
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
        
        # 2. CARREGAR TABELA DE HISTÓRICO
        path_hist = os.path.join(data_dir, 'historico_final.csv')
        if os.path.exists(path_hist):
            print("Carregando histórico detalhado...")
            df_hist = pd.read_csv(path_hist, encoding='utf-8-sig')
            
            df_hist['ValorDespesas'] = pd.to_numeric(df_hist['ValorDespesas'], errors='coerce').fillna(0)
            df_hist['Trimestre'] = df_hist['Trimestre'].astype(str).str.extract(r'(\d+)').fillna(0).astype(int)
            
            cursor.execute("TRUNCATE TABLE despesas_consolidadas")
            
            sql_hist = """
                INSERT INTO despesas_consolidadas 
                (cnpj, razao_social, trimestre, ano, valor_despesa) 
                VALUES (%s, %s, %s, %s, %s)
            """
            for _, r in df_hist.iterrows():
                cursor.execute(sql_hist, (
                    str(r['CNPJ']), r['RazaoSocial'], 
                    int(r['Trimestre']), int(r['Ano']), float(r['ValorDespesas'])
                ))

        # 3. CARREGAR CADASTRO DE OPERADORAS
        path_ops = os.path.join(data_dir, 'operadoras_ativas.csv')
        if os.path.exists(path_ops):
            print("Carregando cadastro de operadoras...")
            df_ops = pd.read_csv(path_ops, sep=';', encoding='latin1', dtype=str)
            df_ops = df_ops.where(pd.notnull(df_ops), None)

            cursor.execute("TRUNCATE TABLE operadoras_ativas")
            
            sql_ops = """
                INSERT IGNORE INTO operadoras_ativas 
                (registro_ans, cnpj, razao_social, nome_fantasia, uf) 
                VALUES (%s, %s, %s, %s, %s)
            """
            for _, r in df_ops.iterrows():
                cursor.execute(sql_ops, (
                    r['REGISTRO_OPERADORA'], r['CNPJ'], r['Razao_Social'], 
                    r['Nome_Fantasia'], r['UF']
                ))

        conn.commit()
        print("✅ Sucesso: Banco de dados populado corretamente!")

    except mysql.connector.Error as err:
        print(f"❌ Erro de Banco de Dados: {err}")
    except Exception as e:
        print(f"❌ Erro inesperado na importação: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    import_all_to_mysql()