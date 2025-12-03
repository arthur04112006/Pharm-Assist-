#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluxograma (CLI) para Diarreia
------------------------------
Baseado no algoritmo clínico do PDF enviado: triagem de diarreia com
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
    age_years: int
    is_pregnant_or_lactating: bool = False
    is_frail_elderly: bool = False
    is_immunosuppressed: bool = False

@dataclass
class Symptoms:
    duration_days: int
    stools_per_day: int
    watery: bool
    mucus: bool
    blood: bool
    nocturnal_diarrhea: bool
    severe_abdominal_pain: bool
    tenesmus: bool
    vomiting_persistent: bool
    fever_over_38: bool
    signs_dehydration: bool  # sede intensa, boca seca, diurese reduzida, tontura ortostática
    black_tarry_stools: bool
    weight_loss: bool

@dataclass
class ClinicalHistory:
    recent_antibiotic_use_30d: bool
    recent_travel_or_outbreak_exposure: bool
    inflammatory_bowel_disease: bool
    ibs_refractory: bool

@dataclass
class MedicationHistory:
    otc_failure_or_adrs: bool

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

    # Tempo/frequência
    if s.duration_days > 7:
        reasons.append("duração >7 dias")
    if s.stools_per_day >= 6:
        reasons.append("≥6 evacuações/dia")

    # Características de alarme
    if s.blood:
        reasons.append("sangue nas fezes")
    if s.mucus:
        reasons.append("muco nas fezes")
    if s.black_tarry_stools:
        reasons.append("fezes enegrecidas (melena)")
    if s.nocturnal_diarrhea:
        reasons.append("diarreia noturna")
    if s.severe_abdominal_pain:
        reasons.append("dor abdominal forte")
    if s.tenesmus:
        reasons.append("tenesmo")
    if s.vomiting_persistent:
        reasons.append("vômitos persistentes")
    if s.fever_over_38:
        reasons.append("febre >38°C")
    if s.signs_dehydration:
        reasons.append("sinais de desidratação (sede intensa, boca seca, pouca urina, tontura)")
    if s.weight_loss:
        reasons.append("perda de peso")

    # Perfis especiais
    if profile.age_years < 5:
        reasons.append("criança <5 anos")
    if profile.is_pregnant_or_lactating:
        reasons.append("gestante/lactante")
    if profile.is_frail_elderly:
        reasons.append("idoso frágil")
    if profile.is_immunosuppressed:
        reasons.append("imunossuprimido")

    # História clínica
    if ch.recent_antibiotic_use_30d:
        reasons.append("uso de antibiótico nos últimos 30 dias")
    if ch.inflammatory_bowel_disease or ch.ibs_refractory:
        reasons.append("DII/SII refratária ou suspeita de doença orgânica")
    if ch.recent_travel_or_outbreak_exposure:
        reasons.append("viagem recente/exposição a surto")

    # Falha terapêutica
    if mh.otc_failure_or_adrs:
        reasons.append("falha/reação adversa com tratamento OTC")

    if reasons:
        return True, " | ".join(reasons)
    return False, ""

def suggest_non_pharm(age_years: int) -> str:
    base = [
        "- Hidratação com **Solução de Reidratação Oral (SRO/ORS)** em pequenos volumes frequentes",
        "- Alternativas: água, água de coco, chás claros; evitar bebidas muito açucaradas/álcool",
        "- Dieta leve: fracionar refeições; priorizar arroz, batata, banana, maçã, torradas; evitar gorduras/laticínios temporariamente",
        "- Higiene das mãos e preparo seguro dos alimentos",
        "- Evitar automedicação com antibióticos",
    ]
    if age_years < 5:
        base.append("- Crianças: oferecer SRO após cada evacuação (10–20 mL/kg), manter aleitamento")
    return "\n".join(base) + "\n"

def suggest_pharm(profile: PatientProfile, s: Symptoms) -> str:
    lines = []
    # Reidratação é sempre a base
    lines.append("**Base:** SRO/ORS conforme necessidade até normalizar hidratação.")
    # Antidiarreico
    if not (s.blood or s.fever_over_38):
        lines.append("**Loperamida** (adultos) para reduzir número de evacuações quando **sem febre alta e sem sangue**.")
    else:
        lines.append("Evitar loperamida quando há **sangue nas fezes** ou **febre**.")
    # Adjuvantes
    lines.append("**Probióticos** como adjuvantes podem reduzir duração (quando disponíveis).")
    if profile.age_years < 5:
        lines.append("**Zinco** (crianças) pode ser considerado conforme diretrizes locais.")
    lines.append("**Antiespasmódicos** podem ajudar na cólica leve/moderada (conforme bula).")
    return "- " + "\n- ".join(lines)

def triage(profile: PatientProfile, s: Symptoms, ch: ClinicalHistory, mh: MedicationHistory) -> TriageResult:
    red, why = has_red_flags(profile, s, ch, mh)
    if red:
        return TriageResult(
            action="ENCAMINHAR",
            rationale=f"Encaminhar para avaliação profissional devido a: {why}.",
            non_pharm="- Enquanto aguarda, priorizar reidratação com SRO e dieta leve.",
            follow_up="Procurar serviço de saúde (urgência se desidratação importante, prostração, sangue nas fezes, febre alta)."
        )

    non_pharm = suggest_non_pharm(profile.age_years)
    pharm = suggest_pharm(profile, s)
    return TriageResult(
        action="AUTOCUIDADO",
        rationale="Diarreia aguda leve/moderada, ≤7 dias, sem sinais de alerta.",
        non_pharm=non_pharm,
        pharm=pharm,
        follow_up="Reavaliar em 48–72h. Se piorar, durar >7 dias, ou surgirem sinais de alarme, procurar atendimento."
    )

# ----------------- CLI -----------------

def ask_bool(q: str) -> bool:
    while True:
        a = input(q + " [s/n]: ").strip().lower()
        if a in ("s","sim","y","yes"): return True
        if a in ("n","nao","não","no"): return False
        print("Responda com 's' ou 'n'.")

def run_cli():
    print("=== Triagem de Diarreia (educacional) ===")
    idade = int(input("Idade (anos): ").strip())
    gest_lac = ask_bool("Gestante ou lactante?")
    idoso = ask_bool("Idoso frágil (dependência/alta vulnerabilidade)?")
    imuno = ask_bool("Imunossuprimido(a)?")

    dur = int(input("Duração dos sintomas (dias): ").strip())
    evac_dia = int(input("Número de evacuações por dia: ").strip())
    aquosa = ask_bool("Fezes aquosas?")
    muco = ask_bool("Muco nas fezes?")
    sangue = ask_bool("Sangue nas fezes?")
    noturna = ask_bool("Diarreia noturna?")
    dor_abd = ask_bool("Dor abdominal forte?")
    tenesmo = ask_bool("Tenesmo (vontade de evacuar sem eliminação)?")
    vom_persist = ask_bool("Vômitos persistentes?")
    febre = ask_bool("Febre >38°C?")
    desidrat = ask_bool("Sinais de desidratação (sede intensa, boca seca, pouca urina, tontura)?")
    melena = ask_bool("Fezes pretas como borra de café (melena)?")
    perda_peso = ask_bool("Perda de peso?")

    atb_30 = ask_bool("Uso de antibiótico nos últimos 30 dias?")
    viagem_surto = ask_bool("Viagem recente ou contato com surto alimentar/hídrico?")
    dii = ask_bool("Doença inflamatória intestinal?")
    sii_ref = ask_bool("Síndrome do Intestino Irritável refratária?")

    falha_otc = ask_bool("Falha ou reação adversa com OTC (SRO, probióticos, loperamida etc.)?")

    profile = PatientProfile(
        age_years=idade,
        is_pregnant_or_lactating=gest_lac,
        is_frail_elderly=idoso,
        is_immunosuppressed=imuno
    )
    s = Symptoms(
        duration_days=dur,
        stools_per_day=evac_dia,
        watery=aquosa,
        mucus=muco,
        blood=sangue,
        nocturnal_diarrhea=noturna,
        severe_abdominal_pain=dor_abd,
        tenesmus=tenesmo,
        vomiting_persistent=vom_persist,
        fever_over_38=febre,
        signs_dehydration=desidrat,
        black_tarry_stools=melena,
        weight_loss=perda_peso
    )
    ch = ClinicalHistory(
        recent_antibiotic_use_30d=atb_30,
        recent_travel_or_outbreak_exposure=viagem_surto,
        inflammatory_bowel_disease=dii,
        ibs_refractory=sii_ref
    )
    mh = MedicationHistory(otc_failure_or_adrs=falha_otc)

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

def iniciar_triagem(paciente):
    """
    Fluxo de perguntas e decisões para diarreia.
    Será implementado conforme diretrizes da ANVISA.
    """
    raise NotImplementedError("Fluxo de diarreia ainda não implementado")
