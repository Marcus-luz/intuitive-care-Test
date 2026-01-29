/intuitive-care-Test
│
├── /backend                # Testes 1, 2 e 4 (Python)
│   ├── /core               # Lógica de ETL e Processamento (Testes 1 e 2)
│   │   ├── crawler.py      # Integração com API ANS
│   │   ├── processor.py    # Normalização e Transformação
│   │   └── validators.py   # Regras de validação de CNPJ/Dados
│   ├── /api                # Teste 4 (FastAPI)
│   │   ├── main.py         # Entrypoint
│   │   ├── routes.py       # Definição dos endpoints
│   │   └── schemas.py      # Modelos Pydantic
│   └── /db                 # Teste 3 (SQL)
│       ├── schema.sql      # DDL e Índices
│       └── queries.sql     # Consultas analíticas
│
├── /frontend               # Teste 4 (Vue.js)
│   └── /src
│       ├── /components     # Tabela e Gráficos
│       └── /services       # Integração com API (Axios)
│
├── /data                   # Arquivos CSV/ZIP gerados (ignorados no git)
├── README.md               # O coração da sua avaliação
└── requirements.txt        # Dependências Python