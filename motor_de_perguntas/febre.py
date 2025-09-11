#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluxograma (CLI) para Febre
---------------------------
Baseado no algoritmo clínico do PDF enviado: triagem de febre com
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
    age_months: int
    is_pregnant: bool = False
    is_postpartum: bool = False
    has_chronic_pulmonary_or_cardiac: bool = False  # DPOC grave, IC descompensada, asma
    has_immunosuppression: bool = False  # HIV, câncer em tto imunossupressor
    has_htn_or_gi_or_renal: bool = False  # hipertensão, distúrbio GI ou insuf. renal

@dataclass
class Symptoms:
    duration_days: int
    recurrence: bool
    max_temp_c: float
    activity_impairment: bool
    suspected_drug_fever: bool
    suspected_hyperthermia: bool
    # sinais associados de alerta
    rash: bool
    breathing_changes: bool
    severe_headache_or_neck_pain: bool
    convulsions_or_confusion: bool
    vomiting: bool
    diarrhea: bool
    severe_abdominal_or_back_pain: bool
    ear_pain: bool
    unusual_symptom: bool
    very_sleepy_or_irritable_child: bool
    bulging_fontanelle: bool
    refuses_liquids: bool

@dataclass
class MedicationHistory:
    anticoagulant_or_thrombolytic: bool
    antihypertensive_use: bool

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

    # Tempo/recorrência
    if s.duration_days > 3:
        reasons.append("febre >3 dias")
    if s.recurrence:
        reasons.append("recorrência após apirexia")

    # Intensidade
    if s.max_temp_c >= 39.5:
        reasons.append("febre alta (≥39,5°C)")
    if s.max_temp_c > 40.5:
        reasons.append("febre muito alta (>40,5°C)")
    if s.activity_impairment:
        reasons.append("febre intensa que compromete atividades diárias")

    # Suspeita especial
    if s.suspected_drug_fever:
        reasons.append("febre associada a medicamento (7–10d do início)")
    if s.suspected_hyperthermia:
        reasons.append("suspeita de hipertermia (não responde a antitérmicos)")

    # Sinais associados
    if s.rash:
        reasons.append("exantema")
    if s.breathing_changes:
        reasons.append("alterações respiratórias/dispneia/taquipneia")
    if s.severe_headache_or_neck_pain:
        reasons.append("cefaleia intensa/dor de pescoço")
    if s.convulsions_or_confusion:
        reasons.append("convulsões/confusão mental")
    if s.vomiting:
        reasons.append("vômitos")
    if s.diarrhea:
        reasons.append("diarreia")
    if s.severe_abdominal_or_back_pain:
        reasons.append("dor intensa na barriga/nas costas")
    if s.ear_pain:
        reasons.append("dor no ouvido")
    if s.unusual_symptom:
        reasons.append("outro sintoma incomum que gere preocupação")
    if s.very_sleepy_or_irritable_child:
        reasons.append("criança muito sonolenta/irritada ou sem resposta")
    if s.bulging_fontanelle:
        reasons.append("fontanela abaulada")
    if s.refuses_liquids:
        reasons.append("criança recusa líquidos/não consegue ingerir")

    # Perfil do paciente
    if profile.age_months < 2:
        reasons.append("criança <2 meses com febre")
    if 3 <= profile.age_months <= 36 and s.max_temp_c >= 39 and (not profile.has_immunosuppression):
        reasons.append("criança 3–36 meses não imunizada/subimunizada com febre ≥39°C")
    if profile.age_months < 6 and s.max_temp_c >= 38:
        reasons.append("criança <6 meses com T≥38°C")
    if profile.age_months >= 6 and s.max_temp_c >= 40:
        reasons.append("criança >6 meses com T≥40°C")
    if profile.is_pregnant and s.duration_days > 0:
        reasons.append("gestante com febre")
    if profile.is_postpartum and s.duration_days > 0:
        reasons.append("puérpera com febre")

    if profile.has_chronic_pulmonary_or_cardiac:
        reasons.append("doença pulmonar/cardiopatia grave")
    if profile.has_immunosuppression:
        reasons.append("imunossupressão grave")
    if profile.has_htn_or_gi_or_renal:
        reasons.append("hipertensão, GI ou insuf. renal")

    # Medicamentos concomitantes
    if mh.anticoagulant_or_thrombolytic:
        reasons.append("risco de sangramento em uso de anticoagulante/trombolítico")
    if mh.antihypertensive_use:
        reasons.append("risco de interação com anti-hipertensivos")

    if reasons:
        return True, " | ".join(reasons)
    return False, ""

def suggest_non_pharm() -> str:
    return (
        "- Resfriamento do corpo: banhos de esponja ou panos embebidos em água morna\n"
        "- Manter em ambiente fresco\n"
        "- Usar roupas leves e cobrir com manta fina\n"
        "- Repor líquidos\n"
        "⚠️ Não recomendado: banhos com álcool, uso de gelo em pontos específicos ou água fria\n"
    )

def suggest_pharm(profile: PatientProfile) -> str:
    if profile.is_pregnant or profile.age_months >= 720:  # adulto idoso = paracetamol preferencial
        return "- Primeira linha: paracetamol\n"
    if profile.age_months < 216:  # criança <18 anos
        return "- Crianças: primeira linha ibuprofeno e paracetamol\n"
    else:
        return (
            "- Adultos: primeira linha ibuprofeno e paracetamol\n"
            "- Segunda linha: AAS\n"
            "- Terceira linha: naproxeno, dipirona\n"
        )

def triage(profile: PatientProfile, s: Symptoms, mh: MedicationHistory) -> TriageResult:
    red, why = has_red_flags(profile, s, mh)
    if red:
        return TriageResult(
            action="ENCAMINHAR",
            rationale=f"Encaminhar para avaliação profissional devido a: {why}.",
            non_pharm="- Enquanto aguarda avaliação, manter líquidos e ambiente fresco.",
            follow_up="Procurar serviço de saúde imediato/urgência conforme gravidade."
        )

    non_pharm = suggest_non_pharm()
    pharm = suggest_pharm(profile)
    return TriageResult(
        action="AUTOCUIDADO",
        rationale="Quadro de febre leve/moderada, <3 dias, sem sinais de alarme.",
        non_pharm=non_pharm,
        pharm=pharm,
        follow_up="Reavaliar em até 72h. Se não houver melhora, se piorar, ou surgirem sinais de alarme, procurar atendimento."
    )

# ----------------- CLI -----------------

def ask_bool(q: str) -> bool:
    while True:
        a = input(q + " [s/n]: ").strip().lower()
        if a in ("s","sim","y","yes"): return True
        if a in ("n","nao","não","no"): return False
        print("Responda com 's' ou 'n'.")

def run_cli():
    print("=== Triagem de Febre (educacional) ===")
    idade_meses = int(input("Idade em meses (ex.: 300 para 25 anos): ").strip())
    gest = ask_bool("Gestante?")
    puerperio = ask_bool("Puérpera?")
    pulmo_card = ask_bool("Doença pulmonar/cardiopatia grave?")
    imuno = ask_bool("Imunossupressão (HIV/câncer em tto)?")
    htn_gi_renal = ask_bool("Hipertensão, distúrbio GI ou insuficiência renal?")

    dur = int(input("Duração da febre (dias): ").strip())
    rec = ask_bool("Febre recorrente após período de apirexia?")
    temp = float(input("Temperatura máxima registrada (°C): ").strip())
    impact = ask_bool("Febre compromete atividades diárias?")
    drug_fever = ask_bool("Suspeita de febre medicamentosa (7–10 dias após início de medicamento)?")
    hyper = ask_bool("Suspeita de hipertermia (não responde a antitérmicos)?")

    rash = ask_bool("Exantema?")
    breathing = ask_bool("Alterações na respiração/dispneia/taquipneia?")
    headache_neck = ask_bool("Cefaleia intensa ou dor de pescoço?")
    conv_conf = ask_bool("Convulsões ou confusão mental?")
    vomit = ask_bool("Vômitos?")
    diarr = ask_bool("Diarreia?")
    abd_back = ask_bool("Dor intensa na barriga ou nas costas?")
    ear = ask_bool("Dor no ouvido?")
    unusual = ask_bool("Outro sintoma incomum que gere preocupação?")
    sleepy_child = ask_bool("Criança muito sonolenta/irritada/sem resposta adequada?")
    font = ask_bool("Fontanela abaulada?")
    refuses = ask_bool("Recusa ingerir líquidos?")

    anticoag = ask_bool("Está em uso de anticoagulante/trombolítico?")
    antihtn = ask_bool("Está em uso de anti-hipertensivo (IECA, beta-bloq, diurético)?")

    profile = PatientProfile(
        age_months=idade_meses,
        is_pregnant=gest,
        is_postpartum=puerperio,
        has_chronic_pulmonary_or_cardiac=pulmo_card,
        has_immunosuppression=imuno,
        has_htn_or_gi_or_renal=htn_gi_renal
    )
    s = Symptoms(
        duration_days=dur,
        recurrence=rec,
        max_temp_c=temp,
        activity_impairment=impact,
        suspected_drug_fever=drug_fever,
        suspected_hyperthermia=hyper,
        rash=rash,
        breathing_changes=breathing,
        severe_headache_or_neck_pain=headache_neck,
        convulsions_or_confusion=conv_conf,
        vomiting=vomit,
        diarrhea=diarr,
        severe_abdominal_or_back_pain=abd_back,
        ear_pain=ear,
        unusual_symptom=unusual,
        very_sleepy_or_irritable_child=sleepy_child,
        bulging_fontanelle=font,
        refuses_liquids=refuses
    )
    mh = MedicationHistory(anticoagulant_or_thrombolytic=anticoag, antihypertensive_use=antihtn)

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

def iniciar_triangem(paciente):
    """
    Fluxo de perguntas e decisões para febre.
    Será implementado conforme diretrizes da ANVISA.
    """
    raise NotImplementedError("Fluxo de febre ainda não implementado")


