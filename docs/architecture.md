# Architecture

Fluxo planejado do backend:

```txt
HTTP Request
-> Router
-> Authentication Dependency
-> Pydantic Schema
-> Service
-> Repository
-> SQLAlchemy Session
-> PostgreSQL
-> Response Schema
```

Responsabilidades:

- Router: contrato HTTP, status codes e dependencias.
- Service: regras de negocio, transacoes e agregacoes.
- Repository: consultas escopadas por usuario.
- PostgreSQL: integridade, constraints e indices.

