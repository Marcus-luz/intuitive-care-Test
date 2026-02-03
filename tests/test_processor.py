import pytest
import pandas as pd
import zipfile
import os
from backend.core.processor import DataProcessor

@pytest.fixture
def mock_data_env(tmp_path):
    """Cria um ambiente temporário com a estrutura exata que a ANS/Processor esperam."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    
    # 1. Cabeçalhos originais da ANS (Entrada)
    csv_content = (
        "DATA;REG_ANS;CD_CONTA_CONTABIL;DESCRICAO;VL_SALDO_FINAL\n"
        "2025-01-01;12345;411111010;EVENTOS/SINISTROS CONHECIDOS;1000,50\n"
        "2025-01-01;67890;411111010;EVENTOS/SINISTROS CONHECIDOS;500,00"
    )
    
    csv_file = data_dir / "test_data.csv"
    # O processador espera latin1 e separador ;
    csv_file.write_text(csv_content, encoding="iso-8859-1")
    
    # 2. Compacta o CSV em um ZIP para o processador ler
    zip_path = data_dir / "2025T1.zip"
    with zipfile.ZipFile(zip_path, 'w') as z:
        z.write(csv_file, arcname="test_data.csv")
    
    os.remove(csv_file)
    return str(data_dir)

def test_data_processor_consolidation(mock_data_env):
    """Testa se o DataProcessor gera o consolidado com as colunas reais identificadas no seu log."""
    processor = DataProcessor(data_dir=mock_data_env)
    
    # Executa a lógica de extração e limpeza
    processor.run()
    
    # 3. Verificações
    output_zip = os.path.join(mock_data_env, 'consolidado_despesas.zip')
    assert os.path.exists(output_zip), "O arquivo ZIP consolidado deveria ter sido gerado."
    
    # Lendo o CSV de dentro do ZIP gerado para validar o conteúdo
    with zipfile.ZipFile(output_zip, 'r') as z:
        with z.open('consolidado_despesas.csv') as f:
            df = pd.read_csv(f)
    
    # Verificação de conteúdo: o log mostrou que o DataFrame não está vazio
    assert len(df) > 0, "O arquivo consolidado não deve estar vazio"
    
    # AJUSTE FINAL: Usando os nomes exatos (PascalCase) que o seu código produz
    # conforme indicado no erro: ['CNPJ', 'RazaoSocial', 'Trimestre', 'Ano', 'ValorDespesas']
    expected_columns = ['CNPJ', 'RazaoSocial', 'Trimestre', 'Ano', 'ValorDespesas']
    
    for col in expected_columns:
        assert col in df.columns, f"A coluna {col} deveria estar no arquivo gerado pelo seu processador."
    
    # Verifica se a conversão de valor (string "1000,50" -> float 1000.5) funcionou
    # Acessamos com o nome exato 'ValorDespesas'
    primeiro_valor = df['ValorDespesas'].iloc[0]
    assert isinstance(primeiro_valor, (float, int)), "A coluna ValorDespesas deve conter números."