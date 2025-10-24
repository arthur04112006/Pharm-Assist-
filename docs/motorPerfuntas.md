## PRD — Integração das Perguntas do motor_de_perguntas na Triagem

### Objetivo
- Integrar, na página de triagem do sistema, todas as perguntas oficiais da ANVISA contidas nos módulos do diretório `motor_de_perguntas/`, preservando integralmente seus textos e quantidades.

### Escopo
- Fonte das perguntas: 13 módulos em `motor_de_perguntas/`:
  - `espirro_congestao_nasal.py`, `dor_lombar.py`, `dor_garganta.py`, `dismenorreia.py`, `febre.py`, `infeccoes_fungicas.py`, `dor_cabeca.py`, `azia_ma_digestao.py`, `queimadura_solar.py`, `constipacao.py`, `hemorroidas.py`, `diarreia.py`, `tosse.py`.
- Implementar uma camada de extração e entrega dessas perguntas para a UI de triagem, sem modificar textos/ordens/quantidades.
- Expor endpoint(s) para a UI solicitar perguntas por sintoma.
- Renderizar as perguntas na página de triagem atual, mantendo UX/estilo.

### Fora de Escopo
- Alterar redação, ordem, número ou conteúdo das perguntas.
- Implementar/alterar a lógica de decisão clínica (análise/encaminhamento). Este PRD cobre apenas coleta e apresentação das perguntas.

### Fontes e Padrões de Extração
- Cada módulo contém um fluxo com prompts das perguntas, expressos como:
  - Chamadas a `ask_bool("texto da pergunta ...?")` → tipo booleano (sim/não).
  - Chamadas a `input("texto da pergunta ...: ")` (convertidas com `int(...)`, `float(...)` etc.) → tipo numérico/texto.
- Este PRD exige preservação literal do texto exibido para o usuário.

### Modelo de Dados (Contrato de Pergunta)
- Estrutura JSON entregável ao frontend para cada pergunta:
```json
{
  "id": "string" ,
  "modulo": "espirro_congestao_nasal",
  "ordem": 1,
  "texto": "Pergunta literal extraída do módulo",
  "tipo": "boolean|number|string",
  "required": true,
  "placeholder": null,
  "opcoes": null,
  "grupo": "etapa"  
}
```
- Observações:
  - "texto": deve ser exatamente o literal presente no código-fonte.
  - "tipo": inferido por padrão de uso (ask_bool → boolean; input→ number|string conforme cast; quando ambíguo, string).
  - "ordem": preserva a ordem de aparição no módulo.
  - "id": gerado determinística e estavelmente a partir de `modulo + ordem` (ex.: `dor_lombar_12`).

### Pipeline de Extração (Backend)
1) Descoberta dos módulos suportados
   - Ler `motor_de_perguntas/__init__.py` e/ou varrer `motor_de_perguntas/` (excluindo subpastas auxiliares) para listar os módulos disponíveis.
2) Parser de perguntas
   - Usar `ast` (Abstract Syntax Tree) do Python para analisar cada módulo e localizar, em `run_cli()` (ou função equivalente), as chamadas a:
     - `ask_bool("...")` → extrair literal e classificar como boolean.
     - `input("...")` → extrair literal e tentar inferir tipo a partir do cast imediato (`int(...)`, `float(...)`, ausência de cast → string).
   - A ordem de leitura no código define a ordem das perguntas.
   - Ignorar variáveis/transformações sem interação com o usuário.
3) Serialização
   - Produzir uma estrutura consolidada em memória e opcionalmente cache local (ex.: `.cache/motor_perguntas/questions.json`) para acelerar respostas.
4) Exposição via API
   - `GET /api/triagem/modulos` → lista de módulos disponíveis (slugs amigáveis e nomes humanos).
   - `GET /api/triagem/perguntas?modulo=<slug>` → retorna lista de perguntas no contrato acima.

### Integração com a Página de Triagem (Frontend/Server-side)
- Página alvo: rotas/templates já existentes (`/triagem`, `/triagem/iniciar/<paciente_id>`) e templates `triagem.html`/`iniciar_triagem.html`.
- Comportamento desejado:
  - Usuário seleciona um sintoma (módulo).
  - A página carrega (AJAX) `GET /api/triagem/perguntas?modulo=<slug>` e renderiza um formulário dinâmico, respeitando ordem e tipos.
  - Controles:
    - `boolean` → switch/checkbox ou botões "Sim/Não".
    - `number` → campo numérico com validação básica.
    - `string` → campo texto.
  - As respostas são enviadas no payload atual de `/triagem/processar` (mantendo compatibilidade). Enquanto a lógica de decisão é refeita, o backend apenas persiste as respostas e retorna placeholder.

### Persistência e Compatibilidade
- `Consulta` e `ConsultaResposta` continuam sendo persistidos como hoje, mapeando:
  - `id_pergunta`: usar o `id` determinístico (exposto no JSON) ou um mapeamento estável em memória para chaves humanas.
  - `resposta`: valor literal do usuário ("sim"/"não"/número/texto).
- Não criar/alterar registros em `Pergunta` no banco para não conflitar com o novo fluxo dinâmico (ou isolar em tipo/préfixo distinto se necessário).

### Validações
- Não alterar texto, ordem ou quantidade de perguntas.
- Inferir tipo sem modificar enunciado.
- Validar apenas formato (ex.: numérico em perguntas numéricas) e obrigatoriedade mínima quando aplicável.

### Critérios de Aceite
- Para cada módulo, o endpoint `/api/triagem/perguntas` retorna:
  - Mesma quantidade de perguntas extraídas do código.
  - Textos exatamente iguais aos literais do módulo, na mesma ordem.
  - Tipos coerentes com os padrões (`ask_bool` → boolean; `int(...)`/`float(...)` → number; demais → string).
- A página de triagem renderiza corretamente todas as perguntas do módulo selecionado e envia respostas para `/triagem/processar`.

### Métricas de Sucesso
- 100% de correspondência entre perguntas renderizadas e perguntas nos módulos.
- Zero divergência de textos/ordem/quantidade em revisão visual automatizada/manual.
- Tempo de resposta do endpoint ≤ 200ms local (cache habilitado após primeiro carregamento).

### Riscos e Mitigações
- Mudanças futuras nos módulos (refatorações) podem alterar a forma de chamar `ask_bool`/`input` → usar AST robusta (buscar chamadas por nome, não por string simples) e adicionar testes de snapshot.
- Textos contendo aspas/caracteres especiais → garantir escaping/unicode adequado.
- Perguntas numéricas sem cast explícito → classificar como `string` por segurança.

### Plano de Implementação (Passo a Passo)
1) Backend
   - Criar utilitário `perguntas_extractor.py` (ou incorporado a uma service) que:
     - Lista módulos e extrai perguntas via AST, construindo estrutura padronizada.
     - Expõe função `get_perguntas_por_modulo(slug)` com cache LRU.
   - Adicionar endpoints:
     - `GET /api/triagem/modulos`
     - `GET /api/triagem/perguntas?modulo=<slug>`
   - Cobrir com testes unitários (contagem/ordem/texto) por módulo.
2) Frontend (templates)
   - Atualizar `iniciar_triagem.html`/`triagem.html` para suportar seleção de módulo e carregamento dinâmico das perguntas.
   - Renderizar tipos de campo conforme `tipo`.
   - Enviar respostas com `{ id, resposta }` para `/triagem/processar`.
3) Persistência
   - Adaptar processamento para armazenar `id` e `resposta` em `ConsultaResposta` sem depender de `Pergunta` do banco.
4) QA/Validação
   - Conferir, para cada módulo, a equivalência 1:1 entre perguntas no código e perguntas na UI.

### Cronograma Sugerido
- Dia 1: Extrator AST + endpoints (sem cache) + testes de 2 módulos.
- Dia 2: Cobertura dos 13 módulos + cache + endpoint de listagem de módulos.
- Dia 3: Integração UI + validações básicas + testes manuais.
- Dia 4: Refino de UX + testes de regressão + documentação.

### Considerações Finais
- Este PRD garante que as perguntas oficiais da ANVISA sejam apresentadas de forma fiel no sistema, com um pipeline reprodutível, auditável e desacoplado da lógica clínica (a ser reimplementada em etapa posterior).


