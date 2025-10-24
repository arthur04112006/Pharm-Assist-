# 🔐 Sistema de Autenticação - Pharm-Assist

## 📋 Visão Geral

O sistema de autenticação foi implementado para proteger os dados sensíveis de pacientes e garantir que apenas usuários autorizados tenham acesso ao sistema de triagem farmacêutica.

## 🚀 Funcionalidades Implementadas

### ✅ Modelo de Usuário
- **Tabela `usuarios`** criada no banco de dados
- Campos: id, nome, email, senha_hash, ativo, is_admin, created_at, updated_at, last_login
- Senhas criptografadas com hash seguro
- Controle de status (ativo/inativo)
- Níveis de permissão (usuário/administrador)

### ✅ Sistema de Sessões
- Controle de sessão com Flask
- Decorators `@login_required` e `@admin_required`
- Middleware de proteção de rotas
- Logout seguro com limpeza de sessão

### ✅ Telas de Interface
- **Login** (`/login`) - Tela de autenticação moderna
- **Cadastro** (`/cadastro`) - Apenas para administradores
- **Perfil** (`/perfil`) - Gerenciamento do usuário
- **Admin Usuários** (`/admin/usuarios`) - Gestão de usuários

### ✅ Área Administrativa
- Apenas administradores podem cadastrar outros usuários
- Controle de ativação/desativação de usuários
- Exclusão de usuários (com proteções)
- Estatísticas de usuários

## 🔑 Credenciais Padrão

### Usuário Administrador
- **Email:** `admin@pharmassist.com`
- **Senha:** `admin123`
- **Privilégios:** Acesso total + gerenciamento de usuários

⚠️ **IMPORTANTE:** Altere a senha padrão após o primeiro login!

## 🛡️ Segurança Implementada

### Proteção de Dados
- Senhas criptografadas com `werkzeug.security`
- Hash seguro com salt automático
- Sessões seguras com chave secreta
- Validação de entrada em todos os formulários

### Controle de Acesso
- Todas as rotas principais protegidas com `@login_required`
- Área administrativa restrita com `@admin_required`
- Validação de permissões em tempo real
- Proteção contra auto-exclusão/desativação

### Validações
- Email único no sistema
- Senha mínima de 6 caracteres
- Confirmação de senha obrigatória
- Validação de formulários no frontend e backend

## 📱 Como Usar

### 1. Primeiro Acesso
1. Execute a aplicação: `python3 app.py`
2. Acesse: `http://localhost:5000/login`
3. Use as credenciais do administrador padrão
4. **Altere a senha padrão imediatamente!**

### 2. Cadastrar Novos Usuários
1. Faça login como administrador
2. Acesse "Gerenciar Usuários" no menu
3. Clique em "Novo Usuário"
4. Preencha os dados e defina permissões
5. Salve o usuário

### 3. Gerenciar Usuários
- **Ativar/Desativar:** Clique no botão de status
- **Excluir:** Use o botão de exclusão (com confirmação)
- **Visualizar:** Acesse o perfil do usuário

### 4. Alterar Senha
1. Acesse "Meu Perfil" no menu do usuário
2. Preencha a senha atual e nova senha
3. Confirme a nova senha
4. Salve as alterações

## 🔧 Configuração Técnica

### Arquivos Modificados
- `models.py` - Adicionado modelo Usuario
- `app.py` - Implementadas rotas de autenticação
- `templates/` - Novos templates de login, cadastro, perfil e admin

### Dependências
- `werkzeug.security` - Criptografia de senhas
- `flask.session` - Gerenciamento de sessões
- `functools.wraps` - Decorators de autenticação

### Banco de Dados
- Tabela `usuarios` criada automaticamente
- Usuário administrador criado na primeira execução
- Índices para performance em consultas frequentes

## 🚨 Considerações de Segurança

### Boas Práticas Implementadas
- ✅ Senhas nunca armazenadas em texto plano
- ✅ Validação de entrada em todos os formulários
- ✅ Controle de sessão seguro
- ✅ Proteção contra auto-exclusão
- ✅ Logs de último login

### Recomendações Adicionais
- 🔄 Alterar senha padrão imediatamente
- 🔄 Implementar política de senhas forte
- 🔄 Considerar autenticação de dois fatores
- 🔄 Implementar logs de auditoria detalhados
- 🔄 Configurar HTTPS em produção

## 📊 Estrutura do Sistema

```
Sistema de Autenticação
├── Modelo de Dados
│   ├── Usuario (tabela usuarios)
│   └── Relacionamentos e índices
├── Controle de Acesso
│   ├── @login_required
│   ├── @admin_required
│   └── Middleware de sessão
├── Interface de Usuário
│   ├── Login (/login)
│   ├── Cadastro (/cadastro)
│   ├── Perfil (/perfil)
│   └── Admin (/admin/usuarios)
└── Segurança
    ├── Criptografia de senhas
    ├── Validação de entrada
    └── Controle de sessão
```

## 🎯 Próximos Passos

1. **Teste o sistema** com as credenciais padrão
2. **Altere a senha** do administrador
3. **Cadastre usuários** para sua equipe
4. **Configure permissões** conforme necessário
5. **Monitore o uso** através das estatísticas

---

**Sistema implementado com sucesso! 🎉**

Todos os dados sensíveis de pacientes agora estão protegidos por um sistema robusto de autenticação e controle de acesso.

