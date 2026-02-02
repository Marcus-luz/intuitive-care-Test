import pandas as pd
import mysql.connector
import os

def import_all_to_mysql():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, '..', '..', 'data')
    
    # Conexão com a base de dados utilizando a tua senha
    conn = mysql.connector.connect(
        host="localhost", 
        user="root", 
        password="Marcusluz1!", 
        database="intuitive_care", 
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
        
        # 2. CARREGAR TABELA DE HISTÓRICO (Corrigido para incluir CNPJ)
        path_hist = os.path.join(data_dir, 'historico_final.csv')
        if os.path.exists(path_hist):
            print("Carregando histórico detalhado para os gráficos...")
            df_hist = pd.read_csv(path_hist, encoding='utf-8-sig')
            
            # --- SANEAMENTO DE DADOS ---
            df_hist['ValorDespesas'] = pd.to_numeric(df_hist['ValorDespesas'], errors='coerce').fillna(0)
            df_hist['Trimestre'] = df_hist['Trimestre'].astype(str).str.extract(r'(\d+)').fillna(0).astype(int)
            df_hist['RazaoSocial'] = df_hist['RazaoSocial'].astype(str).str.strip()
            df_hist['CNPJ'] = df_hist['CNPJ'].astype(str).str.strip() # Garante CNPJ limpo

            cursor.execute("TRUNCATE TABLE despesas_consolidadas")
            
            # AJUSTE: SQL agora inclui o campo 'cnpj' para evitar o erro 1364
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

        conn.commit()
        print("✅ Sucesso: Tabelas Agregada e de Histórico atualizadas com CNPJ!")

    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    import_all_to_mysql()