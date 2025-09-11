#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluxograma (CLI) para Dor Lombar
--------------------------------
Baseado no algoritmo clínico do PDF enviado: triagem de dor lombar com
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
    is_pregnant_or_lactating: bool = False
    is_frail_elderly: bool = False  # dependência AVD/AIVD, vulnerabilidade a estresses, doenças e quedas

@dataclass
class Symptoms:
    duration_weeks: float
    frequency_per_month: int
    relation_to_activity_or_posture: bool
    intensity_impacts_daily_activities: bool
    trauma_or_accident: bool
    difficulty_walking_or_bedridden: bool
    pain_radiates_beyond_knee: bool
    progressive_motor_sensory_deficit: bool
    leg_weakness: bool
    urinary_difficulty: bool
    fecal_incontinence: bool
    generalized_neuro_symptoms: bool  # fraqueza, instabilidade de marcha, queda, dormência/alterações sensitivas
    involuntary_weight_loss: bool
    malaise_fever_chills: bool

@dataclass
class ClinicalHistory:
    recent_uti_or_bacteremia: bool
    osteoporosis: bool
    neoplasia: bool
    previous_traumas: bool
    rheumatoid_arthritis: bool
    hiv: bool
    immunosuppression: bool
    epidural_or_spinal_procedures: bool

@dataclass
class MedicationHistory:
    prolonged_corticosteroid_use: bool
    previous_treatment_failure_or_adrs: bool

@dataclass
class TriageResult:
    action: str  # "ENCAMINHAR" ou "AUTOCUIDADO"
    rationale: str
    non_pharm: Optional[str] = None
    pharm: Optional[str] = None
    follow_up: Optional[str] = None

# ----------------- Regras -----------------

def has_red_flags(profile: PatientProfile, s: Symptoms, ch: ClinicalHistory, mh: MedicationHistory) -> Tuple[bool, str]:
    reasons = []

    # Tempo / recorrência
    if s.duration_weeks >= 4:
        reasons.append("duração persistente ≥4 semanas")
    if s.frequency_per_month > 1:
        reasons.append("recorrência >1 vez/mês")

    # Intensidade / impacto
    if s.intensity_impacts_daily_activities:
        reasons.append("dor intensa com impacto nas atividades diárias")

    # Características / situação
    if not s.relation_to_activity_or_posture:
        reasons.append("dor intensa não relacionada ao tempo/atividade")
    if s.trauma_or_accident:
        reasons.append("dor decorrente de trauma/acidente")
    if s.difficulty_walking_or_bedridden:
        reasons.append("dificuldade de locomoção e/ou acamado")

    # Sinais/sintomas associados neurológicos e sistêmicos
    if s.progressive_motor_sensory_deficit:
        reasons.append("déficit motor/sensitivo progressivo")
    if s.leg_weakness:
        reasons.append("fraqueza nas pernas")
    if s.urinary_difficulty:
        reasons.append("dificuldade para urinar")
    if s.fecal_incontinence:
        reasons.append("incontinência fecal")
    if s.pain_radiates_beyond_knee:
        reasons.append("dor irradiada para baixo do joelho")
    if s.generalized_neuro_symptoms:
        reasons.append("sintomas neurológicos generalizados (fraqueza/instabilidade da marcha/queda/dormência)")
    if s.involuntary_weight_loss:
        reasons.append("perda de peso involuntária")
    if s.malaise_fever_chills:
        reasons.append("mal‑estar/febre/calafrios")

    # Perfil
    if profile.age_years <= 2:
        reasons.append("criança ≤2 anos")
    if profile.is_pregnant_or_lactating:
        reasons.append("gestante/lactante")
    if profile.is_frail_elderly:
        reasons.append("idoso frágil")

    # História clínica
    if ch.recent_uti_or_bacteremia:
        reasons.append("infecção urinária ou bacteremia recente")
    if ch.osteoporosis:
        reasons.append("osteoporose")
    if ch.neoplasia:
        reasons.append("neoplasia")
    if ch.previous_traumas:
        reasons.append("traumas prévios")
    if ch.rheumatoid_arthritis:
        reasons.append("artrite reumatoide")
    if ch.hiv:
        reasons.append("HIV")
    if ch.immunosuppression:
        reasons.append("imunossupressão")
    if ch.epidural_or_spinal_procedures:
        reasons.append("procedimentos peridurais/espinhais")

    # História farmacoterapêutica
    if mh.prolonged_corticosteroid_use:
        reasons.append("uso prolongado de corticosteroides")
    if mh.previous_treatment_failure_or_adrs:
        reasons.append("falha terapêutica prévia/reação adversa importante")

    if reasons:
        return True, " | ".join(reasons)
    return False, ""

def suggest_non_pharm() -> str:
    return (
        "- Compressa quente local\n"
        "- Manter-se ativo: exercícios regulares, alongamentos e exercícios laborais\n"
        "- Evitar repouso/ficar acamado\n"
        "- Acupuntura (opcional)\n"
    )

def suggest_pharm() -> str:
    return (
        "- Analgésico simples: paracetamol (preferir quando AINEs forem contraindicados)\n"
        "- AINEs OTC: ibuprofeno, naproxeno; diclofenaco tópico (AINE oral tende a melhor efetividade)\n"
        "- Associações analgésico + relaxante: p.ex., paracetamol + carisoprodol + cafeína; "
        "ou dipirona monoidratada + citrato de orfenadrina + cafeína (quando disponíveis como MIP no seu país)\n"
        "⚠️ Usar conforme bula/rotulagem, atenção a contraindicações e interações.\n"
    )

def triage(profile: PatientProfile, s: Symptoms, ch: ClinicalHistory, mh: MedicationHistory) -> TriageResult:
    red, why = has_red_flags(profile, s, ch, mh)
    if red:
        return TriageResult(
            action="ENCAMINHAR",
            rationale=f"Encaminhar para avaliação profissional devido a: {why}.",
            non_pharm="- Enquanto aguarda a avaliação, manter atividade leve e calor local conforme tolerado.",
            follow_up="Serviço de saúde (UBS/PA/urgência conforme gravidade). Retorne antes se houver piora."
        )

    # Critérios de problema autolimitado (coluna verde, adaptado)
    non_pharm = suggest_non_pharm()
    pharm = suggest_pharm()
    return TriageResult(
        action="AUTOCUIDADO",
        rationale=(
            "Quadro sem sinais de alarme, com chance de curso autolimitado (se <4 semanas, "
            "relacionado a postura/atividade e sem déficits neurológicos)."
        ),
        non_pharm=non_pharm,
        pharm=pharm,
        follow_up=(
            "Reavalie a dor em 7–14 dias. Se persistir ≥4 semanas, se houver recorrência frequente, "
            "ou surgirem sinais de alarme, procure atendimento."
        )
    )

# ----------------- CLI -----------------

def ask_bool(q: str) -> bool:
    while True:
        a = input(q + " [s/n]: ").strip().lower()
        if a in ("s","sim","y","yes"): return True
        if a in ("n","nao","não","no"): return False
        print("Responda com 's' ou 'n'.")

def run_cli():
    print("=== Triagem de Dor Lombar (educacional) ===")
    idade = float(input("Idade em anos (ex.: 35): ").strip())
    gest_lac = ask_bool("Gestante ou lactante?")
    idoso_fragil = ask_bool("Idoso frágil (dependência/alta vulnerabilidade)?")

    dur = float(input("Duração da dor (semanas): ").strip())
    freq = int(input("Recorrência: quantas vezes por mês? (número inteiro): ").strip())
    relacao = ask_bool("A dor parece relacionada à postura/atividade física?")
    impacto = ask_bool("A dor é intensa a ponto de atrapalhar atividades diárias?")
    trauma = ask_bool("A dor surgiu após trauma/acidente?")
    locomocao = ask_bool("Há dificuldade para andar ou o paciente está acamado?")
    irradia_abaixo_joelho = ask_bool("A dor irradia para além do joelho?")
    deficit_prog = ask_bool("Há déficit motor/sensitivo progressivo?")
    fraq_pernas = ask_bool("Fraqueza nas pernas?")
    dif_urinar = ask_bool("Dificuldade para urinar?")
    inc_fecal = ask_bool("Incontinência fecal?")
    neuro_gen = ask_bool("Sintomas neurológicos generalizados (fraqueza, instabilidade da marcha, quedas, dormência)?")
    perda_peso = ask_bool("Perda de peso involuntária?")
    mal_geral_febre_calafrios = ask_bool("Mal‑estar, febre ou calafrios?")

    uti_bact = ask_bool("História clínica: ITU ou bacteremia recente?")
    osteo = ask_bool("Osteoporose?")
    neo = ask_bool("Neoplasia conhecida?")
    traumas_prev = ask_bool("Traumas prévios relevantes?")
    ar = ask_bool("Artrite reumatoide?")
    hiv = ask_bool("HIV?")
    imunossup = ask_bool("Imunossupressão?")
    proc_esp = ask_bool("Procedimentos peridurais/espinhais prévios?")

    corticoide = ask_bool("Uso prolongado de corticosteroides?")
    falha_trat = ask_bool("Falha terapêutica prévia ou reação adversa importante a tratamento?")

    profile = PatientProfile(idade, gest_lac, idoso_fragil)
    s = Symptoms(
        duration_weeks=dur,
        frequency_per_month=freq,
        relation_to_activity_or_posture=relacao,
        intensity_impacts_daily_activities=impacto,
        trauma_or_accident=trauma,
        difficulty_walking_or_bedridden=locomocao,
        pain_radiates_beyond_knee=irradia_abaixo_joelho,
        progressive_motor_sensory_deficit=deficit_prog,
        leg_weakness=fraq_pernas,
        urinary_difficulty=dif_urinar,
        fecal_incontinence=inc_fecal,
        generalized_neuro_symptoms=neuro_gen,
        involuntary_weight_loss=perda_peso,
        malaise_fever_chills=mal_geral_febre_calafrios,
    )
    ch = ClinicalHistory(
        recent_uti_or_bacteremia=uti_bact,
        osteoporosis=osteo,
        neoplasia=neo,
        previous_traumas=traumas_prev,
        rheumatoid_arthritis=ar,
        hiv=hiv,
        immunosuppression=imunossup,
        epidural_or_spinal_procedures=proc_esp
    )
    mh = MedicationHistory(
        prolonged_corticosteroid_use=corticoide,
        previous_treatment_failure_or_adrs=falha_trat
    )

    result = triage(profile, s, ch, mh)

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
    Fluxo de perguntas e decisões para dor lombar.
    Será implementado conforme diretrizes da ANVISA.
    """
    raise NotImplementedError("Fluxo de dor_lombar ainda não implementado")


