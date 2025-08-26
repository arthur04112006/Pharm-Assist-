def compute_bmi(height_m, weight_kg):
    try:
        if height_m and weight_kg and height_m > 0:
            return round(weight_kg / (height_m**2), 2)
    except:
        pass
    return None

def _true(v): return bool(v) is True
def _num(v, default=None):
    try: return float(v)
    except: return default

def generate_suggestions(patient, answers):
    """
    Regras educacionais de apoio ao farmacêutico.
    Entrada:
      - patient: (tem .imc, .allergies, etc.)
      - answers: dict do questionário (ver campos no front)
    Saída:
      {
        "nao_farmacologicas": [...],
        "farmacologicas": [...],
        "alertas": [...],
        "rationale": [...]   # explicações do porquê
      }
    """
    sug = {
        "nao_farmacologicas": [],
        "farmacologicas": [],
        "alertas": [],
        "rationale": [],
    }

    # -------- dados de apoio --------
    imc = patient.imc
    alergias = set(a.lower() for a in (patient.allergies or []))
    comorb = set(answers.get("comorbidades", []))
    habitos = answers.get("habitos", {})
    adesao = answers.get("adesao", None)  # "boa" | "irregular" | "ruim"
    sintomas = answers.get("sintomas", {})  # {tosse, coriza, dor_garganta, congestao_nasal, dor_cabeca, acidez, nausea, dor_lombar}
    dor_int = _num(answers.get("dor_intensidade"), None)
    febre = bool(answers.get("febre"))
    febre_max = _num(answers.get("febre_temp_max"), None)
    sinais = set(answers.get("sinais_alarme", []))

    # -------- 0) Red flags / Encaminhamento --------
    # exemplos de red flags que você pode coletar no front:
    # "dispneia", "dor_toracica", "rigidez_nuca", "confusao", "sangramento_gi", "vomitos_persistentes"
    if sinais:
        sug["alertas"].append("Sinais de alarme presentes: encaminhar para avaliação médica.")
        sug["rationale"].append(f"Red flags marcadas: {', '.join(sorted(sinais))}.")
        # Mesmo com red flags, ainda podemos trazer medidas gerais seguras:
        sug["nao_farmacologicas"].append("Hidratação adequada e evitar esforço até avaliação.")
        return sug  # prioridade total aos red flags

    # Febre muito alta / persistente
    if febre and febre_max and febre_max >= 39:
        sug["alertas"].append("Febre alta (≥39°C): considerar encaminhamento se persistente >48–72h.")
        sug["rationale"].append(f"Febre reportada de {febre_max}°C.")

    # -------- 1) Controle de peso (IMC) --------
    if imc is not None:
        if imc >= 30:
            sug["nao_farmacologicas"].append("Plano de perda de peso gradual; atividade física moderada 150min/sem.")
            sug["rationale"].append(f"IMC={imc} (obesidade).")
        elif imc >= 25:
            sug["nao_farmacologicas"].append("Controle de peso com reeducação alimentar e rotina de exercícios.")
            sug["rationale"].append(f"IMC={imc} (sobrepeso).")

    # -------- 2) Tabagismo --------
    if habitos.get("tabagismo") is True:
        sug["nao_farmacologicas"].append("Programa de cessação do tabagismo + suporte comportamental.")
        sug["rationale"].append("Hábito tabagismo = sim.")

    # -------- 3) Aderência medicamentosa --------
    if adesao in ("irregular", "ruim"):
        sug["nao_farmacologicas"].append("Educação em saúde: estratégias de adesão (organizadores, alarmes, rotina).")
        sug["rationale"].append(f"Aderência reportada: {adesao}.")

    # -------- 4) Quadro respiratório leve (URTI) --------
    resp_flags = any([_true(sintomas.get(k)) for k in ("tosse","coriza","dor_garganta","congestao_nasal")])
    if resp_flags and not sinais:
        sug["nao_farmacologicas"].append("Hidratação, repouso, lavagem nasal com solução salina.")
        if febre or (dor_int is not None and dor_int >= 3):
            sug["farmacologicas"].append("Analgesia/antitérmico (dose padrão educativa) se necessário.")
        if _true(sintomas.get("congestao_nasal")):
            sug["farmacologicas"].append("Solução salina nasal (higiene nasal).")
        sug["rationale"].append("Sintomas respiratórios leves sem red flags.")

    # -------- 5) Cefaleia tensional (sem sinais de alarme) --------
    # Dor de cabeça leve a moderada, sem rigidez de nuca, sem confusão, sem dor torácica
    if _true(sintomas.get("dor_cabeca")) and not {"rigidez_nuca","confusao","dor_toracica"} & sinais:
        if dor_int is None or dor_int <= 7:
            sug["nao_farmacologicas"].append("Técnicas de relaxamento, hidratação, ergonomia/alongamento.")
            sug["farmacologicas"].append("Analgesia leve (dose padrão educativa) se necessário.")
            sug["rationale"].append(f"Cefaleia sem red flags; intensidade {dor_int if dor_int is not None else 'não informada'}.")

    # -------- 6) Dispepsia/DRGE leve --------
    if _true(sintomas.get("acidez")) or _true(sintomas.get("nausea")):
        sug["nao_farmacologicas"].append("Evitar refeições volumosas, álcool/cafeína; elevar cabeceira; jantar 2–3h antes de deitar.")
        sug["farmacologicas"].append("Antiácido simples (orientação educativa).")
        sug["rationale"].append("Sintomas dispépticos/DRGE leves.")

    # -------- 7) Lombalgia inespecífica leve --------
    if _true(sintomas.get("dor_lombar")) and (dor_int is None or dor_int <= 6):
        sug["nao_farmacologicas"].append("Calor local, alongamentos suaves, orientação postural.")
        sug["farmacologicas"].append("Analgesia leve (dose padrão educativa) se necessário.")
        sug["rationale"].append("Lombalgia sem sinais de alarme.")

    # -------- 8) Comorbidades – orientações de cuidado --------
    if "hipertensao" in comorb:
        sug["nao_farmacologicas"].append("Monitorar PA regularmente; reduzir sódio; atividade física orientada.")
        sug["rationale"].append("Comorbidade: hipertensão.")
    if "diabetes" in comorb:
        sug["nao_farmacologicas"].append("Monitorar glicemia; fracionar refeições; atenção a sinais de hipo/hiperglicemia.")
        sug["rationale"].append("Comorbidade: diabetes.")
    if "asma" in comorb:
        sug["nao_farmacologicas"].append("Evitar gatilhos; revisar técnica inalatória se aplicável.")
        sug["rationale"].append("Comorbidade: asma.")

    # -------- 9) Interações/Atenções (didáticas) --------
    if "dipirona" in alergias:
        sug["alertas"].append("Alergia registrada a dipirona — evitar fármacos relacionados.")
        sug["rationale"].append("Alergia: dipirona.")
    if "ulcera_gastrica" in comorb:
        sug["alertas"].append("Evitar AINEs em histórico de úlcera/gastrite.")
        sug["rationale"].append("Comorbidade: úlcera/gastrite.")
    if "asma" in comorb:
        sug["alertas"].append("Cautela com AINEs em asmáticos (risco de exacerbação em alguns casos).")
        sug["rationale"].append("Asma: atenção a AINEs.")

    # -------- Final --------
    # Deduplicar mantendo ordem simples
    for k in ("nao_farmacologicas","farmacologicas","alertas","rationale"):
        seen = set()
        uniq = []
        for item in sug[k]:
            if item not in seen:
                uniq.append(item); seen.add(item)
        sug[k] = uniq

    return sug
