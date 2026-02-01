Teste de Entrada - Intuitive Care (v2.0)
Candidato: Vinicios Stack: Python, Pandas, BeautifulSoup, Requests.

1. Visão Geral
Este projeto automatiza a extração, transformação e análise de dados de demonstrações contábeis e cadastrais da ANS (Agência Nacional de Saúde Suplementar). O sistema foi projetado seguindo princípios de Clean Architecture e KISS, garantindo modularidade e resiliência no processamento de grandes volumes de dados.

2. Estrutura do Projeto
O projeto está organizado de forma a separar as responsabilidades de infraestrutura (Extração) das regras de negócio (Transformação):

main.py: Ponto de entrada (Entry Point) que orquestra todo o pipeline.

backend/core/crawler.py: Responsável pela navegação e download automatizado dos dados.

backend/core/processor.py: Realiza a extração de ZIPs, normalização de colunas e limpeza financeira inicial.

backend/core/enricher.py: Executa o join entre dados contábeis e cadastrais (Enriquecimento).

backend/core/validators.py: Centraliza a lógica de validação de CNPJ e regras de negócio.

backend/core/aggregator.py: Gera relatórios estatísticos (Média e Desvio Padrão).

3. Como Executar
Certifique-se de ter o Python 3.10+ instalado.

Instale as dependências: pip install pandas requests beautifulsoup4.

Na raiz do projeto, execute:

Bash
python main.py
Os resultados serão gerados na pasta /data.

4. Trade-offs Técnicos e Justificativas (Análise Crítica)
Teste 1: Integração e Saneamento
Navegação Programática vs. URL Estática:

Decisão: Implementado crawler que lê o HTML do portal da ANS.

Justificativa: Garante resiliência caso a ANS altere o nome dos arquivos ou a estrutura de pastas, atendendo ao requisito de "identificação por conteúdo".

Processamento em Chunks (Memória):

Decisão: Uso de chunksize=50000 no Pandas.

Justificativa: Permite o processamento de arquivos contábeis pesados (milhões de linhas) sem estourar a memória RAM do servidor (Trade-off: Baixo consumo de RAM vs. Tempo de I/O).

Teste 2: Transformação e Validação
Validação Estrita de CNPJ:

Decisão: Registros com CNPJs que falham no dígito verificador são descartados.

Justificativa: Prioriza a qualidade do dado para o Banco de Dados (Teste 3), evitando a poluição de registros não auditáveis.

Join de Enriquecimento (Inner Join):

Decisão: Utilizado how='inner' no cruzamento com o cadastro de operadoras.

Justificativa: Dados financeiros sem correspondência no cadastro ativo não possuem UF ou Razão Social válida, sendo irrelevantes para as agregações estatísticas do item 2.3.

Cálculo de Desvio Padrão:

Decisão: Substituição de valores NaN por 0 no desvio padrão.

Justificativa: Operadoras com apenas um registro trimestral não possuem variância estatística; o preenchimento com zero mantém a integridade numérica do relatório final.

5. Tratamento de Erros
Resiliência de Colunas: Implementado mapeamento por "Sinônimos" (Synonyms Mapping) para identificar colunas mesmo que o nome mude entre trimestres (ex: REG_ANS vs REGISTRO_OPERADORA).

Integridade de Caminhos: Uso de injeção de dependência para caminhos de diretórios, resolvendo conflitos de execução em diferentes sistemas operacionais.