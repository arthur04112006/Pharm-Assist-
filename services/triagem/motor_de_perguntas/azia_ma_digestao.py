#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluxograma (CLI) para Azia e Má Digestão
----------------------------------------
Baseado no algoritmo clínico do PDF enviado: triagem de pirose/indigestão com
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
    is_pregnant: bool = False
    is_frail_elderly: bool = False
    family_history_gastric_or_esophageal_ca: bool = False
    gastric_surgery_or_pancreatitis: bool = False
    renal_disease: bool = False

@dataclass
class Symptoms:
    duration_days: int
    freq_per_week: int
    burning_substernal_to_throat: bool
    bad_taste: bool
    fullness_postprandial: bool
    distension: bool
    worse_lying_or_foods: bool
    onset_after_meal_or_exercise: bool
    nocturnal: bool
    mild_moderate_not_limiting: bool

    # Alertas
    chest_pain_radiates_to_neck_arm_sweating_dyspnea: bool
    severe_epigastric_or_ruq_pain_30min: bool
    intense_limit_daily: bool
    dysphagia: bool
    odynophagia: bool
    wheezing_drowning: bool
    recurrent_bronchial: bool
    hoarseness: bool
    recurrent_cough: bool
    gi_bleeding: bool
    anemia: bool
    progressive_weight_loss: bool
    lymphadenopathy: bool
    frequent_nausea_vomit_diarrhea: bool

@dataclass
class MedicationHistory:
    suspected_adr_drugs: bool  # AINEs, valproato, alendronato, anticoagulantes, corticoides, antipsicóticos, etc.
    failure_antacids_or_adrs: bool
    prolonged_ppi_use: bool

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

    # Tempo/frequência
    if s.duration_days > 7:
        reasons.append("azia >7 dias")
    if s.freq_per_week >= 2:
        reasons.append("azia ≥2 vezes/semana")
    if s.nocturnal and s.duration_days > 90:
        reasons.append("azia noturna >3 meses")

    # Características de alerta
    if s.chest_pain_radiates_to_neck_arm_sweating_dyspnea:
        reasons.append("dor/queimação torácica irradiada com sudorese/dispneia (avaliar angina)")
    if s.severe_epigastric_or_ruq_pain_30min:
        reasons.append("dor epigástrica intensa/QUAD sup dir >30 min")
    if s.intense_limit_daily:
        reasons.append("azia intensa que limita atividades/sono/qualidade de vida")
    if s.dysphagia or s.odynophagia:
        reasons.append("disfagia/odinofagia")
    if s.wheezing_drowning or s.recurrent_bronchial:
        reasons.append("sintomas brônquicos recorrentes (dispneia, febre, tosse, rouquidão)")
    if s.hoarseness or s.recurrent_cough:
        reasons.append("rouquidão/tosse recorrente")
    if s.gi_bleeding or s.anemia:
        reasons.append("sinais de sangramento digestivo/anemia")
    if s.progressive_weight_loss:
        reasons.append("emagrecimento progressivo")
    if s.lymphadenopathy:
        reasons.append("linfadenopatia")
    if s.frequent_nausea_vomit_diarrhea:
        reasons.append("náusea/vômito/diarreia frequentes")

    # Perfil
    if profile.age_years < 4:
        reasons.append("criança <4 anos")
    if profile.is_pregnant:
        reasons.append("gestante sem melhora com medidas não farmacológicas")
    if profile.is_frail_elderly:
        reasons.append("idoso frágil")
    if profile.age_years >= 50:
        reasons.append("pirose de instalação recente após 50–55 anos")
    if profile.family_history_gastric_or_esophageal_ca:
        reasons.append("história familiar de adenocarcinoma gástrico/esofágico")
    if profile.gastric_surgery_or_pancreatitis:
        reasons.append("cirurgia gástrica prévia/pancreatite")
    if profile.renal_disease:
        reasons.append("insuficiência renal aguda/crônica")

    # Farmacoterapêutica
    if mh.suspected_adr_drugs:
        reasons.append("suspeita de reação adversa a medicamentos (AINEs, valproato, alendronato, anticoag., corticoides, antipsicóticos, etc.)")
    if mh.failure_antacids_or_adrs:
        reasons.append("falha/reações adversas com antiácidos OTC")
    if mh.prolonged_ppi_use:
        reasons.append("uso prolongado de IBP >12 semanas")

    if reasons:
        return True, " | ".join(reasons)
    return False, ""

def suggest_non_pharm() -> str:
    return (
        "- Elevar a cabeceira da cama\n"
        "- Perder peso (se aplicável)\n"
        "- Dieta: refeições menores e frequentes; reduzir gorduras, condimentos e ácidos; evitar comer 3h antes de deitar\n"
        "- Evitar alimentos que precipitam azia (ex.: café, chocolate, álcool, cítricos, frituras, refrigerantes)\n"
        "- Cessar tabagismo\n"
        "- Evitar automedicação com AINEs\n"
    )

def suggest_pharm() -> str:
    return (
        "- Antiácidos OTC (isolados ou em combinação): carbonato de cálcio, bicarbonato de sódio, sais de magnésio, sais de alumínio\n"
        "- Preferir formulações líquidas (mais eficazes que comprimidos)\n"
        "- Simeticona pode ser adjuvante quando há gases\n"
        "⚠️ Usar conforme bula, respeitar contraindicações (renal, gestação, interações)\n"
    )

def triage(profile: PatientProfile, s: Symptoms, mh: MedicationHistory) -> TriageResult:
    red, why = has_red_flags(profile, s, mh)
    if red:
        return TriageResult(
            action="ENCAMINHAR",
            rationale=f"Encaminhar para avaliação profissional devido a: {why}.",
            non_pharm="- Enquanto aguarda, evitar alimentos gatilho e manter medidas não farmacológicas.",
            follow_up="Procurar serviço de saúde (clínica/PA/gastro) conforme gravidade."
        )

    non_pharm = suggest_non_pharm()
    pharm = suggest_pharm()
    return TriageResult(
        action="AUTOCUIDADO",
        rationale=(
            "Quadro típico de pirose/digestão difícil ≤7 dias, <2 vezes/semana, leve a moderado, "
            "sem sinais de alarme, desencadeado por postura ou alimentos específicos, sem histórico relevante."
        ),
        non_pharm=non_pharm,
        pharm=pharm,
        follow_up=(
            "Reavaliar em até 7 dias. Se persistir ou piorar, ou se surgirem sinais de alerta, procurar atendimento."
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
    print("=== Triagem de Azia e Má Digestão (educacional) ===")
    idade = int(input("Idade (anos): ").strip())
    gest = ask_bool("Gestante?")
    idoso_fragil = ask_bool("Idoso frágil?")
    hist_ca = ask_bool("História familiar de câncer gástrico/esofágico?")
    cir_pancre = ask_bool("Cirurgia gástrica prévia ou pancreatite?")
    renal = ask_bool("Doença renal aguda/crônica?")

    dur = int(input("Duração dos sintomas (dias): ").strip())
    freq = int(input("Frequência (vezes por semana): ").strip())
    queima = ask_bool("Sensação de queimação subesternal irradiando à garganta?")
    gosto = ask_bool("Gosto desagradável na boca associado?")
    plen = ask_bool("Plenitude pós-prandial?")
    dist = ask_bool("Distensão abdominal?")
    piora_deitar = ask_bool("Piora ao deitar, se curvar ou com certos alimentos?")
    inicio_ref = ask_bool("Início ~2h após refeições, exercício, decúbito ou noite?")
    noturna = ask_bool("Azia noturna frequente?")
    leve_mod = ask_bool("Sintomas leves a moderados, não limitam atividades?")

    dor_peito = ask_bool("Dor/queimação no peito irradiada para pescoço/ombros/braços, com sudorese/dispneia?")
    dor_epi = ask_bool("Dor epigástrica intensa ou no quadrante sup dir, ≥30min?")
    intensa_lim = ask_bool("Sintomas intensos que limitam atividades/sono/qualidade de vida?")
    disfagia = ask_bool("Disfagia (dificuldade para engolir)?")
    odino = ask_bool("Odinofagia (dor ao engolir)?")
    sib = ask_bool("Sibilância/sensação de afogamento?")
    bronq = ask_bool("Sintomas brônquicos recorrentes (dispneia/febre)?")
    rouq = ask_bool("Rouquidão?")
    tosse = ask_bool("Tosse recorrente?")
    sangra = ask_bool("Sinais de sangramento gastrointestinal (hematêmese, melena)?")
    anemia = ask_bool("Anemia confirmada?")
    emag = ask_bool("Emagrecimento progressivo não intencional?")
    linfon = ask_bool("Linfadenopatia?")
    nvd = ask_bool("Náuseas, vômitos ou diarreia frequentes?")

    adr = ask_bool("Uso de medicamento suspeito de ADR (AINEs, valproato, alendronato, corticoides, antipsicóticos, etc.)?")
    falha = ask_bool("Falha ou reação adversa com antiácidos OTC?")
    ibp = ask_bool("Uso prolongado de IBP (>12 semanas)?")

    profile = PatientProfile(
        age_years=idade,
        is_pregnant=gest,
        is_frail_elderly=idoso_fragil,
        family_history_gastric_or_esophageal_ca=hist_ca,
        gastric_surgery_or_pancreatitis=cir_pancre,
        renal_disease=renal
    )
    s = Symptoms(
        duration_days=dur,
        freq_per_week=freq,
        burning_substernal_to_throat=queima,
        bad_taste=gosto,
        fullness_postprandial=plen,
        distension=dist,
        worse_lying_or_foods=piora_deitar,
        onset_after_meal_or_exercise=inicio_ref,
        nocturnal=noturna,
        mild_moderate_not_limiting=leve_mod,
        chest_pain_radiates_to_neck_arm_sweating_dyspnea=dor_peito,
        severe_epigastric_or_ruq_pain_30min=dor_epi,
        intense_limit_daily=intensa_lim,
        dysphagia=disfagia,
        odynophagia=odino,
        wheezing_drowning=sib,
        recurrent_bronchial=bronq,
        hoarseness=rouq,
        recurrent_cough=tosse,
        gi_bleeding=sangra,
        anemia=anemia,
        progressive_weight_loss=emag,
        lymphadenopathy=linfon,
        frequent_nausea_vomit_diarrhea=nvd
    )
    mh = MedicationHistory(
        suspected_adr_drugs=adr,
        failure_antacids_or_adrs=falha,
        prolonged_ppi_use=ibp
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
    Fluxo de perguntas e decisões para azia e má digestão.
    Será implementado conforme diretrizes da ANVISA.
    """
    raise NotImplementedError("Fluxo de azia_ma_digestao ainda não implementado")
