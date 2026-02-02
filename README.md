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

📁 2. Transformação e Validação
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



📁 3. TESTE DE BANCO DE DADOS E ANÁLISE

Nota para o Recrutador (Teste 3): Devido às restrições do MySQL com caminhos absolutos no comando LOAD DATA INFILE, é necessário abrir o arquivo db/import.sql e substituir <CAMINHO_ABSOLUTO_DO_PROJETO> pelo caminho onde o repositório foi clonado em sua máquina.

Trade-off Técnico - Importação de Dados (Item 3.2):

Decisão: Utilizei caminhos absolutos com marcadores no script SQL.

Justificativa: O comando LOAD DATA INFILE do MySQL exige caminhos absolutos por questões de segurança do servidor. Considerei criar um script de importação em Python para automatizar o caminho, mas optei por manter a carga via SQL puro para simplificar a avaliação da estrutura do banco de dados (KISS), documentando claramente a necessidade de ajuste de path no README.

📝 Atualização Final do README (Secção Banco de Dados)
Para demonstrar o seu Pensamento Crítico nesta etapa final do Teste 3, adicione estas justificativas ao seu README.md:

Consultas Analíticas (Itens 3.4 e 3.5):

Decisão: Implementei subconsultas ((SELECT MAX(ano)...)) para filtrar os resultados.

Justificativa: Evita o uso de valores "hardcoded" (fixos), permitindo que o sistema funcione automaticamente para dados de 2024, 2025 ou anos futuros sem necessidade de alteração no código SQL.

Performance:

Decisão: Utilização de agrupamento (GROUP BY) e ordenação (ORDER BY) em colunas indexadas.

Justificativa: Garante que os relatórios de "Top 10" sejam gerados em milissegundos, mesmo que a tabela despesas_consolidadas contenha milhões de registros originais das operadoras da ANS.



📁 4. TESTE DE API E INTERFACE WEB 
Para o item 4.1, utilizaremos o banco de dados MySQL que você já estruturou no Teste 3.

Decisão: Consultas SQL diretas via mysql-connector-python.

Justificativa: Diferente de ler CSVs em tempo real (que consumiria muita memória e IO), o banco de dados nos permite usar índices para buscas rápidas e paginação eficiente no servidor.

4.2. Tarefa de Código: Rota de Listagem com Paginação
Vamos implementar a rota GET /api/operadoras.

Trade-off Técnico 4.2.2: Estratégia de Paginação
Opção Escolhida: Opção A: Offset-based (usando LIMIT e OFFSET).

Justificativa: É a abordagem mais adequada para o volume de dados das operadoras da ANS e a mais fácil de integrar com componentes de tabela no Vue.js. Como os dados não sofrem inserções em alta frequência (são cargas trimestrais), o problema de "pular itens" ou a perda de performance de grandes offsets é irrelevante neste cenário.

Trade-off Técnico 4.2.4: Estrutura de Resposta
Opção Escolhida: Opção B: Dados + Metadados.

Justificativa: Para o Vue.js construir a paginação (botões "Anterior/Próximo" e números de página), ele precisa saber o total de registros. Retornar um objeto { data: [...], total: 100 } é o padrão de mercado.

Para garantir que você passe na avaliação de "Pensamento Crítico", certifique-se de que o seu README contenha estas justificativas exatas baseadas no seu código:

Framework: Escolhido FastAPI pela performance assíncrona e geração automática de Swagger (acessível em /docs).

Paginação: Escolhida Offset-based pela facilidade de implementação no SQL e compatibilidade direta com componentes de tabela do Vue.js.

Estatísticas: Escolhida a Opção C (Pré-calcular). Como os dados da ANS são trimestrais e não mudam em tempo real, calculamos as médias/desvios no Python (Teste 2) e salvamos no banco para que a API seja extremamente rápida.

Resposta da API: Escolhida a Opção B (Dados + Metadados) para que o Frontend saiba exatamente quantas páginas criar na interface sem precisar de uma segunda requisição.
```
Ao documentar esta estrutura no Item 4.4, podes justificar desta forma:

Trade-off: Organização de Pastas (Arquitetura Modular)

Abordagem Escolhida: Separação entre core (Lógica de Negócio/ETL) e api (Camada de Transporte/FastAPI).

Justificativa: Optei por esta estrutura para garantir que a lógica de processamento de dados da ANS seja independente da interface de entrega. Isso facilita a manutenção e permite que a API consuma os dados processados sem precisar de conhecer as regras complexas de extração de CSVs/ZIPs.

Trade-offs Técnicos - Frontend (Para o seu README)
Aqui estão as justificativas que você deve incluir no item 4.4 para demonstrar pensamento crítico:

4.3.1 Busca/Filtro: Opção A (Busca no Servidor).

Justificativa: Como o volume de dados das operadoras da ANS pode ser massivo, filtrar milhares de linhas no navegador prejudicaria a experiência do usuário (UX). A busca no servidor via FastAPI/SQL é mais performática e escalável.

4.3.2 Gerenciamento de Estado: Opção C (Composables).

Justificativa: Para uma aplicação deste porte, o uso de Pinia ou Vuex seria um excesso de complexidade (overengineering). Composables oferecem uma forma limpa e nativa do Vue 3 para compartilhar lógica de estado entre a tabela e os gráficos.

4.3.3 Performance da Tabela: Paginação Server-side.

Justificativa: Em vez de carregar todos os registros, solicitamos apenas 10 por vez. Isso garante um carregamento instantâneo e baixo consumo de memória, independentemente do tamanho do banco de dados.


4.3.1. Estratégia de Busca/Filtro
Nossa Escolha: Opção A: Busca no servidor.

Como está no código: No seu Dashboard.vue, a função fetchData envia o parâmetro q para a API (/api/operadoras?q=${search.value}). O banco de dados faz o filtro usando LIKE.

Justificativa para o seu README: "Escolhi a busca no servidor (SQL LIKE) porque os dados da ANS são volumosos. Filtrar no cliente exigiria baixar milhares de registros, o que degradaria a experiência do usuário (UX) e consumiria memória excessiva do navegador. No servidor, a resposta é rápida e escalável."

4.3.2. Gerenciamento de Estado
Nossa Escolha: Opção C: Composables (Vue 3).

Como está no código: Estamos usando a Composition API (ref, computed, watch). No exemplo que te passei anteriormente, sugeri o arquivo useOperadoras.js para isolar a lógica.

Justificativa para o seu README: "Utilizei Composables por ser a forma mais moderna e leve de gerenciar estado no Vue 3. Para esta aplicação, o uso de Pinia ou Vuex seria um exagero de complexidade (overengineering), violando o princípio KISS. Composables permitem compartilhar lógica de forma modular sem o peso de uma biblioteca externa."

4.3.3. Performance da Tabela
Nossa Escolha: Paginação Server-side (Renderização por Lotes).

Como está no código: A tabela exibe apenas 10 registros por vez (limit=10). Quando o usuário clica em "Próximo", pedimos um novo lote para a API.

Justificativa para o seu README: "Para garantir alta performance, implementei a paginação no servidor. Isso garante que o navegador renderize apenas 10 elementos por vez, mantendo a interface instantânea mesmo que o banco de dados contenha milhões de operadoras. Diferente do Infinite Scroll, a paginação clássica facilita a localização exata de dados financeiros pelo usuário."

4. Análise Crítica: Mensagens Específicas vs Genéricas
No seu README, você deve justificar que escolheu mensagens específicas.

Sua justificativa: "Optei por mensagens específicas (ex: 'Verifique se o Backend está ativo') em vez de genéricas (ex: 'Erro') para melhorar a Experiência do Usuário (UX). Isso permite que o usuário identifique se o problema é de rede, se o sistema está fora do ar ou se apenas não existem dados para o filtro aplicado."


............................
Por que estas bibliotecas? (Justificativa Técnica)
Para o seu README demonstrar maturidade, é bom saber o papel de cada uma:

fastapi & uvicorn: O FastAPI é o framework moderno para sua API, e o Uvicorn é o servidor ASGI que a coloca no ar.

pandas: Essencial para o Teste 2. Ele lida com a leitura dos CSVs, normalização de colunas e os cálculos de média e desvio padrão de forma performática.

requests & beautifulsoup4: O requests baixa os arquivos do site da ANS, e o beautifulsoup4 (com o parser lxml) ajuda o seu crawler a encontrar os links de download dentro do HTML da página.

mysql-connector-python: É o driver oficial para o Python conversar com o seu banco MySQL, permitindo o uso do dictionary=True que usamos nas rotas da API.

python-dotenv: Recomendado para que você não deixe sua senha do banco de dados exposta diretamente no código (você as coloca em um arquivo .env).
```