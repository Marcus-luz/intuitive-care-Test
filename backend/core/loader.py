import pandas as pd
import mysql.connector
import os

def import_csv_to_mysql():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, '..', '..', 'data', 'despesas_agregadas.csv')
    
    print(f"Buscando arquivo em: {csv_path}")

    if not os.path.exists(csv_path):
        print(f"ERRO: O arquivo {csv_path} não foi encontrado!")
        return

    # Leitura do CSV
    df = pd.read_csv(csv_path, encoding='utf-8-sig')

    # Conexão com o Banco
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Marcusluz1!", 
        database="intuitive_care", #
        charset='utf8mb4'
    )
    cursor = conn.cursor()

    try:
        print("Limpando dados antigos...")
        cursor.execute("TRUNCATE TABLE despesas_agregadas")

        print("Importando dados com acentuação corrigida...")
        sql = """
            INSERT INTO despesas_agregadas 
            (razao_social, uf, total_despesas, media_trimestral, desvio_padrao) 
            VALUES (%s, %s, %s, %s, %s)
        """
        
        for _, row in df.iterrows():
            cursor.execute(sql, (
                row['RazaoSocial'], 
                row['UF'], 
                row['Total_Despesas'], 
                row['Media_Trimestral'], 
                row['Desvio_Padrao']
            ))

        conn.commit()
        print(f"Sucesso! {len(df)} registros importados corretamente.")

    except Exception as e:
        print(f"Erro na importação: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    import_csv_to_mysql()