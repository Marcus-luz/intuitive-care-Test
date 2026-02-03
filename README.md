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

---

Se quiser, posso agora:

* 🔹 **fundir isso diretamente na sua README completa**,
* 🔹 entregar uma versão **em inglês**, ou
* 🔹 gerar uma **README com badges profissionais** (Python | FastAPI | Vue | MySQL | ETL).

Basta me dizer como prefere 🚀



