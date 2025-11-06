# Implementação de Gráfico de Linha com Média

## 📊 Resumo das Melhorias

Este documento descreve as melhorias implementadas no módulo de estatísticas avançadas do **Pharm-Assist**, adicionando visualização automática de média móvel no gráfico de consultas que acompanha a tendência dos dados.

---

## 🎯 Funcionalidades Implementadas

### 1. **Cálculo de Média no Backend** ✅

**Arquivo:** `core/app.py` - Rota `/api/estatisticas/consultas`

**Melhorias:**
- ✅ Adicionado cálculo automático de **média móvel** (acompanha a tendência dos dados)
- ✅ Janela de média móvel: **7 dias** (padrão)
- ✅ Novos períodos de filtro: **7 dias**, **30 dias**, **90 dias**
- ✅ A média é calculada automaticamente para todos os períodos selecionados

**Exemplo de resposta da API:**
```json
{
  "success": true,
  "periodo": "30dias",
  "tipo_media": "movel",
  "janela_media": 7,
  "media_geral": 5.43,
  "total_consultas": 150,
  "dados": [
    {
      "data": "01/11",
      "data_completa": "2025-11-01",
      "count": 8,
      "media": 5.2,
      "encaminhamentos": 2
    },
    ...
  ]
}
```

---

### 2. **Filtros Avançados no Frontend** ✅

**Arquivo:** `templates/estatisticas_avancadas.html`

**Novos Filtros:**

#### a) **Período de Análise**
- Hoje
- **Últimos 7 Dias** 🆕
- **Últimos 30 Dias** 🆕 (padrão)
- **Últimos 90 Dias** 🆕
- Último Ano
- Personalizado (com seleção de data início/fim)

#### b) **Média Móvel Automática**
- **Média Móvel (7 dias)**: Calculada automaticamente e exibida como linha que acompanha a tendência
- Suaviza variações diárias mostrando a tendência geral
- Não requer configuração adicional - sempre ativa

---

### 3. **Gráfico de Linha Dual** ✅

**Biblioteca:** Chart.js

**Visualização:**
O gráfico de consultas agora exibe **duas linhas simultâneas**:

1. **Linha Azul (Consultas Realizadas)**
   - Cor: `#6366f1` (índigo)
   - Estilo: Linha sólida com preenchimento gradiente
   - Pontos: Círculos com destaque no hover
   - Representa: Dados reais de consultas por dia

2. **Linha Vermelha (Média Móvel)**
   - Cor: `#ef4444` (vermelho)
   - Estilo: Linha tracejada com preenchimento sutil
   - Pontos: Losangos (formato diferente para distinção)
   - Label: "Média Móvel (7 dias)"
   - Representa: Média dos últimos 7 dias em cada ponto, criando uma linha suavizada que acompanha a tendência

**Características:**
- ✅ Gradientes modernos e suaves
- ✅ Animações fluidas ao carregar (1.5s)
- ✅ Tooltips informativos com porcentagens
- ✅ Legendas interativas
- ✅ Design responsivo para mobile
- ✅ Consistente com o tema visual do projeto

---

### 4. **Event Listeners e Interatividade** ✅

**JavaScript implementado:**

```javascript
// Atualização dinâmica do gráfico ao aplicar filtros
function aplicarFiltros() {
    carregarDesempenho();
    carregarConsultas();  // ← Agora inclui média automaticamente
    carregarMedicamentos();
    carregarPacientes('faixa_etaria');
}

// Média móvel (7 dias) sempre calculada e exibida por padrão
params.append('tipo_media', 'movel');
params.append('janela_media', '7');
```

---

## 🧮 Algoritmos de Cálculo

### Média Móvel (Janela de 7 dias)
```python
for i in range(len(valores)):
    if i < 7 - 1:
        # Primeiros 6 pontos: média dos valores disponíveis
        media = sum(valores[:i+1]) / (i+1)
    else:
        # A partir do 7º dia: média dos últimos 7 dias
        janela = valores[i-6:i+1]
        media = sum(janela) / 7
```

**Exemplo:**
- Consultas: [10, 8, 12, 6, 9, 15, 7, 11, 8]
- Médias Móveis (7 dias): [10.0, 9.0, 10.0, 9.0, 9.0, 10.0, 9.57, 9.71, 9.71]
- **Linha acompanha a tendência dos dados** ✅


---

## 🎨 Design e Estilo

### Paleta de Cores
| Elemento | Cor Hex | RGB | Descrição |
|----------|---------|-----|-----------|
| Linha Principal | `#6366f1` | rgb(99, 102, 241) | Azul índigo (primária do projeto) |
| Linha Média | `#ef4444` | rgb(239, 68, 68) | Vermelho (contraste) |
| Gradiente 1 | `rgba(99, 102, 241, 0.5)` | - | Azul semi-transparente |
| Gradiente 2 | `rgba(239, 68, 68, 0.2)` | - | Vermelho muito sutil |

### Acessibilidade
- ✅ Contraste adequado (WCAG AA)
- ✅ Linhas com estilos diferentes (sólida vs. tracejada)
- ✅ Formas de pontos diferentes (círculo vs. losango)
- ✅ Labels descritivos
- ✅ Tooltips informativos

---

## 📱 Responsividade

### Desktop (> 992px)
- Altura do gráfico: 400px
- Filtros em linha (grid)
- Tooltips completos

### Tablet (768px - 992px)
- Altura do gráfico: 350px
- Filtros ajustados
- Labels reduzidos

### Mobile (< 768px)
- Altura do gráfico: 300px
- Filtros em coluna (100% largura)
- Botões full-width
- Fonte menor

---

## 🚀 Como Usar

### 1. Iniciar o Sistema
```bash
# Ativar venv (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Executar aplicação
python run.py
```

### 2. Acessar Estatísticas
1. Fazer login no sistema
2. Navegar para **Estatísticas Avançadas** no menu
3. Selecionar o período desejado (7, 30 ou 90 dias)
4. Clicar em **"Aplicar Filtros"**
5. Visualizar o gráfico com **duas linhas** automaticamente

### 3. Interpretar o Gráfico
- **Linha Azul Sólida**: Dados reais de consultas por dia (pode variar muito)
- **Linha Vermelha Tracejada**: Média móvel (7 dias) - acompanha a tendência suavemente
- **Distância entre linhas**: Mostra picos e quedas em relação à tendência
- **Direção da linha vermelha**: 
  - Subindo = tendência de aumento
  - Descendo = tendência de queda
  - Horizontal = estabilidade

---

## 🔧 Configurações Técnicas

### Dependências (já presentes)
- **Flask**: Framework web
- **SQLAlchemy**: ORM para banco de dados
- **Chart.js**: Biblioteca de gráficos (CDN)
- **Bootstrap 5**: Framework CSS
- **Bootstrap Icons**: Ícones

### APIs Modificadas

#### `/api/estatisticas/consultas`
**Parâmetros:**
- `periodo`: `dia`, `7dias`, `30dias`, `90dias`, `ano`, `personalizado`
- `data_inicio`: String no formato `YYYY-MM-DD` (apenas se periodo=personalizado)
- `data_fim`: String no formato `YYYY-MM-DD` (apenas se periodo=personalizado)
- `tipo_media`: `movel` (sempre, calculado automaticamente)
- `janela_media`: `7` (fixo, média dos últimos 7 dias)

#### `/api/estatisticas/desempenho`
**Parâmetros atualizados:**
- Suporte a `7dias`, `30dias`, `90dias`

---

## 📊 Casos de Uso

### 1. Identificar Tendências de Crescimento/Queda
**Cenário:** Farmacêutico quer saber se as consultas estão aumentando ou diminuindo ao longo do tempo

**Ação:**
- Período: Últimos 90 dias

**Resultado:** Linha de média móvel mostra claramente a tendência:
- Se a linha vermelha está subindo → consultas aumentando
- Se está descendo → consultas diminuindo
- Se estável → volume constante

---

### 2. Suavizar Variações de Fim de Semana
**Cenário:** Fins de semana sempre têm menos consultas, dificulta ver a tendência real

**Ação:**
- Período: Últimos 30 dias

**Resultado:** A média móvel suaviza as quedas de fim de semana, mostrando a tendência geral do mês

---

### 3. Detectar Mudanças Recentes
**Cenário:** Houve uma campanha de saúde recente, quer ver o impacto

**Ação:**
- Período: Últimos 30 dias

**Resultado:** A linha vermelha mostra se houve aumento sustentado após a campanha, não apenas um pico isolado

---

## 🐛 Tratamento de Erros

### Sem dados no período
- API retorna arrays vazios
- Gráfico exibe mensagem "Nenhum dado disponível"

### Erro na API
- Loading spinner desaparece
- Mensagem de erro no console
- Gráfico anterior mantido (não quebra)

### Período inválido
- Backend retorna erro 400
- Frontend exibe alerta

---

## ✅ Checklist de Implementação

- [x] Modificar API `/api/estatisticas/consultas` com cálculo de média simples
- [x] Adicionar períodos 7, 30, 90 dias no filtro
- [x] Modificar função `carregarConsultas()` no JavaScript
- [x] Adicionar segunda linha (média) ao gráfico Chart.js automaticamente
- [x] Atualizar função `getFiltroParams()` para incluir média
- [x] Atualizar API `/api/estatisticas/desempenho`
- [x] Testar responsividade
- [x] Verificar consistência de estilos
- [x] Documentar funcionalidades

---

## 📖 Referências

- **Chart.js Documentation**: https://www.chartjs.org/docs/
- **Flask Documentation**: https://flask.palletsprojects.com/
- **Bootstrap 5**: https://getbootstrap.com/docs/5.0/

---

## 👨‍💻 Autor

Implementação realizada em: **Novembro 6, 2025**

Sistema: **Pharm-Assist - Sistema de Triagem Farmacêutica**

---

## 📝 Notas Finais

Esta implementação mantém **100% de compatibilidade** com o sistema existente:
- ✅ Não quebra funcionalidades anteriores
- ✅ APIs retrocompatíveis (parâmetros novos são opcionais)
- ✅ Interface consistente com o design existente
- ✅ Sem erros de linter
- ✅ Código documentado e comentado

**Próximas melhorias sugeridas:**
- [ ] Exportar dados do gráfico para CSV/Excel
- [ ] Adicionar opção de escolher entre média simples e média móvel
- [ ] Permitir comparação entre múltiplos períodos
- [ ] Adicionar previsões com base nas tendências
- [ ] Implementar alertas quando valores fogem muito da média

