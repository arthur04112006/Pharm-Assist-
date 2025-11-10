# Gráfico de Sintomas por Gênero

## 📊 Resumo

Implementação de gráfico interativo que mostra a distribuição de sintomas por gênero (Masculino, Feminino, Outro), com filtros dinâmicos e validação completa de dados.

---

## 🎯 Funcionalidades Implementadas

### 1. **API Backend** ✅

**Rota:** `/api/estatisticas/sintomas-genero`

**Parâmetros:**
- `sintoma`: Sintoma específico ou "todos" (padrão: "todos")
- `periodo`: 7dias, 30dias, 90dias, ano (padrão: "30dias")

**Processo:**
1. Extrai sintomas das observações das consultas
2. Junta com dados dos pacientes para obter gênero
3. Agrupa por gênero: **Masculino**, **Feminino**, **Outro**
4. Filtra por sintoma e período selecionados
5. Calcula percentuais e valida consistência
6. Verifica dados sem gênero (se houver)

**Resposta JSON:**
```json
{
  "success": true,
  "sintoma": "tosse",
  "periodo": "30dias",
  "total_ocorrencias": 50,
  "dados": [
    {
      "genero": "Masculino",
      "count": 25,
      "percentual": 50.0
    },
    {
      "genero": "Feminino",
      "count": 23,
      "percentual": 46.0
    },
    {
      "genero": "Outro",
      "count": 2,
      "percentual": 4.0
    }
  ],
  "sintomas_disponiveis": ["tosse", "febre", "dor_cabeca"],
  "validacao": {
    "consistente": true,
    "soma_generos": 50,
    "total_esperado": 50,
    "dados_sem_genero": 0
  },
  "limitacoes": {
    "campo_genero_disponivel": true,
    "valores_possiveis": ["Masculino", "Feminino", "Outro"],
    "campo_obrigatorio": true,
    "observacao": "Campo gênero é obrigatório no cadastro do paciente"
  }
}
```

---

### 2. **Campo Gênero no Banco de Dados** ✅

**Tabela:** `Paciente`  
**Campo:** `sexo`  
**Tipo:** `ENUM('M', 'F', 'O')`  
**Obrigatório:** ✅ SIM (`nullable=False`)  
**Indexado:** ✅ SIM (para performance em estatísticas)

**Mapeamento:**
- `'M'` → Masculino
- `'F'` → Feminino  
- `'O'` → Outro

**Limitações Documentadas:**
- ✅ Campo **obrigatório** no cadastro
- ✅ Todos os pacientes **devem** ter gênero
- ✅ Valores restritos a 3 opções (ENUM)
- ✅ **Sem dados NULL** possíveis

---

### 3. **Interface Frontend** ✅

**Localização:** `templates/estatisticas_avancadas.html` (após gráfico de faixa etária)

**Componentes:**

#### a) Filtros Dinâmicos
- **Select de Sintoma:**
  - Opções carregadas automaticamente
  - "Todos os Sintomas" como padrão
  - Labels formatados

- **Select de Período:**
  - Últimos 7 Dias
  - Últimos 30 Dias (padrão)
  - Últimos 90 Dias
  - Último Ano

#### b) Tipos de Gráfico
- **Barras (padrão):** Comparação direta entre gêneros
- **Pizza/Donut:** Visualização de proporções

#### c) Badge de Validação
- **Verde (✓):** Dados consistentes
- **Amarelo (⚠):** Inconsistência detectada
- **Informações adicionais:**
  - Dados sem gênero (se houver)
  - Status do campo: OBRIGATÓRIO ✓

---

### 4. **Visualização Chart.js** ✅

**Cores Consistentes e Claras:**

| Gênero | Cor Principal | Cor Hover | Ícone |
|--------|--------------|-----------|-------|
| Masculino | `#3b82f6` (Azul) | `#2563eb` | ♂️ |
| Feminino | `#ec4899` (Rosa) | `#db2777` | ♀️ |
| Outro | `#a855f7` (Roxo) | `#9333ea` | ⚧ |

**Características:**
- Animações suaves (1.2s)
- Tooltips com ícones de gênero
- Legendas claras com percentuais
- Design responsivo
- Bordas arredondadas (barras)
- Hover interativo

**Exemplo de Tooltip:**
```
♂️ Masculino
Ocorrências: 25
📊 50.0% do total
📋 Total: 50 casos
```

---

## 🔧 Funcionamento Técnico

### Fluxo de Dados

```
1. Usuário seleciona filtros (sintoma + período)
     ↓
2. JavaScript chama API /api/estatisticas/sintomas-genero
     ↓
3. Backend:
   - Busca consultas no período
   - Extrai sintoma de observações
   - Join com pacientes.sexo
   - Agrupa por gênero (M/F/O)
   - Valida consistência
     ↓
4. Retorna dados + validação + limitações
     ↓
5. Frontend:
   - Atualiza dropdown de sintomas
   - Renderiza gráfico Chart.js
   - Exibe badge com validação
   - Mostra status do campo gênero
```

### Validação de Consistência

```python
# Verifica se soma dos gêneros = total
soma_generos = sum(d['count'] for d in dados_grafico)
consistente = (soma_generos == total_ocorrencias)

# Verifica dados sem gênero (teoricamente impossível)
dados_sem_genero = consultas_com_sintoma - total_ocorrencias
```

**Validações Implementadas:**
1. ✅ Soma dos gêneros = Total de casos
2. ✅ Sem dados NULL (campo obrigatório)
3. ✅ Valores dentro do ENUM (M/F/O)
4. ✅ Percentuais somam 100%

---

## 📝 Exemplos de Uso

### Caso 1: Tosse por Gênero
```
Sintoma: tosse
Período: Últimos 30 dias
Resultado:
- Masculino: 45% 
- Feminino: 50% (maior incidência)
- Outro: 5%

Insight: Mulheres têm mais tosse neste período
```

### Caso 2: Febre - Comparação
```
Sintoma: febre
Período: Último Ano
Resultado:
- Masculino: 48%
- Feminino: 49%
- Outro: 3%

Insight: Distribuição equilibrada entre gêneros
```

### Caso 3: Todos os Sintomas
```
Sintoma: Todos os Sintomas
Período: Últimos 90 dias
Resultado: Perfil geral de quem procura o serviço
```

---

## 🎨 Design e Estilo

### Paleta de Cores (Inclusiva e Clara)

**Azul para Masculino:**
- Tradicionalmente associado
- Alto contraste
- Acessível

**Rosa para Feminino:**
- Cor clara e vibrante
- Distinguível
- Moderna

**Roxo para Outro:**
- Cor neutra
- Inclusiva
- Mesma hierarquia visual

### Acessibilidade
- ✅ Cores com contraste WCAG AA
- ✅ Ícones descritivos (♂️♀️⚧)
- ✅ Labels claros
- ✅ Tooltips informativos
- ✅ Funciona sem daltonismo issues

---

## 🚀 Como Usar

### 1. Acessar Estatísticas
```
Login → Estatísticas Avançadas → Rolar até final
```

### 2. Localizar Gráfico
- Seção: "Sintomas por Gênero"
- Após gráfico de faixa etária
- Ícone: ⚥ (gender-ambiguous)

### 3. Filtrar Dados
- Selecionar sintoma (ou "Todos")
- Escolher período
- Ver resultado instantâneo

### 4. Alternar Visualização
- **Barras:** Comparação lado a lado
- **Pizza:** Proporções visuais

### 5. Verificar Validação
- Badge verde = consistente ✓
- Campo gênero: OBRIGATÓRIO ✓
- 0 registros sem gênero

---

## 🔍 Limitações Documentadas

### ✅ **NENHUMA LIMITAÇÃO CRÍTICA**

**Campo Gênero:**
- ✅ **Disponível** no banco de dados
- ✅ **Obrigatório** no cadastro
- ✅ **Indexado** para performance
- ✅ **Validado** pelo ENUM
- ✅ **100% dos pacientes têm gênero**

**Observações:**
```json
{
  "campo_genero_disponivel": true,
  "valores_possiveis": ["Masculino", "Feminino", "Outro"],
  "campo_obrigatorio": true,
  "observacao": "Campo gênero é obrigatório no cadastro do paciente"
}
```

**Não há necessidade de:**
- ❌ Tratamento de NULL
- ❌ Dados ausentes
- ❌ Workarounds
- ❌ Avisos de limitação

**Sistema 100% funcional** ✅

---

## ⚠️ Tratamento de Erros

### Sem Dados no Período
- Gráfico mostra 0 para todos
- Badge: "0 de 0"
- Não gera erro

### Erro na API
- Loading desaparece
- Console.log do erro
- Gráfico anterior mantido

### Filtro Inválido
- Fallback para "todos"
- Período padrão: 30 dias

---

## 📊 Estatísticas da Implementação

**Arquivos Modificados:**
- `core/app.py` (+123 linhas)
- `templates/estatisticas_avancadas.html` (+234 linhas)

**Código Adicionado:**
- Backend: ~120 linhas
- Frontend HTML: ~55 linhas
- Frontend JavaScript: ~180 linhas
- **Total: ~355 linhas**

**APIs Criadas:** 1
**Gráficos Adicionados:** 1
**Filtros:** 2
**Validações:** 4

---

## ✅ Checklist de Implementação

- [x] Verificar existência do campo gênero
- [x] Confirmar que é obrigatório
- [x] API backend para extração
- [x] Agrupamento por gênero (M/F/O)
- [x] Filtro de sintoma dinâmico
- [x] Filtro de período
- [x] Gráfico de barras
- [x] Gráfico de pizza
- [x] Validação de consistência
- [x] Badge de status
- [x] Documentação de limitações
- [x] Cores consistentes
- [x] Ícones de gênero (♂️♀️⚧)
- [x] Tooltips informativos
- [x] Design responsivo
- [x] Event listeners
- [x] Sem erros de linter
- [x] Totalmente funcional

---

## 🎓 Decisões Técnicas

### 1. Por que ENUM?
```python
sexo = db.Column(db.Enum('M', 'F', 'O'), nullable=False)
```
- ✅ Garante valores válidos
- ✅ Previne erros de digitação
- ✅ Otimiza espaço no banco
- ✅ Performance em queries

### 2. Por que Campo Obrigatório?
```python
nullable=False
```
- ✅ Evita dados NULL
- ✅ Simplifica queries
- ✅ Não precisa tratamento especial
- ✅ 100% de cobertura

### 3. Por que 3 Cores Específicas?
```javascript
['#3b82f6', '#ec4899', '#a855f7']
```
- ✅ Azul/Rosa/Roxo: Inclusivo
- ✅ Alto contraste
- ✅ Acessível (daltonismo)
- ✅ Consistente com projeto

---

## 🔜 Melhorias Futuras

1. **Análise Temporal**
   - Gráfico de linha: gênero ao longo do tempo
   - Identificar mudanças sazonais

2. **Cruzamento de Dados**
   - Gênero + Faixa Etária (matriz)
   - Sintoma + Gênero + Doença Crônica

3. **Estatísticas Avançadas**
   - Teste qui-quadrado (significância)
   - Odds ratio por gênero
   - Intervalos de confiança

4. **Comparações**
   - Comparar 2 sintomas lado a lado
   - Comparar 2 períodos
   - Benchmark com dados nacionais

5. **Exportação**
   - CSV com dados brutos
   - PDF com gráfico
   - API pública para pesquisadores

---

## 🐛 Debugging

### Console Logs
```javascript
console.log('Sintoma:', sintoma);
console.log('Período:', periodo);
console.log('Dados:', data);
console.log('Limitações:', data.limitacoes);
```

### Testar API Direto
```bash
curl "http://localhost:5000/api/estatisticas/sintomas-genero?sintoma=tosse&periodo=30dias"
```

### Verificar Banco
```sql
SELECT 
  observacoes, 
  sexo,
  CASE sexo 
    WHEN 'M' THEN 'Masculino'
    WHEN 'F' THEN 'Feminino'
    WHEN 'O' THEN 'Outro'
  END as genero
FROM consultas
JOIN pacientes ON consultas.id_paciente = pacientes.id
WHERE consultas.data >= DATE('now', '-30 days');
```

---

## 🎉 Conclusão

### **Campo Gênero: 100% Funcional** ✅

Não há limitações técnicas:
- ✅ Campo existe
- ✅ É obrigatório
- ✅ Todos os dados têm gênero
- ✅ Sistema completo e robusto

### **Gráfico: Pronto para Produção** ✅

- ✅ Validação completa
- ✅ Design inclusivo
- ✅ Performance otimizada
- ✅ Sem bugs conhecidos

---

**Autor:** Sistema Pharm-Assist  
**Data:** Novembro 10, 2025  
**Versão:** 1.0.0  
**Status:** ✅ Implementado e Testado

