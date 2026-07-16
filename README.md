# Training Intelligence System

Aplicacao web pessoal para registrar, organizar e analisar treinos de calistenia, com foco inicial em Front Lever e Iron Cross.

Esta primeira entrega cria a fundacao do projeto:

- Monorepo com `frontend/`, `backend/`, `database/` e `docs/`.
- PostgreSQL local via Docker Compose.
- Backend FastAPI minimo com `GET /health`.
- SQLAlchemy 2, Alembic e Pytest configurados.
- Frontend Next.js com TypeScript e Tailwind CSS.
- `.env` na raiz como fonte local de configuracao.

## Estrutura

```txt
training-intelligence/
+-- frontend/
+-- backend/
+-- database/
+-- docs/
+-- docker-compose.yml
+-- .env
+-- README.md
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
postgresql://training:training@localhost:5433/training_intelligence
```

## Configuracao

O backend le as variaveis diretamente do arquivo `.env` na raiz do projeto. Valores obrigatorios para a fundacao atual:

```env
ENVIRONMENT=development
DATABASE_URL=postgresql+asyncpg://training:training@localhost:5433/training_intelligence
FRONTEND_URL=http://localhost:3000
```

## Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Consultar a migration atual:

```bash
alembic current
```

Health check:

```bash
curl http://localhost:8000/health
```

## Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

Aplicacao:

```txt
http://localhost:3000
```

## Proximos passos

1. Criar autenticacao Supabase e dependencia `get_current_user` no FastAPI.
2. Implementar CRUD de skills e exercises com testes de isolamento por usuario.
3. Implementar sessoes, exercicios da sessao e series em transacao.
4. Implementar registros de dor e dashboard inicial.
