# 📚 Documentação Completa - Pharm-Assist

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Estrutura de Diretórios](#estrutura-de-diretórios)
4. [Tecnologias Utilizadas](#tecnologias-utilizadas)
5. [Modelos de Dados](#modelos-de-dados)
6. [Funcionalidades](#funcionalidades)
7. [Sistema de Triagem](#sistema-de-triagem)
8. [Sistema de Recomendações](#sistema-de-recomendações)
9. [API Endpoints](#api-endpoints)
10. [Instalação e Configuração](#instalação-e-configuração)
11. [Uso do Sistema](#uso-do-sistema)
12. [Segurança](#segurança)
13. [Manutenção](#manutenção)

---

## 🎯 Visão Geral

**Pharm-Assist** é um sistema web de triagem farmacêutica automatizada que auxilia farmacêuticos e profissionais de saúde na avaliação de sintomas comuns e geração de recomendações baseadas em evidências científicas e diretrizes da ANVISA.

### Objetivos Principais

- **Triagem Eficiente**: Avaliação rápida e estruturada de sintomas
- **Recomendações Personalizadas**: Sugestões farmacológicas e não-farmacológicas baseadas no perfil do paciente
- **Segurança**: Sistema de pontuação para identificar casos que necessitam encaminhamento médico
- **Rastreabilidade**: Registro completo de todas as consultas e recomendações
- **Relatórios Profissionais**: Geração de PDFs com informações completas da triagem

### Características Principais

✅ Interface web moderna e responsiva
✅ Sistema de autenticação e autorização
✅ Cadastro e gerenciamento de pacientes
✅ Base de dados com medicamentos da ANVISA
✅ Motor de perguntas modular por sintoma (13 módulos)
✅ Sistema de pontuação inteligente (scoring)
✅ Geração automática de recomendações
✅ Relatórios em PDF profissionais
✅ Dashboard com estatísticas e gráficos
✅ Sistema de controle de estoque de medicamentos

---

## 🏗️ Arquitetura do Sistema

O Pharm-Assist segue uma arquitetura modular baseada no padrão MVC (Model-View-Controller) com camadas bem definidas:

```
┌─────────────────────────────────────────┐
│         Interface Web (Templates)       │
│              Flask + Jinja2             │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│          Camada de Aplicação            │
│         (core/app.py - Flask)           │
└─────┬────────────┬────────────┬─────────┘
      │            │            │
┌─────▼─────┐ ┌───▼────┐ ┌────▼─────┐
│  Services │ │ Utils  │ │  Models  │
│           │ │        │ │          │
│ • Triagem │ │ • Score│ │ Database │
│ • Reports │ │ • Extract│  SQLite │
│ • Recom.  │ │        │ │          │
└───────────┘ └────────┘ └──────────┘
```

### Camadas

1. **Interface (Templates)**: Interface web responsiva usando Bootstrap
2. **Aplicação (Core)**: Lógica de rotas, autenticação e controle de fluxo
3. **Serviços (Services)**: Lógica de negócio (triagem, relatórios, recomendações)
4. **Utilitários (Utils)**: Funções auxiliares (scoring, extractors)
5. **Modelos (Models)**: Definição de entidades e relacionamentos do banco de dados

---

## 📁 Estrutura de Diretórios

```
Pharm-Assist/
├── core/                           # Módulos principais da aplicação
│   ├── __init__.py                # Inicialização do pacote core
│   ├── app.py                     # Aplicação Flask principal (1545 linhas)
│   ├── config.py                  # Configurações do sistema
│   └── run.py                     # Script de execução
│
├── models/                        # Modelos de dados
│   ├── __init__.py               # Inicialização do pacote models
│   └── models.py                 # Definições das tabelas do banco (324 linhas)
│
├── services/                      # Serviços de negócio
│   ├── __init__.py               # Inicialização do pacote services
│   ├── auth/                     # Autenticação (futuro)
│   │   └── __init__.py
│   ├── reports/                  # Geração de relatórios
│   │   ├── __init__.py
│   │   └── report_generator.py  # Gerador de PDFs (300+ linhas)
│   ├── triagem/                  # Sistema de triagem
│   │   ├── __init__.py
│   │   └── motor_de_perguntas/  # Módulos de perguntas por sintoma
│   │       ├── __init__.py
│   │       ├── tosse.py         # Triagem para tosse (300 linhas)
│   │       ├── febre.py         # Triagem para febre
│   │       ├── dor_cabeca.py    # Triagem para dor de cabeça
│   │       ├── dor_garganta.py  # Triagem para dor de garganta
│   │       ├── diarreia.py      # Triagem para diarreia
│   │       ├── constipacao.py   # Triagem para constipação
│   │       ├── azia_ma_digestao.py       # Triagem para azia/má digestão
│   │       ├── dismenorreia.py           # Triagem para dismenorreia
│   │       ├── dor_lombar.py             # Triagem para dor lombar
│   │       ├── hemorroidas.py            # Triagem para hemorroidas
│   │       ├── espirro_congestao_nasal.py # Triagem para congestão nasal
│   │       ├── infeccoes_fungicas.py     # Triagem para infecções fúngicas
│   │       └── queimadura_solar.py       # Triagem para queimadura solar
│   └── recomendacoes_farmacologicas.py   # Sistema de recomendações (2475 linhas)
│
├── utils/                         # Utilitários e helpers
│   ├── __init__.py               # Inicialização do pacote utils
│   ├── scoring/                  # Sistema de pontuação
│   │   ├── __init__.py
│   │   └── triagem_scoring.py   # Lógica de scoring e decisão
│   ├── extractors/               # Extratores de dados
│   │   ├── __init__.py
│   │   └── perguntas_extractor.py # Extração de perguntas dos módulos
│   ├── import_medicamentos_anvisa.py    # Importador de medicamentos ANVISA
│   ├── popular_medicamentos_teste.py    # Populador de dados de teste
│   └── fix_template.py                  # Corretor de templates
│
├── templates/                     # Templates HTML (26 arquivos)
│   ├── base.html                 # Template base com layout
│   ├── base_simple.html          # Template simplificado
│   ├── index.html                # Dashboard principal
│   ├── login.html                # Página de login
│   ├── cadastro.html             # Cadastro de usuários
│   ├── perfil.html               # Perfil do usuário
│   ├── admin.html                # Painel administrativo
│   ├── admin_usuarios.html       # Gerenciamento de usuários
│   ├── pacientes.html            # Lista de pacientes
│   ├── novo_paciente.html        # Cadastro de paciente
│   ├── editar_paciente.html      # Edição de paciente
│   ├── visualizar_paciente.html  # Visualização de paciente
│   ├── medicamentos.html         # Lista de medicamentos
│   ├── medicamentos_inativos.html # Medicamentos desativados
│   ├── novo_medicamento.html     # Cadastro de medicamento
│   ├── editar_medicamento.html   # Edição de medicamento
│   ├── triagem.html              # Página inicial da triagem
│   ├── buscar_paciente_triagem.html # Busca de paciente para triagem
│   ├── novo_paciente_triagem.html   # Cadastro rápido para triagem
│   ├── iniciar_triagem.html         # Questionário de triagem
│   ├── resultado_triagem.html       # Resultado da triagem
│   ├── test.html                    # Página de teste
│   ├── 404.html                     # Erro 404
│   └── 500.html                     # Erro 500
│
├── static/                        # Arquivos estáticos (CSS, JS, imagens)
│
├── data/                          # Dados estáticos e configurações
│   ├── contraindicacoes.json     # Contraindicações de medicamentos
│   └── sinonimos.json            # Sinônimos de sintomas
│
├── docs/                          # Documentação do projeto
│   ├── README.md                 # Documentação principal
│   ├── CHANGELOG.md              # Histórico de alterações
│   ├── CONTRIBUTING.md           # Guia de contribuição
│   ├── SECURITY.md               # Políticas de segurança
│   ├── AUTENTICACAO.md           # Documentação de autenticação
│   ├── IMPLEMENTACAO_BUSCA_SEMANTICA.md
│   ├── MELHORIAS_SISTEMA_RECOMENDACOES.md
│   ├── motorPerfuntas.md
│   └── arquivos pra substituis/  # Fluxos antigos (referência)
│
├── instance/                      # Dados da instância (gerado)
│   └── triagem_farmaceutica.db   # Banco de dados SQLite
│
├── reports/                       # Relatórios PDF gerados
├── uploads/                       # Arquivos enviados
│
├── app.py                         # Wrapper de compatibilidade
├── run.py                         # Wrapper de compatibilidade
├── requirements.txt               # Dependências Python
├── .env.example                   # Exemplo de variáveis de ambiente
├── .gitignore                     # Arquivos ignorados pelo Git
├── LICENSE                        # Licença do projeto
└── README.md                      # README principal do projeto
```

---

## 💻 Tecnologias Utilizadas

### Backend

- **Python 3.10+**: Linguagem de programação principal
- **Flask 3.0.3**: Framework web minimalista
- **Flask-SQLAlchemy 3.1.1**: ORM para banco de dados
- **SQLAlchemy 2.0.30**: Biblioteca de mapeamento objeto-relacional
- **Werkzeug 3.0.3**: Utilitários WSGI (segurança, hashing)

### Banco de Dados

- **SQLite**: Banco de dados relacional leve (desenvolvimento)
- **MySQL Connector 9.1.0**: Suporte para MySQL (produção opcional)

### Machine Learning e Análise

- **scikit-learn 1.4.2**: Biblioteca de machine learning
- **numpy 1.26.4**: Computação numérica
- **pandas 2.2.2**: Manipulação de dados

### Geração de Documentos

- **ReportLab 4.2.2**: Geração de relatórios PDF

### Processamento de Texto

- **unidecode 1.3.8**: Remoção de acentos e normalização

### Ambiente e Configuração

- **python-dotenv 1.0.1**: Gerenciamento de variáveis de ambiente

### Frontend

- **HTML5 + CSS3**: Estrutura e estilização
- **Bootstrap 5**: Framework CSS responsivo
- **JavaScript (Vanilla)**: Interatividade do lado do cliente
- **jQuery**: Manipulação DOM e AJAX
- **Chart.js**: Gráficos e visualizações

---

## 🗄️ Modelos de Dados

O sistema utiliza 9 modelos principais organizados em um schema relacional otimizado.

### 1. Usuario

Gerenciamento de usuários do sistema com autenticação e autorização.

**Campos:**
- `id` (Integer, PK): Identificador único
- `nome` (String(200), indexed): Nome completo
- `email` (String(120), unique, indexed): Email para login
- `senha_hash` (String(255)): Hash bcrypt da senha
- `ativo` (Boolean, indexed): Status do usuário
- `is_admin` (Boolean, indexed): Privilégios administrativos
- `created_at` (Timestamp, indexed): Data de criação
- `updated_at` (Timestamp): Última atualização
- `last_login` (Timestamp): Último acesso

**Métodos:**
- `set_password(senha)`: Define senha com hash
- `check_password(senha)`: Verifica senha
- `to_dict()`: Serialização (sem senha)

**Credenciais Padrão:**
- Email: `admin@pharmassist.com`
- Senha: `admin123`

### 2. Paciente

Dados pessoais e clínicos dos pacientes.

**Campos:**
- `id` (Integer, PK): Identificador único
- `nome` (String(200), indexed): Nome completo
- `idade` (Integer, indexed): Idade em anos
- `peso` (Numeric(5,2)): Peso em kg
- `altura` (Numeric(3,2)): Altura em metros
- `sexo` (Enum: M/F/O, indexed): Sexo biológico
- `fuma` (Boolean): Fumante
- `bebe` (Boolean): Consome álcool
- `created_at` (Timestamp, indexed): Data de cadastro
- `updated_at` (Timestamp): Última atualização

**Relacionamentos:**
- `doencas_cronicas`: Doenças crônicas (N:N via PacienteDoenca)
- `consultas`: Histórico de consultas (1:N)

### 3. DoencaCronica

Catálogo de doenças crônicas.

**Campos:**
- `id` (Integer, PK): Identificador único
- `nome` (String(100), unique): Nome da doença
- `descricao` (Text): Descrição detalhada
- `created_at` (Timestamp): Data de cadastro

**Doenças Padrão:**
- Hipertensão
- Diabetes
- Asma
- Doença Cardíaca
- Obesidade
- Colesterol Alto

### 4. PacienteDoenca

Relacionamento N:N entre Paciente e DoencaCronica.

**Campos:**
- `id` (Integer, PK): Identificador único
- `id_paciente` (FK → pacientes.id, cascade): Referência ao paciente
- `id_doenca_cronica` (FK → doencas_cronicas.id, cascade): Referência à doença
- `created_at` (Timestamp): Data de associação

### 5. Sintoma

Catálogo de sintomas para triagem.

**Campos:**
- `id` (Integer, PK): Identificador único
- `nome` (String(100), unique): Nome do sintoma
- `categoria` (String(50)): Categoria do sintoma
- `created_at` (Timestamp): Data de cadastro

### 6. Pergunta

Perguntas do questionário de triagem.

**Campos:**
- `id` (Integer, PK): Identificador único
- `texto` (Text): Texto da pergunta
- `tipo` (Enum: sintoma/habito/historico/geral): Tipo da pergunta
- `ordem` (Integer): Ordem de exibição
- `ativa` (Boolean): Pergunta ativa
- `created_at` (Timestamp): Data de criação

### 7. Medicamento

Base de medicamentos (ANVISA).

**Campos:**
- `id` (Integer, PK): Identificador único
- `nome_comercial` (String(200), indexed): Nome comercial
- `nome_generico` (String(200), indexed): Princípio ativo
- `descricao` (Text): Descrição do medicamento
- `indicacao` (Text): Indicações terapêuticas
- `contraindicacao` (Text): Contraindicações
- `tipo` (Enum: farmacologico/fitoterapico, indexed): Tipo
- `ativo` (Boolean, indexed): Status
- `created_at` (Timestamp, indexed): Data de cadastro

### 8. Consulta

Registro de consultas de triagem.

**Campos:**
- `id` (Integer, PK): Identificador único
- `id_paciente` (FK → pacientes.id, cascade): Referência ao paciente
- `data` (DateTime): Data/hora da consulta
- `encaminhamento` (Boolean): Necessita encaminhamento médico
- `motivo_encaminhamento` (Text): Motivo do encaminhamento
- `observacoes` (Text): Observações gerais
- `created_at` (Timestamp): Data de criação

**Relacionamentos:**
- `paciente`: Paciente da consulta (N:1)
- `respostas`: Respostas do questionário (1:N)
- `recomendacoes`: Recomendações geradas (1:N)

### 9. ConsultaResposta

Respostas do questionário de triagem.

**Campos:**
- `id` (Integer, PK): Identificador único
- `id_consulta` (FK → consultas.id, cascade): Referência à consulta
- `id_pergunta` (FK → perguntas.id, cascade): Referência à pergunta
- `resposta` (Text): Resposta do paciente
- `created_at` (Timestamp): Data da resposta

### 10. ConsultaRecomendacao

Recomendações geradas pela triagem.

**Campos:**
- `id` (Integer, PK): Identificador único
- `id_consulta` (FK → consultas.id, cascade): Referência à consulta
- `tipo` (Enum: medicamento/nao_farmacologico/encaminhamento): Tipo
- `descricao` (Text): Descrição da recomendação
- `justificativa` (Text): Justificativa técnica
- `created_at` (Timestamp): Data da recomendação

---

## 🎯 Funcionalidades

### 1. Sistema de Autenticação

**Login e Controle de Acesso**
- Login com email e senha
- Hash de senha com Werkzeug (bcrypt)
- Sessões seguras com Flask
- Controle de privilégios (usuário/admin)
- Registro de último login

**Gerenciamento de Usuários (Admin)**
- Cadastro de novos usuários
- Ativação/desativação de contas
- Exclusão de usuários
- Controle de permissões administrativas

**Perfil do Usuário**
- Visualização de dados pessoais
- Alteração de senha
- Histórico de atividades

### 2. Gerenciamento de Pacientes

**Cadastro de Pacientes**
- Dados pessoais (nome, idade, sexo)
- Dados antropométricos (peso, altura)
- Hábitos (fumante, etilista)
- Doenças crônicas (múltipla seleção)

**Visualização e Edição**
- Lista paginada de pacientes
- Busca por nome
- Visualização completa do perfil
- Edição de dados cadastrais
- Histórico de consultas

**Estatísticas**
- Distribuição por faixa etária
- Distribuição por sexo
- Prevalência de doenças crônicas

### 3. Gerenciamento de Medicamentos

**Cadastro de Medicamentos**
- Nome comercial e genérico
- Descrição e indicações
- Contraindicações
- Tipo (farmacológico/fitoterápico)
- Status (ativo/inativo)

**Busca e Filtros**
- Busca por nome (comercial ou genérico)
- Filtro por tipo
- Filtro por status
- Paginação de resultados

**Controle de Estoque**
- Ativação/desativação de medicamentos
- Medicamentos inativos separados
- Impossibilidade de exclusão se em uso

**Importação ANVISA**
- Script para importar base da ANVISA
- Atualização em massa

### 4. Sistema de Triagem

**Fluxo de Triagem**

1. **Seleção do Paciente**
   - Busca de paciente existente
   - Cadastro rápido de novo paciente

2. **Seleção do Sintoma Principal**
   - 13 módulos disponíveis:
     - Tosse
     - Febre
     - Dor de Cabeça
     - Dor de Garganta
     - Diarreia
     - Constipação
     - Azia/Má Digestão
     - Dismenorreia
     - Dor Lombar
     - Hemorroidas
     - Espirro/Congestão Nasal
     - Infecções Fúngicas
     - Queimadura Solar

3. **Questionário Dinâmico**
   - Perguntas específicas do módulo
   - Extração automática via AST
   - Filtragem de perguntas desnecessárias
   - Interface intuitiva (Sim/Não, texto livre)

4. **Processamento e Resultado**
   - Cálculo de pontuação (scoring)
   - Identificação de sinais de alerta
   - Geração de recomendações
   - Decisão de encaminhamento

**Sistema de Pontuação (Scoring)**

O sistema utiliza um algoritmo sofisticado de scoring:

```python
Pontuação Total = Σ(peso_pergunta × valor_resposta) +
                  bônus_categoria +
                  penalidade_perfil
```

**Categorias de Pontuação:**
- Sintomas principais (peso: 1.0 - 3.0)
- Sintomas secundários (peso: 0.5 - 1.5)
- Sinais de alerta (peso: 5.0 - 10.0)
- Fatores de risco (peso: 2.0 - 4.0)

**Níveis de Risco:**
- **Baixo** (0-30 pontos): Autocuidado
- **Médio** (31-60 pontos): Autocuidado com follow-up
- **Alto** (61-100 pontos): Encaminhamento médico
- **Crítico** (>100 ou sinais críticos): Encaminhamento urgente

**Confiança da Decisão:**
- Baseada na completude das respostas
- Consistência das informações
- Presença de sinais críticos
- Histórico do paciente

### 5. Sistema de Recomendações

**Recomendações Farmacológicas**

O sistema gera recomendações baseadas em:
- Sintoma principal
- Sintomas secundários
- Perfil do paciente (idade, sexo, gestação)
- Doenças crônicas
- Contraindicações
- Interações medicamentosas

**Estrutura da Recomendação:**
```
Nome do Medicamento - Indicação | Posologia: dosagem | Observações
```

**Exemplo:**
```
Paracetamol 500mg - Analgésico e antitérmico |
Posologia: 1 comprimido a cada 6-8h |
Dose máxima: 4g/dia. Evitar em hepatopatas.
```

**Medicamentos Iniciais vs Adicionais:**
- Primeiros 6: Recomendações principais
- A partir do 7º: Alternativas terapêuticas
- Carregamento progressivo (performance)

**Recomendações Não-Farmacológicas**

Orientações de autocuidado:
- Medidas gerais (hidratação, repouso)
- Mudanças de hábitos
- Prevenção de complicações
- Sinais de alerta para retorno
- Orientações nutricionais

**Sistema de Contraindicações**

O sistema verifica automaticamente:
- Idade do paciente
- Gestação/lactação
- Doenças crônicas
- Alergias conhecidas
- Interações medicamentosas

Arquivo: `data/contraindicacoes.json`

**Sistema de Sinônimos**

Expansão de sintomas para melhor busca:
- "dor de cabeça" → cefaleia, enxaqueca
- "febre" → temperatura elevada, hipertermia
- "tosse" → tussis, pigarro

Arquivo: `data/sinonimos.json`

### 6. Geração de Relatórios

**Relatório de Consulta (PDF)**

Geração automática de relatório profissional contendo:

**Cabeçalho:**
- Logo Pharm-Assist
- Título "Relatório de Triagem Farmacêutica"
- Data e hora de geração

**Dados do Paciente:**
- Nome, idade, sexo
- Peso, altura, IMC
- Hábitos (fumante, etilista)
- Doenças crônicas

**Dados da Consulta:**
- Data/hora da triagem
- ID da consulta
- Profissional responsável

**Respostas do Questionário:**
- Perguntas e respostas em tabela
- Formatação clara e legível

**Resultado da Triagem:**
- Encaminhamento médico (SIM/NÃO)
- Motivo do encaminhamento
- Pontuação total
- Nível de risco
- Confiança da decisão

**Recomendações Farmacológicas:**
- Lista de medicamentos
- Posologia
- Justificativa técnica

**Recomendações Não-Farmacológicas:**
- Medidas de autocuidado
- Orientações gerais

**Observações:**
- Informações adicionais
- Categoria do sintoma
- Módulo utilizado

**Rodapé:**
- Data/hora de geração
- Aviso legal
- Assinatura digital (opcional)

**Características Técnicas:**
- Formato: PDF/A (arquivamento)
- Tamanho: A4 (21cm × 29,7cm)
- Margens: 2cm
- Fonte: Helvetica
- Cores corporativas: #2c3e50, #3498db

### 7. Dashboard e Estatísticas

**Dashboard Principal**

Visão geral do sistema com:

**Métricas Principais:**
- Total de pacientes cadastrados
- Total de medicamentos ativos
- Consultas realizadas hoje
- Total de encaminhamentos

**Gráficos:**
- **Consultas por dia** (últimos 7 dias)
  - Gráfico de linhas
  - Identificação de tendências

- **Pacientes por faixa etária**
  - Gráfico de barras
  - 5 faixas: 0-18, 19-30, 31-50, 51-65, 65+

- **Taxa de encaminhamentos**
  - Gráfico de pizza
  - Percentual de encaminhamentos vs autocuidado

**Consultas Recentes:**
- Últimas 5 consultas
- Paciente, data, resultado
- Link para visualização completa

**Painel Administrativo**

Estatísticas avançadas para administradores:

**Métricas Detalhadas:**
- Total de consultas (histórico completo)
- Consultas por mês (últimos 6 meses)
- Taxa de encaminhamento
- Eficácia das recomendações

**Análises:**
- **Medicamentos mais recomendados** (Top 5)
- **Sintomas mais frequentes**
- **Distribuição por gênero**
- **Pacientes por faixa etária**

**Gestão de Usuários:**
- Lista de todos os usuários
- Status (ativo/inativo)
- Último login
- Ações (editar, ativar/desativar, excluir)

### 8. API Endpoints

**Endpoints Públicos:**

```
GET  /login              → Página de login
POST /login              → Autenticação
GET  /logout             → Encerrar sessão
```

**Endpoints Autenticados:**

**Dashboard:**
```
GET  /                   → Dashboard principal
GET  /perfil             → Perfil do usuário
POST /alterar_senha      → Alterar senha
```

**Pacientes:**
```
GET  /pacientes                    → Lista de pacientes
GET  /pacientes/novo               → Formulário novo paciente
POST /pacientes/novo               → Cadastrar paciente
GET  /pacientes/<id>               → Visualizar paciente
GET  /pacientes/<id>/editar        → Formulário edição
POST /pacientes/<id>/editar        → Atualizar paciente
```

**Medicamentos:**
```
GET  /medicamentos                 → Lista de medicamentos ativos
GET  /medicamentos/inativos        → Lista de inativos
GET  /medicamentos/novo            → Formulário novo medicamento
POST /medicamentos/novo            → Cadastrar medicamento
GET  /medicamentos/<id>/editar     → Formulário edição
POST /medicamentos/<id>/editar     → Atualizar medicamento
POST /medicamentos/<id>/desativar  → Desativar medicamento
POST /medicamentos/<id>/reativar   → Reativar medicamento
POST /medicamentos/<id>/excluir    → Excluir medicamento
```

**Triagem:**
```
GET  /triagem                              → Página inicial triagem
GET  /triagem/buscar_paciente              → Buscar paciente
GET  /triagem/novo_paciente                → Cadastro rápido
POST /triagem/novo_paciente                → Criar e iniciar triagem
GET  /triagem/iniciar/<paciente_id>        → Iniciar triagem
POST /triagem/processar                    → Processar respostas
GET  /triagem/resultado/<consulta_id>      → Resultado da triagem
GET  /relatorio/<consulta_id>              → Gerar PDF
```

**API REST:**
```
GET  /api/perguntas                        → Perguntas ativas
GET  /api/triagem/modulos                  → Módulos disponíveis
GET  /api/triagem/perguntas?modulo=tosse   → Perguntas do módulo
GET  /api/sintomas                         → Lista de sintomas
GET  /api/medicamentos                     → Medicamentos ativos
GET  /api/triagem/medicamentos_adicionais/<id> → Medicamentos extras
```

**Endpoints Admin:**
```
GET  /admin                             → Painel administrativo
GET  /cadastro                          → Formulário novo usuário
POST /cadastro                          → Cadastrar usuário
GET  /admin/usuarios                    → Lista de usuários
POST /admin/usuarios/<id>/toggle_status → Ativar/desativar
POST /admin/usuarios/<id>/excluir       → Excluir usuário
```

**Formato de Resposta API:**

```json
{
  "success": true,
  "data": { ... },
  "message": "Operação realizada com sucesso"
}
```

**Códigos de Status:**
- `200`: Sucesso
- `302`: Redirecionamento
- `400`: Requisição inválida
- `401`: Não autenticado
- `403`: Não autorizado
- `404`: Não encontrado
- `500`: Erro interno

---

## ⚙️ Instalação e Configuração

### Requisitos do Sistema

**Software:**
- Python 3.10 ou superior
- pip (gerenciador de pacotes Python)
- Git (opcional, para clonar repositório)

**Sistema Operacional:**
- Linux (Ubuntu 20.04+, Debian 10+)
- macOS (10.15+)
- Windows 10/11

**Hardware Mínimo:**
- CPU: 2 cores
- RAM: 2GB
- Disco: 500MB livres

### Instalação Passo a Passo

**1. Clonar o Repositório (ou baixar ZIP)**

```bash
git clone https://github.com/seu-usuario/Pharm-Assist.git
cd Pharm-Assist
```

**2. Criar Ambiente Virtual (Recomendado)**

```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

**3. Instalar Dependências**

```bash
pip install -r requirements.txt
```

**4. Configurar Variáveis de Ambiente (Opcional)**

Copiar arquivo de exemplo:
```bash
cp .env.example .env
```

Editar `.env`:
```bash
SECRET_KEY=sua-chave-secreta-aqui
FLASK_DEBUG=True
DATABASE_URI=sqlite:///triagem_farmaceutica.db
```

**5. Inicializar Banco de Dados**

O banco é criado automaticamente na primeira execução, mas você pode forçar:

```bash
python3 -c "from core.app import app, db; app.app_context().push(); db.create_all()"
```

**6. Popular Medicamentos (Opcional)**

```bash
# Dados de teste
python3 utils/popular_medicamentos_teste.py

# Importar base ANVISA (se disponível)
python3 utils/import_medicamentos_anvisa.py
```

**7. Executar o Sistema**

```bash
python3 run.py
```

**8. Acessar a Aplicação**

Abrir navegador em: `http://localhost:5000`

**Credenciais padrão:**
- Email: `admin@pharmassist.com`
- Senha: `admin123`

**⚠️ IMPORTANTE: Altere a senha padrão após o primeiro login!**

### Configuração Avançada

**Configurar MySQL (Produção)**

Editar `core/config.py`:
```python
SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://user:pass@localhost/pharm_assist'
```

**Configurar Uploads**

Editar `core/config.py`:
```python
UPLOAD_FOLDER = '/caminho/para/uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
```

**Configurar Relatórios**

Editar `core/config.py`:
```python
REPORTS_FOLDER = '/caminho/para/reports'
```

**Configurar Paginação**

Editar `core/config.py`:
```python
ITEMS_PER_PAGE = 20  # Itens por página
```

### Deploy em Produção

**Usando Gunicorn (Recomendado)**

```bash
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:8000 'core.app:app'
```

**Usando Nginx (Proxy Reverso)**

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /caminho/para/Pharm-Assist/static;
    }
}
```

**Usando Docker (Futuro)**

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "core.app:app"]
```

---

## 🎮 Uso do Sistema

### Fluxo Básico de Uso

**1. Login**
- Acessar `http://localhost:5000/login`
- Inserir email e senha
- Clicar em "Entrar"

**2. Dashboard**
- Visualizar estatísticas gerais
- Acessar menu lateral
- Navegar pelas funcionalidades

**3. Cadastrar Paciente**
- Menu: Pacientes → Novo Paciente
- Preencher formulário
- Selecionar doenças crônicas
- Salvar

**4. Realizar Triagem**
- Menu: Triagem → Nova Triagem
- Buscar ou cadastrar paciente
- Selecionar sintoma principal
- Responder questionário
- Visualizar resultado
- Gerar relatório PDF (opcional)

**5. Gerenciar Medicamentos**
- Menu: Medicamentos
- Buscar medicamento
- Cadastrar novo (se necessário)
- Editar ou desativar

### Casos de Uso Detalhados

**Caso 1: Triagem de Tosse**

1. Paciente: Maria Silva, 35 anos
2. Sintoma principal: Tosse
3. Questionário:
   - Duração: 5 dias
   - Tipo: Seca
   - Febre: Não
   - Dificuldade para respirar: Não
   - Alergias: Sim (rinite)
4. Resultado:
   - Pontuação: 25 (Baixo risco)
   - Recomendação: Autocuidado
   - Medicamentos:
     - Dextrometorfano (antitussígeno)
     - Loratadina (antialérgico)
   - Medidas não-farmacológicas:
     - Hidratação
     - Mel
     - Umidificador
5. Encaminhamento: Não
6. Follow-up: Reavaliar em 7 dias

**Caso 2: Triagem de Febre com Encaminhamento**

1. Paciente: João Santos, 68 anos, diabético
2. Sintoma principal: Febre
3. Questionário:
   - Temperatura: 38.5°C
   - Duração: 3 dias
   - Tosse: Sim, produtiva
   - Dificuldade para respirar: Sim
   - Idade: >65 anos
   - Comorbidade: Diabetes
4. Resultado:
   - Pontuação: 85 (Alto risco)
   - Recomendação: **Encaminhamento médico**
   - Motivo: Febre persistente + dispneia + idade + comorbidade
5. Orientações:
   - Procurar unidade de saúde
   - Manter hidratação
   - Monitorar sinais vitais

---

## 🔒 Segurança

### Autenticação e Autorização

**Hashing de Senhas:**
- Algoritmo: bcrypt via Werkzeug
- Salt automático
- Custo: 12 rounds (padrão)

**Sessões:**
- Cookies HTTPOnly
- Timeout: 1 hora de inatividade
- Secret Key rotacionável

**Controle de Acesso:**
- Decorators `@login_required`
- Decorators `@admin_required`
- Verificação de privilégios em cada rota

### Proteção de Dados

**Banco de Dados:**
- SQLite: Arquivo local com permissões restritas
- MySQL: Conexão criptografada (SSL opcional)
- Backups automáticos recomendados

**Uploads:**
- Validação de tipo de arquivo
- Limite de tamanho (16MB)
- Sanitização de nomes de arquivo
- Armazenamento em diretório protegido

**Relatórios PDF:**
- Geração em memória
- Armazenamento temporário
- Limpeza automática (opcional)

### Boas Práticas

**Variáveis de Ambiente:**
- Nunca commitir `.env`
- Usar `.env.example` como template
- Rotacionar SECRET_KEY periodicamente

**Logs:**
- Registro de acessos
- Registro de erros
- Monitoramento de atividades suspeitas

**Atualizações:**
- Manter dependências atualizadas
- Aplicar patches de segurança
- Monitorar CVEs

### Compliance

**LGPD (Lei Geral de Proteção de Dados):**
- Consentimento do paciente
- Direito de exclusão de dados
- Minimização de dados coletados
- Transparência no processamento

**Boas Práticas Médicas:**
- Não substitui avaliação profissional
- Aviso legal em todos os relatórios
- Rastreabilidade de decisões
- Auditoria completa

---

## 🔧 Manutenção

### Backup do Banco de Dados

**SQLite:**
```bash
# Backup manual
cp instance/triagem_farmaceutica.db backups/backup_$(date +%Y%m%d).db

# Backup automático (cron)
0 2 * * * cp instance/triagem_farmaceutica.db backups/backup_$(date +%Y%m%d).db
```

**MySQL:**
```bash
mysqldump -u user -p pharm_assist > backup_$(date +%Y%m%d).sql
```

### Limpeza de Dados

**Remover relatórios antigos:**
```bash
# Remover PDFs com mais de 30 dias
find reports/ -name "*.pdf" -mtime +30 -delete
```

**Limpar consultas antigas (cuidado!):**
```sql
DELETE FROM consultas WHERE created_at < DATE_SUB(NOW(), INTERVAL 1 YEAR);
```

### Atualização do Sistema

**1. Backup completo:**
```bash
cp -r Pharm-Assist Pharm-Assist-backup
```

**2. Atualizar código:**
```bash
git pull origin main
```

**3. Atualizar dependências:**
```bash
pip install -r requirements.txt --upgrade
```

**4. Migrar banco (se necessário):**
```bash
# Futuro: Flask-Migrate
flask db upgrade
```

**5. Testar:**
```bash
pytest tests/
```

### Monitoramento

**Logs de Aplicação:**
```python
# Adicionar em core/app.py
import logging

logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

**Métricas de Performance:**
- Tempo de resposta das rotas
- Uso de memória
- Queries lentas ao banco
- Taxa de erros

**Alertas:**
- Disco cheio
- Banco de dados offline
- Erros críticos
- Tentativas de acesso não autorizado

### Troubleshooting

**Problema: Erro ao iniciar**
```
Solução: Verificar se todas as dependências estão instaladas
pip install -r requirements.txt
```

**Problema: Banco de dados corrompido**
```
Solução: Restaurar backup
cp backups/backup_YYYYMMDD.db instance/triagem_farmaceutica.db
```

**Problema: Relatórios não são gerados**
```
Solução: Verificar permissões da pasta reports/
chmod 755 reports/
```

**Problema: Performance lenta**
```
Solução: Adicionar índices ao banco, limpar dados antigos, otimizar queries
```

---

## 📊 Estatísticas do Projeto

**Linhas de Código:**
- Python: ~10.000+ linhas
- HTML/Templates: ~5.000+ linhas
- JavaScript: ~2.000+ linhas
- Total: ~17.000+ linhas

**Arquivos:**
- Módulos Python: 48 arquivos
- Templates HTML: 26 arquivos
- Arquivos de configuração: 10 arquivos

**Modelos de Dados:**
- 10 tabelas principais
- 15+ índices para performance
- 8 relacionamentos (1:N, N:N)

**Funcionalidades:**
- 13 módulos de triagem
- 50+ rotas/endpoints
- 2.475 linhas de lógica de recomendações
- Sistema de scoring completo

---

## 🚀 Roadmap Futuro

**Versão 1.1:**
- [ ] Sistema de notificações
- [ ] Exportação de dados (CSV, Excel)
- [ ] Gráficos avançados
- [ ] API RESTful completa

**Versão 1.2:**
- [ ] Integração com sistemas externos
- [ ] Machine Learning para recomendações
- [ ] Análise preditiva de encaminhamentos
- [ ] Dashboard em tempo real

**Versão 2.0:**
- [ ] Aplicativo mobile
- [ ] Telemedicina integrada
- [ ] Prontuário eletrônico
- [ ] Sistema de agendamento

---

## 📞 Suporte e Contribuição

**Reportar Bugs:**
- GitHub Issues: [seu-repositorio/issues]

**Contribuir:**
- Ver `docs/CONTRIBUTING.md`
- Fork + Pull Request

**Contato:**
- Email: suporte@pharmassist.com
- Documentação: https://docs.pharmassist.com

---

## 📄 Licença

Este projeto está sob a licença especificada no arquivo `LICENSE`.

---

## ✨ Créditos

**Desenvolvido por:** Equipe Pharm-Assist
**Versão:** 1.0.0
**Última Atualização:** Outubro 2024

---

**Pharm-Assist** - Transformando a triagem farmacêutica através da tecnologia 💊🏥
