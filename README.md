# Training Intelligence System

Aplicacao web pessoal para registrar, organizar e analisar treinos de calistenia, com foco inicial em Front Lever e Iron Cross.

Esta primeira entrega cria apenas a fundacao do projeto:

- Monorepo com `frontend/`, `backend/`, `database/` e `docs/`.
- PostgreSQL local via Docker Compose.
- Backend FastAPI minimo com `GET /health`.
- SQLAlchemy 2, Alembic e Pytest configurados.
- Frontend Next.js com TypeScript e Tailwind CSS.
- `.env.example` com variaveis esperadas.

## Estrutura

```txt
training-intelligence/
├── frontend/
├── backend/
├── database/
├── docs/
├── docker-compose.yml
├── .env.example
└── README.md
```

## Requisitos locais

- Docker Desktop
- Python 3.12+
- Node.js 20+
- pnpm ou npm

## Banco local

```bash
docker compose up -d postgres
```

Conexao padrao:

```txt
postgresql://training:training@localhost:5432/training_intelligence
```

## Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
cp ../.env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Health check:

```bash
curl http://localhost:8000/health
```

## Frontend

```bash
cd frontend
pnpm install
cp ../.env.example .env.local
pnpm dev
```

Aplicacao:

```txt
http://localhost:3000
```

## Proximos passos

1. Criar autenticacao Supabase e dependencia `get_current_user` no FastAPI.
2. Criar primeira migration de dominio com `profiles`, `skills` e `exercises`.
3. Implementar CRUD de skills e exercises com testes de isolamento por usuario.
4. Implementar sessoes, exercicios da sessao e series em transacao.
5. Implementar registros de dor e dashboard inicial.

