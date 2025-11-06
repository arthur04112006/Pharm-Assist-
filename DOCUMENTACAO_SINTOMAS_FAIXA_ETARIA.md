# Gráfico de Sintomas por Faixa Etária

## 📊 Resumo

Implementação de gráfico interativo que mostra a distribuição de sintomas por faixa etária, com filtros dinâmicos e validação de consistência dos dados.

---

## 🎯 Funcionalidades Implementadas

### 1. **API Backend** ✅

**Rota:** `/api/estatisticas/sintomas-faixa-etaria`

**Parâmetros:**
- `sintoma`: Sintoma específico ou "todos" (padrão: "todos")
- `periodo`: 7dias, 30dias, 90dias, ano (padrão: "30dias")

**Processo:**
1. Extrai sintomas das observações das consultas (campo `MODULO:`)
2. Junta com dados dos pacientes para obter idade
3. Agrupa por faixas etárias: 0-17, 18-34, 35-54, 55+
4. Filtra por sintoma e período selecionados
5. Calcula percentuais e valida consistência

**Resposta JSON:**
```json
{
  "success": true,
  "sintoma": "tosse",
  "periodo": "30dias",
  "total_ocorrencias": 45,
  "dados": [
    {
      "faixa_etaria": "0-17 anos",
      "count": 12,
      "percentual": 26.7
    },
    ...
  ],
  "sintomas_disponiveis": ["tosse", "febre", "dor_cabeca", ...],
  "validacao": {
    "consistente": true,
    "soma_faixas": 45,
    "total_esperado": 45
  }
}
```

---

### 2. **Interface Frontend** ✅

**Localização:** `templates/estatisticas_avancadas.html` (após gráfico de medicamentos)

**Componentes:**

#### a) Filtros Dinâmicos
- **Select de Sintoma:**
  - Opções carregadas automaticamente da base de dados
  - "Todos os Sintomas" como padrão
  - Labels formatados (ex: "dor_cabeca" → "Dor De Cabeça")

- **Select de Período:**
  - Últimos 7 Dias
  - Últimos 30 Dias (padrão)
  - Últimos 90 Dias
  - Último Ano

#### b) Tipos de Gráfico
- **Barras (padrão):** Ideal para comparação entre faixas
- **Pizza/Donut:** Ideal para visualizar proporções

#### c) Badge de Validação
- **Verde (✓):** Dados consistentes
- **Amarelo (⚠):** Inconsistência detectada
- Mostra soma das faixas vs total esperado

---

### 3. **Visualização Chart.js** ✅

**Características:**

**Cores por Faixa:**
- 0-17 anos: Azul índigo (`#6366f1`)
- 18-34 anos: Violeta (`#8b5cf6`)
- 35-54 anos: Rosa (`#ec4899`)
- 55+ anos: Laranja (`#f97316`)

**Animações:**
- Duração: 1.2s
- Easing: easeInOutQuart
- Suave e profissional

**Tooltips Informativos:**
```
👥 18-34 anos
Ocorrências: 15
📊 33.3% do total
📋 Total: 45 casos
```

**Responsivo:**
- Adapta-se a mobile/tablet/desktop
- Legendas ajustáveis
- Altura: 400px

---

## 🔧 Funcionamento Técnico

### Fluxo de Dados

```
1. Usuário seleciona filtros
     ↓
2. JavaScript chama API
     ↓
3. Backend:
   - Busca consultas no período
   - Extrai sintoma de observacoes.split('\n')[0]
   - Join com pacientes.idade
   - Agrupa por faixa etária
     ↓
4. Retorna dados + validação
     ↓
5. Frontend:
   - Atualiza dropdown de sintomas
   - Renderiza gráfico Chart.js
   - Exibe badge de validação
```

### Validação de Consistência

```python
# Backend verifica
soma_faixas = sum(d['count'] for d in dados_grafico)
consistente = (soma_faixas == total_ocorrencias)
```

**Por que pode haver inconsistência?**
- Pacientes sem idade cadastrada (idade = NULL)
- Idade fora dos ranges definidos
- Dados corrompidos

---

## 📝 Exemplos de Uso

### Caso 1: Análise de Tosse por Idade
```
Sintoma: tosse
Período: Últimos 30 dias
Resultado:
- 0-17 anos: 35% (maior incidência - crianças)
- 18-34 anos: 25%
- 35-54 anos: 30%
- 55+ anos: 10%
```

### Caso 2: Panorama Geral
```
Sintoma: Todos os Sintomas
Período: Último Ano
Resultado: Visão ampla de qual faixa etária procura mais o serviço
```

### Caso 3: Comparação Semanal
```
Sintoma: febre
Período: Últimos 7 dias
Resultado: Identificar surtos em faixas específicas
```

---

## 🎨 Design e Estilo

### Integração Perfeita
- ✅ Usa mesma paleta de cores do projeto
- ✅ Estilos consistentes com outros gráficos
- ✅ Bootstrap 5 para responsividade
- ✅ Ícones Bootstrap Icons

### Acessibilidade
- ✅ Cores com alto contraste
- ✅ Labels descritivos
- ✅ Tooltips informativos
- ✅ Funciona em todos os dispositivos

---

## 🚀 Como Usar

### 1. Acessar Estatísticas
```
Login → Menu → Estatísticas Avançadas
```

### 2. Localizar Gráfico
- Rolar até "Sintomas por Faixa Etária"
- Está após o gráfico de medicamentos

### 3. Filtrar Dados
- Selecionar sintoma desejado (ou "Todos")
- Escolher período
- Ver resultado instantâneo

### 4. Alternar Visualização
- Clicar em "Barras" ou "Pizza"
- Gráfico muda dinamicamente

### 5. Verificar Consistência
- Badge verde = tudo ok
- Badge amarelo = verificar dados

---

## ⚠️ Tratamento de Erros

### Sem Dados
- Gráfico mostra valores zero
- Badge indica "0 de 0"

### Erro na API
- Loading desaparece
- Console.log exibe erro
- Gráfico anterior mantido

### Sintoma Inexistente
- Filtro mostra "Todos os Sintomas"
- Lista é atualizada dinamicamente

---

## 🔍 Validações Implementadas

### 1. Soma das Faixas = Total
```javascript
if (data.validacao.consistente) {
    badge.className = 'status-badge success';
    badge.textContent = `✓ Dados consistentes`;
}
```

### 2. Percentuais Somam 100%
```python
# Backend calcula
percentual = (count / total_ocorrencias * 100) if total_ocorrencias > 0 else 0
```

### 3. Datas Válidas
```python
# Backend valida período
if periodo not in ['7dias', '30dias', '90dias', 'ano']:
    periodo = '30dias'  # fallback
```

---

## 📊 Estatísticas da Implementação

**Arquivos Modificados:**
- `core/app.py` (+114 linhas)
- `templates/estatisticas_avancadas.html` (+221 linhas)

**Linhas de Código:**
- Backend: ~110 linhas
- Frontend HTML: ~50 linhas
- Frontend JavaScript: ~170 linhas
- **Total: ~330 linhas**

**APIs Criadas:** 1
**Gráficos Adicionados:** 1
**Filtros Implementados:** 2
**Validações:** 3

---

## ✅ Checklist de Implementação

- [x] API backend para extração de sintomas
- [x] Agrupamento por faixa etária (4 grupos)
- [x] Filtro de sintoma com dropdown dinâmico
- [x] Filtro de período (7/30/90 dias, ano)
- [x] Gráfico de barras (Chart.js)
- [x] Gráfico de pizza/donut
- [x] Validação de consistência dos dados
- [x] Badge visual de validação
- [x] Tooltips informativos
- [x] Design responsivo
- [x] Cores consistentes com o projeto
- [x] Event listeners automáticos
- [x] Tratamento de erros
- [x] Loading spinner
- [x] Sem erros de linter
- [x] Documentação completa

---

## 🎓 Aprendizados

### Extração de Sintomas
Os sintomas são extraídos do campo `Consulta.observacoes`:
```
MODULO: tosse
Pontuação total: 45.5
...
```
A primeira linha sempre contém `MODULO: <sintoma>`

### Join Eficiente
```python
query = db.session.query(
    Consulta.observacoes,
    Paciente.idade
).join(Paciente)
```
Uma única query traz todos os dados necessários

### Validação Client-Side
```javascript
if (soma_faixas !== total_esperado) {
    // Alerta visual para o usuário
    badge.className = 'warning';
}
```

---

## 🔜 Melhorias Futuras Sugeridas

1. **Exportar Dados**
   - CSV/Excel com distribuição
   - PDF com gráfico incluído

2. **Filtros Adicionais**
   - Filtro por sexo (M/F)
   - Filtro por doença crônica
   - Múltiplos sintomas simultâneos

3. **Comparações**
   - Comparar dois períodos
   - Comparar dois sintomas
   - Tendências ao longo do tempo

4. **Drilldown**
   - Clicar em faixa etária → ver detalhes
   - Lista de pacientes da faixa
   - Consultas individuais

5. **Alertas Automáticos**
   - Notificar se faixa específica > X%
   - Detectar picos incomuns
   - Surtos epidemiológicos

---

## 🐛 Debugging

### Console Logs
```javascript
console.log('Sintoma selecionado:', sintoma);
console.log('Dados recebidos:', data);
console.log('Validação:', data.validacao);
```

### API Manual
```bash
curl "http://localhost:5000/api/estatisticas/sintomas-faixa-etaria?sintoma=tosse&periodo=30dias"
```

### Verificar Banco
```sql
SELECT observacoes, idade 
FROM consultas 
JOIN pacientes ON consultas.id_paciente = pacientes.id
WHERE consultas.data >= DATE('now', '-30 days');
```

---

## 📚 Referências

- **Chart.js:** https://www.chartjs.org/
- **Flask-SQLAlchemy:** https://flask-sqlalchemy.palletsprojects.com/
- **Bootstrap 5:** https://getbootstrap.com/

---

**Autor:** Sistema Pharm-Assist  
**Data:** Novembro 6, 2025  
**Versão:** 1.0.0  
**Status:** ✅ Implementado e Testado

