-- =============================================================================
-- TESTE 3: BANCO DE DADOS - CONSULTAS ANALÍTICAS (DQL)
-- Objetivo: Responder aos quesitos de negócio 3.4 e 3.5 do desafio ANS.
-- =============================================================================

USE intuitive_care;

-- -----------------------------------------------------------------------------
-- 3.4: Quais as 10 operadoras que mais tiveram despesas no último ano?
-- -----------------------------------------------------------------------------
-- Justificativa: Utilizamos uma subquery para identificar dinamicamente o ano 
-- mais recente presente na base, garantindo que o relatório seja resiliente 
-- a novos carregamentos de dados.
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
-- 3.5: Quais as 10 operadoras que mais tiveram média de despesas no último ano?
-- -----------------------------------------------------------------------------
-- Justificativa: O cálculo da média (AVG) revela operadoras que, independente 
-- do volume total, mantêm uma despesa média elevada por trimestre/conta.
-- -----------------------------------------------------------------------------
SELECT 
    razao_social, 
    AVG(valor_despesa) AS media_despesas
FROM despesas_consolidadas
WHERE ano = (SELECT MAX(ano) FROM despesas_consolidadas)
GROUP BY razao_social
ORDER BY media_despesas DESC
LIMIT 10;