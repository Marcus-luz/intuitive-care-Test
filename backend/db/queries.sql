-- =============================================================================
-- TESTE 3: BANCO DE DADOS - CONSULTAS ANALÍTICAS (DQL)
-- Objetivo: Responder aos quesitos de negócio 3.4 e 3.5 do desafio ANS.
-- =============================================================================

USE intuitive_care;

-- -----------------------------------------------------------------------------
-- Quais as 10 operadoras que mais tiveram despesas no último ano?
-- -----------------------------------------------------------------------------
-- Justificativa: Utilizamos uma subquery para identificar dinamicamente o ano 
-- mais recente presente na base, garantindo que o relatório seja resiliente.
-- -----------------------------------------------------------------------------
SELECT 
    razao_social, 
    SUM(valor_despesa) AS total_despesas
FROM despesas_consolidadas
WHERE ano = (SELECT MAX(ano) FROM despesas_consolidadas)
GROUP BY razao_social
ORDER BY total_despesas DESC
LIMIT 10;

-- -----------------------------------------------------------------------------
-- Quais as 10 operadoras que mais tiveram média de despesas no último ano?
-- -----------------------------------------------------------------------------
-- Justificativa: O cálculo da média (AVG) revela operadoras que mantêm 
-- uma despesa média elevada por trimestre.
-- -----------------------------------------------------------------------------
SELECT 
    razao_social, 
    AVG(valor_despesa) AS media_despesas
FROM despesas_consolidadas
WHERE ano = (SELECT MAX(ano) FROM despesas_consolidadas)
GROUP BY razao_social
ORDER BY media_despesas DESC
LIMIT 10;

-- -----------------------------------------------------------------------------
-- Query 1: Quais as 5 operadoras com maior crescimento percentual de despesas 
-- entre o primeiro e o último trimestre analisado (1T vs 3T de 2025)?
-- -----------------------------------------------------------------------------
-- Tratamento de dados ausentes: Operadoras sem dados no 1T são desconsideradas, 
-- pois o cálculo de crescimento exige uma base inicial para evitar divisão por zero.
-- -----------------------------------------------------------------------------
WITH despesas_trimestrais AS (
    SELECT 
        razao_social,
        SUM(CASE WHEN trimestre LIKE '%1%' THEN valor_despesa ELSE 0 END) as v1t,
        SUM(CASE WHEN trimestre LIKE '%3%' THEN valor_despesa ELSE 0 END) as v3t
    FROM despesas_consolidadas
    WHERE ano = 2025
    GROUP BY razao_social
)
SELECT 
    razao_social,
    v1t as valor_1t,
    v3t as valor_3t,
    ((v3t - v1t) / v1t) * 100 as crescimento_percentual
FROM despesas_trimestrais
WHERE v1t > 0 
ORDER BY crescimento_percentual DESC
LIMIT 5;

-- -----------------------------------------------------------------------------
-- Query 2: Qual a distribuição de despesas por UF? Liste os 5 estados com 
-- maiores despesas totais e a média por operadora em cada um.
-- -----------------------------------------------------------------------------
-- Justificativa: Cruzamos a tabela de fatos (despesas) com a de operadoras via 
-- CNPJ para obter a UF. A média por operadora normaliza o custo por estado.
-- -----------------------------------------------------------------------------
SELECT 
    o.uf,
    SUM(d.valor_despesa) as despesa_total,
    AVG(d.valor_despesa) as media_por_operadora
FROM despesas_consolidadas d
JOIN operadoras_ativas o ON d.cnpj = o.cnpj
GROUP BY o.uf
ORDER BY despesa_total DESC
LIMIT 5;

-- -----------------------------------------------------------------------------
-- Query 3: Quantas operadoras tiveram despesas acima da média geral em pelo 
-- menos 2 dos 3 trimestres analisados?
-- -----------------------------------------------------------------------------
-- Trade-off técnico: Optou-se pelo uso de CTEs (Common Table Expressions) para 
-- separar o cálculo da média global da verificação trimestral. Isso aumenta a 
-- legibilidade e manutenibilidade do código com impacto mínimo em performance.
-- -----------------------------------------------------------------------------
WITH media_global AS (
    SELECT AVG(valor_despesa) as media FROM despesas_consolidadas
),
status_por_trimestre AS (
    SELECT 
        razao_social,
        trimestre,
        SUM(valor_despesa) as total_tri
    FROM despesas_consolidadas
    GROUP BY razao_social, trimestre
)
SELECT COUNT(*) as qtd_operadoras_consistentes
FROM (
    SELECT razao_social
    FROM status_por_trimestre
    WHERE total_tri > (SELECT media FROM media_global)
    GROUP BY razao_social
    HAVING COUNT(trimestre) >= 2
) as sub_analise;