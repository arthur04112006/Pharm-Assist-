# Melhorias no Sistema de Recomendações Farmacológicas

## Visão Geral

O sistema de recomendações farmacológicas foi significativamente aprimorado para fornecer sugestões mais precisas e personalizadas baseadas no diagnóstico feito através das perguntas da triagem.

## Principais Melhorias Implementadas

### 1. Mapeamento Inteligente de Medicamentos

**Antes:** O sistema usava apenas recomendações fixas baseadas no módulo.

**Agora:** 
- Busca medicamentos do banco de dados baseado nas indicações
- Calcula relevância baseada em palavras-chave específicas
- Ordena medicamentos por relevância para o sintoma

```python
def _calcular_relevancia_medicamento(self, medicamento: Medicamento, modulo: str) -> float:
    """Calcula a relevância de um medicamento para um módulo específico"""
    # Conta palavras-chave presentes na indicação
    # Bonus para indicações específicas
    # Penalidade para medicamentos genéricos demais
```

### 2. Análise Avançada de Sintomas

**Antes:** Análise básica de respostas sim/não.

**Agora:**
- Identifica sintomas específicos das respostas da triagem
- Detecta gravidade alta, duração longa e sinais de alerta
- Ajusta recomendações baseado na severidade

```python
sintomas_identificados = {
    'tosse_seca': False,
    'tosse_produtiva': False,
    'gravidade_alta': False,
    'duracao_longa': False,
    'sinais_alerta': False
}
```

### 3. Sistema de Priorização Inteligente

**Antes:** Prioridade fixa para todos os medicamentos.

**Agora:**
- **Prioridade 1:** Casos graves com sinais de alerta
- **Prioridade 2:** Duração longa ou gravidade moderada  
- **Prioridade 3:** Casos leves

```python
# Ajustar prioridade baseada na gravidade
prioridade_base = 1
if sintomas.get('gravidade_alta', False):
    prioridade_base = 1
elif sintomas.get('duracao_longa', False):
    prioridade_base = 2
else:
    prioridade_base = 3
```

### 4. Filtros de Contraindicações

**Antes:** Não verificava contraindicações.

**Agora:**
- Verifica contraindicações para gestantes/lactantes
- Ajusta doses para idosos frágeis
- Considera restrições para crianças

```python
def _aplicar_filtros_contraindicacoes(self, recomendacoes, paciente_profile):
    # Verificar contraindicações para gestantes/lactantes
    if paciente_profile.get('is_pregnant_or_lactating', False):
        if any(termo in rec.medicamento.lower() for termo in ['aspirina', 'ibuprofeno']):
            rec.observacoes += " | Cautela em gestantes - consultar médico"
```

### 5. Observações Personalizadas

**Antes:** Observações genéricas.

**Agora:**
- Adiciona observações baseadas no perfil do paciente
- Inclui alertas para sinais de alarme
- Sugere acompanhamento médico quando necessário

```python
observacoes = "Não associar com expectorantes"
if sintomas.get('duracao_longa', False):
    observacoes += " | Se persistir >7 dias, consultar médico"

if sintomas.get('sinais_alerta', False):
    rec.observacoes += " | ATENÇÃO: Sinais de alerta detectados - monitorar evolução"
```

## Exemplos de Funcionamento

### Cenário 1: Tosse Seca Leve (3 dias)
- **Sintomas identificados:** tosse_seca=True, gravidade_alta=False, duracao_longa=False
- **Prioridade:** 3 (caso leve)
- **Recomendações:** Antitussígenos com observação padrão

### Cenário 2: Tosse Produtiva com Sinais de Alerta (10 dias)
- **Sintomas identificados:** tosse_produtiva=True, duracao_longa=True, sinais_alerta=True
- **Prioridade:** 1 (caso grave)
- **Recomendações:** Expectorantes com alertas de monitoramento

### Cenário 3: Tosse Alérgica em Gestante
- **Sintomas identificados:** tosse_seca=True, alergia=True
- **Perfil:** is_pregnant_or_lactating=True
- **Recomendações:** Antialérgicos com cautela para gestantes

## Benefícios das Melhorias

1. **Precisão:** Recomendações baseadas em dados reais do banco de medicamentos
2. **Personalização:** Considera perfil específico do paciente
3. **Segurança:** Verifica contraindicações automaticamente
4. **Inteligência:** Prioriza medicamentos baseado na gravidade
5. **Orientação:** Fornece observações específicas para cada caso

## Como Usar

O sistema melhorado é usado automaticamente quando o método `gerar_recomendacoes` é chamado:

```python
recomendacoes = sistema_recomendacoes.gerar_recomendacoes(
    modulo='tosse',
    respostas=respostas_da_triagem,
    paciente_profile=perfil_do_paciente
)
```

O sistema agora:
1. Analisa as respostas para identificar sintomas específicos
2. Busca medicamentos relevantes no banco de dados
3. Gera recomendações inteligentes baseadas nos sintomas
4. Aplica filtros de contraindicações
5. Ordena por prioridade e retorna as melhores opções

## Teste do Sistema

Execute o script de teste para ver o sistema em ação:

```bash
python test_sistema_melhorado.py
```

Este script demonstra diferentes cenários e mostra como o sistema responde de forma inteligente a cada situação.
