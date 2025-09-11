
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluxograma (CLI) para Espirro e Congestão Nasal
------------------------------------------------
Baseado em um algoritmo clínico resumido: faz anamnese rápida,
checa "sinais de alerta" (encaminhar) e sugere manejo não farmacológico
e farmacológico básico quando apropriado.

⚠️ Aviso: Este script é material educacional e NÃO substitui avaliação médica.
Em caso de dúvida, piora ou sintomas importantes, procure um profissional de saúde.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Tuple

@dataclass
class PatientProfile:
    age_years: float
    is_pregnant_or_lactating: bool = False
    has_major_comorbidity: bool = False  # ex.: DPOC, ICC, doença coronariana, imunossupressão
    occupational_irritant_exposure: bool = False

@dataclass
class Symptoms:
    days_of_symptoms: int
    impact_daily_activities: bool
    sneezing: bool = True
    nasal_congestion: bool = True
    itchy_nose_or_eyes: bool = False
    tearing: bool = False
    fever: bool = False
    purulent_discharge_persistent_4d: bool = False
    blood_in_mucus: bool = False
    facial_pain_persistent: bool = False
    cough: bool = False
    shortness_of_breath: bool = False
    halitosis: bool = False

@dataclass
class MedicationHistory:
    recent_decongestant_continuous_use: bool = False  # uso contínuo/abusivo sem melhora
    tried_any_treatment: bool = False

@dataclass
class TriageResult:
    action: str  # "ENCAMINHAR" ou "AUTOCUIDADO"
    rationale: str
    non_pharm: Optional[str] = None
    pharm: Optional[str] = None
    follow_up: Optional[str] = None

def check_red_flags(profile: PatientProfile, sym: Symptoms, meds: MedicationHistory) -> Tuple[bool, str]:
    reasons = []

    if sym.days_of_symptoms > 10:
        reasons.append("sintomas por mais de 10 dias")
    if sym.impact_daily_activities:
        reasons.append("compromete atividades diárias")
    if sym.purulent_discharge_persistent_4d:
        reasons.append("secreção purulenta persistente (>4 dias)")
    if sym.blood_in_mucus:
        reasons.append("sangue no muco")
    if sym.shortness_of_breath:
        reasons.append("presença de dispneia")
    if sym.facial_pain_persistent:
        reasons.append("dor facial persistente/importante")
    if profile.age_years < 2:
        reasons.append("idade < 2 anos")
    if profile.is_pregnant_or_lactating:
        reasons.append("gestação/lactação")
    if profile.has_major_comorbidity:
        reasons.append("comorbidade relevante (ex.: DPOC/ICC/doença coronariana/imunossupressão)")
    if meds.recent_decongestant_continuous_use:
        reasons.append("uso contínuo de descongestionante nasal sem melhora")
    if profile.occupational_irritant_exposure and (sym.cough or sym.nasal_congestion or sym.sneezing):
        reasons.append("suspeita de exposição ocupacional a irritantes")

    if reasons:
        return True, " | ".join(reasons)
    return False, ""

def suggest_management(profile: PatientProfile, sym: Symptoms) -> Tuple[str, str]:
    # Não farmacológico para todos
    non_pharm = (
        "- Lavagem nasal com solução salina 2–4x/dia\n"
        "- Hidratação (água/chás/sopas) e descanso adequado\n"
        "- Evitar poeira, fumaça, odores fortes; arejar ambientes\n"
        "- Evitar álcool/cafeína em excesso\n"
        "- Alimentação equilibrada; atividade física leve se possível\n"
    )

    # Heurística simples para fenótipo alérgico
    allergic_like = (sym.itchy_nose_or_eyes or sym.tearing) and not sym.fever and sym.days_of_symptoms <= 10
    pharm_lines = []

    if allergic_like:
        pharm_lines.append("Alergia provável: considerar anti-histamínico não sedativo (ex.: loratadina) + lavagem nasal.")
        pharm_lines.append("Se congestão importante em adulto, considerar corticoide intranasal conforme bula.")
    else:
        pharm_lines.append("Resfriado/quadros inespecíficos: priorize medidas não farmacológicas + analgésico/antitérmico se necessário.")
        pharm_lines.append("Descongestionantes nasais tópicos: se usados, apenas por curto prazo e conforme bula.")

    if profile.age_years < 12:
        pharm_lines.append("Crianças: priorizar lavagem nasal/hidratação; anti-histamínico apenas se alergia e conforme orientação profissional.")

    pharm = "\n".join(f"- {p}" for p in pharm_lines)

    return non_pharm, pharm

def triage(profile: PatientProfile, sym: Symptoms, meds: MedicationHistory) -> TriageResult:
    red, why = check_red_flags(profile, sym, meds)
    if red:
        return TriageResult(
            action="ENCAMINHAR",
            rationale=f"Encaminhar para avaliação profissional devido a: {why}.",
            non_pharm="- Manter lavagem nasal e hidratação até a consulta.",
            pharm=None,
            follow_up="Procure serviço de saúde (UBS/PA). Retorne antes se houver piora, febre alta ou sinais de alarme adicionais."
        )

    non_pharm, pharm = suggest_management(profile, sym)
    return TriageResult(
        action="AUTOCUIDADO",
        rationale="Sem sinais de alarme identificados na triagem.",
        non_pharm=non_pharm,
        pharm=pharm,
        follow_up=(
            "Reavalie em 48–72h. Se não houver melhora em até 10 dias, "
            "ou se surgirem sinais de alarme, procure atendimento."
        )
    )

# ----------------- CLI simples -----------------

def ask_bool(prompt: str) -> bool:
    while True:
        val = input(prompt + " [s/n]: ").strip().lower()
        if val in ("s", "sim", "y", "yes"): return True
        if val in ("n", "nao", "não", "no"): return False
        print("Responda com 's' ou 'n'.")

def run_cli():
    print("=== Triagem de Espirro e Congestão Nasal (educacional) ===")
    idade = float(input("Idade em anos (ex.: 25): ").strip())
    gest = False
    if idade >= 10:  # pergunta apenas se fizer sentido
        gest = ask_bool("Gestante ou em lactação?")

    comorb = ask_bool("Comorbidade importante (DPOC/ICC/doença coronariana/imunossupressão)?")
    ocup = ask_bool("Exposição ocupacional a irritantes (poeiras/químicos) com sintomas relacionados?")

    dias = int(input("Dias de sintomas (número inteiro): ").strip())
    impacto = ask_bool("Os sintomas atrapalham suas atividades do dia a dia?")
    prurido = ask_bool("Coceira nasal/ocular?")
    lacrimejamento = ask_bool("Lacrimejamento?")
    febre = ask_bool("Febre?")
    purulento = ask_bool("Secreção purulenta persistente por ≥4 dias?")
    sangue = ask_bool("Sangue no muco?")
    dor_facial = ask_bool("Dor facial persistente/importante?")
    tosse = ask_bool("Tosse?")
    dispneia = ask_bool("Falta de ar?")
    halitose = ask_bool("Halitose (mau hálito)?")

    abuso_descong = ask_bool("Uso contínuo/abusivo de descongestionante nasal sem melhora?")

    profile = PatientProfile(
        age_years=idade,
        is_pregnant_or_lactating=gest,
        has_major_comorbidity=comorb,
        occupational_irritant_exposure=ocup
    )
    sym = Symptoms(
        days_of_symptoms=dias,
        impact_daily_activities=impacto,
        itchy_nose_or_eyes=prurido,
        tearing=lacrimejamento,
        fever=febre,
        purulent_discharge_persistent_4d=purulento,
        blood_in_mucus=sangue,
        facial_pain_persistent=dor_facial,
        cough=tosse,
        shortness_of_breath=dispneia,
        halitosis=halitose
    )
    meds = MedicationHistory(recent_decongestant_continuous_use=abuso_descong)

    result = triage(profile, sym, meds)

    print("\n=== Resultado ===")
    print(f"Ação: {result.action}")
    print(f"Motivo: {result.rationale}")
    if result.non_pharm:
        print("\nMedidas não farmacológicas:")
        print(result.non_pharm)
    if result.pharm:
        print("\nOpções farmacológicas:")
        print(result.pharm)
    if result.follow_up:
        print("\nAcompanhamento:")
        print(result.follow_up)

if __name__ == "__main__":
    run_cli()
