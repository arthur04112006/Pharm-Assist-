# Métrica de Score para Medicamentos por Sintoma

## Visão Geral

O sistema calcula um score para cada medicamento baseado em múltiplos fatores que indicam sua eficácia e relevância para um sintoma específico.

## Fórmula de Cálculo

```
Score = Frequência × 1.0 + Casos de Sucesso × 0.3 + Score Total da Triagem × 0.1
```

### Componentes do Score

#### 1. Frequência (Peso: 1.0)
- **Definição**: Número de vezes que o medicamento foi recomendado para o sintoma específico
- **Peso**: 1.0 (maior peso)
- **Justificativa**: Medicamentos mais frequentemente recomendados são mais relevantes

#### 2. Casos de Sucesso (Peso: 0.3)
- **Definição**: Número de casos onde o medicamento foi recomendado e o paciente **não** precisou de encaminhamento médico
- **Peso**: 0.3
- **Justificativa**: Indica que o medicamento foi eficaz (paciente não precisou de atendimento médico adicional)

#### 3. Score Total da Triagem (Peso: 0.1)
- **Definição**: Soma dos scores de triagem de todos os casos onde o medicamento foi recomendado
- **Peso**: 0.1 (menor peso)
- **Justificativa**: Medicamentos usados em casos mais graves (score alto) podem ser mais relevantes

## Exemplo de Cálculo

Considere um medicamento "Paracetamol" para o sintoma "febre":

- **Frequência**: 50 vezes recomendado
- **Casos de Sucesso**: 40 casos sem encaminhamento
- **Score Total da Triagem**: 200 pontos (soma de todos os scores)

```
Score = (50 × 1.0) + (40 × 0.3) + (200 × 0.1)
Score = 50 + 12 + 20
Score = 82.0
```

## Métricas Adicionais Retornadas

Além do score, a API retorna:

- **frequencia**: Número de vezes recomendado
- **casos_sucesso**: Casos sem encaminhamento
- **total_casos**: Total de casos onde foi recomendado
- **taxa_sucesso**: Percentual de casos sem encaminhamento
- **score_medio_triagem**: Média do score de triagem dos casos

## Filtros Disponíveis

O score pode ser calculado com filtros:

- **Sintoma**: Sintoma específico (obrigatório)
- **Período**: Últimos 7 dias, 30 dias, 90 dias ou 1 ano
- **Gênero**: Masculino, Feminino, Outro ou Todos
- **Faixa Etária**: 0-17, 18-34, 35-54, 55+ ou Todas

## Ordenação

Os medicamentos são ordenados por score em ordem decrescente (maior score primeiro).

## Limitações

1. **Dados Históricos**: O score depende de dados históricos de consultas
2. **Encaminhamento como Proxy**: Usamos "não encaminhamento" como proxy de eficácia, mas pode haver outros fatores
3. **Score de Triagem**: Nem todas as consultas podem ter score de triagem calculado

## Melhorias Futuras

- Adicionar feedback explícito de eficácia dos pacientes
- Considerar tempo de resolução dos sintomas
- Ponderar por gravidade do caso (score de triagem mais alto)
- Adicionar análise temporal (tendências de uso)

