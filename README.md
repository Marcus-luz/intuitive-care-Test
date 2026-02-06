# 🚀 Desafio Técnico – Estágio em Tecnologia (v2.0)

**Candidato:** Marcus Vinicius da Luz Araújo
**Stack Principal:** Python | FastAPI | Vue.js 3 | MySQL

Este repositório contém a solução do desafio técnico para a **Intuitive Care**.
O projeto automatiza o pipeline de dados da ANS — desde a coleta bruta via **Web Scraping** até a visualização em um **Dashboard Analítico moderno**.

---

## 📌 Sumário

* [🏗️ 1. Visão Geral e Arquitetura](#1-visão-geral-e-arquitetura)
* [📂 2. Estrutura do Repositório](#2-estrutura-do-repositório)
* [🔹 Testes Técnicos Implementados](#testes-técnicos-implementados)
* [🕷️ 1. Web Scraping](#1-teste-de-integração-com-api-pública-web-scraping)
* [⚙️ 2. ETL e Transformação](#2-teste-de-transformação-e-validação-de-dados-etl)
* [🗄️ 3. Banco de Dados e SQL](#3-teste-de-banco-de-dados-e-sql)
* [🖥️ 4. API + Dashboard](#4-api--dashboard)
* [🛠️ Guia Completo de Execução](#guia-completo-de-execução-passo-a-passo)
* [⚖️ Análise Exaustiva de Trade-offs](#análise-exaustiva-de-trade-offs-técnicos)
* [🔮 Melhorias Futuras (Roadmap)](#melhorias-futuras-roadmap)

## 🏗️ 1. Visão Geral e Arquitetura

A solução foi projetada seguindo os princípios **KISS (Keep It Simple, Stupid)** e **Clean Code**, garantindo um sistema:

* Modular
* Testável
* Fácil de manter
* Escalável

### 📌 Divisão de Responsabilidades

| Camada               | Responsabilidade                                               |
| -------------------- | -------------------------------------------------------------- |
| **ETL Pipeline**     | Extração, limpeza e agregação dos dados                        |
| **Banco de Dados**   | Armazenamento relacional com foco em integridade e performance |
| **API (FastAPI)**    | Backend assíncrono para distribuição dos dados                 |
| **Frontend (Vue 3)** | Interface reativa para análise e visualização                  |

---

## 📂 2. Estrutura do Repositório

```text
├── backend/
│   ├── api/            # Servidor FastAPI e rotas
│   ├── core/           # Pipeline de Dados (Crawler, Processor, Aggregator)
│   └── db/             # Scripts SQL (Setup, Import e Queries Analíticas)
├── data/               # Arquivos brutos e processados
├── frontend/           # Aplicação Vue.js 3 (Vite + Tailwind CSS)
├── run_etl.py          # Orquestrador do pipeline (Testes 1 e 2)
├── main.py             # script orquestrador único
├── test                # Testes Automatizados
└── requirements.txt    # Dependências Python

```

---

# 🔹 TESTES TÉCNICOS IMPLEMENTADOS

---

## 🕷️ 1. Teste de Integração com API Pública (Web Scraping)

### 🎯 Objetivo

Automatizar a coleta de dados públicos do portal da **ANS (Agência Nacional de Saúde Suplementar)**, baixando informações de **Operadoras Ativas** e seus **históricos contábeis**.

### 🛠️ Implementação Técnica

Arquivo principal:

```text
backend/core/crawler.py
```

Bibliotecas utilizadas:

* `requests` → Requisições HTTP
* `BeautifulSoup4` → Parsing de HTML
* `zipfile` → Extração automática de arquivos ZIP

### 🔄 Fluxo do Crawler

1. **Navegação Programática** → Acessa a página de dados abertos da ANS
2. **Identificação Dinâmica de Links**

   * Busca pelos textos:

     * “Relatório de dados cadastrais”
     * “Demonstrações Contábeis”
3. **Download Automático** → Salva em:

```text
data/raw/
```

4. **Extração Automatizada** → Descompacta arquivos `.zip` e extrai `.csv`

---

### ⚖️ Trade-offs Técnicos (Decisões Arquiteturais)

#### 1) BeautifulSoup4 vs. Selenium

**Escolha:** BeautifulSoup4

**Justificativa:**

* Página é estática (não precisa renderizar JS)
* Selenium seria over-engineering
* BeautifulSoup é mais leve, rápido e aderente ao princípio KISS

#### 2) Busca por Texto vs. CSS/XPath

**Escolha:** Busca por texto dinâmico

**Por quê?**
Layouts de sites governamentais mudam com frequência. Buscar pelo texto do link torna o crawler mais resiliente.

#### 3) ZIP em Disco vs. Memória

**Escolha:** Extrair em disco (`data/`)

Vantagens:

* Maior auditabilidade
* Evita consumo excessivo de RAM
* Facilita inspeção manual dos arquivos

---

### 🛡️ Tratamento de Erros Implementado

* ⏳ Timeout de conexão
* ✅ Verificação de integridade do download
* 📄 Validação de arquivos `.csv`
* 🔓 Bypass seguro de SSL quando necessário

---

### 🚀 Como executar SOMENTE o crawler

```sh
python backend/core/crawler.py
```

Os arquivos estarão em:

```text
/data
```

Ou execute o pipeline completo:

```sh
python run_etl.py
```

---

## ⚙️ 2. Teste de Transformação e Validação de Dados (ETL)

### 🎯 Objetivo

Transformar os CSVs brutos em um dataset limpo, agregando métricas estatísticas e cruzando dados financeiros com informações cadastrais das operadoras.

### 🛠️ Módulos do Pipeline

| Arquivo           | Função                               |
| ----------------- | ------------------------------------ |
| **processor.py**  | Leitura e limpeza de CSV             |
| **validators.py** | Conversão monetária e validação      |
| **aggregator.py** | Média e desvio padrão por operadora  |
| **enricher.py**   | Join com tabela de operadoras ativas |

---

### ⚖️ Decisões Técnicas

#### Pandas vs. CSV nativo

**Escolha:** Pandas

Benefícios:

* Código mais curto
* Processamento vetorizado
* Mais rápido
* Fácil para `groupby()` e `merge()`

#### Normalização de Cabeçalhos

Mapeamento dinâmico para evitar quebra do pipeline quando a ANS muda nomes das colunas.

#### Encoding

Conversão forçada para **UTF-8** para evitar erros de acentuação.

---

### 🛡️ Tratamento de Edge Cases

* Dados faltantes → preenchimento seguro
* Operadoras sem cadastro → Left Join para não perder dados
* Registros incompletos → tratamento automático

---

## 🗄️ 3. Teste de Banco de Dados e SQL

Scripts em:

```text
backend/db/
```

Arquivos principais:

* `setup.sql` → Criação de tabelas
* `import.sql` → Carga de dados
* `queries.sql` → Análises de negócio

### 📊 Queries Implementadas

* Top 10 operadoras por **despesa anual**
* Top operadoras por **trimestre**

---

### ⚖️ Decisões de Banco

| Decisão             | Motivo                    |
| ------------------- | ------------------------- |
| **SQL puro**        | Melhor avaliação técnica  |
| **DECIMAL(15,2)**   | Precisão financeira       |
| **Fato + Dimensão** | Performance e integridade |
| **Índices**         | Respostas mais rápidas    |

---

### 🚀 Como rodar o banco

Criar database:

```sql
CREATE DATABASE intuitive_care;
```

Criar tabelas:

```sh
mysql -u usuario -p intuitive_care < backend/db/setup.sql
```

Importar dados:

```sh
python backend/core/loader.py
```

Rodar queries:

```sh
mysql -u usuario -p intuitive_care < backend/db/queries.sql
```

---

## 🖥️ 4. API + Dashboard

### 🔹 Backend — FastAPI

Endpoint principal:

```
GET /operadoras
```

Suporta filtros por:

* Nome
* Registro ANS

Documentação automática:

```
/docs
```

---

### 🔹 Frontend — Vue 3

Tecnologias:

* Vue 3 + Vite
* Tailwind CSS
* Axios

Características:

* Dashboard reativo
* Paginação no frontend
* Busca instantânea
* Loading visual
* Tratamento de erros amigável

---

### 🚀 Como rodar a aplicação

#### 1️⃣ Iniciar Backend

```sh
cd backend/api
uvicorn main_api:app --reload
```

#### 2️⃣ Iniciar Frontend (novo terminal)

```sh
cd frontend
npm install
npm run dev
```

Acesse:

```
http://localhost:5173
```

---

## 🛠️ Configuração do Ambiente (Importante)

Para que o projeto funcione corretamente na sua máquina, siga estes passos:

1. **Banco de Dados (MySQL 8.0):**
   - Certifique-se de ter uma instância do **MySQL 8.0** rodando localmente.
   - Execute o script `backend/db/setup.sql` para criar as tabelas necessárias.

2. **Variáveis de Ambiente (.env):**
   - Na raiz do projeto, você encontrará um arquivo `.env` (ou crie um baseado no `.env.example`).
   - **Ajuste as credenciais** (`DB_USER`, `DB_PASS`, `DB_HOST`) de acordo com a sua configuração local do MySQL.
   - Exemplo:
     ```env
     DB_HOST=localhost
     DB_USER=seu_usuario
     DB_PASS=sua_senha
     DB_NAME=intuitive_care
     ```

3. **Dependências:**
   - Instale as bibliotecas necessárias: `pip install -r requirements.txt`.
   - O projeto agora utiliza `python-dotenv` para carregar as configurações de forma segura.


# 🛠️ Guia Completo de Execução (Passo a Passo)

Este projeto foi desenhado para ser **simples de executar, resiliente e reproduzível em ambiente local**, sem necessidade de configurações manuais complexas entre pipeline de dados e aplicação.

---

## ✅ 1. Pré-requisitos

Certifique-se de ter instalado e em funcionamento:

* **Python 3.11+**
* **Node.js 18+** (Frontend)
* **MySQL 8.0+** rodando localmente

---

## 🗄️ 2. Configuração do Banco de Dados

Antes de rodar o sistema, crie o schema no MySQL (o pipeline criará as tabelas automaticamente):

```sql
CREATE DATABASE IF NOT EXISTS intuitive_care;
```

> ✔️ O restante da estrutura (tabelas, índices e carga inicial) será gerenciado automaticamente pelo pipeline.

---

## ⚙️ 3. Backend e Pipeline de Dados (Execução Orquestrada)

O projeto inclui um **script orquestrador único** que:

* valida o ambiente,
* executa o ETL completo,
* carrega os dados no MySQL,
* e sobe a API automaticamente.

## ⚙️ 3.1. Configuração do Ambiente (Recomendado)

Para garantir que o projeto execute com as versões corretas das bibliotecas e não interfira em seu ambiente global de Python, recomenda-se utilizar um ambiente virtual isolado.

🔹 Passo a passo
1️⃣ Criar o ambiente virtual

Na raiz do projeto, execute:
```bash
python -m venv venv
```
2️⃣ Ativar o ambiente

Windows:
```bash
.\venv\Scripts\activate
```

Linux / macOS:
```bash
source venv/bin/activate
```

Você saberá que o ambiente está ativo quando aparecer algo como:

(venv) C:\seu-projeto>
3️⃣ Instalar dependências

Com o ambiente ativo, execute:
```bash
pip install -r requirements.txt
```
🧩 Nota de Compatibilidade

Este projeto utiliza o operador walrus (:=), portanto requer:

✅ Python 3.8 ou superior

📌 Recomendação oficial:
👉 Utilize Python 3.11+ para melhor desempenho e compatibilidade.



3️⃣ Inicie o processo completo:

```bash
python main.py
```

### 🔄 O que esse comando faz?

Ele executa **três etapas automaticamente**:

**🔹 Validação**

* Testa conexão com o MySQL antes de qualquer processamento.

**🔹 ETL – Testes 1 e 2**

* Faz **Web Scraping** dos dados públicos da ANS
* Limpa e padroniza os CSVs com **Pandas**
* Calcula **média e desvio padrão** das despesas
* Carrega tudo no MySQL de forma estruturada

**🔹 API – Teste 4**

* Após o sucesso do ETL, o **FastAPI é iniciado automaticamente**.

---

## 🖥️ 4. Frontend (Dashboard Analítico)

Em **um novo terminal**, faça:

```bash
cd frontend
npm install
npm run dev
```

Acesse o Dashboard em:

```
http://localhost:5173
```

---

# 🚀 Diferenciais Técnicos e Resiliência

### 🛡️ Pipeline “À Prova de Falhas”

O sistema inclui:

* Tratamento para **falhas de rede** no site da ANS
* Validação de integridade dos CSVs baixados
* Logs estruturados em:

```text
pipeline.log
```

### 🌍 Configuração via Variáveis de Ambiente

Embora configurado para **localhost por padrão**, o projeto usa:

```python
os.getenv(...)
```

Isso permite alterar:

* host do MySQL
* usuário
* senha
* porta

**sem modificar o código-fonte.**

### ⚡ Performance por Design

* Média e desvio padrão são **pré-calculados no ETL**
* A API apenas lê dados já agregados
* Resultado: respostas extremamente rápidas no Dashboard.

---

# 🔮 Melhorias Futuras (Roadmap)

### 🐳 Dockerização Total

Criar:

* `Dockerfile`
* `docker-compose.yml`

Para:

* isolar ambiente
* facilitar deploy
* garantir portabilidade total

> Escolha preterida nesta versão inicial para priorizar simplicidade de execução (KISS).

### 🧪 Testes Automatizados

Adicionar cobertura com **pytest** para:

* DataProcessor

# Por que aplicar isso?
* Isolamento: O teste acima não baixa nada da internet e não apaga seus dados reais. Ele cria tudo em uma pasta que o   próprio Windows/Linux deleta depois.

# Testes de API (Contrato e Integração)

 * O teste adicional valioso seria garantir que, se você mudar o nome de uma coluna no banco de dados, a API não "quebre" silenciosamente. 

* O que testar: Se o endpoint /api/operadoras retorna um status 200 OK e se a estrutura do JSON é exatamente o que o Frontend espera.


### 📊 Logging e Monitoramento

Integrar ferramentas de observabilidade para:

* rastreio de erros em tempo real
* métricas de performance do pipeline
* alertas automáticos

---


# ⚖️ Análise Exaustiva de Trade-offs Técnicos

Atendendo ao **item 4.4 do desafio**, esta seção documenta comparativamente as principais decisões arquiteturais do projeto, destacando alternativas consideradas, vantagens, limitações e justificativas técnicas.

---

## 🔹 1. Tratamento de Dados e ETL (Módulo Core)

### **1.1. CNPJs Inválidos ou Mal Formatados**

**Abordagem escolhida:**

> **Sanitização + Padding + Tentativa de Conversão**

**Contexto**
Os arquivos CSV da ANS frequentemente apresentam CNPJs:

* sem zeros à esquerda;
* com pontos, barras e traços inconsistentes;
* ou com formatação variável entre trimestres.

**Prós**

* Evita perda de registros financeiros relevantes apenas por erro de formatação.
* Aumenta a robustez do pipeline frente à baixa qualidade dos dados públicos.

**Contras**

* Pode manter registros tecnicamente inválidos caso o CNPJ seja irrecuperável.

**Justificativa técnica**
O pipeline:

1. Remove caracteres não numéricos;
2. Garante 14 dígitos via padding à esquerda;
3. Se ainda inválido, **o registro é mantido**, porém **sinalizado para auditoria**, evitando distorções nas métricas financeiras agregadas.

---

### **1.2. Estratégia de Cruzamento (Join)**

**Abordagem escolhida:**

> **Processamento híbrido: Pandas (ETL) + SQL (API)**

**Contexto**
Cruzamento entre:

* Base financeira (milhares de linhas);
* Base cadastral de operadoras.

**Prós**

* **Pandas**: extremamente eficiente para processamento em batch no ETL.
* **SQL**: garante integridade e desempenho em tempo real na API.

**Contras**

* Exige consistência entre os modelos de dados do Python e do MySQL.

**Resultado prático**

* ETL rápido e escalável
* API confiável e performática

---

## 🔹 2. Banco de Dados (SQL)

### **2.1. Normalização (Opção B – Tabelas Separadas)**

**Modelo adotado:**

> Tabela Fato (Despesas) + Tabela Dimensão (Operadoras)

**Prós**

* Reduz redundância de dados (nomes de operadoras não se repetem).
* Permite atualizar cadastro sem reprocessar histórico financeiro.
* Melhor uso de espaço em disco.

**Contras**

* Exige JOIN em consultas analíticas (ligeiramente mais complexo).

**Justificativa técnica**
Dado o alto volume de dados financeiros e baixa frequência de alteração cadastral, a normalização oferece melhor custo-benefício e segue boas práticas de modelagem relacional.

---

### **2.2. Tipagem de Dados**

| Campo              | Tipo Escolhido    | Justificativa                               |
| ------------------ | ----------------- | ------------------------------------------- |
| Valores monetários | **DECIMAL(18,2)** | Evita erros de arredondamento do FLOAT/REAL |
| Ano                | **INT**           | Indexação rápida                            |
| Trimestre          | **INT**           | Evita parsing de DATE em queries analíticas |

**Racional técnico**
Separar **ano** e **trimestre** em inteiros acelera drasticamente filtros e agregações exigidas pelo desafio.

---

## 🔹 3. Backend e API

### **3.1. Framework (Opção B – FastAPI)**

**Alternativas consideradas:** Flask vs FastAPI

**Escolha final:** **FastAPI**

**Prós**

* Arquitetura assíncrona (alta performance)
* Validação automática com **Pydantic**
* Documentação Swagger nativa (`/docs`)

**Contras**

* Curva de aprendizado um pouco maior que Flask.

**Justificativa**
Ideal para aplicações orientadas a dados, com foco em desempenho, qualidade e documentação automática.

---

### **3.2. Estrutura de Resposta da API**

**Opção escolhida:**

> **Dados + Metadados**

Exemplo conceitual:

```json
{
  "total_registros": 1024,
  "pagina": 1,
  "dados": [ ... ]
}
```

**Benefícios**

* Frontend sabe exatamente quantos registros existem.
* Evita múltiplas consultas desnecessárias ao banco.
* Melhora confiabilidade da paginação e UX.

---

## 🔹 4. Frontend (Vue.js)

### **4.1. Estratégia de Busca/Filtro**

**Opção escolhida:**

> **Busca no Cliente (Frontend)**

**Prós**

* Busca instantânea (0ms após primeiro carregamento).
* Menor carga no backend.

**Contras**

* Consome mais memória do navegador (irrelevante para ~1.000 operadoras).

**Justificativa**
O volume atual é pequeno, logo a experiência do usuário é priorizada.

---

### **4.2. Gerenciamento de Estado**

**Opção escolhida:**

> **Composables (Composition API)**

Alternativas consideradas:

* Props
* Vuex
* Pinia

**Por que Composables?**

* Código modular
* Fácil de testar
* Sem boilerplate pesado
* Mantém lógica separada da interface

**Princípio aplicado:** **KISS (Keep It Simple, Stupid)**




