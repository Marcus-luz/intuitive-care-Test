-- =============================================================================
-- TESTE 3: BANCO DE DADOS - SCRIPT DE CONFIGURAÇÃO (DDL)
-- Objetivo: Criar a estrutura necessária para persistência dos dados da ANS.
-- =============================================================================

-- 1. Criação do Banco de Dados
CREATE DATABASE IF NOT EXISTS intuitive_care;
USE intuitive_care;

-- 2. Tabela de Despesas Consolidadas (Referente ao Item 1.3)
-- Armazena os registros individuais saneados e prontos para consulta.
CREATE TABLE IF NOT EXISTS despesas_consolidadas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cnpj VARCHAR(18) NOT NULL,            -- Mantido como String para preservar zeros à esquerda
    razao_social VARCHAR(255) NOT NULL,
    trimestre VARCHAR(10) NOT NULL,
    ano INT NOT NULL,
    valor_despesa DECIMAL(18, 2) NOT NULL -- DECIMAL garante precisão financeira
);

-- 3. Tabela de Estatísticas Agregadas (Referente ao Item 2.3)
-- Armazena o resultado do enriquecimento e cálculos de média/desvio padrão.
CREATE TABLE IF NOT EXISTS despesas_agregadas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    razao_social VARCHAR(255) NOT NULL,
    uf CHAR(2) NOT NULL,                  -- ISO 3166-2 para estados brasileiros
    total_despesas DECIMAL(18, 2) NOT NULL,
    media_trimestral DECIMAL(18, 2) NOT NULL,
    desvio_padrao DECIMAL(18, 2) DEFAULT 0.00
);

-- =============================================================================
-- OTIMIZAÇÃO (PENSAMENTO CRÍTICO)
-- Índices criados para acelerar as consultas analíticas dos itens 3.4 e 3.5.
-- =============================================================================

-- Índice para acelerar buscas e agrupamentos por ano e operadora (Item 3.4 e 3.5)
CREATE INDEX idx_ano_razao ON despesas_consolidadas(ano, razao_social);

-- Índice para consultas geográficas e por nome na tabela de estatísticas
CREATE INDEX idx_uf_razao ON despesas_agregadas(uf, razao_social);

-- =============================================================================
-- NOTAS DE EXECUÇÃO:
-- 1. Este script deve ser executado antes da importação via LOAD DATA INFILE.
-- 2. Os tipos DECIMAL(18,2) evitam erros de arredondamento comuns em FLOAT/DOUBLE.
-- =============================================================================