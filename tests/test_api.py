import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from backend.api.main_api import app

# Criamos o cliente de teste
client = TestClient(app)

def test_get_operadoras_pagination():
    """Teste para verificar se a rota de listagem retorna dados e paginação corretos."""
    
    # Mockando a conexão com o banco de dados
    with patch("backend.api.main_api.get_db_connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.return_value.cursor.return_value = mock_cursor
        
        # Simulando o retorno do fetchall (lista de operadoras)
        mock_cursor.fetchall.return_value = [
            {"id": 1, "razao_social": "OPERADORA TESTE A", "uf": "BA"},
            {"id": 2, "razao_social": "OPERADORA TESTE B", "uf": "SP"}
        ]
        # Simulando o retorno do count (total de registros)
        mock_cursor.fetchone.return_value = {"total": 2}

        # Fazendo a requisição para a API
        response = client.get("/api/operadoras?page=1&limit=10")

        # Asserções
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["total"] == 2
        assert len(json_data["data"]) == 2
        assert json_data["data"][0]["razao_social"] == "OPERADORA TESTE A"

def test_get_estatisticas_contrato():
    """Verifica se a rota de estatísticas retorna as chaves JSON esperadas pelo Frontend."""
    
    with patch("backend.api.main_api.get_db_connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.return_value.cursor.return_value = mock_cursor
        
        # Simulando as duas queries que a rota faz (Top 5 e Distribuição UF)
        mock_cursor.fetchall.side_effect = [
            [{"razao_social": "Op 1", "total_despesas": 1000.0}], # Resultado da primeira query
            [{"uf": "RJ", "despesa_uf": 5000.0}]                # Resultado da segunda query
        ]

        response = client.get("/api/estatisticas")
        
        assert response.status_code == 200
        data = response.json()
        assert "top_5" in data
        assert "uf_distribution" in data
        assert data["uf_distribution"][0]["uf"] == "RJ"

def test_operadora_nao_encontrada():
    """Valida o tratamento de erro quando uma operadora não existe."""
    
    with patch("backend.api.main_api.get_db_connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [] # Simulando operadora não encontrada

        response = client.get("/api/operadoras/historico/EMPRESA_INEXISTENTE")
        
        # Se sua rota retorna lista vazia em vez de 404:
        assert response.status_code == 200
        assert response.json() == []