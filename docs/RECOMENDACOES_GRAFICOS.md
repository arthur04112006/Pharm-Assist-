# 📊 Recomendações de Gráficos para Pharm-Assist

## Análise do Projeto

### Gráficos Existentes ✅
1. **Consultas por Período** - Evolução temporal das consultas
2. **Sintomas Mais Comuns** - Ranking de sintomas por frequência
3. **Sintomas por Faixa Etária** - Distribuição de sintomas por idade
4. **Sintomas por Gênero** - Distribuição de sintomas por sexo
5. **Sintomas por Localização** - Distribuição por bairro/cidade
6. **Medicamentos Mais Usados por Sintoma** - Ranking com score
7. **Medicamentos Mais Recomendados** - Ranking geral de medicamentos

### Dados Disponíveis no Banco
- **Paciente**: idade, peso, altura, sexo, fuma, bebe, bairro, cidade, created_at
- **Consulta**: data, encaminhamento, motivo_encaminhamento, observacoes
- **ConsultaRecomendacao**: tipo (medicamento/nao_farmacologico/encaminhamento), descricao, justificativa
- **PacienteDoenca**: relacionamento paciente-doença crônica
- **Medicamento**: tipo (farmacologico/fitoterapico), ativo
- **ConsultaResposta**: respostas do questionário

---

## 🎯 Gráficos Recomendados

### 1. **Taxa de Encaminhamentos ao Longo do Tempo** ⭐⭐⭐⭐⭐
**Prioridade: ALTA**

**Descrição**: Gráfico de linha mostrando a evolução da taxa de encaminhamentos médicos ao longo do tempo.

**Dados necessários**:
- `Consulta.encaminhamento` (True/False)
- `Consulta.data` (agrupado por período)

**Visualização**: 
- Linha temporal mostrando % de encaminhamentos
- Comparação com taxa de resolução (sem encaminhamento)
- Indicadores de tendência (aumentando/diminuindo)

**Filtros**:
- Período (7 dias, 30 dias, 90 dias, ano)
- Gênero
- Faixa etária

**Valor para o negócio**: 
- Monitorar eficácia do atendimento
- Identificar períodos com maior necessidade de encaminhamento
- Avaliar impacto de mudanças no protocolo

---

### 2. **Distribuição de Tipos de Recomendações** ⭐⭐⭐⭐⭐
**Prioridade: ALTA**

**Descrição**: Gráfico de pizza/donut mostrando a proporção entre medicamentos, recomendações não-farmacológicas e encaminhamentos.

**Dados necessários**:
- `ConsultaRecomendacao.tipo` (medicamento/nao_farmacologico/encaminhamento)
- Contagem por tipo

**Visualização**: 
- Pizza/Donut com 3 segmentos
- Percentuais e valores absolutos
- Tooltip com detalhes

**Filtros**:
- Período
- Sintoma específico
- Gênero/Faixa etária

**Valor para o negócio**: 
- Entender o perfil de atendimento
- Verificar se há equilíbrio entre tipos de recomendações
- Identificar oportunidades de melhorias

---

### 3. **Doenças Crônicas Mais Prevalentes** ⭐⭐⭐⭐
**Prioridade: MÉDIA-ALTA**

**Descrição**: Gráfico de barras horizontais mostrando as doenças crônicas mais comuns entre os pacientes.

**Dados necessários**:
- `PacienteDoenca` (relacionamento)
- `DoencaCronica.nome`
- Contagem de pacientes por doença

**Visualização**: 
- Barras horizontais ordenadas por frequência
- Top 10 ou Top 15
- Percentual do total de pacientes

**Filtros**:
- Período de cadastro
- Gênero
- Faixa etária
- Cidade/Bairro

**Valor para o negócio**: 
- Identificar comorbidades mais comuns
- Planejar estoque de medicamentos específicos
- Entender perfil epidemiológico da população atendida

---

### 4. **Evolução de Pacientes Cadastrados** ⭐⭐⭐⭐
**Prioridade: MÉDIA-ALTA**

**Descrição**: Gráfico de linha mostrando o crescimento do cadastro de pacientes ao longo do tempo.

**Dados necessários**:
- `Paciente.created_at`
- Contagem acumulada por período

**Visualização**: 
- Linha temporal com crescimento acumulado
- Opção de mostrar apenas novos cadastros por período
- Comparação entre períodos

**Filtros**:
- Período de visualização
- Por cidade/bairro

**Valor para o negócio**: 
- Monitorar crescimento da base de pacientes
- Identificar tendências de cadastro
- Planejar recursos necessários

---

### 5. **Medicamentos Farmacológicos vs Fitoterápicos** ⭐⭐⭐⭐
**Prioridade: MÉDIA**

**Descrição**: Gráfico comparando a proporção de recomendações de medicamentos farmacológicos vs fitoterápicos.

**Dados necessários**:
- `ConsultaRecomendacao.tipo == 'medicamento'`
- `Medicamento.tipo` (farmacologico/fitoterapico)
- Join entre ConsultaRecomendacao e Medicamento

**Visualização**: 
- Pizza/Donut com 2 segmentos
- Comparação percentual
- Evolução temporal (opcional)

**Filtros**:
- Período
- Sintoma específico

**Valor para o negócio**: 
- Entender preferência por tipo de tratamento
- Avaliar aderência a tratamentos naturais
- Planejar estoque

---

### 6. **Taxa de Resolução por Sintoma** ⭐⭐⭐⭐⭐
**Prioridade: ALTA**

**Descrição**: Gráfico de barras mostrando a taxa de resolução (sem encaminhamento) para cada sintoma.

**Dados necessários**:
- `Consulta.observacoes` (extrair sintoma)
- `Consulta.encaminhamento` (True/False)
- Calcular taxa: (consultas sem encaminhamento / total) * 100

**Visualização**: 
- Barras horizontais ordenadas por taxa
- Cores: verde (alta resolução), amarelo (média), vermelho (baixa)
- Valores absolutos e percentuais

**Filtros**:
- Período
- Gênero/Faixa etária

**Valor para o negócio**: 
- Identificar sintomas com maior/menor taxa de resolução
- Avaliar eficácia do protocolo por sintoma
- Priorizar melhorias em protocolos específicos

---

### 7. **Distribuição de Hábitos (Fumantes/Etilistas)** ⭐⭐⭐
**Prioridade: MÉDIA**

**Descrição**: Gráfico mostrando a distribuição de pacientes fumantes e etilistas.

**Dados necessários**:
- `Paciente.fuma` (True/False)
- `Paciente.bebe` (True/False)
- Contagem e percentuais

**Visualização**: 
- Gráfico de barras agrupadas
- 4 categorias: Não fuma/Não bebe, Fuma/Não bebe, Não fuma/Bebe, Fuma/Bebe
- Percentuais do total

**Filtros**:
- Período de cadastro
- Gênero
- Faixa etária
- Cidade/Bairro

**Valor para o negócio**: 
- Entender perfil de hábitos da população
- Identificar fatores de risco
- Planejar ações educativas

---

### 8. **Horários de Pico de Consultas** ⭐⭐⭐
**Prioridade: MÉDIA**

**Descrição**: Gráfico de barras mostrando a distribuição de consultas por horário do dia.

**Dados necessários**:
- `Consulta.data` (extrair hora)
- Agrupar por faixas horárias (manhã, tarde, noite)

**Visualização**: 
- Barras verticais por faixa horária
- Mostrar horários de maior movimento
- Comparação entre dias da semana

**Filtros**:
- Período
- Dia da semana específico

**Valor para o negócio**: 
- Otimizar escalas de atendimento
- Planejar recursos humanos
- Identificar horários de maior demanda

---

### 9. **Recomendações Não-Farmacológicas Mais Comuns** ⭐⭐⭐⭐
**Prioridade: MÉDIA-ALTA**

**Descrição**: Gráfico de barras horizontais mostrando as recomendações não-farmacológicas mais frequentes.

**Dados necessários**:
- `ConsultaRecomendacao.tipo == 'nao_farmacologico'`
- `ConsultaRecomendacao.descricao`
- Contagem por descrição

**Visualização**: 
- Barras horizontais ordenadas por frequência
- Top 10 ou Top 15
- Agrupar por categorias similares (se possível)

**Filtros**:
- Período
- Sintoma específico

**Valor para o negócio**: 
- Identificar recomendações mais efetivas
- Padronizar orientações
- Melhorar protocolos de atendimento

---

### 10. **Índice de Massa Corporal (IMC) por Faixa Etária** ⭐⭐⭐
**Prioridade: BAIXA-MÉDIA**

**Descrição**: Gráfico de boxplot ou barras mostrando a distribuição de IMC por faixa etária.

**Dados necessários**:
- `Paciente.peso`
- `Paciente.altura`
- Calcular IMC: peso / (altura²)
- Classificar: Abaixo do peso, Normal, Sobrepeso, Obesidade

**Visualização**: 
- Gráfico de barras agrupadas por faixa etária
- 4 categorias de IMC
- Percentuais por faixa

**Filtros**:
- Gênero
- Cidade/Bairro

**Valor para o negócio**: 
- Entender perfil nutricional da população
- Identificar grupos de risco
- Planejar ações preventivas

---

### 11. **Eficácia de Medicamentos por Taxa de Não-Encaminhamento** ⭐⭐⭐⭐⭐
**Prioridade: ALTA**

**Descrição**: Gráfico de barras horizontais mostrando medicamentos ordenados por taxa de sucesso (consultas sem encaminhamento).

**Dados necessários**:
- `ConsultaRecomendacao.tipo == 'medicamento'`
- `Consulta.encaminhamento`
- Calcular taxa: (consultas sem encaminhamento / total) * 100

**Visualização**: 
- Barras horizontais ordenadas por taxa
- Cores por faixa de eficácia
- Valores absolutos e percentuais

**Filtros**:
- Período
- Sintoma específico
- Top N medicamentos

**Valor para o negócio**: 
- Identificar medicamentos mais efetivos
- Avaliar eficácia real dos tratamentos
- Melhorar recomendações baseadas em evidências

---

### 12. **Distribuição de Consultas por Dia da Semana** ⭐⭐⭐
**Prioridade: MÉDIA**

**Descrição**: Gráfico de barras mostrando a distribuição de consultas por dia da semana.

**Dados necessários**:
- `Consulta.data`
- Extrair dia da semana
- Contagem por dia

**Visualização**: 
- Barras verticais para cada dia da semana
- Ordenar de segunda a domingo
- Mostrar média semanal

**Filtros**:
- Período
- Comparar períodos

**Valor para o negócio**: 
- Identificar dias de maior movimento
- Planejar escalas
- Otimizar recursos

---

## 📋 Priorização Recomendada

### Implementação Imediata (Alto Impacto)
1. ✅ **Taxa de Encaminhamentos ao Longo do Tempo**
2. ✅ **Distribuição de Tipos de Recomendações**
3. ✅ **Taxa de Resolução por Sintoma**
4. ✅ **Eficácia de Medicamentos por Taxa de Não-Encaminhamento**

### Implementação Curto Prazo (Médio Impacto)
5. ✅ **Doenças Crônicas Mais Prevalentes**
6. ✅ **Evolução de Pacientes Cadastrados**
7. ✅ **Recomendações Não-Farmacológicas Mais Comuns**
8. ✅ **Medicamentos Farmacológicos vs Fitoterápicos**

### Implementação Longo Prazo (Baixo-Médio Impacto)
9. ✅ **Distribuição de Hábitos (Fumantes/Etilistas)**
10. ✅ **Horários de Pico de Consultas**
11. ✅ **Distribuição de Consultas por Dia da Semana**
12. ✅ **Índice de Massa Corporal (IMC) por Faixa Etária**

---

## 🎨 Sugestões de Visualização

### Tipos de Gráficos Recomendados:
- **Linha**: Para evolução temporal (encaminhamentos, pacientes cadastrados)
- **Pizza/Donut**: Para distribuições proporcionais (tipos de recomendações, farmacológico vs fitoterápico)
- **Barras Horizontais**: Para rankings (doenças crônicas, recomendações não-farmacológicas, eficácia)
- **Barras Verticais**: Para comparações categóricas (hábitos, dias da semana, horários)
- **Boxplot**: Para distribuições estatísticas (IMC)

### Padrões de Cores:
- **Verde**: Sucesso, resolução, eficácia alta
- **Amarelo**: Atenção, média eficácia
- **Vermelho**: Alerta, baixa eficácia, encaminhamentos
- **Azul**: Neutro, informativo
- **Roxo**: Destaque especial

---

## 💡 Observações Técnicas

### Dados que Requerem Processamento:
- **IMC**: Calcular a partir de peso e altura
- **Taxa de Resolução**: Calcular a partir de encaminhamentos
- **Taxa de Eficácia**: Calcular a partir de medicamentos e encaminhamentos
- **Sintomas**: Extrair de `Consulta.observacoes` (campo MODULO:)

### Considerações de Performance:
- Índices já existem em campos importantes
- Usar agregações SQL quando possível
- Cachear resultados para gráficos pesados
- Limitar resultados (Top N) quando apropriado

### Filtros Padrão:
- Período (7 dias, 30 dias, 90 dias, ano, personalizado)
- Gênero (Todos, Masculino, Feminino, Outro)
- Faixa Etária (Todas, 0-17, 18-34, 35-54, 55+)
- Localização (Bairro/Cidade) quando aplicável

---

## 📊 Resumo Executivo

**Total de Gráficos Recomendados**: 12

**Por Prioridade**:
- Alta: 4 gráficos
- Média-Alta: 4 gráficos
- Média: 3 gráficos
- Baixa-Média: 1 gráfico

**Por Tipo de Visualização**:
- Linha: 2 gráficos
- Pizza/Donut: 2 gráficos
- Barras Horizontais: 5 gráficos
- Barras Verticais: 2 gráficos
- Boxplot: 1 gráfico

**Impacto Esperado**:
- Melhoria na tomada de decisões clínicas
- Otimização de recursos e escalas
- Identificação de padrões e tendências
- Avaliação de eficácia de tratamentos
- Planejamento estratégico baseado em dados

