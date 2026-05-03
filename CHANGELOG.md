# Changelog — GB & N.Comin Advocacia

Todas as mudanças notáveis são documentadas aqui.
Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

---

## [1.1.0-dev] — em desenvolvimento (branch: develop)
### Adicionado
- Autenticação de dois fatores (2FA) via TOTP — configurável por usuário
- Sistema de permissões centralizado (`apps/accounts/permissions.py`)
- Isolamento real de filiais em todas as queries do backend (não apenas frontend)
- Financeiro: leitura para todos, escrita restrita a administradores
- Tarefas: fluxo de dupla confirmação (advogado → aguarda validação → admin valida)
- Apenas administradores podem cadastrar advogados (`@admin_required`)
- Rate limiting e bloqueio de brute-force no login
- Headers de segurança reforçados (HSTS, CSP, etc.)
- Git inicializado com branches `main` (produção) e `develop` (desenvolvimento)
- Documentação de versão (`VERSION`, `CHANGELOG.md`, `docs/`)

### Removido
- Módulo de Documentos removido conforme solicitação (app mantida apenas para migrations)

### Alterado
- Middleware de filial agora valida acesso no backend a cada request
- `switch_branch` expandido: advogados com acesso multi-filial também podem alternar
- Senhas requerem complexidade mínima

---

## [1.0.0] — 2026-04-26 (branch: main) — PRODUÇÃO ATUAL
### Adicionado
- Dashboard com gráficos de receitas/despesas e status de processos
- Módulo de Clientes (CRUD, exportação PDF/Excel, procuração)
- Módulo de Processos (CRUD, andamentos, exportação)
- Módulo Financeiro (receitas, despesas, controle de status)
- Módulo de Contratos (CRUD, exportação PDF/Excel)
- Módulo de Tarefas (CRUD básico)
- Módulo de Advogados (CRUD, exportação)
- Multi-filial: Caxias do Sul e Nova Prata
- Sistema de roles: Super Admin, Admin, Advogado, Secretário
- Docker Compose com PostgreSQL 15, Redis 7, Nginx
- Histórico de alterações via `django-simple-history`

---

## Estratégia de Branches

| Branch    | Finalidade           | Deploy         |
|-----------|----------------------|----------------|
| `main`    | Produção estável     | Automático     |
| `develop` | Desenvolvimento ativo| Manual (QA)    |
| `feature/*` | Features isoladas  | Merge → develop|
| `hotfix/*`| Correções urgentes   | Merge → main+develop |

### Como criar uma feature
```bash
git checkout develop
git checkout -b feature/nome-da-feature
# ... desenvolver ...
git push origin feature/nome-da-feature
# Abrir Pull Request → develop
```

### Como fazer deploy em produção
```bash
git checkout main
git merge develop --no-ff -m "Release v1.1.0"
git tag v1.1.0
git push origin main --tags
docker compose -f docker-compose.prod.yml up -d --build
```
