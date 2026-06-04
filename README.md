# GB & N.Comin Advocacia — Sistema de Gestão Jurídica

Plataforma web para gestão fiscal e administrativa, desenvolvida com foco em automação de processos, organização de documentos e controle de informações empresariais. Possui arquitetura voltada para escalabilidade, segurança e usabilidade, otimizando atividades rotineiras e aumentando a produtividade dos usuários.

Sistema completo de gestão de escritório de advocacia com multi-filial, controle de acesso granular, 2FA e fluxo de dupla confirmação de tarefas.

---

## 🚀 Início Rápido (Desenvolvimento)

```bash
# 1. Copiar e ajustar variáveis de ambiente
cp .env.example .env

# 2. Subir containers
docker compose up -d --build

# 3. Acessar o sistema
http://localhost/
```

**Usuários criados automaticamente:**

| Usuário       | Senha      | Role           | Filial       |
|---------------|------------|----------------|--------------|
| `admin`       | Admin@123  | Super Admin    | Caxias do Sul|
| `admin_caxias`| Admin@123  | Admin          | Caxias do Sul|
| `admin_np`    | Admin@123  | Admin          | Nova Prata   |

> ⚠️ **Troque as senhas e ative o 2FA antes de usar em produção!**

**Nota:** As senhas padrão listadas acima são inseguras e devem ser alteradas imediatamente após o primeiro login para evitar riscos de segurança. O 2FA (Autenticação de Dois Fatores) adiciona uma camada extra de proteção, exigindo um código temporário gerado por um aplicativo como Google Authenticator, além da senha. Consulte a seção de Segurança abaixo para mais detalhes.

---

## 🏗️ Stack

| Camada     | Tecnologia              |
|------------|-------------------------|
| Backend    | Django 4.2 (Python 3.11)|
| Banco      | PostgreSQL 15           |
| Cache/Sessão| Redis 7                |
| Servidor   | Gunicorn + Nginx        |
| Containers | Docker + Docker Compose |
| 2FA        | TOTP via pyotp          |
| PDF        | ReportLab               |
| Excel      | openpyxl                |
| Histórico  | django-simple-history   |

---

## 🔐 Segurança

### Controle de Acesso (backend real)

- **Super Admin** — acesso total, todas as filiais
- **Admin** — acesso completo na sua filial, incluindo validar tarefas e cadastrar advogados
- **Advogado** — somente leitura no financeiro, tarefas próprias, sem acesso entre filiais (exceto se configurado)
- **Secretário(a)** — somente leitura no financeiro

### Módulo de Permissões (`apps/accounts/permissions.py`)

```python
@admin_required          # Apenas admins
@financial_edit_required # Leitura todos, edição só admins
@twofa_required          # Exige 2FA ativo e verificado
branch_queryset(model, request)          # Query isolada por filial
get_branch_object_or_403(model, request) # Objeto com 403 se fora da filial
```

### 2FA (TOTP)

1. Acesse **Perfil → Configurar 2FA**
2. Escaneie o QR com Google Authenticator / Authy
3. Digite o código de 6 dígitos para ativar
4. A partir daí, login exige código TOTP

### Proteção Brute-Force

- 5 tentativas falhas → bloqueio de 15 minutos
- IP do último login registrado no perfil

---

## 📋 Módulos

| Módulo      | Quem pode ver | Quem pode editar    |
|-------------|---------------|---------------------|
| Dashboard   | Todos         | —                   |
| Clientes    | Todos (filial)| Todos (filial)      |
| Processos   | Todos (filial)| Todos (filial)      |
| Financeiro  | Todos (filial)| Apenas admins       |
| Contratos   | Todos (filial)| Todos (filial)      |
| Tarefas     | Por atribuição| Workflow duplo (ver abaixo)|
| Advogados   | Todos (filial)| Apenas admins       |
| Documentos  | Removido      | —                   |

### Fluxo de Tarefas

```
[Criação] → Pendente
          → Em Andamento
          → [Advogado clica "Concluir"] → Aguardando Validação
                                              ↓
                                    [Admin: Aprovar] → ✅ Concluída
                                    [Admin: Devolver] → Em Andamento
```

---

## 🌿 Git — Branches e Versões

```
main     ← produção estável (v1.0.0)
develop  ← desenvolvimento ativo (v1.1.0-dev)
```

Veja `docs/DEPLOY.md` para o guia completo de release e rollback.

---

## 📁 Estrutura do Projeto

```
advocacia/
├── apps/
│   ├── accounts/       # Usuários, 2FA, permissões, middleware
│   ├── branches/       # Filiais
│   ├── clients/        # Clientes
│   ├── contracts/      # Contratos
│   ├── dashboard/      # Dashboard com gráficos
│   ├── financial/      # Controle financeiro
│   ├── lawyers/        # Advogados
│   ├── processes/      # Processos jurídicos
│   └── tasks/          # Tarefas com dupla confirmação
├── config/
│   ├── settings/
│   │   ├── base.py        # Configurações base
│   │   ├── development.py # Dev overrides
│   │   └── production.py  # Produção com HSTS/HTTPS
│   └── urls.py
├── templates/          # Templates HTML com tema escuro
├── docs/
│   ├── DEPLOY.md       # Guia de deploy e versionamento
│   └── SECURITY.md     # Documentação de segurança
├── docker-compose.yml       # Dev stack
├── docker-compose.prod.yml  # Produção
├── CHANGELOG.md             # Histórico de versões
└── VERSION                  # Versão atual prod/dev
```
