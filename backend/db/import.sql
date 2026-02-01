-- =============================================================================
-- TESTE 3: BANCO DE DADOS - SCRIPT DE IMPORTAÇÃO (DML)
-- Objetivo: Carregar os dados processados pelos scripts Python para o MySQL.
-- =============================================================================

USE intuitive_care;

-- 1. Importação das Despesas Consolidadas (Resultado do Teste 1.3)
-- Arquivo movido para a pasta de permissão segura do MySQL (secure-file-priv)
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/consolidado_despesas.csv'
INTO TABLE despesas_consolidadas
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(cnpj, razao_social, trimestre, ano, valor_despesa);

-- 2. Importação das Estatísticas Agregadas (Resultado do Teste 2.3)
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/despesas_agregadas.csv'
INTO TABLE despesas_agregadas
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(razao_social, uf, total_despesas, media_trimestral, desvio_padrao);

-- =============================================================================
-- NOTAS TÉCNICAS IMPORTANTES:
-- =============================================================================
-- 1. CAMINHOS: O MySQL exige o uso de barras normais (/) nos caminhos.
-- 2. LOCALIZAÇÃO: Os arquivos CSV devem estar fisicamente dentro da pasta Uploads
--    indicada acima para que o comando funcione sem erros de permissão.
-- 3. ENCODING: Os arquivos foram salvos em UTF-8 pelo Python para evitar erros
--    em caracteres especiais de 'Razão Social'.
-- =============================================================================