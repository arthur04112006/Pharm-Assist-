#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluxograma (CLI) para Constipação
---------------------------------
Baseado no algoritmo clínico do PDF enviado: triagem de constipação
com anamnese, checagem de sinais de alerta (encaminhar) e orientações de manejo
não farmacológico e farmacológico (apenas MIPs/OTC).

⚠️ Aviso: Uso educacional. NÃO substitui avaliação médica.
Procure um serviço de saúde diante de dúvidas, piora ou sinais de alarme.
"""

from dataclasses import dataclass
from typing import Optional, Tuple

# ----------------- Modelos -----------------

@dataclass
class PatientProfile:
    age_years: int
    is_child_leq6: bool = False
    is_pregnant_or_lactating: bool = False
    is_frail_elderly: bool = False
    bedridden_or_paraplegic: bool = False
    has_predisposing_conditions: bool = False  # DII, SII refratária, hemorroidas sangrantes, anorexia, hipotireoidismo descompensado, anemia, diverticulite, hérnia de disco

@dataclass
class Symptoms:
    duration_days: int
    recurrent: bool
    stool_thin_black_white_mucus_blood: bool
    intense_abdominal_pain: bool
    incapacitating: bool
    alternating_diarrhea_constipation: bool
    unintentional_weight_loss_or_fever: bool
    incomplete_evacuations: bool
    hard_small_dry_stools: bool
    fullness_or_tolerable_pain: bool

@dataclass
class MedicationHistory:
    constipation_inducing_drugs: bool
    chronic_laxative_self_medication: bool
    treatment_failure: bool

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

    # Tempo
    if s.duration_days > 14:
        reasons.append("constipação persistente >2 semanas")
    if s.recurrent:
        reasons.append("constipação recorrente (>1 episódio em 3 meses)")

    # Características
    if s.stool_thin_black_white_mucus_blood:
        reasons.append("fezes alteradas (finas, escuras, claras, com muco ou sangue)")
    if s.intense_abdominal_pain:
        reasons.append("dor abdominal intensa")
    if s.incapacitating:
        reasons.append("sinal/sintoma incapacita atividades diárias")
    if s.alternating_diarrhea_constipation:
        reasons.append("diarreia alternada com constipação")
    if s.unintentional_weight_loss_or_fever:
        reasons.append("perda de peso involuntária/febre")

    # Perfis especiais
    if profile.is_child_leq6:
        reasons.append("criança ≤6 anos")
    if profile.is_pregnant_or_lactating:
        reasons.append("gestante/lactante com sintomas persistentes >1 semana de MEV")
    if profile.is_frail_elderly:
        reasons.append("idoso frágil")
    if profile.bedridden_or_paraplegic:
        reasons.append("paciente acamado/paraplégico")

    # Condições clínicas
    if profile.has_predisposing_conditions:
        reasons.append("doenças que predispõem/agravam constipação (DII, SII refratária, hemorroida com sangramento, anorexia, hipotireoidismo, anemia, diverticulite, hérnia de disco)")

    # História farmacoterapêutica
    if mh.treatment_failure:
        reasons.append("falha com laxantes")

    if reasons:
        return True, " | ".join(reasons)
    return False, ""

def suggest_non_pharm() -> str:
    return (
        "- Ingestão de líquidos: adultos ≥1,5–2L/dia; crianças ≥960–1920mL (ou fórmula: idade + 5–10g fibras/dia)\n"
        "- Ingestão de fibras: adultos 20–35g/dia (não exceder 50g)\n"
        "- Mudança de hábitos: evacuar em horários fixos (manhã ou após refeições); permitir tempo suficiente\n"
        "- Prática de exercícios físicos\n"
        "- Estimular deambulação\n"
    )

def suggest_pharm() -> str:
    return (
        "Ordem de preferência (até 7 dias, apenas MIPs):\n"
        "- Laxantes formadores de massa (evitar em impactação)\n"
        "- Surfactantes/emolientes\n"
        "- Agentes osmóticos\n"
        "- Laxantes estimulantes/irritativos\n"
        "⚠️ Atenção: uso apenas para alívio agudo, até 7 dias.\n"
    )

def triage(profile: PatientProfile, s: Symptoms, mh: MedicationHistory) -> TriageResult:
    red, why = has_red_flags(profile, s, mh)
    if red:
        return TriageResult(
            action="ENCAMINHAR",
            rationale=f"Encaminhar para avaliação profissional devido a: {why}.",
            non_pharm="- Enquanto aguarda, manter hidratação adequada e fibras na dieta.",
            follow_up="Procurar serviço de saúde se sintomas persistirem ou piorarem."
        )

    non_pharm = suggest_non_pharm()
    pharm = suggest_pharm()
    return TriageResult(
        action="AUTOCUIDADO",
        rationale=(
            "Constipação autolimitada (≤2 semanas), fezes duras/secas/pequenas, "
            "sem sinais de alarme ou condições predisponentes."
        ),
        non_pharm=non_pharm,
        pharm=pharm,
        follow_up="Reavaliar em até 7 dias. Se persistir ou sinais de alerta surgirem, procurar atendimento."
    )

# ----------------- CLI -----------------

def ask_bool(q: str) -> bool:
    while True:
        a = input(q + " [s/n]: ").strip().lower()
        if a in ("s","sim","y","yes"): return True
        if a in ("n","nao","não","no"): return False
        print("Responda com 's' ou 'n'.")

def run_cli():
    print("=== Triagem de Constipação (educacional) ===")
    idade = int(input("Idade (anos): ").strip())
    crianca = ask_bool("Criança ≤6 anos?")
    gest_lac = ask_bool("Gestante ou lactante?")
    idoso = ask_bool("Idoso frágil (dependência/alta vulnerabilidade)?")
    acamado = ask_bool("Paciente acamado ou paraplégico?")
    condicoes = ask_bool("Doença que predispõe/agrava constipação (DII, SII refratária, hemorroida com sangramento, anorexia, hipotireoidismo, anemia, diverticulite, hérnia de disco)?")

    dur = int(input("Duração dos sintomas (dias): ").strip())
    recorr = ask_bool("Constipação recorrente (≥1 episódio em 3 meses)?")
    fezes_alteradas = ask_bool("Fezes finas, muito escuras, claras, com muco abundante ou sangue?")
    dor_intensa = ask_bool("Dor abdominal intensa?")
    incap = ask_bool("Sintoma incapacita atividades diárias?")
    diarreia_alternada = ask_bool("Diarreia alternada com constipação?")
    perda_peso_febre = ask_bool("Perda de peso involuntária ou febre?")

    evac_incomp = ask_bool("Sensação de evacuação incompleta?")
    fezes_duras = ask_bool("Fezes duras, pequenas ou secas?")
    plenitude = ask_bool("Sensação de plenitude gástrica e/ou dor suportável na evacuação?")

    meds_constip = ask_bool("Uso de medicamentos que podem causar constipação?")
    lax_cronico = ask_bool("Uso crônico de laxantes por automedicação?")
    falha_lax = ask_bool("Falha com uso de laxantes?")

    profile = PatientProfile(
        age_years=idade,
        is_child_leq6=crianca,
        is_pregnant_or_lactating=gest_lac,
        is_frail_elderly=idoso,
        bedridden_or_paraplegic=acamado,
        has_predisposing_conditions=condicoes
    )
    s = Symptoms(
        duration_days=dur,
        recurrent=recorr,
        stool_thin_black_white_mucus_blood=fezes_alteradas,
        intense_abdominal_pain=dor_intensa,
        incapacitating=incap,
        alternating_diarrhea_constipation=diarreia_alternada,
        unintentional_weight_loss_or_fever=perda_peso_febre,
        incomplete_evacuations=evac_incomp,
        hard_small_dry_stools=fezes_duras,
        fullness_or_tolerable_pain=plenitude
    )
    mh = MedicationHistory(
        constipation_inducing_drugs=meds_constip,
        chronic_laxative_self_medication=lax_cronico,
        treatment_failure=falha_lax
    )

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
    Fluxo de perguntas e decisões para constipação.
    Será implementado conforme diretrizes da ANVISA.
    """
    raise NotImplementedError("Fluxo de constipacao ainda não implementado")
