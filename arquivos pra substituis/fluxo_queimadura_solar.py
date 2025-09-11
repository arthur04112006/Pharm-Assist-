
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluxograma (CLI) para Queimadura Solar
--------------------------------------
Baseado no algoritmo clínico do PDF enviado: triagem de queimadura solar
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
    is_pregnant_or_lactating: bool = False
    is_frail_elderly: bool = False
    lupus_or_vitiligo: bool = False

@dataclass
class Symptoms:
    duration_days: int
    erythema_blanching: bool  # eritema que desaparece na digitopressão
    mild_moderate_pain: bool
    heat_sensitivity: bool
    intact_skin: bool

    # Alertas
    blisters_or_bleeding: bool
    intense_pain: bool
    erythema_non_blanching: bool
    incapacitating: bool
    chemical_or_phytophotodermatitis_exposure: bool
    no_relief_cold_water: bool
    intense_headache_fever_dehydration_nv: bool

@dataclass
class MedicationHistory:
    treatment_failure_or_adrs: bool

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
    if s.duration_days > 7:
        reasons.append("queimadura >7 dias")

    # Características de alerta
    if s.blisters_or_bleeding:
        reasons.append("presença de bolhas/vesículas/sangramento")
    if s.intense_pain:
        reasons.append("dor intensa")
    if s.erythema_non_blanching:
        reasons.append("eritema que não desaparece à digitopressão")
    if s.incapacitating:
        reasons.append("incapacita atividades diárias")
    if s.chemical_or_phytophotodermatitis_exposure:
        reasons.append("exposição a químicos irritativos/vesicantes ou plantas com furocumarinas")
    if s.no_relief_cold_water:
        reasons.append("sem alívio mesmo com água fria corrente")
    if s.intense_headache_fever_dehydration_nv:
        reasons.append("cefaleia intensa, febre, sinais de desidratação, náuseas/vômitos")

    # Perfil
    if profile.age_years < 2:
        reasons.append("criança <2 anos")
    if profile.is_frail_elderly:
        reasons.append("idoso frágil")
    if profile.lupus_or_vitiligo:
        reasons.append("histórico de lúpus ou vitiligo")
    if profile.is_pregnant_or_lactating:
        reasons.append("gestante/lactante")

    # História farmacoterapêutica
    if mh.treatment_failure_or_adrs:
        reasons.append("falha terapêutica prévia/reações adversas com analgésicos/AINEs/loções")

    if reasons:
        return True, " | ".join(reasons)
    return False, ""

def suggest_non_pharm() -> str:
    return (
        "- Educação para fotoproteção (uso de protetor solar, evitar exposição excessiva)\n"
        "- Compressas frias ou imersão\n"
        "- Loção de calamina ou géis de Aloe vera\n"
        "- Emolientes em pele íntegra\n"
        "- Se houver bolhas rompidas: limpar com água/sabão neutro e cobrir com curativo úmido\n"
        "- Se usar fármacos fotossensibilizantes, evitar exposição solar e reforçar fotoproteção\n"
        "- Iniciar tratamento ao primeiro sinal/sintoma e manter por 24–48h\n"
    )

def suggest_pharm() -> str:
    return (
        "- Analgésicos/AINEs OTC para dor e inflamação:\n"
        "   • Ácido acetilsalicílico\n"
        "   • Ibuprofeno\n"
        "   • Naproxeno\n"
        "- AINE tópico: diclofenaco gel (apenas em pele íntegra)\n"
        "⚠️ Não utilizar corticosteroides tópicos.\n"
    )

def triage(profile: PatientProfile, s: Symptoms, mh: MedicationHistory) -> TriageResult:
    red, why = has_red_flags(profile, s, mh)
    if red:
        return TriageResult(
            action="ENCAMINHAR",
            rationale=f"Encaminhar para avaliação profissional devido a: {why}.",
            non_pharm="- Enquanto aguarda, manter compressas frias e fotoproteção.",
            follow_up="Procurar serviço de saúde se sinais graves persistirem."
        )

    non_pharm = suggest_non_pharm()
    pharm = suggest_pharm()
    return TriageResult(
        action="AUTOCUIDADO",
        rationale=(
            "Queimadura solar leve/moderada (≤7 dias, eritema que desaparece à digitopressão, dor leve a moderada, "
            "pele íntegra, sensibilidade ao calor)."
        ),
        non_pharm=non_pharm,
        pharm=pharm,
        follow_up=(
            "Reavaliar diariamente. Se não melhorar em 7 dias, se houver piora ou sinais de alerta, procurar atendimento."
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
    print("=== Triagem de Queimadura Solar (educacional) ===")
    idade = int(input("Idade (anos): ").strip())
    gest_lac = ask_bool("Gestante ou lactante?")
    idoso = ask_bool("Idoso frágil (dependência/alta vulnerabilidade)?")
    lupus = ask_bool("Histórico de lúpus ou vitiligo?")

    dur = int(input("Duração da queimadura (dias): ").strip())
    eritema_branqueia = ask_bool("Eritema desaparece à digitopressão?")
    dor_leve = ask_bool("Dor leve a moderada na região exposta?")
    sens_calor = ask_bool("Sensibilidade ao calor?")
    pele_integra = ask_bool("Pele íntegra?")

    bolhas = ask_bool("Presença de bolhas/vesículas/sangramento?")
    dor_intensa = ask_bool("Dor intensa?")
    eritema_nao_some = ask_bool("Eritema que não desaparece à digitopressão?")
    incap = ask_bool("Sinal/sintoma incapacita atividades diárias?")
    exp_quimica = ask_bool("Exposição a substância química irritativa/vesicante ou plantas (furocumarinas)?")
    sem_alivio = ask_bool("Sem alívio mesmo lavando com água fria?")
    cef_feb_desid = ask_bool("Cefaleia intensa, febre, sinais de desidratação, náuseas/vômitos?")

    falha_trat = ask_bool("Já tentou tratamento com analgésicos/AINEs/loções e houve falha/reação adversa?")

    profile = PatientProfile(
        age_years=idade,
        is_pregnant_or_lactating=gest_lac,
        is_frail_elderly=idoso,
        lupus_or_vitiligo=lupus
    )
    s = Symptoms(
        duration_days=dur,
        erythema_blanching=eritema_branqueia,
        mild_moderate_pain=dor_leve,
        heat_sensitivity=sens_calor,
        intact_skin=pele_integra,
        blisters_or_bleeding=bolhas,
        intense_pain=dor_intensa,
        erythema_non_blanching=eritema_nao_some,
        incapacitating=incap,
        chemical_or_phytophotodermatitis_exposure=exp_quimica,
        no_relief_cold_water=sem_alivio,
        intense_headache_fever_dehydration_nv=cef_feb_desid
    )
    mh = MedicationHistory(treatment_failure_or_adrs=falha_trat)

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
