# 🤝 Guia de Contribuição - Pharm-Assist

Obrigado por considerar contribuir com o **Pharm-Assist - Sistema de Triagem Farmacêutica**! 🎉

Este documento fornece diretrizes e informações importantes para contribuidores.

---

## 📋 Índice

- [🎯 Como Contribuir](#-como-contribuir)
- [🔧 Configuração do Ambiente](#-configuração-do-ambiente)
- [📝 Padrões de Código](#-padrões-de-código)
- [🧪 Testes](#-testes)
- [📚 Documentação](#-documentação)
- [🔒 Segurança](#-segurança)
- [📋 Processo de Pull Request](#-processo-de-pull-request)
- [🐛 Reportando Bugs](#-reportando-bugs)
- [💡 Sugerindo Melhorias](#-sugerindo-melhorias)

---

## 🎯 Como Contribuir

### **Tipos de Contribuição Aceitas:**
- 🐛 **Correção de bugs**
- ✨ **Novas funcionalidades**
- 📚 **Melhorias na documentação**
- 🎨 **Melhorias na interface**
- 🧪 **Testes e qualidade**
- 🔒 **Melhorias de segurança**
- 🌐 **Traduções**

### **Antes de Começar:**
1. **Leia** este guia completamente
2. **Verifique** se já existe uma issue relacionada
3. **Entre em contato** se tiver dúvidas
4. **Configure** o ambiente de desenvolvimento

---

## 🔧 Configuração do Ambiente

### **1. Fork e Clone**
```bash
# Fork o repositório no GitHub, depois clone
git clone https://github.com/SEU-USUARIO/pharm-assist.git
cd pharm-assist
```

### **2. Configurar Ambiente Virtual**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### **3. Instalar Dependências**
```bash
pip install -r requirements.txt
```

### **4. Configurar Variáveis de Ambiente**
```bash
# Copiar arquivo de exemplo
cp env.example .env

# Editar com suas configurações de desenvolvimento
# NUNCA commitar o arquivo .env
```

### **5. Inicializar Banco de Dados**
```bash
# Executar o sistema para criar o banco
python app.py

# Ou importar dados da ANVISA (opcional)
python import_medicamentos_anvisa.py
```

### **6. Verificar Instalação**
```bash
# Executar testes básicos
python test_system.py
```

---

## 📝 Padrões de Código

### **1. Python Style Guide**
Seguimos o **PEP 8** com algumas adaptações:

```python
# ✅ Bom
def processar_triagem(paciente_id: int, sintomas: List[str]) -> Dict:
    """
    Processa triagem farmacêutica para um paciente.
    
    Args:
        paciente_id: ID único do paciente
        sintomas: Lista de sintomas relatados
        
    Returns:
        Dicionário com resultado da triagem
    """
    # Implementação aqui
    pass

# ❌ Evitar
def processarTriagem(pacienteId,sintomas):
    # Código sem documentação
    pass
```

### **2. Estrutura de Arquivos**
```
pharm-assist/
├── app.py                 # Aplicação principal
├── models.py              # Modelos do banco
├── config.py              # Configurações
├── requirements.txt       # Dependências
├── templates/             # Templates HTML
├── motor_de_perguntas/    # Lógica de triagem
└── tests/                 # Testes (criar se necessário)
```

### **3. Nomenclatura**
- **Arquivos**: snake_case (`motor_de_perguntas.py`)
- **Classes**: PascalCase (`Paciente`, `Consulta`)
- **Funções**: snake_case (`processar_triagem`)
- **Constantes**: UPPER_CASE (`MAX_CONTENT_LENGTH`)

### **4. Documentação**
```python
def calcular_imc(peso: float, altura: float) -> float:
    """
    Calcula o Índice de Massa Corporal (IMC).
    
    Args:
        peso: Peso em quilogramas
        altura: Altura em metros
        
    Returns:
        IMC calculado
        
    Raises:
        ValueError: Se peso ou altura forem inválidos
        
    Example:
        >>> calcular_imc(70, 1.75)
        22.86
    """
    if peso <= 0 or altura <= 0:
        raise ValueError("Peso e altura devem ser positivos")
    
    return peso / (altura ** 2)
```

---

## 🧪 Testes

### **1. Executar Testes Existentes**
```bash
# Testes básicos do sistema
python test_system.py

# Com cobertura (se disponível)
pytest --cov=app tests/
```

### **2. Escrever Novos Testes**
```python
# tests/test_models.py
import unittest
from app import app, db
from models import Paciente

class TestPaciente(unittest.TestCase):
    def setUp(self):
        """Configurar ambiente de teste"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()
    
    def test_criar_paciente(self):
        """Testar criação de paciente"""
        paciente = Paciente(
            nome="João Silva",
            idade=30,
            sexo="M"
        )
        db.session.add(paciente)
        db.session.commit()
        
        self.assertEqual(paciente.nome, "João Silva")
        self.assertEqual(paciente.idade, 30)
```

### **3. Cobertura de Testes**
- **Mínimo**: 80% de cobertura
- **Ideal**: 90%+ de cobertura
- **Foco**: Funcionalidades críticas (triagem, dados de pacientes)

---

## 📚 Documentação

### **1. Atualizar README.md**
- Adicionar novas funcionalidades
- Atualizar instruções de instalação
- Melhorar exemplos de uso

### **2. Documentar Código**
- Docstrings em todas as funções públicas
- Comentários explicativos em código complexo
- Exemplos de uso quando apropriado

### **3. Atualizar SECURITY.md**
- Reportar vulnerabilidades encontradas
- Sugerir melhorias de segurança
- Atualizar procedimentos de emergência

---

## 🔒 Segurança

### **⚠️ CRÍTICO - Antes de Qualquer Commit:**

1. **Verificar Credenciais**
   ```bash
   # Procurar por credenciais hardcoded
   grep -r "password\|secret\|key\|token" . --exclude-dir=.git
   ```

2. **Verificar Arquivos Sensíveis**
   ```bash
   # Verificar se .env não está sendo commitado
   git status
   ```

3. **Validar Dados de Teste**
   - Usar apenas dados fictícios
   - Nunca usar dados reais de pacientes
   - Validar sanitização de entrada

### **Checklist de Segurança:**
- [ ] Nenhuma credencial hardcoded
- [ ] Arquivo .env não commitado
- [ ] Dados de teste fictícios
- [ ] Validação de entrada implementada
- [ ] Logs sem informações sensíveis

---

## 📋 Processo de Pull Request

### **1. Preparação**
```bash
# Criar branch para sua feature
git checkout -b feature/nova-funcionalidade

# Fazer commits pequenos e descritivos
git commit -m "feat: adicionar validação de idade do paciente"

# Push para seu fork
git push origin feature/nova-funcionalidade
```

### **2. Criar Pull Request**
- **Título**: Descritivo e claro
- **Descrição**: Explicar o que foi feito e por quê
- **Issue**: Referenciar issue relacionada se existir
- **Screenshots**: Para mudanças na interface

### **3. Template de Pull Request**
```markdown
## 📝 Descrição
Breve descrição das mudanças implementadas.

## 🔗 Issue Relacionada
Closes #123

## 🧪 Testes
- [ ] Testes passando
- [ ] Novos testes adicionados
- [ ] Cobertura mantida/melhorada

## 📸 Screenshots (se aplicável)
[Adicionar screenshots das mudanças]

## ✅ Checklist
- [ ] Código segue padrões do projeto
- [ ] Documentação atualizada
- [ ] Testes implementados
- [ ] Verificação de segurança feita
```

### **4. Review Process**
- **Automático**: Verificação de linting e testes
- **Manual**: Review de código por mantenedores
- **Feedback**: Incorporar sugestões do review

---

## 🐛 Reportando Bugs

### **Template de Bug Report**
```markdown
## 🐛 Descrição do Bug
Descrição clara e concisa do problema.

## 🔄 Passos para Reproduzir
1. Ir para '...'
2. Clicar em '...'
3. Ver erro '...'

## 🎯 Comportamento Esperado
O que deveria acontecer.

## 📱 Ambiente
- OS: Windows 10
- Navegador: Chrome 120
- Versão do Pharm-Assist: 1.0.0

## 📸 Screenshots
[Adicionar screenshots se aplicável]

## 📋 Logs
[Adicionar logs relevantes]
```

### **Informações Importantes:**
- **Severidade**: Crítica/Alta/Média/Baixa
- **Frequência**: Sempre/Às vezes/Raramente
- **Impacto**: Quantos usuários afetados

---

## 💡 Sugerindo Melhorias

### **Template de Feature Request**
```markdown
## 💡 Descrição da Melhoria
Descrição clara da funcionalidade desejada.

## 🎯 Problema que Resolve
Qual problema esta melhoria resolve?

## 💭 Solução Proposta
Como você imagina que deveria funcionar?

## 🔄 Alternativas Consideradas
Outras soluções que você considerou?

## 📋 Contexto Adicional
Qualquer informação adicional relevante.
```

### **Critérios de Aceitação:**
- **Alinhamento**: Com objetivos do projeto
- **Viabilidade**: Técnica e de recursos
- **Impacto**: Benefício para usuários
- **Complexidade**: Esforço vs benefício

---

## 🏆 Reconhecimento

### **Contribuidores Serão Reconhecidos:**
- 📝 **README.md**: Lista de contribuidores
- 🏆 **Releases**: Créditos nas notas de versão
- 💬 **Issues/PRs**: Agradecimentos públicos
- 📜 **Licença**: Manutenção de créditos

### **Tipos de Contribuição:**
- 💻 **Código**: Desenvolvimento de funcionalidades
- 📚 **Documentação**: Melhorias na documentação
- 🐛 **Bugs**: Correção de problemas
- 🎨 **Design**: Melhorias na interface
- 🌐 **Tradução**: Tradução para outros idiomas
- 🧪 **Testes**: Melhoria na cobertura de testes

---

## 📞 Contato e Suporte

### **Canais de Comunicação:**
- 💬 **Issues**: Para bugs e melhorias
- 💻 **Pull Requests**: Para contribuições de código
- 📧 **Email**: [seu-email@exemplo.com]
- 🐦 **Twitter**: [@pharmassist] (se disponível)

### **Horários de Resposta:**
- **Issues**: 2-3 dias úteis
- **Pull Requests**: 1-2 dias úteis
- **Bugs Críticos**: 24 horas

---

## 📄 Código de Conduta

### **Nossos Compromissos:**
- 🌟 **Respeito**: Tratar todos com respeito
- 🤝 **Colaboração**: Trabalhar juntos construtivamente
- 📚 **Aprendizado**: Aprender com diferentes perspectivas
- 🔒 **Privacidade**: Respeitar privacidade e dados sensíveis

### **Comportamentos Inaceitáveis:**
- ❌ Linguagem ofensiva ou discriminatória
- ❌ Comportamento intimidatório ou assédio
- ❌ Compartilhamento de informações privadas
- ❌ Spam ou conteúdo comercial não solicitado

---

## 🙏 Agradecimentos

Obrigado por contribuir com o **Pharm-Assist**! Cada contribuição, por menor que seja, faz a diferença para melhorar o sistema de triagem farmacêutica e ajudar profissionais de saúde em todo o Brasil.

**Juntos, estamos construindo um futuro melhor para a saúde pública! 🏥✨**

---

<div align="center">

**🤝 Contribua hoje e faça parte da transformação da saúde! 🤝**

*Pharm-Assist - Sistema de Triagem Farmacêutica Inteligente*

</div>
