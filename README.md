# Pharm-Assist - Sistema de Triagem Farmacêutica

Sistema inteligente de triagem farmacêutica com interface web moderna e sistema de pontuação avançado.

## 🏗️ Arquitetura Reorganizada

O projeto foi reorganizado seguindo princípios de arquitetura limpa e modular:

```
Pharm-Assist/
├── core/                    # Módulos principais da aplicação
│   ├── app.py              # Aplicação Flask principal
│   ├── config.py          # Configurações
│   └── run.py             # Script de execução
├── models/                 # Modelos de dados
│   └── models.py          # Modelos SQLAlchemy
├── services/               # Serviços de negócio
│   ├── triagem/           # Motor de perguntas e triagem
│   │   └── motor_de_perguntas/
│   ├── reports/           # Geração de relatórios
│   ├── auth/              # Autenticação
│   └── recomendacoes_farmacologicas.py
├── utils/                  # Utilitários e helpers
│   ├── scoring/           # Sistema de pontuação
│   ├── extractors/        # Extratores de dados
│   └── scripts/           # Scripts de manutenção
├── data/                   # Dados estáticos
├── templates/              # Templates HTML
├── static/                 # Arquivos estáticos
├── docs/                   # Documentação
└── tests/                  # Testes
```

## 🚀 Funcionalidades

- **Sistema de Triagem Inteligente**: Motor de perguntas modular por sintoma
- **Sistema de Pontuação**: Algoritmo avançado para cálculo de risco
- **Recomendações Farmacológicas**: Sistema inteligente de recomendações
- **Relatórios PDF**: Geração automática de relatórios profissionais
- **Interface Web**: Interface responsiva e moderna
- **Gerenciamento**: Pacientes, medicamentos e usuários
- **Base de Dados**: Medicamentos da ANVISA integrados

## 📋 Pré-requisitos

- Python 3.8+
- pip
- SQLite (incluído no Python)

## 🛠️ Instalação

1. **Clone o repositório**:
```bash
git clone <repository-url>
cd Pharm-Assist
```

2. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

3. **Execute o sistema**:
```bash
python run.py
```

## 🎯 Uso

1. **Acesse o sistema**: http://localhost:5000
2. **Login padrão**: admin@pharmassist.com / admin123
3. **Cadastre pacientes** e **inicie triagens**
4. **Gere relatórios** automaticamente

## 📚 Documentação

- [README Completo](docs/README.md)
- [Changelog](docs/CHANGELOG.md)
- [Contribuindo](docs/CONTRIBUTING.md)
- [Segurança](docs/SECURITY.md)

## 🔧 Desenvolvimento

### Estrutura Modular

- **Core**: Aplicação Flask principal
- **Models**: Modelos de dados SQLAlchemy
- **Services**: Lógica de negócio
- **Utils**: Utilitários e helpers
- **Templates**: Interface web
- **Data**: Dados estáticos

### Adicionando Novos Módulos

1. Crie o módulo em `services/triagem/motor_de_perguntas/`
2. Implemente a função `run_cli()`
3. Adicione perguntas com `ask_bool()` e `input()`
4. O sistema detectará automaticamente

## 📊 Sistema de Pontuação

O sistema utiliza um algoritmo inteligente que:
- Calcula pontuações baseadas em respostas
- Considera perfil do paciente
- Gera recomendações personalizadas
- Identifica casos de encaminhamento

## 🏥 Módulos Disponíveis

- Tosse
- Diarreia
- Dor de cabeça
- Febre
- Dor de garganta
- Azia e má digestão
- Constipação
- Hemorroidas
- Dor lombar
- Congestão nasal
- Dismenorreia
- Infecções fúngicas
- Queimadura solar

## 📈 Melhorias Implementadas

- ✅ Arquitetura modular e escalável
- ✅ Separação clara de responsabilidades
- ✅ Sistema de pontuação inteligente
- ✅ Motor de perguntas flexível
- ✅ Relatórios profissionais
- ✅ Interface moderna
- ✅ Base de dados otimizada

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

Para dúvidas ou problemas:
- Abra uma issue no GitHub
- Consulte a documentação
- Entre em contato com a equipe

---

**Pharm-Assist** - Sistema de Triagem Farmacêutica Inteligente
