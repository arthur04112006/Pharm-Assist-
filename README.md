# 🏥 Sistema de Triagem Farmacêutica

## 📋 Descrição do Projeto

O **Sistema de Triagem Farmacêutica** é um sistema especialista desenvolvido para auxiliar farmacêuticos na avaliação inicial de pacientes. O sistema utiliza um motor de regras baseado em algoritmos de decisão clínica para analisar sintomas, histórico do paciente e gerar recomendações personalizadas.

## 🚀 **INÍCIO SUPER SIMPLES - UM SÓ COMANDO!**

### **✨ Sistema Tudo-em-Um (Recomendado)**

```bash
python3 run.py
```

**🎉 PRONTO!** O sistema abre automaticamente no navegador em **http://localhost:5000**

---

## 🎯 Funcionalidades Principais

### 1. **Cadastro de Pacientes**
- ✅ Nome, idade, peso, altura, sexo
- ✅ Hábitos (fuma, bebe)
- ✅ Doenças crônicas (hipertensão, diabetes, etc.)
- ✅ Histórico de consultas anteriores

### 2. **Cadastro de Medicamentos**
- ✅ Nome comercial e genérico
- ✅ Descrição e indicações
- ✅ Contraindicações
- ✅ Tipo: farmacológico ou fitoterápico

### 3. **Sistema de Triagem Inteligente**
- ✅ Questionário adaptativo baseado em sintomas
- ✅ Motor de regras clínicas
- ✅ Cálculo automático de score de risco (0-100)
- ✅ Identificação de sinais de alerta (red flags)

### 4. **Recomendações Personalizadas**
- ✅ **Não Farmacológicas**: Medidas caseiras, mudanças de hábitos
- ✅ **Farmacológicas**: Medicamentos apropriados com orientações
- ✅ **Alertas**: Interações medicamentosas, contraindicações

### 5. **Relatórios e Documentação**
- ✅ Geração automática de relatórios em PDF
- ✅ Histórico completo de atendimentos
- ✅ Exportação estruturada com dados organizados

## 🏗️ Arquitetura do Sistema

### **Backend (Python/Flask)**
- **`app.py`**: Aplicação principal Flask com todas as rotas
- **`models.py`**: Modelos SQLAlchemy para o banco de dados
- **`triagem_engine.py`**: Motor de triagem com lógica de decisão
- **`report_generator.py`**: Gerador de relatórios PDF com ReportLab
- **`config.py`**: Configurações do sistema

### **Banco de Dados**
- **MySQL** (padrão) com fallback para **SQLite**
- **Schema completo** com todas as entidades necessárias
- **Dados iniciais** incluindo sintomas, perguntas e medicamentos comuns

### **Frontend (HTML + Bootstrap)**
- **Interface responsiva** e moderna
- **Templates organizados** por funcionalidade
- **JavaScript interativo** para a triagem
- **Design intuitivo** para uso profissional

## 🚀 Como Executar

### **Pré-requisitos**
- Python 3.8+
- MySQL (opcional, o sistema usa SQLite como alternativa)

### **Execução Simples**
```bash
# APENAS ISSO! 🎉
python3 run.py
```

**🎯 Resultado:**
- Sistema roda em **http://localhost:5000**
- Navegador abre automaticamente
- Banco de dados configurado automaticamente
- Para tudo com **Ctrl+C**

### **Execução Manual (Para Desenvolvimento)**
```bash
# 1. Instalar dependências
pip3 install -r requirements.txt

# 2. Configurar banco (opcional)
mysql -u root < database/schema.sql

# 3. Executar aplicação
python3 app.py
```

---

## 📊 Fluxo de Triagem

### 1. **Identificação do Paciente**
- Busca de paciente existente ou cadastro de novo
- Verificação de dados demográficos e hábitos

### 2. **Questionário de Triagem**
- Sistema apresenta perguntas uma a uma
- Respostas são registradas em tempo real
- Progresso visual com barra de progresso

### 3. **Análise Inteligente**
- Motor de regras analisa todas as respostas
- Cálculo automático do score de risco
- Identificação de padrões clínicos

### 4. **Geração de Recomendações**
- **Baixo Risco (0-30)**: Tratamento caseiro adequado
- **Médio Risco (31-70)**: Acompanhamento farmacêutico
- **Alto Risco (71-100)**: Encaminhamento médico urgente

### 5. **Relatório Final**
- Geração automática de PDF estruturado
- Dados do paciente, perguntas/respostas, recomendações
- Histórico salvo para consultas futuras

## 🔬 Algoritmo de Scoring

### **Fatores de Risco**
- **Sinais de Alarme**: 20-35 pontos
- **Febre Alta (≥39°C)**: 15 pontos
- **Dor Intensa (≥8/10)**: 20 pontos
- **Duração Prolongada**: 10-15 pontos
- **Comorbidades**: 8-12 pontos
- **Idade Avançada**: 5-10 pontos

### **Classificação de Risco**
- **0-30**: Baixo risco (tratamento caseiro)
- **31-70**: Médio risco (aconselhamento farmacêutico)
- **71-100**: Alto risco (encaminhamento médico)

## 📱 Interface do Usuário

### **Design Responsivo**
- Interface moderna e intuitiva
- Indicadores visuais de risco em tempo real
- Progresso da triagem com barra visual
- Alertas destacados para sintomas críticos

### **Navegação Intuitiva**
- Fluxo step-by-step organizado
- Botões de navegação claros
- Validação em tempo real
- Salvamento automático das respostas

## 🗄️ Estrutura do Banco de Dados

### **Tabelas Principais**
```sql
pacientes           -- Dados dos pacientes
doencas_cronicas   -- Catálogo de doenças
paciente_doencas   -- Relacionamento paciente-doença
sintomas           -- Catálogo de sintomas
perguntas          -- Perguntas da triagem
medicamentos       -- Catálogo de medicamentos
consultas          -- Registro de consultas
consulta_respostas -- Respostas das consultas
consulta_recomendacoes -- Recomendações geradas
```

### **Relacionamentos**
- Paciente ↔ Doenças Crônicas (M:N)
- Consulta → Paciente (1:N)
- Consulta → Respostas (1:N)
- Consulta → Recomendações (1:N)

## 📋 Estrutura de Arquivos

```
sistema-triagem-farmaceutica/
├── app.py                 # Aplicação Flask principal
├── models.py              # Modelos do banco de dados
├── triagem_engine.py      # Motor de triagem
├── report_generator.py    # Gerador de relatórios PDF
├── config.py              # Configurações
├── requirements.txt       # Dependências Python
├── run.py                 # Script de execução principal
├── database/
│   └── schema.sql        # Schema do banco MySQL
├── templates/             # Templates HTML
│   ├── base.html         # Template base
│   ├── index.html        # Dashboard
│   ├── triagem.html      # Página de triagem
│   └── iniciar_triagem.html # Questionário interativo
├── uploads/               # Arquivos enviados
├── reports/               # Relatórios PDF gerados
└── README.md              # Este arquivo
```

## 🔧 Configuração

### **Variáveis de Ambiente (Opcional)**
```bash
# .env
FLASK_DEBUG=True
SECRET_KEY=sua-chave-secreta
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DB=triagem_farmaceutica
MYSQL_PORT=3306
```

### **Configuração do Banco**
- **MySQL**: Configurado automaticamente se disponível
- **SQLite**: Fallback automático se MySQL não estiver disponível
- **Dados iniciais**: Incluídos automaticamente no schema

## 🚀 Melhorias Futuras

### **Funcionalidades Planejadas**
- [ ] Integração com sistemas de saúde
- [ ] Machine Learning para refinamento das regras
- [ ] Aplicativo mobile para farmacêuticos
- [ ] Base de dados de medicamentos atualizada
- [ ] Sistema de notificações para follow-up

### **Expansão Clínica**
- [ ] Mais especialidades médicas
- [ ] Protocolos específicos por região
- [ ] Integração com guidelines clínicos
- [ ] Sistema de teleconsulta

## 🤝 Contribuição

Este projeto foi desenvolvido como trabalho de conclusão de curso. Para contribuições ou dúvidas, entre em contato com os desenvolvedores.

## 📄 Licença

Projeto acadêmico - Todos os direitos reservados.

## 🏆 Reconhecimentos

- **Orientador**: [Nome do Orientador]
- **Instituição**: [Nome da Instituição]
- **Curso**: [Nome do Curso]
- **Ano**: 2024

---

## 🎉 **RESUMO: COMO USAR**

### **1. Primeira vez (apenas uma vez):**
```bash
python3 run.py
```
- ✅ **UM SÓ COMANDO**
- ✅ Dependências instaladas automaticamente
- ✅ Banco configurado automaticamente
- ✅ Navegador abre automaticamente

### **2. Todo dia (apenas isso):**
```bash
python3 run.py
```

### **3. Acessar:**
- Sistema abre automaticamente em **http://localhost:5000**
- Ou acesse manualmente: **http://localhost:5000**

### **4. Parar:**
- Pressione **Ctrl+C** no terminal

---

## 🔍 **Troubleshooting**

### **Problema: MySQL não conecta**
**Solução**: O sistema automaticamente usa SQLite como alternativa

### **Problema: Dependências não instalam**
**Solução**: Execute manualmente `pip3 install -r requirements.txt`

### **Problema: Porta 5000 ocupada**
**Solução**: O sistema tentará usar outra porta automaticamente

### **Problema: Erro de permissão**
**Solução**: Execute com `sudo python3 run.py` (Linux/Mac)

---

*Desenvolvido com ❤️ para melhorar a assistência farmacêutica e a saúde da população.*
