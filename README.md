# 🚀 Desafio Técnico – Estágio em Tecnologia (v2.0)

**Candidato:** Marcus Vinicius da Luz Arzújo
**Stack Principal:** Python | FastAPI | Vue.js 3 | MySQL

Este repositório contém a solução do desafio técnico para a **Intuitive Care**.
O projeto automatiza o pipeline de dados da ANS — desde a coleta bruta via **Web Scraping** até a visualização em um **Dashboard Analítico moderno**.

---

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

# 📌 Guia Completo de Execução (Passo a Passo)

## ✅ Pré-requisitos

```sh
Python 3.10+
Node.js + NPM
MySQL 8.0 ativo
```

## 🔹 Configuração do Banco

```sql
CREATE DATABASE intuitive_care;
```

```sh
mysql -u seu_usuario -p intuitive_care < backend/db/setup.sql
```

## 🔹 Ambiente Python

```sh
python -m venv venv
```

Ativar ambiente:

```sh
Windows: venv\Scripts\activate
Linux/Mac: source venv/bin/activate
```

Instalar dependências:

```sh
pip install -r requirements.txt
```

## 🔹 Rodar Pipeline Completo

```sh
python run_etl.py
python backend/core/loader.py
```

## 🔹 Subir API

```sh
cd backend/api
uvicorn main_api:app --reload
```

## 🔹 Subir Frontend

```sh
cd frontend
npm install
npm run dev
```

---

## 📬 Documentação da API (Postman)

O repositório inclui:

```
collection.json
```

Dica:

> Para funcionar corretamente, o FastAPI **precisa estar rodando**.


