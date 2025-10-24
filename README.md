# 🏥 Pharm-Assist - Sistema de Triagem Farmacêutica Inteligente

<div align="center">

![Pharm-Assist Logo](https://img.shields.io/badge/Pharm--Assist-Healthcare-blue?style=for-the-badge&logo=healthcare)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0.3-green?style=for-the-badge&logo=flask)
![SQLite](https://img.shields.io/badge/SQLite-3.x-blue?style=for-the-badge&logo=sqlite)

**Sistema inteligente de triagem farmacêutica baseado em IA e dados da ANVISA para otimizar o atendimento e melhorar a qualidade do cuidado ao paciente**

[🚀 **Começar Agora**](#-execução) • [📖 **Documentação**](#-funcionalidades) • [🛠️ **Tecnologias**](#-tecnologias-utilizadas)

</div>

---

## 📋 Índice

- [🎯 Sobre o Projeto](#-sobre-o-projeto)
- [✨ Funcionalidades](#-funcionalidades)
- [🛠️ Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [📦 Instalação](#-instalação)
- [🚀 Execução](#-execução)
- [⚙️ Estrutura do Projeto](#️-estrutura-do-projeto)
- [🧠 Funcionalidades](#-funcionalidades)
- [🧪 Testes](#-testes)
- [🔐 Variáveis de Ambiente](#-variáveis-de-ambiente)
- [🤝 Contribuindo](#-contribuindo)
- [📄 Licença](#-licença)

---

## 🎯 Sobre o Projeto

O **Pharm-Assist** é um sistema completo de triagem farmacêutica desenvolvido como **Projeto Integrador** da matéria de **Inteligência Artificial** do **Segundo Semestre** do curso de **IA da Faculdade Donaduzzi**, em parceria com a **Prefeitura de Toledo - Paraná**.

O sistema foi desenvolvido para modernizar e otimizar o processo de atendimento na rede pública de saúde do município, utilizando inteligência artificial e regras clínicas para fornecer triagem precisa e recomendações personalizadas aos cidadãos de Toledo.

### 🎯 **Objetivos Principais**
- **Automatizar** o processo de triagem farmacêutica
- **Melhorar** a qualidade do atendimento ao paciente
- **Reduzir** riscos de interações medicamentosas
- **Otimizar** o fluxo de trabalho dos farmacêuticos
- **Gerar** relatórios profissionais e detalhados
- **Integrar** base de medicamentos da ANVISA (17.535+ medicamentos)

---

## ✨ Funcionalidades

### 🏠 **Dashboard Inteligente**
- 📊 **Métricas em tempo real**: Estatísticas de pacientes, consultas e medicamentos
- 📈 **Gráficos interativos**: Visualização de dados com Chart.js
- 🎯 **Ações rápidas**: Acesso direto às funcionalidades principais
- 📅 **Calendário de consultas**: Agendamento e acompanhamento

### 👥 **Gestão de Pacientes**
- ➕ **Cadastro completo**: Dados pessoais, médicos e histórico
- 🔍 **Busca avançada**: Filtros por nome, idade, sintomas
- 📝 **Histórico médico**: Acompanhamento de consultas anteriores
- 🏥 **Doenças crônicas**: Registro e monitoramento

### 🔬 **Sistema de Triagem Inteligente**
- 🧠 **Motor de IA**: Análise baseada em regras clínicas
- ⚠️ **Detecção de riscos**: Identificação automática de sinais de alerta
- 💊 **Recomendações personalizadas**: Medicamentos e tratamentos
- 🚨 **Encaminhamento médico**: Quando necessário
- 📊 **Sistema de pontuação**: Algoritmo avançado para cálculo de risco

### 💊 **Gestão de Medicamentos**
- 📚 **Base de dados ANVISA**: 17.535+ medicamentos autorizados importados
- 🔍 **Busca inteligente**: Filtros por nome comercial, genérico e descrição
- 📄 **Paginação otimizada**: Carregamento rápido com 20 itens por página
- ⚠️ **Interações**: Verificação de contraindicações
- 💡 **Alternativas**: Sugestões de medicamentos similares
- 📋 **Controle de estoque**: Gestão de disponibilidade
- 🏷️ **Classificação**: Medicamentos farmacológicos e fitoterápicos
- ✅ **Status ativo/inativo**: Controle de medicamentos disponíveis

### 📄 **Relatórios Profissionais**
- 🖨️ **Geração PDF**: Relatórios detalhados das consultas
- 📊 **Análises estatísticas**: Dados de performance e tendências
- 📱 **Exportação**: Múltiplos formatos de saída
- 🔒 **Segurança**: Controle de acesso e auditoria

### 🏥 **Módulos de Triagem Disponíveis**
- **Tosse** - Sistema completo de perguntas e recomendações
- **Diarreia** - Triagem para distúrbios gastrointestinais
- **Dor de cabeça** - Análise de cefaleias e enxaquecas
- **Febre** - Avaliação de estados febris
- **Dor de garganta** - Triagem para faringites
- **Azia e má digestão** - Problemas gastroesofágicos
- **Constipação** - Distúrbios intestinais
- **Hemorroidas** - Problemas anorretais
- **Dor lombar** - Distúrbios musculoesqueléticos
- **Congestão nasal** - Problemas respiratórios
- **Dismenorreia** - Distúrbios menstruais
- **Infecções fúngicas** - Micoses superficiais
- **Queimadura solar** - Problemas dermatológicos

---

## 🛠️ Tecnologias Utilizadas

### **Backend**
- ![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat&logo=python) **Python 3.10+** - Linguagem principal
- ![Flask](https://img.shields.io/badge/Flask-3.0.3-green?style=flat&logo=flask) **Flask 3.0.3** - Framework web
- ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.30-red?style=flat&logo=sqlalchemy) **SQLAlchemy 2.0.30** - ORM para banco de dados
- ![ReportLab](https://img.shields.io/badge/ReportLab-4.2.2-orange?style=flat&logo=reportlab) **ReportLab 4.2.2** - Geração de PDFs
- ![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.4.2-orange?style=flat&logo=scikit-learn) **Scikit-learn 1.4.2** - Machine Learning

### **Frontend**
- ![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3.2-purple?style=flat&logo=bootstrap) **Bootstrap 5.3.2** - Framework CSS responsivo
- ![Chart.js](https://img.shields.io/badge/Chart.js-3.x-yellow?style=flat&logo=chartjs) **Chart.js** - Gráficos interativos
- ![Google Fonts](https://img.shields.io/badge/Google_Fonts-Inter-blue?style=flat&logo=google) **Google Fonts (Inter)** - Tipografia

### **Banco de Dados**
- ![SQLite](https://img.shields.io/badge/SQLite-3.x-blue?style=flat&logo=sqlite) **SQLite 3.x** - Banco de dados principal
- ![MySQL](https://img.shields.io/badge/MySQL-8.1.0-orange?style=flat&logo=mysql) **MySQL 8.1.0** - Suporte opcional

---

## 📦 Instalação

### **Pré-requisitos**
- Python 3.10 ou superior
- pip (gerenciador de pacotes Python)
- Git (para clonar o repositório)

### **1. Clone o Repositório**
```bash
git clone https://github.com/seu-usuario/pharm-assist.git
cd pharm-assist
```

### **2. Crie um Ambiente Virtual (Recomendado)**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### **3. Instale as Dependências**
```bash
pip install -r requirements.txt
```

### **4. Configure o Ambiente**
```bash
# Copie o arquivo de exemplo
cp env.example .env

# Edite as variáveis de ambiente conforme necessário
# (Banco de dados, chaves secretas, etc.)
```

### **5. Importe a Base de Medicamentos ANVISA (Opcional)**
```bash
# Execute o script de importação para carregar 17.535+ medicamentos
python utils/import_medicamentos_anvisa.py

# Ou use o script simplificado
python -c "from core.app import app; from utils.import_medicamentos_anvisa import MedicamentoImporter; app.app_context().push(); importer = MedicamentoImporter(); importer.importar_medicamentos('data/DADOS_ABERTOS_MEDICAMENTOS.csv')"
```

---

## 🚀 Execução

### **Opção 1: Usando run.py (Recomendado)**
```bash
python run.py
```

### **Opção 2: Usando app.py**
```bash
python app.py
```

### **Opção 3: Usando Flask diretamente**
```bash
flask run
```

### **Acesse o Sistema**
🌐 Abra seu navegador e acesse: **http://localhost:5000**

### **Login Padrão**
- **Email**: admin@pharmassist.com
- **Senha**: admin123

---

## ⚙️ Estrutura do Projeto

```
Pharm-Assist/
├── 📁 core/                           # Módulos principais da aplicação
│   ├── app.py                        # Aplicação Flask principal
│   ├── config.py                     # Configurações
│   └── run.py                        # Script de execução
├── 📁 models/                        # Modelos de dados
│   └── models.py                     # Modelos SQLAlchemy
├── 📁 services/                      # Serviços de negócio
│   ├── triagem/                      # Motor de perguntas e triagem
│   │   └── motor_de_perguntas/       # Módulos por sintoma
│   ├── reports/                      # Geração de relatórios
│   ├── auth/                         # Autenticação
│   └── recomendacoes_farmacologicas.py
├── 📁 utils/                         # Utilitários e helpers
│   ├── scoring/                      # Sistema de pontuação
│   ├── extractors/                   # Extratores de dados
│   └── import_medicamentos_anvisa.py # Importador ANVISA
├── 📁 data/                          # Dados estáticos
│   ├── DADOS_ABERTOS_MEDICAMENTOS.csv # Base ANVISA
│   ├── contraindicacoes.json         # Contraindicações
│   └── sinonimos.json                # Sinônimos de medicamentos
├── 📁 templates/                     # Templates HTML
├── 📁 static/                        # Arquivos estáticos
├── 📁 docs/                          # Documentação
├── 📁 tests/                         # Testes
├── 📁 reports/                       # Relatórios gerados
├── 📁 uploads/                       # Arquivos enviados
└── 📁 instance/                      # Dados da instância
    └── triagem_farmaceutica.db       # Banco SQLite principal
```

---

## 🧠 Funcionalidades

### **⚡ Otimizações de Performance**
- **Cache inteligente**: Sistema LRU para consultas frequentes
- **Índices de banco**: Otimização de consultas com índices estratégicos
- **Paginação eficiente**: Carregamento otimizado de grandes datasets
- **Lazy loading**: Carregamento sob demanda de relacionamentos
- **API limitada**: Controle de resultados para evitar sobrecarga

### **🧠 Motor de Triagem Inteligente**
- **Análise de risco**: Score baseado em múltiplos fatores
- **Detecção de sinais de alerta**: Identificação automática de emergências
- **Recomendações personalizadas**: Baseadas no perfil do paciente
- **Histórico de triagens**: Acompanhamento temporal
- **Cache de medicamentos**: Consultas otimizadas para base ANVISA

### **📊 Sistema de Relatórios**
- **Relatórios PDF**: Documentação profissional das consultas
- **Análises estatísticas**: Métricas de performance e tendências
- **Exportação de dados**: Múltiplos formatos (PDF, CSV, JSON)
- **Templates personalizáveis**: Cabeçalhos e rodapés personalizados

### **🔒 Segurança e Auditoria**
- **Controle de acesso**: Níveis de usuário e permissões
- **Log de atividades**: Registro de todas as ações
- **Backup automático**: Proteção contra perda de dados
- **Criptografia**: Dados sensíveis protegidos

---

## 🧪 Testes

### **Executar Testes**
```bash
# Testes básicos
python test_system.py

# Testes com cobertura
pip install pytest-cov
pytest --cov=app tests/
```

### **Testes Disponíveis**
- ✅ **Testes de modelo**: Validação de dados
- ✅ **Testes de API**: Endpoints e funcionalidades
- ✅ **Testes de triagem**: Motor de análise
- ✅ **Testes de relatórios**: Geração de PDFs

---

## 🔐 Variáveis de Ambiente

### **Configuração Básica (.env)**
```bash
# Configurações do Flask
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=sua-chave-secreta-muito-segura-aqui

# Banco de dados
DATABASE_URL=sqlite:///instance/triagem_farmaceutica.db

# Configurações da aplicação
APP_NAME=Pharm-Assist - Sistema de Triagem Farmacêutica
APP_VERSION=1.0.0
ITEMS_PER_PAGE=20

# Diretórios
UPLOAD_FOLDER=uploads
REPORTS_FOLDER=reports
```

### **Configurações Avançadas**
- **MySQL**: Suporte opcional para produção
- **Logs**: Configuração de níveis e rotação
- **Segurança**: Configurações de CSRF e rate limiting
- **Email**: SMTP para envio de relatórios (opcional)

---

## 🤝 Contribuindo

Contribuições são muito bem-vindas! 🎉

### **Como Contribuir**
1. 🍴 **Fork** o projeto
2. 🌿 **Crie** uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. 💾 **Commit** suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. 📤 **Push** para a branch (`git push origin feature/AmazingFeature`)
5. 🔀 **Abra** um Pull Request

### **Diretrizes de Contribuição**
- 📝 **Documente** suas mudanças
- 🧪 **Adicione testes** para novas funcionalidades
- 🎨 **Siga o padrão** de código existente
- 📱 **Teste** em diferentes dispositivos

### **Reportando Bugs**
- 🐛 Use o sistema de Issues do GitHub
- 📋 Inclua informações detalhadas sobre o problema
- 🖥️ Especifique o ambiente (OS, navegador, versão)
- 📸 Adicione screenshots quando possível

---

## 📄 Licença

Este projeto está licenciado sob a **Licença MIT** - veja o arquivo [LICENSE](LICENSE) para detalhes.

```
MIT License

Copyright (c) 2024 Pharm-Assist

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Agradecimentos

- 🏛️ **Faculdade Donaduzzi** pela oportunidade de desenvolver este projeto integrador
- 🏢 **Prefeitura de Toledo - Paraná** pela parceria e confiança no projeto
- 👨‍🏫 **Professores e orientadores** da matéria de Inteligência Artificial
- 🏥 **Profissionais de saúde** de Toledo que contribuíram com feedback
- 🐍 **Comunidade Python** pelas ferramentas e bibliotecas utilizadas
- 🎨 **Comunidade de design** por inspiração e recursos visuais
- 🌟 **Colegas de curso** que colaboraram no desenvolvimento

---

<div align="center">

**Pharm-Assist** - Transformando a triagem farmacêutica com tecnologia e design modernos 💊✨

[⭐ **Deixe uma estrela**](https://github.com/seu-usuario/pharm-assist) • [🔄 **Última atualização**: Dezembro 2024]

</div>
