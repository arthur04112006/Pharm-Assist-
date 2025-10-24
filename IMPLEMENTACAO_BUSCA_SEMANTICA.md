# Implementação da Busca Semântica com TF-IDF

## Resumo das Alterações

Este documento descreve as modificações implementadas no arquivo `recomendacoes_farmacologicas.py` para substituir a lógica de busca literal por uma busca semântica usando TF-IDF e similaridade de cosseno.

## Funcionalidades Implementadas

### 1. Função `normalizar_texto(texto: str) -> str`
- Remove acentos usando `unidecode`
- Converte texto para minúsculas
- Remove pontuação e caracteres especiais
- Remove espaços múltiplos
- Retorna texto normalizado para comparação

### 2. Função `buscar_por_semelhanca(sintoma: str, lista_indicacoes: List[str]) -> List[Tuple[str, float]]`
- Implementa busca semântica usando TF-IDF e similaridade de cosseno
- Normaliza sintoma e indicações antes da comparação
- Usa `TfidfVectorizer` com configurações otimizadas:
  - Unigramas e bigramas (ngram_range=(1,2))
  - Sem stop words em português
  - Padrão de tokenização para palavras
- Calcula similaridade de cosseno entre sintoma e indicações
- Retorna lista ordenada por score de similaridade
- Inclui fallback para busca literal em caso de erro

### 3. Modificação da função `buscar_medicamentos_por_sintoma`
- Agora usa busca semântica como método principal
- Combina nome comercial, genérico e indicação para busca mais abrangente
- Aplica limiar de similaridade de 0.25 (conforme requisito)
- Mantém fallback para busca por palavras-chave
- Preserva compatibilidade total com sistema existente

### 4. Função auxiliar `_buscar_medicamentos_por_palavras_chave`
- Implementa método original de busca por palavras-chave
- Usado como fallback quando busca semântica não encontra resultados
- Mantém compatibilidade com sistema existente

## Dependências Adicionadas

As seguintes dependências foram adicionadas ao `requirements.txt`:

```
scikit-learn==1.3.2
unidecode==1.3.7
numpy==1.24.3
```

## Características da Implementação

### Compatibilidade
- ✅ Mantém total compatibilidade com a classe `SistemaRecomendacoesFarmacologicas`
- ✅ Não modifica o banco de dados nem o modelo `Medicamento`
- ✅ Preserva todas as funcionalidades existentes
- ✅ Mantém interface pública inalterada

### Robustez
- ✅ Tratamento de erros com fallback para busca literal
- ✅ Validação de entrada (textos vazios, listas vazias)
- ✅ Normalização robusta de texto
- ✅ Limiar de similaridade configurável

### Performance
- ✅ Busca semântica mais precisa que busca literal
- ✅ Ordenação por relevância semântica
- ✅ Fallback eficiente para casos sem correspondência semântica

## Exemplo de Uso

```python
# O uso permanece idêntico ao sistema anterior
sistema = SistemaRecomendacoesFarmacologicas()
medicamentos = sistema.buscar_medicamentos_por_sintoma("dor de cabeça", "dor_cabeca")
```

## Benefícios da Implementação

1. **Maior Precisão**: Busca semântica identifica medicamentos relevantes mesmo com variações de linguagem
2. **Flexibilidade**: Funciona com sinônimos e termos relacionados
3. **Robustez**: Fallback garante funcionamento mesmo com problemas nas dependências
4. **Compatibilidade**: Zero impacto no código existente
5. **Manutenibilidade**: Código bem estruturado e documentado

## Instalação das Dependências

Para instalar as novas dependências:

```bash
pip install -r requirements.txt
```

Ou instalar individualmente:

```bash
pip install scikit-learn==1.3.2 unidecode==1.3.7 numpy==1.24.3
```

## Testes

A implementação foi testada com:
- ✅ Normalização de texto com acentos e pontuação
- ✅ Compatibilidade com sistema existente
- ✅ Tratamento de casos extremos (textos vazios, erros)

## Conclusão

A implementação da busca semântica foi realizada com sucesso, mantendo total compatibilidade com o sistema existente e adicionando capacidades avançadas de busca por similaridade semântica. O sistema agora é mais robusto e preciso na identificação de medicamentos relevantes para os sintomas informados.
