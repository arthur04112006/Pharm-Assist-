# 🏥 Pharm-Assist - Sistema de Triagem Farmacêutica Inteligente

<div align="center">

![Pharm-Assist Logo](https://img.shields.io/badge/Pharm--Assist-Healthcare-blue?style=for-the-badge&logo=healthcare)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green?style=for-the-badge&logo=flask)
![SQLite](https://img.shields.io/badge/SQLite-3.x-blue?style=for-the-badge&logo=sqlite)

**Sistema inteligente de triagem farmacêutica para otimizar o atendimento e melhorar a qualidade do cuidado ao paciente**

[🚀 **Começar Agora**](#-como-executar) • [📖 **Documentação**](#-funcionalidades) • [🛠️ **Tecnologias**](#-tecnologias-utilizadas)

</div>

---

## 📋 Índice

- [🎯 Sobre o Projeto](#-sobre-o-projeto)
- [✨ Funcionalidades](#-funcionalidades)
- [🛠️ Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [🚀 Como Executar](#-como-executar)
- [📊 Estrutura do Projeto](#-estrutura-do-projeto)
- [🎨 Interface e Design](#-interface-e-design)
- [📱 Compatibilidade](#-compatibilidade)
- [🔧 Configuração](#-configuração)
- [📈 Funcionalidades Avançadas](#-funcionalidades-avançadas)
- [🤝 Contribuição](#-contribuição)
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

---

## 🛠️ Tecnologias Utilizadas

### **Backend**
- ![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat&logo=python) **Python 3.8+** - Linguagem principal
- ![Flask](https://img.shields.io/badge/Flask-2.3.3-green?style=flat&logo=flask) **Flask 2.3.3** - Framework web
- ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-3.0.5-red?style=flat&logo=sqlalchemy) **SQLAlchemy 3.0.5** - ORM para banco de dados
- ![ReportLab](https://img.shields.io/badge/ReportLab-4.0.4-orange?style=flat&logo=reportlab) **ReportLab 4.0.4** - Geração de PDFs

### **Frontend**
- ![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3.2-purple?style=flat&logo=bootstrap) **Bootstrap 5.3.2** - Framework CSS responsivo
- ![Bootstrap Icons](https://img.shields.io/badge/Bootstrap_Icons-1.11.1-purple?style=flat&logo=bootstrap) **Bootstrap Icons 1.11.1** - Conjunto de ícones
- ![Chart.js](https://img.shields.io/badge/Chart.js-3.x-yellow?style=flat&logo=chartjs) **Chart.js** - Gráficos interativos
- ![Google Fonts](https://img.shields.io/badge/Google_Fonts-Inter-blue?style=flat&logo=google) **Google Fonts (Inter)** - Tipografia

### **Banco de Dados**
- ![SQLite](https://img.shields.io/badge/SQLite-3.x-blue?style=flat&logo=sqlite) **SQLite 3.x** - Banco de dados principal
- ![MySQL](https://img.shields.io/badge/MySQL-8.1.0-orange?style=flat&logo=mysql) **MySQL 8.1.0** - Suporte opcional

---

## 🚀 Como Executar

### **Pré-requisitos**
- Python 3.8 ou superior
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
python import_medicamentos_anvisa.py

# Ou use o script simplificado
python -c "from app import app; from import_medicamentos_anvisa import MedicamentoImporter; app.app_context().push(); importer = MedicamentoImporter(); importer.importar_medicamentos('DADOS_ABERTOS_MEDICAMENTOS.csv')"
```

### **6. Execute o Sistema**
```bash
# Opção 1: Usando run.py
python run.py

# Opção 2: Usando Flask diretamente
flask run

# Opção 3: Usando app.py
python app.py
```

### **7. Acesse o Sistema**
🌐 Abra seu navegador e acesse: **http://localhost:5000**

---

## 📊 Estrutura do Projeto

```
pharm-assist/
├── 📁 app.py                          # Aplicação Flask principal (otimizada)
├── 📁 models.py                       # Modelos do banco de dados (com índices)
├── 📁 motor_de_perguntas/             # Módulos de perguntas por sintoma (estrutura inicial)
│   ├── __init__.py
│   ├── espirro_congestao_nasal.py
│   ├── dor_lombar.py
│   ├── dor_garganta.py
│   ├── dismenorreia.py
│   ├── febre.py
│   ├── infeccoes_fungicas.py
│   ├── dor_cabeca.py
│   ├── azia_ma_digestao.py
│   ├── queimadura_solar.py
│   ├── constipacao.py
│   ├── hemorroidas.py
│   ├── diarreia.py
│   └── tosse.py
├── 📁 report_generator.py             # Gerador de relatórios PDF (comentado)
├── 📁 config.py                       # Configurações do sistema
├── 📁 run.py                          # Script de execução
├── 📁 requirements.txt                # Dependências Python
├── 📁 install.sh                      # Script de instalação (Linux/Mac)
├── 📁 test_system.py                  # Testes do sistema
├── 📁 import_medicamentos_anvisa.py   # Importador de dados ANVISA
├── 📁 DADOS_ABERTOS_MEDICAMENTOS.csv  # Base de dados ANVISA (17.535+ medicamentos)
├── 📁 README.md                       # Este arquivo (atualizado)
├── 📁 .env.example                    # Exemplo de variáveis de ambiente
│
├── 📁 database/                       # Banco de dados
│   └── 📄 schema.sql                  # Esquema do banco
│
├── 📁 templates/                      # Templates HTML (responsivos)
│   ├── 📄 base.html                   # Template base (otimizado)
│   ├── 📄 index.html                  # Dashboard principal
│   ├── 📄 pacientes.html              # Lista de pacientes
│   ├── 📄 triagem.html                # Sistema de triagem
│   ├── 📄 medicamentos.html           # Gestão de medicamentos (paginado)
│   ├── 📄 medicamentos_inativos.html  # Medicamentos inativos (paginado)
│   └── ...                            # Outros templates
│
├── 📁 reports/                        # Relatórios gerados
├── 📁 uploads/                        # Arquivos enviados
└── 📁 instance/                       # Dados da instância
    └── 📄 triagem_farmaceutica.db     # Banco SQLite principal
```

---

## 🎨 Interface e Design

### **🎯 Design System Moderno**
- **Paleta de cores profissional**: Azuis, roxos e verdes para transmitir confiança
- **Tipografia Inter**: Fonte moderna e altamente legível
- **Gradientes elegantes**: Transições suaves entre cores
- **Sombras e elevações**: Sistema consistente de hierarquia visual

### **🚀 Componentes Redesenhados**
- **Cards modernos**: Bordas arredondadas e efeitos hover
- **Botões interativos**: Animações e transições suaves
- **Tabelas responsivas**: Melhor legibilidade e interação
- **Formulários aprimorados**: Validação visual e feedback

### **📱 Responsividade Total**
- **Mobile-first**: Design otimizado para dispositivos móveis
- **Breakpoints inteligentes**: Adaptação para todos os tamanhos de tela
- **Flexbox/Grid**: Layouts flexíveis e responsivos
- **Touch-friendly**: Interface otimizada para toque

---

## 📱 Compatibilidade

| Plataforma | Navegador | Status | Versão Mínima |
|------------|-----------|---------|---------------|
| 🖥️ **Desktop** | Chrome | ✅ Suportado | 90+ |
| 🖥️ **Desktop** | Firefox | ✅ Suportado | 88+ |
| 🖥️ **Desktop** | Safari | ✅ Suportado | 14+ |
| 🖥️ **Desktop** | Edge | ✅ Suportado | 90+ |
| 📱 **Mobile** | iOS Safari | ✅ Suportado | 14+ |
| 📱 **Mobile** | Chrome Mobile | ✅ Suportado | 90+ |
| 📱 **Mobile** | Samsung Internet | ✅ Suportado | 14+ |
| 📱 **Mobile** | Firefox Mobile | ✅ Suportado | 88+ |

---

## 🔧 Configuração

### **Variáveis de Ambiente**
```bash
# .env
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=sua_chave_secreta_aqui
DATABASE_URL=sqlite:///instance/triagem_farmaceutica.db
UPLOAD_FOLDER=uploads
REPORTS_FOLDER=reports
```

### **Configurações do Banco de Dados**
```python
# config.py
class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///instance/triagem_farmaceutica.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
```

### **Personalização de Cores**
```css
:root {
    --primary-color: #6366f1;      /* Azul principal */
    --secondary-color: #8b5cf6;    /* Roxo secundário */
    --success-color: #10b981;      /* Verde sucesso */
    --warning-color: #f59e0b;      /* Amarelo aviso */
    --danger-color: #ef4444;       /* Vermelho perigo */
    --info-color: #06b6d4;         /* Azul informação */
}
```

---

## 📈 Funcionalidades Avançadas

### **⚡ Otimizações de Performance**
- **Cache inteligente**: Sistema LRU para consultas frequentes
- **Índices de banco**: Otimização de consultas com índices estratégicos
- **Paginação eficiente**: Carregamento otimizado de grandes datasets
- **Lazy loading**: Carregamento sob demanda de relacionamentos
- **API limitada**: Controle de resultados para evitar sobrecarga
- **Consultas otimizadas**: Redução de queries N+1 e consultas desnecessárias

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

## 🚀 Deploy em Produção

### **Usando Gunicorn (Linux/Mac)**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### **Usando Waitress (Windows)**
```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=8000 app:app
```

### **Docker (Recomendado)**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

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

## 🤝 Contribuição

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

## 🎓 Sobre o Projeto Acadêmico

### **🏛️ Instituição**
Este projeto foi desenvolvido como parte do **Projeto Integrador** da matéria de **Inteligência Artificial** do **Segundo Semestre** do curso de **Inteligência Artificial** da **Faculdade Donaduzzi**.

### **🏢 Parceiro Institucional**
O **Pharm-Assist** foi desenvolvido em parceria com a **Prefeitura de Toledo - Paraná**, visando modernizar e otimizar o sistema de triagem farmacêutica da rede pública de saúde do município.

### **🎯 Objetivos Acadêmicos**
- **Integração de conhecimentos** das disciplinas do semestre
- **Aplicação prática** de conceitos de IA e Machine Learning
- **Desenvolvimento de solução real** para problema da comunidade
- **Experiência profissional** em projeto com parceiro institucional

---

<div align="center">

**Pharm-Assist** - Transformando a triagem farmacêutica com tecnologia e design modernos 💊✨

[⭐ **Deixe uma estrela**](https://github.com/seu-usuario/pharm-assist) • [🔄 **Última atualização**: Setembro 2025]

</div>
