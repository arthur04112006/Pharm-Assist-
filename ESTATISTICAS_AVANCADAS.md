# 📊 Estatísticas Avançadas - Pharm-Assist

## 🎯 Visão Geral

A nova página de **Estatísticas Avançadas** oferece uma visualização interativa e personalizável dos dados do sistema, com filtros dinâmicos e gráficos responsivos usando Chart.js.

---

## ✨ Funcionalidades Implementadas

### 1️⃣ **Filtros Dinâmicos**

#### **Filtro de Período**
- ⏱️ **Hoje:** Dados do dia atual
- 📅 **Última Semana:** Últimos 7 dias
- 📆 **Último Mês:** Últimos 30 dias (padrão)
- 📅 **Último Ano:** Últimos 365 dias
- 🎯 **Personalizado:** Selecione datas específicas de início e fim

#### **Filtro de Limite**
- Top 5, 10, 15 ou 20 resultados para medicamentos mais recomendados

---

### 2️⃣ **Cards de Métricas em Tempo Real**

Exibe 4 métricas principais que atualizam conforme os filtros:

| Métrica | Descrição | Cor |
|---------|-----------|-----|
| **Total de Consultas** | Quantidade de consultas no período | Azul 🔵 |
| **Encaminhamentos** | Total de encaminhamentos + taxa percentual | Laranja 🟠 |
| **Taxa de Resolução** | Consultas resolvidas sem encaminhamento | Verde 🟢 |
| **Pacientes Atendidos** | Pacientes únicos + média por dia | Azul claro 🔵 |

---

### 3️⃣ **Gráficos Interativos**

#### **📈 Gráfico 1: Consultas por Período**
- **Tipos disponíveis:**
  - 📈 Linha (padrão)
  - 📊 Barras
- **Interatividade:**
  - Hover mostra dados detalhados
  - Animações suaves
  - Responsivo

#### **👥 Gráfico 2: Distribuição de Pacientes**
- **Agrupamentos disponíveis:**
  - 🎂 Por Faixa Etária (padrão)
    - 0-18 anos
    - 19-30 anos
    - 31-50 anos
    - 51-65 anos
    - 65+ anos
  - ⚧️ Por Gênero
    - Masculino
    - Feminino
    - Outros
- **Tipo:** Gráfico de Rosca (Doughnut)
- **Interatividade:**
  - Hover mostra percentual
  - Legendas clicáveis

#### **💊 Gráfico 3: Medicamentos Mais Recomendados**
- **Tipos disponíveis:**
  - 📊 Barras Verticais (padrão)
  - ↔️ Barras Horizontais
- **Funcionalidades:**
  - Exibe top N medicamentos (configurável)
  - Mostra quantidade e percentual
  - Cores gradientes
- **Filtros aplicáveis:**
  - Período temporal
  - Limite de resultados

---

## 🔧 APIs Implementadas

### **1. API de Consultas**
```
GET /api/estatisticas/consultas
```

**Parâmetros:**
- `periodo`: dia | semana | mes | ano
- `data_inicio`: YYYY-MM-DD (opcional)
- `data_fim`: YYYY-MM-DD (opcional)

**Resposta:**
```json
{
  "success": true,
  "periodo": "mes",
  "total_consultas": 47,
  "dados": [
    {
      "data": "01/11",
      "data_completa": "2025-11-01",
      "count": 5,
      "encaminhamentos": 1
    }
  ]
}
```

---

### **2. API de Medicamentos**
```
GET /api/estatisticas/medicamentos
```

**Parâmetros:**
- `periodo`: dia | semana | mes | ano
- `limite`: 5 | 10 | 15 | 20 (padrão: 10)
- `data_inicio`: YYYY-MM-DD (opcional)
- `data_fim`: YYYY-MM-DD (opcional)

**Resposta:**
```json
{
  "success": true,
  "periodo": "mes",
  "total_recomendacoes": 156,
  "medicamentos_unicos": 42,
  "dados": [
    {
      "medicamento": "Sorine (Cloridrato de Naftazolina)",
      "count": 18,
      "percentual": 38.3
    }
  ]
}
```

---

### **3. API de Pacientes**
```
GET /api/estatisticas/pacientes
```

**Parâmetros:**
- `agrupamento`: faixa_etaria | genero

**Resposta:**
```json
{
  "success": true,
  "agrupamento": "faixa_etaria",
  "total_pacientes": 6,
  "dados": [
    {
      "categoria": "0-18 anos",
      "count": 4
    }
  ]
}
```

---

### **4. API de Desempenho**
```
GET /api/estatisticas/desempenho
```

**Parâmetros:**
- `periodo`: dia | semana | mes | ano

**Resposta:**
```json
{
  "success": true,
  "periodo": "mes",
  "metricas": {
    "total_consultas": 47,
    "total_encaminhamentos": 3,
    "total_pacientes_atendidos": 6,
    "total_recomendacoes": 156,
    "taxa_encaminhamento": 6.4,
    "taxa_resolucao": 93.6,
    "media_consultas_dia": 1.6
  }
}
```

---

## 🎨 Design e UX

### **Cores e Temas**
- 🔵 **Azul (#6366f1):** Consultas, principal
- 🟢 **Verde (#10b981):** Sucesso, resolução
- 🟠 **Laranja (#f59e0b):** Medicamentos, avisos
- 🔴 **Vermelho (#ef4444):** Encaminhamentos, alertas

### **Responsividade**
- ✅ Desktop (1920x1080)
- ✅ Tablet (768x1024)
- ✅ Mobile (375x667)

### **Animações**
- ⚡ Transições suaves (0.3s)
- 🎭 Efeitos hover nos cards
- 📊 Animações de gráficos ao carregar
- 💫 Loading spinners durante carregamento

---

## 🚀 Como Usar

### **Acesso**
1. Faça login no sistema
2. No menu superior, clique em **"Estatísticas"**
3. Selecione **"Estatísticas Avançadas"**

### **Aplicando Filtros**
1. **Selecione o período:**
   - Escolha um período pré-definido OU
   - Selecione "Personalizado" e defina datas específicas

2. **Defina o limite de resultados:**
   - Escolha quantos medicamentos exibir (5-20)

3. **Clique em "Aplicar Filtros":**
   - Todos os gráficos serão atualizados
   - Métricas serão recalculadas

4. **Para limpar filtros:**
   - Clique em "Limpar" para voltar aos padrões

### **Interagindo com Gráficos**
- **Hover:** Passe o mouse sobre os dados para ver detalhes
- **Trocar tipo:** Use os botões no canto superior direito de cada gráfico
- **Alternar visualização:** Experimente diferentes tipos de gráficos

---

## 📱 Comparação: Dashboard vs Estatísticas Avançadas

| Recurso | Dashboard | Estatísticas Avançadas |
|---------|-----------|------------------------|
| Filtros de Período | ❌ | ✅ |
| Filtros de Data Personalizada | ❌ | ✅ |
| Tipos de Gráfico Alternáveis | ❌ | ✅ |
| Métricas de Desempenho | Limitadas | Completas |
| Limite Configurável | ❌ | ✅ |
| APIs Dedicadas | ❌ | ✅ |
| Atualização em Tempo Real | ❌ | ✅ |
| Exportação de Dados | ❌ | 🔜 Futuro |

---

## 🔮 Melhorias Futuras

### **Curto Prazo** (1-2 semanas)
- [ ] Exportar gráficos como PNG
- [ ] Exportar dados como CSV/Excel
- [ ] Adicionar mais agrupamentos de pacientes (por doença)
- [ ] Gráfico de tendências de medicamentos

### **Médio Prazo** (1-2 meses)
- [ ] Comparação de períodos (mês atual vs mês anterior)
- [ ] Previsões usando Machine Learning
- [ ] Dashboard personalizável (arrastar e soltar)
- [ ] Relatórios agendados por email

### **Longo Prazo** (3-6 meses)
- [ ] Análise de correlações (sintomas x medicamentos)
- [ ] Heatmap de horários de atendimento
- [ ] Análise geográfica (se houver dados de localização)
- [ ] Integração com BI (Business Intelligence)

---

## 🛠️ Tecnologias Utilizadas

- **Backend:**
  - Python 3.x
  - Flask
  - SQLAlchemy
  - APIs RESTful

- **Frontend:**
  - HTML5
  - CSS3 (com variáveis CSS)
  - JavaScript (ES6+)
  - Chart.js 4.x
  - Bootstrap 5
  - Bootstrap Icons

---

## 📝 Exemplos de Uso

### **Exemplo 1: Análise Mensal**
```
1. Selecione "Último Mês" no filtro de período
2. Defina "Top 10" no limite
3. Clique em "Aplicar Filtros"
4. Visualize:
   - Quantas consultas foram realizadas
   - Qual a taxa de encaminhamento
   - Quais medicamentos foram mais recomendados
```

### **Exemplo 2: Comparação de Períodos**
```
1. Anote as métricas do "Último Mês"
2. Mude para "Última Semana"
3. Compare as variações:
   - Aumento/diminuição de consultas
   - Mudanças nos medicamentos mais usados
```

### **Exemplo 3: Análise Personalizada**
```
1. Selecione "Personalizado"
2. Defina: 01/10/2025 a 31/10/2025
3. Analise dados específicos de outubro
4. Troque tipo de gráfico para melhor visualização
```

---

## 🐛 Troubleshooting

### **Gráficos não aparecem**
- ✅ Verifique se há dados no período selecionado
- ✅ Limpe o cache do navegador
- ✅ Verifique o console do navegador (F12)

### **Filtros não funcionam**
- ✅ Certifique-se de clicar em "Aplicar Filtros"
- ✅ Verifique se as datas são válidas
- ✅ Data início deve ser menor que data fim

### **Carregamento lento**
- ✅ Normal para períodos muito longos (1 ano)
- ✅ Use períodos menores para performance
- ✅ O sistema é otimizado, mas grandes volumes levam tempo

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique este documento
2. Consulte o administrador do sistema
3. Abra uma issue no repositório

---

## 📄 Changelog

### **Versão 1.0** (05/11/2025)
- ✅ Implementação inicial
- ✅ 4 APIs de dados filtrados
- ✅ 3 gráficos interativos
- ✅ 4 cards de métricas
- ✅ Filtros dinâmicos completos
- ✅ Design responsivo
- ✅ Integração com menu principal

---

**Desenvolvido para Pharm-Assist**  
**Versão:** 1.0  
**Data:** 05/11/2025

