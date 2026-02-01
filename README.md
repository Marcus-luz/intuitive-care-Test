🚀 Teste de Entrada - Intuitive Care (v2.0)
Candidato: Vinicios

Stack Técnica: Python, Pandas, BeautifulSoup, Requests.

1. Visão Geral
Este projeto automatiza a extração, transformação e análise de dados de demonstrações contábeis e cadastrais da ANS (Agência Nacional de Saúde Suplementar). O sistema foi projetado seguindo princípios de Clean Architecture e KISS (Keep It Simple, Stupid), garantindo modularidade e resiliência no processamento de grandes volumes de dados.

2. Estrutura do Projeto
A arquitetura separa rigorosamente as responsabilidades de infraestrutura (Extração) das regras de negócio (Transformação e Validação):

main.py: Ponto de entrada (Entry Point) que orquestra todo o pipeline de dados.

backend/core/crawler.py: Responsável pela navegação programática e download automatizado.

backend/core/processor.py: Executa a extração de ZIPs, normalização de colunas e limpeza financeira.

backend/core/enricher.py: Realiza o join entre dados contábeis e cadastrais (Enriquecimento).

backend/core/validators.py: Centraliza a lógica de validação de CNPJ e regras de negócio.

backend/core/aggregator.py: Motor de cálculo para relatórios estatísticos (Média e Desvio Padrão).

3. Como Executar
Ambiente: Certifique-se de ter o Python 3.10+ instalado em sua máquina.

Dependências: É necessário que as bibliotecas pandas, requests e beautifulsoup4 estejam disponíveis no ambiente.

Execução: Na raiz do projeto, execute o comando: python main.py

Saída: Os resultados finais serão gerados automaticamente na pasta /data.

4. Trade-offs Técnicos e Justificativas (Análise Crítica)
O desenvolvimento foi pautado pela tomada de decisões técnicas fundamentadas em cada etapa do desafio:

📁 Teste 1: Integração e Saneamento
Navegação Programática vs. URL Estática:

Decisão: Implementação de um crawler que lê o HTML do portal da ANS.

Justificativa: Garante resiliência total caso a ANS altere nomes de arquivos ou estruturas de pastas, cumprindo o requisito de "identificação por conteúdo".

Processamento em Chunks (Memória):

Decisão: Utilização de chunksize=50000 no processamento via Pandas.

Justificativa: Permite processar arquivos contábeis extremamente pesados sem comprometer a memória RAM, otimizando o tempo de I/O em relação ao consumo de hardware.

⚖️ Teste 2: Transformação e Validação
Validação Estrita de CNPJ:

Decisão: Registros com CNPJs que falham no cálculo do dígito verificador são descartados.

Justificativa: Prioriza a integridade dos dados para a etapa de Banco de Dados (Teste 3), eliminando ruídos e inconsistências na origem.

Join de Enriquecimento (Inner Join):

Decisão: Uso do método how='inner' no cruzamento com o cadastro de operadoras.

Justificativa: Registros financeiros sem correspondência ativa no cadastro da ANS carecem de UF ou Razão Social válida, tornando-os irrelevantes para as agregações estatísticas finais.

Cálculo de Desvio Padrão:

Decisão: Substituição técnica de valores NaN por 0 no cálculo do desvio padrão.

Justificativa: Operadoras com apenas um registro trimestral não possuem variância estatística; o preenchimento com zero preserva a precisão do relatório final.

5. Tratamento de Erros e Resiliência
Mapeamento de Sinônimos: Implementado sistema de Synonyms Mapping para identificar colunas de forma dinâmica (ex: REG_ANS vs REGISTRO_OPERADORA), suportando variações nos cabeçalhos entre diferentes trimestres.

Integridade de Caminhos: Utilização de injeção de dependência para caminhos de diretórios, garantindo que o software opere corretamente em diferentes sistemas operacionais e ambientes de execução.
