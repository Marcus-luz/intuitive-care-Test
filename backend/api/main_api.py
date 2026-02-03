from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
from typing import Optional
import os

app = FastAPI(title="Intuitive Care API v2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    # AJUSTE PARA DOCKER: Busca as configurações do docker-compose.yml
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASS", "Marcusluz1!"), 
        database=os.getenv("DB_NAME", "intuitive_care"),
        charset='utf8mb4',           
        use_unicode=True,             
        collation='utf8mb4_general_ci' 
    )

# 4.2. Rota: Listar Operadoras com Paginação (Item 4.2 e 4.3 do PDF)
@app.get("/api/operadoras")
def list_operadoras(
    page: int = Query(1, ge=1), 
    limit: int = Query(10, ge=1, le=100), 
    q: Optional[str] = None
):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        offset = (page - 1) * limit
        where_clause = ""
        params = []
        
        if q:
            # AJUSTE: Agora busca por Razão Social OU CNPJ conforme requisito 4.3 
            where_clause = "WHERE razao_social LIKE %s OR cnpj LIKE %s"
            params = [f"%{q}%", f"%{q}%"]

        cursor.execute(f"SELECT COUNT(*) as total FROM despesas_agregadas {where_clause}", params)
        total = cursor.fetchone()['total']

        sql = f"SELECT * FROM despesas_agregadas {where_clause} LIMIT %s OFFSET %s"
        cursor.execute(sql, params + [limit, offset])
        data = cursor.fetchall()
        
        # Estrutura de Metadados conforme item 4.2.4 do PDF 
        return {
            "data": data,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }
    finally:
        cursor.close()
        conn.close()

# 4.2. Rota: Histórico de Despesas (Item 4.2 e 4.3.2 do PDF)
@app.get("/api/operadoras/historico/{razao_social}")
def get_historico(razao_social: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # O CAST garante que o MySQL envie um número que o JSON entenda como float, eliminando o NaN
        cursor.execute("""
            SELECT trimestre, ano, CAST(valor_despesa AS FLOAT) as valor_despesa 
            FROM despesas_consolidadas 
            WHERE TRIM(razao_social) = TRIM(%s) 
            ORDER BY ano ASC, trimestre ASC
        """, (razao_social,))
        result = cursor.fetchall()
        return result
    finally:
        cursor.close()
        conn.close()

# 4.2. Rota: Estatísticas Agregadas (Item 4.2.3 do PDF)
@app.get("/api/estatisticas")
def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Top 5 operadoras por gasto [cite: 145]
        cursor.execute("SELECT razao_social, total_despesas FROM despesas_agregadas ORDER BY total_despesas DESC LIMIT 5")
        top_5 = cursor.fetchall()
        
        # Distribuição por UF conforme item 4.3 [cite: 171]
        cursor.execute("SELECT uf, SUM(total_despesas) as despesa_uf FROM despesas_agregadas GROUP BY uf")
        uf_dist = cursor.fetchall()
        
        return {
            "top_5": top_5,
            "uf_distribution": uf_dist
        }
    finally:
        cursor.close()
        conn.close()