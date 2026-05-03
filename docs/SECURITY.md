# Segurança — GB & N.Comin Advocacia

## Modelo de Permissões

### Roles

| Role           | Acesso Financeiro | Cadastrar Advogados | Ver Todas Filiais | Validar Tarefas |
|----------------|:-----------------:|:-------------------:|:-----------------:|:---------------:|
| Super Admin    | ✅ Editar          | ✅                   | ✅                 | ✅               |
| Admin          | ✅ Editar          | ✅                   | ❌ (só sua filial) | ✅               |
| Advogado       | 👁 Somente Leitura | ❌                   | ❌ (por config)    | ❌               |
| Secretário(a)  | 👁 Somente Leitura | ❌                   | ❌                 | ❌               |

### Isolamento de Filial

- Todas as queries são filtradas por `branch=current_branch` no backend.
- O `BranchMiddleware` valida a permissão a cada request.
- Esconder elementos no frontend é cosmético — a restrição real está nas views.
- Um advogado não pode ver clientes, processos ou contratos de outra filial.
- Advogados com `accessible_branches` configurado podem alternar via menu.

### Fluxo de Tarefas (Dupla Confirmação)

```
Pendente → Em Andamento → [Advogado: Concluir] → Aguardando Validação
                                                        ↓
                                              [Admin: Aprovar] → Concluída
                                              [Admin: Devolver] → Em Andamento
```

### 2FA (Two-Factor Authentication)

- Implementado via TOTP (RFC 6238) com `pyotp`.
- QR Code gerado na página de perfil.
- Compatible com Google Authenticator, Authy, etc.
- Sessão marcada como `2fa_verified=True` após verificação.
- Vistas protegidas verificam o estado 2FA na sessão.

### Proteção Brute-Force

- 5 tentativas falhas → conta bloqueada por 15 minutos.
- Contagem zerada após login bem-sucedido.
- IP do último login registrado.

### Headers de Segurança

Configurados em `base.py`:
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection`
- `Referrer-Policy: strict-origin-when-cross-origin`
- Em produção: HSTS habilitado.
