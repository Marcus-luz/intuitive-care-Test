from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
from typing import Optional

app = FastAPI(title="Intuitive Care API v2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Marcusluz1!", 
        database="intuitive_care",
        charset='utf8mb4',           
        use_unicode=True,             
        collation='utf8mb4_general_ci' 
    )

# 4.2. Rota: Listar Operadoras com Paginação
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
            # CORREÇÃO: Buscando apenas por razao_social, pois cnpj não existe na tabela
            where_clause = "WHERE razao_social LIKE %s"
            params = [f"%{q}%"]

        cursor.execute(f"SELECT COUNT(*) as total FROM despesas_agregadas {where_clause}", params)
        total = cursor.fetchone()['total']

        sql = f"SELECT * FROM despesas_agregadas {where_clause} LIMIT %s OFFSET %s"
        cursor.execute(sql, params + [limit, offset])
        data = cursor.fetchall()
        
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

# 4.2. Rota: Detalhes por Razão Social (Usando como ID)
@app.get("/api/operadoras/{razao_social}")
def get_operadora(razao_social: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM despesas_agregadas WHERE razao_social = %s", (razao_social,))
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Operadora não encontrada")
        return result
    finally:
        cursor.close()
        conn.close()

# 4.2. Rota: Histórico de Despesas
@app.get("/api/operadoras/historico/{razao_social}")
def get_historico(razao_social: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Nota: Ajustado para buscar por Razão Social na tabela de histórico
        cursor.execute("""
            SELECT trimestre, ano, valor_despesa 
            FROM despesas_consolidadas 
            WHERE razao_social = %s 
            ORDER BY ano DESC, trimestre DESC
        """, (razao_social,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

@app.get("/api/estatisticas")
def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT razao_social, total_despesas FROM despesas_agregadas ORDER BY total_despesas DESC LIMIT 5")
        top_5 = cursor.fetchall()
        
        cursor.execute("SELECT uf, SUM(total_despesas) as despesa_uf FROM despesas_agregadas GROUP BY uf")
        uf_dist = cursor.fetchall()
        
        return {
            "top_5": top_5,
            "uf_distribution": uf_dist
        }
    finally:
        cursor.close()
        conn.close()