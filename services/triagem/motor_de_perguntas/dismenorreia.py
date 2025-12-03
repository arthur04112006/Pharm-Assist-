#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluxograma (CLI) para Dismenorreia
----------------------------------
Baseado no algoritmo clínico do PDF enviado: triagem de dismenorreia com
anamnese, checagem de sinais de alerta (encaminhar) e orientações de manejo
não farmacológico e farmacológico (apenas MIPs/OTC).

⚠️ Aviso: Uso educacional. NÃO substitui avaliação médica.
Procure um serviço de saúde diante de dúvidas, piora ou sinais de alarme.
"""

from dataclasses import dataclass
from typing import Optional, Tuple

# ----------------- Modelos -----------------

@dataclass
class PatientProfile:
    age_years: float
    has_htn_or_hf: bool = False       # hipertensão / insuficiência cardíaca
    has_renal_insuff: bool = False    # insuficiência renal
    has_gi_disease: bool = False      # doença gastrointestinal
    has_asthma_or_bronchitis: bool = False  # asma ou bronquite
    is_pregnant_or_lactating: bool = False

@dataclass
class Symptoms:
    cyclical_with_menses: bool                  # dor associada ao período menstrual
    typical_onset_age_12_13: bool               # início 12-13 anos (6-12m após menarca)
    starts_2d_before_menses_reduces_72h: bool   # 2 dias antes, reduz em 72h
    suprapubic_cramp: bool                      # cólica suprapúbica
    monthly_recurrence: bool
    intensity_impairs_daily_activities: bool
    improves_with_nsaid: bool

    # Alertas de características/tempo/localização
    pain_outside_menses: bool
    location_changed_or_unilateral: bool

    # Sintomas associados de alerta
    abdominal_pain_with_diarrhea_nausea_vomit_heartburn: bool
    periumbilical_pain_to_rlq: bool
    suprapubic_with_urinary_urgency_or_hematuria: bool
    vascular_headache_frequent_intense: bool
    dysuria_or_urinary_urgency_or_hematuria: bool
    menorrhagia_or_oligomenorrhea_or_intermenstrual_bleeding: bool

@dataclass
class MedicationHistory:
    previous_treatment_failure_or_adrs: bool

@dataclass
class TriageResult:
    action: str  # "ENCAMINHAR" ou "AUTOCUIDADO"
    rationale: str
    non_pharm: Optional[str] = None
    pharm: Optional[str] = None
    follow_up: Optional[str] = None

# ----------------- Regras -----------------

def has_red_flags(profile: PatientProfile, s: Symptoms, mh: MedicationHistory) -> Tuple[bool, str]:
    reasons = []

    # Perfil/idade
    if profile.age_years >= 25:
        reasons.append("início/sintomas após 25 anos (30–40)")

    # Características/tempo/localização
    if s.pain_outside_menses:
        reasons.append("dor suprapúbica fora do período menstrual")
    if s.location_changed_or_unilateral:
        reasons.append("alteração do local da dor menstrual e/ou dor unilateral")
    if s.intensity_impairs_daily_activities:
        reasons.append("dor intensa que incapacita atividades diárias")

    # Sintomas associados de alerta
    if s.abdominal_pain_with_diarrhea_nausea_vomit_heartburn:
        reasons.append("dor abdominal com diarreia/náusea/vômito/queimação")
    if s.periumbilical_pain_to_rlq:
        reasons.append("dor periumbilical irradiando para quadrante inferior direito (suspeita de apendicite)")
    if s.suprapubic_with_urinary_urgency_or_hematuria:
        reasons.append("dor suprapúbica com urgência urinária/hematúria")
    if s.vascular_headache_frequent_intense:
        reasons.append("cefaleia vascular frequente/intensa")
    if s.dysuria_or_urinary_urgency_or_hematuria:
        reasons.append("alterações urinárias (disúria/urgência/hematúria)")
    if s.menorrhagia_or_oligomenorrhea_or_intermenstrual_bleeding:
        reasons.append("menorragia/oligomenorreia/sangramento intermenstrual")

    # Comorbidades que limitam AINEs
    if profile.has_htn_or_hf or profile.has_renal_insuff or profile.has_gi_disease or profile.has_asthma_or_bronchitis:
        reasons.append("comorbidades com limitações ao uso de AINEs (HAS/IC, renal, GI, asma/bronquite)")

    # Gravidez/lactação não se aplica ao algoritmo de dismenorreia, mas é alerta para manejo
    if profile.is_pregnant_or_lactating:
        reasons.append("gestação/lactação (avaliar causas e segurança medicamentosa)")

    # História farmacoterapêutica
    if mh.previous_treatment_failure_or_adrs:
        reasons.append("falha terapêutica prévia/reação adversa importante")

    if reasons:
        return True, " | ".join(reasons)
    return False, ""

def suggest_non_pharm() -> str:
    return (
        "- Calor local (bolsa térmica de água/gel/adesivo térmico)\n"
        "- Exercícios físicos regulares\n"
        "- Eletroestimulação transcutânea (TENS)\n"
        "- Acuestimulação\n"
        "- Cessar tabagismo\n"
        "- Ajustes dietéticos: reduzir gorduras; aumentar frutas e vegetais\n"
    )

def suggest_pharm(profile: PatientProfile) -> str:
    lines = []
    # 1ª linha: AINEs (se não houver contraindicações)
    if not (profile.has_htn_or_hf or profile.has_renal_insuff or profile.has_gi_disease or profile.has_asthma_or_bronchitis):
        lines.append("1ª linha – AINEs OTC: ibuprofeno, naproxeno (usar conforme bula).")
    else:
        lines.append("AINEs podem ser limitados por comorbidades (HAS/IC, renal, GI, asma/bronquite). Avaliar alternativas.")

    # 2ª linha: paracetamol
    lines.append("2ª linha – Analgésico simples: paracetamol.")

    # 3ª linha: antiespasmódico
    lines.append("3ª linha – Antiespasmódico (monoterapia ou combinações fixas), conforme disponibilidade e bula.")

    lines.append("⚠️ Usar apenas medicamentos isentos de prescrição e seguir rotulagem/bula.")

    return "\n- " + "\n- ".join(lines)

def triage(profile: PatientProfile, s: Symptoms, mh: MedicationHistory) -> TriageResult:
    red, why = has_red_flags(profile, s, mh)
    if red:
        return TriageResult(
            action="ENCAMINHAR",
            rationale=f"Encaminhar para avaliação profissional devido a: {why}.",
            non_pharm="- Enquanto aguarda avaliação, pode usar calor local e medidas de conforto.",
            follow_up="Procurar serviço de saúde (clínica/PA/GO) conforme gravidade."
        )

    # Critérios de problema autolimitado (coluna verde, adaptado)
    non_pharm = suggest_non_pharm()
    pharm = suggest_pharm(profile)
    return TriageResult(
        action="AUTOCUIDADO",
        rationale=(
            "Quadro compatível com dismenorreia primária (início típico 12–13 anos, mensal, cólica suprapúbica, "
            "associada ao período menstrual, melhora com AINEs e curso de até ~72h)."
        ),
        non_pharm=non_pharm,
        pharm=pharm,
        follow_up="Reavaliar por 2–3 ciclos. Se piora, persistência atípica ou sinais de alerta, procurar atendimento."
    )

# ----------------- CLI -----------------

def ask_bool(q: str) -> bool:
    while True:
        a = input(q + " [s/n]: ").strip().lower()
        if a in ("s","sim","y","yes"): return True
        if a in ("n","nao","não","no"): return False
        print("Responda com 's' ou 'n'.")

def run_cli():
    print("=== Triagem de Dismenorreia (educacional) ===")
    idade = float(input("Idade em anos (ex.: 19): ").strip())

    # Comorbidades relevantes para AINEs
    has_htn_or_hf = ask_bool("Hipertensão arterial ou insuficiência cardíaca?")
    has_renal_insuff = ask_bool("Insuficiência renal?")
    has_gi_disease = ask_bool("Doença gastrointestinal importante (ex.: úlcera, gastrite grave)?")
    has_asthma_or_bronchitis = ask_bool("Asma ou bronquite?")
    gest_lac = ask_bool("Gestante ou lactante?")

    cyclical = ask_bool("A dor está claramente associada ao período menstrual?")
    onset_twelve = ask_bool("Início típico entre 12–13 anos (6–12 meses após menarca)?")
    starts_2d = ask_bool("Começa ~2 dias antes e reduz em ~72 horas?")
    suprapubic = ask_bool("Dor tipo cólica, suprapúbica?")
    monthly = ask_bool("Recorrente mensalmente?")
    impact = ask_bool("A dor é intensa e incapacita atividades diárias?")
    improves_nsaid = ask_bool("Costuma melhorar com anti-inflamatório (AINE)?")

    outside_menses = ask_bool("Há dor suprapúbica fora do período menstrual?")
    location_change = ask_bool("Houve mudança do local da dor menstrual e/ou dor unilateral?")

    gi_alert = ask_bool("Dor abdominal com diarreia, náuseas, vômitos ou queimação?")
    rlq = ask_bool("Dor periumbilical que irradia para o quadrante inferior direito?")
    urinary_suprapubic = ask_bool("Dor suprapúbica com urgência urinária e/ou hematúria?")
    vascular_headache = ask_bool("Cefaleia vascular frequente/intensa?")
    urinary_alt = ask_bool("Dor ao urinar, urgência miccional e/ou sangue na urina?")
    abnormal_bleeding = ask_bool("Menorragia/oligomenorreia/sangramento intermenstrual?")

    falha_trat = ask_bool("Tratamentos prévios com falha ou reações adversas importantes?")

    profile = PatientProfile(
        age_years=idade,
        has_htn_or_hf=has_htn_or_hf,
        has_renal_insuff=has_renal_insuff,
        has_gi_disease=has_gi_disease,
        has_asthma_or_bronchitis=has_asthma_or_bronchitis,
        is_pregnant_or_lactating=gest_lac
    )
    s = Symptoms(
        cyclical_with_menses=cyclical,
        typical_onset_age_12_13=onset_twelve,
        starts_2d_before_menses_reduces_72h=starts_2d,
        suprapubic_cramp=suprapubic,
        monthly_recurrence=monthly,
        intensity_impairs_daily_activities=impact,
        improves_with_nsaid=improves_nsaid,
        pain_outside_menses=outside_menses,
        location_changed_or_unilateral=location_change,
        abdominal_pain_with_diarrhea_nausea_vomit_heartburn=gi_alert,
        periumbilical_pain_to_rlq=rlq,
        suprapubic_with_urinary_urgency_or_hematuria=urinary_suprapubic,
        vascular_headache_frequent_intense=vascular_headache,
        dysuria_or_urinary_urgency_or_hematuria=urinary_alt,
        menorrhagia_or_oligomenorrhea_or_intermenstrual_bleeding=abnormal_bleeding
    )
    mh = MedicationHistory(previous_treatment_failure_or_adrs=falha_trat)

    result = triage(profile, s, mh)

    print("\n=== Resultado ===")
    print(f"Ação: {result.action}")
    print(f"Motivo: {result.rationale}")
    if result.non_pharm:
        print("\nMedidas não farmacológicas:")
        print(result.non_pharm)
    if result.pharm:
        print("\nOpções farmacológicas (MIP/OTC):")
        print(result.pharm)
    if result.follow_up:
        print("\nAcompanhamento:")
        print(result.follow_up)

if __name__ == "__main__":
    run_cli()

def iniciar_triagem(paciente):
    """
    Fluxo de perguntas e decisões para dismenorreia.
    Será implementado conforme diretrizes da ANVISA.
    """
    raise NotImplementedError("Fluxo de dismenorreia ainda não implementado")
