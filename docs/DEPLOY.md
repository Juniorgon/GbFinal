# Guia de Deploy — GB & N.Comin Advocacia

## Arquitetura de Branches

| Branch      | Finalidade             | Arquivo Docker              | Env              |
|-------------|------------------------|-----------------------------|------------------|
| `main`      | Produção estável       | `docker-compose.prod.yml`   | `.env.prod`      |
| `develop`   | Desenvolvimento ativo  | `docker-compose.yml`        | `.env`           |
| `feature/*` | Features isoladas      | (local)                     | `.env`           |
| `hotfix/*`  | Correções urgentes     | Merge → main e develop      | —                |

## Desenvolvimento Local

```bash
# 1. Clonar e criar .env
git clone <repo>
cd advocacia
cp .env.example .env   # editar conforme necessário

# 2. Subir dev stack
docker compose up -d --build

# Acessar: http://localhost
# Login: admin / Admin@123
```

## Deploy em Produção

```bash
# 1. Criar .env.prod com segredos reais
cp .env.example .env.prod
# EDITAR .env.prod — trocar DEBUG=False, SECRET_KEY real, DB passwords fortes

# 2. Garantir que está no branch main
git checkout main
git pull origin main

# 3. Subir produção (não derruba dev se estiver em servidor separado)
docker compose -f docker-compose.prod.yml up -d --build

# 4. Verificar logs
docker compose -f docker-compose.prod.yml logs -f web
```

## Release de Nova Versão

```bash
# No branch develop, com features testadas:
git checkout main
git merge develop --no-ff -m "Release v1.1.0: 2FA, permissions, dual-task-confirmation"
git tag v1.1.0 -m "v1.1.0 - 2FA, isolamento de filiais, tarefas com dupla confirmação"
git push origin main --tags

# Atualizar VERSION file
sed -i 's/PRODUCTION_VERSION=.*/PRODUCTION_VERSION=1.1.0/' VERSION
sed -i 's/LAST_DEPLOY=.*/LAST_DEPLOY='$(date +%Y-%m-%d)'/' VERSION
git add VERSION && git commit -m "chore: update VERSION file"
git push origin main

# Fazer deploy
docker compose -f docker-compose.prod.yml up -d --build
```

## Rollback Rápido

```bash
# Voltar para tag anterior
git checkout v1.0.0
docker compose -f docker-compose.prod.yml up -d --build
```

## Segurança — Checklist Pós-Deploy

- [ ] `DEBUG=False` no .env.prod
- [ ] `SECRET_KEY` único e longo (50+ chars)
- [ ] Senhas do banco trocadas (não usar defaults)
- [ ] 2FA ativado em todos os admins
- [ ] Backup automático do PostgreSQL configurado
- [ ] HTTPS configurado (SECURE_SSL_REDIRECT=True)
