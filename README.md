## 🚀 Desafio Técnico - Estágio em Tecnologia (v2.0)
Candidato: Marcus Vinicisu da Luz Arzújo

Stack Principal: Python, FastAPI, Vue.js 3, SQL (MySQL).

Este repositório contém a solução do desafio técnico para a Intuitive Care. O projeto automatiza o pipeline de dados da ANS, desde a coleta bruta via Scraping até a visualização em um Dashboard moderno.


................................................................................................................................................................

## 🏗️ 1. Visão Geral e Arquitetura
A solução foi desenhada seguindo os princípios KISS (Keep It Simple, Stupid) e Clean Code, garantindo que o sistema seja modular, fácil de testar e manter.

Divisão de Responsabilidades:

Pipeline ETL: Extração, Limpeza e Agregação de dados.

Database: Armazenamento relacional com foco em integridade e performance.

API: Backend assíncrono para distribuição de dados.

Frontend: Interface reativa para consumo e análise.

................................................................................................................................................................

## 📂 2. Estrutura do Repositório

├── backend/
│   ├── api/            # Servidor FastAPI e definições de rotas
│   ├── core/           # Pipeline de Dados (Crawler, Processor, Aggregator)
│   └── db/             # Scripts SQL (Setup, Import e Queries Analíticas)
├── data/               # Repositório de arquivos (Brutos e Processados)
├── frontend/           # Aplicação Vue.js 3 (Vite + Tailwind CSS)
├── run_etl.py          # Orquestrador do pipeline (Testes 1 e 2)
└── requirements.txt    # Dependências do ecossistema Python


...........................................................................................................................
## 🏗️ 1. Teste de Integração com API Pública (Web Scraping)

🎯 Objetivo
O objetivo deste módulo é automatizar a coleta de dados públicos do portal da ANS (Agência Nacional de Saúde Suplementar). O pipeline identifica, baixa e prepara os dados de Operadoras Ativas e seus respectivos históricos contábeis.

## 🛠️ Implementação Técnica
A lógica central reside no arquivo backend/core/crawler.py. O script utiliza as bibliotecas requests para requisições HTTP e BeautifulSoup4 para o parsing do HTML.

O fluxo de execução segue estes passos:

Navegação Programática: O crawler acessa a página inicial de dados abertos da ANS.

Identificação Dinâmica: Em vez de usar URLs estáticas (que quebram frequentemente), o código busca pelo padrão de texto "Relatório de dados cadastrais" e "Demonstrações Contábeis" para localizar os links de download.

Gestão de Downloads: Os arquivos são baixados e armazenados temporariamente na pasta data/raw/.

Extração Automatizada: Como os dados contábeis são fornecidos em arquivos .zip, o módulo utiliza a biblioteca zipfile para extrair os arquivos .csv de forma automática.

## ⚖️ Trade-offs Técnicos e Justificativas
Seguindo os critérios de avaliação de Praticidade (KISS) e Pensamento Crítico, abaixo detalho as decisões tomadas:

1. BeautifulSoup4 vs. Selenium
Escolha: BeautifulSoup4.

Justificativa: O portal da ANS fornece os links diretamente no HTML estático da página, sem dependência pesada de renderização via JavaScript (SPA). Utilizar Selenium seria um "over-engineering" que adicionaria complexidade desnecessária (instalação de drivers, maior consumo de memória e tempo de execução mais lento). O BeautifulSoup atende ao princípio KISS, sendo mais leve e rápido.

2. Localização de Links por Texto vs. Seletores CSS/XPath
Escolha: Busca baseada em texto dinâmico.

Justificativa: Portais governamentais costumam sofrer alterações frequentes de layout (mudança de IDs de divs ou classes CSS). Ao buscar pelo link que contém o texto "Relatório de dados cadastrais", o crawler torna-se mais resiliente a mudanças puramente visuais na página, garantindo que o teste de Funcionalidade continue passando a longo prazo.

3. Tratamento de Arquivos ZIP em Disco vs. Memória
Escolha: Extração em Disco (data/).

Justificativa: Embora processar arquivos diretamente na memória (usando io.BytesIO) seja tecnicamente elegante, optei por salvar os arquivos no diretório data/. Isso permite que o avaliador inspecione os arquivos brutos baixados (Auditabilidade) e evita problemas de estouro de memória (RAM) caso o volume de dados contábeis da ANS cresça exponencialmente nos próximos trimestres.

## 🛡️ Tratamento de Erros e Casos Extremos
Para demonstrar a Qualidade do Código, foram implementadas as seguintes validações:

Timeout de Conexão: Tratamento para casos onde o servidor da ANS está instável ou fora do ar, evitando que o script fique travado indefinidamente.

Verificação de Integridade: Antes de processar, o script valida se o download foi concluído e se o arquivo extraído possui a extensão .csv esperada.

SSL Verification: Implementado bypass seguro para possíveis erros de certificados SSL comuns em domínios .gov.br.

## 🚀 Como executar esta etapa individualmente
Caso queira validar apenas a coleta de dados:

# Navegue até a raiz do projeto e execute:
python backend/core/crawler.py
Os arquivos resultantes estarão disponíveis em /data.

                  ou

# 🚀 5. Executar o Pipeline de Dados (Testes 1 e 2)
python run_etl.py
Este comando baixará os arquivos da ANS e gerará os CSVs higienizados na pasta /data.

...........................................................................................................................

## ⚙️ 2. Teste de Transformação e Validação de Dados (ETL)
🎯 Objetivo
Transformar os arquivos brutos (CSV/ZIP) baixados do portal da ANS em um conjunto de dados higienizado, agregando métricas estatísticas (Média e Desvio Padrão) e enriquecendo as informações financeiras com dados cadastrais das operadoras.

🛠️ Implementação do Pipeline
A lógica foi fragmentada em módulos especializados para garantir a Qualidade do Código e facilidade de manutenção:

processor.py (Ingestão e Limpeza): Realiza a leitura dos CSVs tratando inconsistências de delimitadores (; vs ,) e codificação (Encoding).

validators.py (Sanitização): Converte strings monetárias brasileiras (ex: 1.250,50) em floats computáveis e remove registros com campos essenciais nulos.

aggregator.py (Processamento Estatístico): Agrupa os dados por Registro ANS e calcula a média e o desvio padrão das despesas dos últimos 3 trimestres.

enricher.py (Cruzamento de Dados): Realiza um Join (Merge) entre o resultado financeiro e a tabela de "Operadoras Ativas" para incluir Nome Fantasia e CNPJ.

## ⚖️ Trade-offs Técnicos e Justificativas
1. Uso da Biblioteca Pandas vs. CSV Nativo
Escolha: Pandas.

Justificativa: Seguindo o critério de Praticidade (KISS), o Pandas oferece funções vetorizadas que substituem loops complexos de Python nativo. Isso torna o código 10x mais curto e significativamente mais rápido para processar milhares de linhas, além de facilitar operações de agrupamento (groupby) e cruzamento de tabelas (merge).

2. Normalização de Cabeçalhos
Decisão: Mapeamento explícito de colunas.

Justificativa (Pensamento Crítico): Os arquivos da ANS muitas vezes alteram o nome das colunas entre um trimestre e outro (ex: "Data" para "Data_Base"). Implementei um mapeador dinâmico que normaliza esses nomes, garantindo que o pipeline não quebre quando novos dados forem publicados.

3. Tratamento de Encoding (ISO-8859-1 para UTF-8)
Escolha: Detecção e conversão forçada.

Justificativa: Arquivos governamentais no Brasil frequentemente utilizam codificações legadas. O código força a conversão para UTF-8 durante a leitura para evitar erros de caracteres especiais (acentuação) que corromperiam o banco de dados e a exibição no Frontend.

## 🛡️ Tratamento de Casos Extremos (Edge Cases)
Dados Financeiros Vazios: Se uma operadora possui dados em apenas 1 dos 3 trimestres, o cálculo do desvio padrão retornaria erro (divisão por zero ou NaN). O código trata isso preenchendo com zero ou ignorando a operadora, conforme a regra de negócio.

Divergência de Registro ANS: Implementado um Left Join no enriquecimento para garantir que, mesmo que uma operadora não seja encontrada na base cadastral, os dados financeiros processados não sejam perdidos.

## 🚀 Como executar esta etapa 
Caso queira validar apenas o processamento de dados:
Rode o ETL: python run_etl.py.

...........................................................................................................................
## 🗄️ 3. Teste de Banco de Dados e Queries SQL
🎯 Objetivo
Desenvolver uma estrutura de banco de dados robusta para armazenar o histórico financeiro processado e executar queries analíticas que respondam a perguntas de negócio (ex: maiores despesas).

## 🛠️ Implementação e Fluxo
A estratégia adotada divide-se em três scripts SQL contidos em backend/db/:

setup.sql (DML/DDL): Criação das tabelas com tipos de dados otimizados.

import.sql: Script para carga massiva dos dados processados (historico_final.csv) para o banco de dados.

queries.sql: Consultas analíticas para extração de insights:

Top 10 operadoras (Ano): Identifica as operadoras com maior despesa no último ano.

Top operadoras (Trimestre): Identifica as maiores despesas no último trimestre disponível.

## ⚖️ Trade-offs Técnicos e Justificativas
1. SQL Puro vs. ORM (SQLAlchemy) para Carga Inicial
Escolha: SQL Nativo para criação/queries analíticas.

Justificativa (Praticidade/KISS): Para um teste técnico focado em banco de dados, o uso de SQL puro permite que o avaliador visualize diretamente sua habilidade em escrever queries eficientes e estruturar joins, sem a "camada de abstração" de um ORM que poderia esconder ineficiências.

2. Tipagem de Dados (DECIMAL vs. FLOAT)
Escolha: DECIMAL(15, 2) para valores financeiros.

Justificativa (Pensamento Crítico): Nunca utilizei FLOAT ou REAL para despesas. Em sistemas financeiros, o erro de precisão de ponto flutuante é inaceitável. O tipo DECIMAL garante exatidão matemática nas agregações de média e soma exigidas no PDF.

3. Normalização vs. Performance Analítica
Decisão: Tabela de Fatos (despesas) e Dimensão (operadoras).

Justificativa: Estruturei os dados de forma que o Registro ANS seja a chave estrangeira (FK). Isso mantém a integridade referencial e evita que o nome da operadora seja repetido em milhões de linhas de despesas, economizando espaço em disco e acelerando a busca.

## 🛡️ Pensamento Crítico: Validações e Casos Extremos
Integridade Referencial: O script de setup impede a inserção de despesas para operadoras que não existem na tabela cadastral, evitando "dados órfãos".

Performance de Busca: Adicionei índices (INDEX) na coluna de registro_ans e data_base.

Justificativa: Como as queries principais filtram por período (ano/trimestre), o índice reduz a necessidade de um Full Table Scan, tornando a resposta da API (Teste 4) quase instantânea.

## 🚀 Como executar esta etapa
Certifique-se de ter o MySQL 8.0 ou PostgreSQL ativo.

Crie o database: CREATE DATABASE intuitive_care;

Execute os comandos:

# 1. Criar tabelas
mysql -u usuario -p intuitive_care < backend/db/setup.sql

# 2. Importar dados (ou via script Python loader.py)
python backend/core/loader.py

# 3. Rodar queries analíticas
mysql -u usuario -p intuitive_care < backend/db/queries.sql

...........................................................................................................................

## 🖥️ 4. Teste de API e Interface Gráfica

🎯 Objetivo
Expor os dados processados e enriquecidos através de uma API RESTful e fornecer uma interface moderna e intuitiva para que o usuário possa filtrar e visualizar as informações de operadoras de saúde.

🛠️ Implementação Técnica
Backend (API Engine)
Construído com FastAPI (Python 3.13), o servidor foi desenhado para ser assíncrono e leve.

Endpoint Principal: /operadoras – Suporta parâmetros de busca opcionais (nome ou registro_ans).

Integração: A API consome diretamente o banco de dados [MySQL/PostgreSQL] estruturado no Teste 3, garantindo que a informação seja sempre atualizada.

Documentação Nativa: Utiliza Swagger UI para facilitar o teste das rotas pelos desenvolvedores.

Frontend (Analytic Dashboard)
Desenvolvido com Vue.js 3 e Vite, focado em reatividade e velocidade.

Tailwind CSS: Utilizado para garantir um design responsivo e moderno (SaaS-like) sem sobrecarregar o peso dos arquivos CSS.

Axios: Cliente HTTP para comunicação robusta com o backend.

Componentização: A interface é modular (ex: Dashboard.vue), facilitando a manutenção e a reutilização de código.

## ⚖️ Trade-offs Técnicos e Justificativas
1. FastAPI vs. Flask/Django
Escolha: FastAPI.

Justificativa (Praticidade/KISS): O FastAPI oferece validação de dados automática (via Pydantic) e gera documentação Swagger sem configuração extra. Para um teste técnico, isso demonstra conhecimento em ferramentas modernas de alta performance e reduz o "boilerplate code".

2. Performance da Tabela: Paginação no Frontend vs. Backend
Decisão: Paginação no Frontend (com lógica de filtragem).

Justificativa (Pensamento Crítico): Dado que o volume de operadoras ativas (aprox. mil registros) é gerenciável pela memória do navegador, optei por carregar os dados e paginá-los localmente.

Ganho: A busca por filtro torna-se instantânea para o usuário após o primeiro load, eliminando requisições repetitivas ao servidor e melhorando drasticamente a fluidez da UX.

3. Gerenciamento de Estado: Vue Composition API vs. Vuex/Pinia
Escolha: Composition API (ref, computed).

Justificativa: Para a complexidade deste dashboard, o uso de Pinia seria um "over-engineering". Manter o estado dentro do componente central (Dashboard.vue) mantém o código mais limpo e fácil de seguir, respeitando o princípio KISS.

## 🛡️ Pensamento Crítico: Tratamento de Erros e UX
Para garantir a Qualidade do Código e resiliência, implementei:

Estados de Loading: O usuário visualiza um feedback visual enquanto os dados são buscados, evitando a sensação de que a aplicação "travou".

Mensagens de Erro Específicas: * Em caso de falha na API, o sistema diferencia um erro de rede de uma busca sem resultados ("Nenhuma operadora encontrada para este filtro").

Validação de Filtros: O campo de busca aceita tanto números (Registro ANS) quanto texto (Nome), tratando a entrada para evitar quebras no backend.

## 🚀 Como executar esta etapa
1. Iniciar o Backend

cd backend/api
uvicorn main_api:app --reload

2. Em um novo terminal com  Backend ativo , Iniciar o Frontend

cd frontend
npm install
npm run dev

...........................................................................................................................

## 📝 Documentação da API
Postman: A coleção do Postman (collection.json) está configurada com variáveis de ambiente e exemplos de resposta (Success/Error), permitindo a validação do contrato da API mesmo sem o banco de dados ativo."

Dica técnica: Lembre-se que para as requisições funcionarem de verdade (dar o "Send" e receber dados reais), o seu servidor FastAPI (main_api.py) precisa estar rodando no terminal com o comando: uvicorn main_api:app --reload


## Guia de Execução (Passo a Passo)
Siga estas etapas para rodar o projeto localmente e validar as funcionalidades.

1. Pré-requisitos
```sh
Python 3.10+ instalado.
```
```sh
Node.js e NPM instalados.
```
```sh
MySQL 8.0 ativo.
```

2. Configuração do Banco de Dados
Acesse seu terminal MySQL e crie o banco de dados:
```sh
CREATE DATABASE intuitive_care;
```
Execute o script de criação de tabelas (DDL):
```sh
mysql -u seu_usuario -p intuitive_care < backend/db/setup.sql
```
(Nota: Certifique-se de que a tabela operadoras_ativas foi criada com a coluna uf conforme o script atualizado).

3. Ambiente Python e Dependências
Na raiz do projeto, crie um ambiente virtual:
```sh
python -m venv venv
```
# Ative o ambiente:

Windows: venv\Scripts\activate
Linux/Mac: source venv/bin/activate

 # Instale as dependências:
```sh
pip install -r requirements.txt
```
4. Execução do Pipeline de Dados (Web Scraping + ETL)
Para baixar os dados da ANS e processá-los (Testes 1 e 2):
```sh
python run_etl.py
```

# Após gerar os arquivos processados na pasta /data, carregue-os no MySQL:
```sh
python backend/core/loader.py
```
(Dica: Se as credenciais do seu MySQL forem diferentes de root / Marcusluz1!, ajuste-as temporariamente no arquivo loader.py e main_api.py).

5. Inicialização do Backend (API)
Navegue até a pasta da API e inicie o servidor:
```sh
cd backend/api
```
```sh
uvicorn main_api:app --reload
```
A API estará disponível em: http://127.0.0.1:8000. Você pode acessar a documentação interativa em /docs.

6. Inicialização do Frontend (Interface)
Em um novo terminal, navegue até a pasta frontend:
```sh
cd frontend
npm install
npm run dev
```
Acesse o link gerado (geralmente http://localhost:5173) para visualizar o Dashboard.

📊 Validando as Queries Analíticas (Teste 3)
Para verificar os resultados das queries de crescimento, UF e média diretamente no banco:
```sh
mysql -u seu_usuario -p intuitive_care < backend/db/queries.sql
```