
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluxograma (CLI) para Dor de Garganta
-------------------------------------
Baseado no algoritmo clínico do PDF enviado: triagem de dor de garganta com
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
    is_frail_elderly: bool = False

@dataclass
class Symptoms:
    duration_days: int
    recurrent: bool
    abrupt_onset: bool
    pus_or_white_spots: bool
    intense_pain_no_improvement_24h: bool
    incapacitating: bool
    suspected_irritant_exposure: bool
    smoker_with_cough_gt14d: bool
    dyspnea: bool
    neck_rigidity_headache: bool
    fever_over_38_for_24h: bool
    dysphagia: bool
    hoarseness_gt3w: bool
    rash_or_skin_blisters: bool
    lymph_node_swelling: bool
    excessive_salivation: bool

@dataclass
class ClinicalHistory:
    recurrent_infections: bool
    throat_neoplasia: bool

@dataclass
class MedicationHistory:
    prolonged_agranulocytosis_drugs: bool
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
    if s.duration_days > 7:
        reasons.append("duração >7 dias")
    if s.recurrent:
        reasons.append("frequência recorrente")

    # Características de alerta
    if s.abrupt_onset:
        reasons.append("início abrupto")
    if s.pus_or_white_spots:
        reasons.append("presença de pus/manchas brancas na garganta")
    if s.intense_pain_no_improvement_24h:
        reasons.append("dor intensa sem melhora após 24h")
    if s.incapacitating:
        reasons.append("dor incapacita atividades diárias")
    if s.suspected_irritant_exposure:
        reasons.append("suspeita de exposição a irritantes químicos ou IVAS grave")
    if s.smoker_with_cough_gt14d:
        reasons.append("tabagismo com tosse >14 dias")
    if s.dyspnea:
        reasons.append("dispneia")
    if s.neck_rigidity_headache:
        reasons.append("rigidez de pescoço/dor de cabeça")
    if s.fever_over_38_for_24h:
        reasons.append("febre >38°C por >24h")
    if s.dysphagia:
        reasons.append("dificuldade para engolir (disfagia)")
    if s.hoarseness_gt3w:
        reasons.append("rouquidão >3 semanas")
    if s.rash_or_skin_blisters:
        reasons.append("erupção cutânea/bolhas")
    if s.lymph_node_swelling:
        reasons.append("inchaço em linfonodos/pescoço")
    if s.excessive_salivation:
        reasons.append("sialorreia devido à disfagia")

    # Perfil do paciente
    if profile.age_years <= 2:
        reasons.append("criança ≤2 anos")
    if profile.is_pregnant_or_lactating:
        reasons.append("gestante/lactante")
    if profile.is_frail_elderly:
        reasons.append("idoso frágil")

    # História clínica
    if ch.recurrent_infections:
        reasons.append("histórico de infecções recorrentes")
    if ch.throat_neoplasia:
        reasons.append("neoplasia de garganta")

    # História farmacoterapêutica
    if mh.prolonged_agranulocytosis_drugs:
        reasons.append("uso prolongado de medicamentos que podem causar agranulocitose")
    if mh.previous_treatment_failure_or_adrs:
        reasons.append("falha terapêutica prévia/reação adversa importante")

    if reasons:
        return True, " | ".join(reasons)
    return False, ""

def suggest_non_pharm() -> str:
    return (
        "- Ingerir líquidos: água, sucos, chás\n"
        "- Gargarejo com água morna + sal (¼ col. chá em 1 xícara), até 4x/dia\n"
        "- Usar umidificador de ambiente\n"
        "- Evitar/diminuir exposição ao fumo (ativo ou passivo)\n"
    )

def suggest_pharm() -> str:
    return (
        "- Analgésicos/antitérmicos: paracetamol, dipirona\n"
        "- AINEs OTC: ibuprofeno, ácido acetilsalicílico\n"
        "- Combinações tópicas: sprays, colutórios, pastilhas (conforme bula)\n"
        "⚠️ Usar apenas medicamentos isentos de prescrição e seguir a bula.\n"
    )

def triage(profile: PatientProfile, s: Symptoms, ch: ClinicalHistory, mh: MedicationHistory) -> TriageResult:
    red, why = has_red_flags(profile, s, ch, mh)
    if red:
        return TriageResult(
            action="ENCAMINHAR",
            rationale=f"Encaminhar para avaliação profissional devido a: {why}.",
            non_pharm="- Enquanto aguarda avaliação, manter hidratação e gargarejos.",
            follow_up="Procurar serviço de saúde imediatamente."
        )

    non_pharm = suggest_non_pharm()
    pharm = suggest_pharm()
    return TriageResult(
        action="AUTOCUIDADO",
        rationale="Quadro sem sinais de alarme, sugestivo de problema autolimitado (≤7 dias, leve/moderado).",
        non_pharm=non_pharm,
        pharm=pharm,
        follow_up="Reavaliar em até 7 dias. Se piorar, não melhorar, ou surgirem sinais de alerta, procurar atendimento."
    )

# ----------------- CLI -----------------

def ask_bool(q: str) -> bool:
    while True:
        a = input(q + " [s/n]: ").strip().lower()
        if a in ("s","sim","y","yes"): return True
        if a in ("n","nao","não","no"): return False
        print("Responda com 's' ou 'n'.")

def run_cli():
    print("=== Triagem de Dor de Garganta (educacional) ===")
    idade = float(input("Idade em anos (ex.: 30): ").strip())
    gest = ask_bool("Gestante ou lactante?")
    idoso = ask_bool("Idoso frágil (dependência/alta vulnerabilidade)?")

    dur = int(input("Duração da dor (dias): ").strip())
    recorrente = ask_bool("É recorrente?")
    abrupto = ask_bool("Início abrupto da dor?")
    pus = ask_bool("Presença de pus/manchas brancas na garganta?")
    intensa_sem_melhora = ask_bool("Dor intensa sem melhora após 24h?")
    incap = ask_bool("Dor incapacita atividades diárias?")
    irritante = ask_bool("Suspeita de exposição a irritantes químicos/IVAS grave?")
    tabaco_tosse = ask_bool("Tabagismo ativo/passivo com tosse >14 dias?")
    dispneia = ask_bool("Dispneia?")
    rigidez = ask_bool("Rigidez no pescoço e dor de cabeça?")
    febre38 = ask_bool("Febre >38°C por mais de 24h?")
    disfagia = ask_bool("Dificuldade de engolir (disfagia)?")
    rouquidao = ask_bool("Rouquidão >3 semanas?")
    rash = ask_bool("Erupção cutânea/bolhas?")
    linfonodos = ask_bool("Inchaço nos linfonodos/pescoço?")
    sialorreia = ask_bool("Salivação excessiva devido à disfagia?")

    inf_rec = ask_bool("Histórico de infecções recorrentes?")
    neo_garganta = ask_bool("Histórico de neoplasia de garganta?")

    agra_med = ask_bool("Uso prolongado de fármacos que podem causar agranulocitose? (carbimazol, neurolépticos, sulfas, citotóxicos)")
    falha_trat = ask_bool("Falha terapêutica prévia ou reação adversa importante?")

    profile = PatientProfile(idade, gest, idoso)
    s = Symptoms(
        duration_days=dur,
        recurrent=recorrente,
        abrupt_onset=abrupto,
        pus_or_white_spots=pus,
        intense_pain_no_improvement_24h=intensa_sem_melhora,
        incapacitating=incap,
        suspected_irritant_exposure=irritante,
        smoker_with_cough_gt14d=tabaco_tosse,
        dyspnea=dispneia,
        neck_rigidity_headache=rigidez,
        fever_over_38_for_24h=febre38,
        dysphagia=disfagia,
        hoarseness_gt3w=rouquidao,
        rash_or_skin_blisters=rash,
        lymph_node_swelling=linfonodos,
        excessive_salivation=sialorreia
    )
    ch = ClinicalHistory(inf_rec, neo_garganta)
    mh = MedicationHistory(agra_med, falha_trat)

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
