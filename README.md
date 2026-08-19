# Training Intelligence System

Aplicação web pessoal para registrar, organizar e analisar treinos de calistenia, com foco nas skills do usuário.

O objetivo do projeto é centralizar o histórico de treinos, exercícios, séries, percepção de esforço, qualidade técnica e registros de dor em uma interface simples para uso no dia a dia.

## Estrutura

```txt
daily/
├── backend/
├── frontend/
├── database/
├── docs/
├── docker-compose.yml
└── README.md
```

- `backend/`: API FastAPI com SQLAlchemy, Alembic e Pytest.
- `frontend/`: aplicação Next.js com React e TypeScript.
- `database/`: documentação auxiliar de banco.
- `docs/`: documentação complementar do projeto.

## Requisitos

- Docker Desktop
- Python 3.12+
- Node.js 20+
- pnpm ou npm

## Rodar Banco Local

```bash
docker compose up -d postgres
```

## Rodar Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e ".[dev]"
alembic upgrade headpython -m uvicorn app.main:app --reload --port 8000

```

Se o Windows bloquear o executável do Uvicorn, use o formato com módulo Python:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

Health check:

```bash
curl http://localhost:8000/health
```

## Rodar Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

A aplicação local roda em:

```txt
http://localhost:3000
```

## Migrations

Consultar migration atual:

```bash
cd backend
alembic current
```

Aplicar migrations:

```bash
cd backend
alembic upgrade head
```

Verificar se os models e migrations estão alinhados:

```bash
cd backend
alembic check
```

## Validação

Backend:

```bash
cd backend
python -m ruff check
python -m pytest
```

Frontend:

```bash
cd frontend
pnpm lint
pnpm typecheck
pnpm build
```

## Deploy

Stack prevista para o MVP:

- Frontend na Vercel.
- Backend no Render.
- Banco e autenticação no Supabase.

Ordem recomendada:

1. Configurar Supabase.
2. Executar migrations no banco de produção.
3. Publicar backend e configurar CORS e SSL do banco no Render.
4. Publicar frontend.
5. Validar login, criação de sessão, registro de sets, registro de dor, finalização de sessão e dashboard.

Para o backend em produção usando Supabase, configure o modo de SSL do banco
por variável de ambiente e deixe a `DATABASE_URL` sem parâmetros `ssl` ou
`sslmode`, mantendo uma única fonte de configuração.
