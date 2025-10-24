
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluxograma (CLI) para Dor de Cabeça
-----------------------------------
Baseado no algoritmo clínico do PDF enviado: triagem de cefaleia com
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
    is_pregnant_or_gt20w: bool = False
    is_frail_elderly: bool = False
    is_immunosuppressed: bool = False
    has_htn_hf_renal_gi_asthma_bronchitis: bool = False  # limitações relativas a AINEs
    underlying_conditions: bool = False  # hipertensão, sinusite, traumas, glaucoma, câncer, SAOS, bruxismo, DPOC

@dataclass
class Symptoms:
    duration_days: int
    freq_days_per_month: int
    duration_4_to_72h: bool
    unilateral_periorbital_temporal_explosive_abrupt: bool
    pulsatile_gradual_increase_no_prev_migraine_dx: bool
    morning_worse_lying_better_day: bool
    pattern_change_last_6_months: bool
    severe_occipital: bool
    moderate_to_severe_incapacitating: bool

    bilateral_tight_band: bool
    pericranial_tenderness: bool
    stable_6_months: bool
    known_migraine_with_pulsatile_gradual: bool

    triggers_present: bool  # estresse, menstruação, clima, jejum, privação do sono, rotina alterada
    relief_dark_quiet: bool

    # sintomas associados
    photophobia_or_phonophobia_only: bool
    fever_chills: bool
    drowsiness: bool
    nausea_vomiting: bool
    myalgia: bool
    high_bp_measurement: bool
    weight_loss: bool
    neck_rigidity: bool
    dizziness: bool
    confusion: bool
    tearing_redness_eye: bool
    rhinorrhea_sweating_agitation: bool
    focal_neuro_signs: bool
    eyelid_edema_miosis_ptosis: bool
    blurred_or_double_vision: bool
    papilledema: bool
    unequal_or_nonreactive_pupils: bool
    aura_without_prior_migraine_dx: bool  # alterações sensitivas/visuais/fala/parestesia etc.

@dataclass
class MedicationHistory:
    suspected_adr_drugs: bool  # anticoncepcionais, BCC, nitratos
    previous_treatment_failure_or_adrs: bool
    overuse_analgesic_nsaid_15dmo: bool
    overuse_triptan_opioid_ergot_combo_10dmo: bool

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
        reasons.append(">7 dias de dor")
    if s.freq_days_per_month >= 15:
        reasons.append("frequente (≥15 dias/mês por >3 meses)")

    # Padrões e características de alerta
    if s.duration_4_to_72h:
        reasons.append("duração de 4–72h associada a outras características de alerta")
    if s.unilateral_periorbital_temporal_explosive_abrupt:
        reasons.append("dor unilateral periorbitária/temporal, explosiva de início abrupto")
    if s.pulsatile_gradual_increase_no_prev_migraine_dx:
        reasons.append("pulsátil, início gradual e crescente, sem diagnóstico prévio de enxaqueca")
    if s.morning_worse_lying_better_day:
        reasons.append("inicia pela manhã, piora deitado e melhora ao longo do dia")
    if s.pattern_change_last_6_months:
        reasons.append("mudança do padrão nos últimos 6 meses")
    if s.severe_occipital:
        reasons.append("dor occipital grave")
    if s.moderate_to_severe_incapacitating:
        reasons.append("moderada a grave, incapacita atividades")

    # Sintomas associados de alerta
    if s.fever_chills:
        reasons.append("febre/calafrios")
    if s.drowsiness:
        reasons.append("sonolência excessiva")
    if s.nausea_vomiting:
        reasons.append("náuseas/vômitos intensos")
    if s.myalgia:
        reasons.append("mialgias")
    if s.high_bp_measurement:
        reasons.append("pressão arterial elevada")
    if s.weight_loss:
        reasons.append("perda de peso")
    if s.neck_rigidity:
        reasons.append("rigidez de nuca")
    if s.dizziness:
        reasons.append("tontura")
    if s.confusion:
        reasons.append("confusão mental")
    if s.tearing_redness_eye:
        reasons.append("lacrimejamento/vermelhidão periocular")
    if s.rhinorrhea_sweating_agitation:
        reasons.append("rinorreia/sudorese/inquietação")
    if s.focal_neuro_signs:
        reasons.append("sinais neurológicos focais")
    if s.eyelid_edema_miosis_ptosis:
        reasons.append("edema palpebral/miose/ptose")
    if s.blurred_or_double_vision:
        reasons.append("visão turva/dupla")
    if s.papilledema:
        reasons.append("papiledema")
    if s.unequal_or_nonreactive_pupils:
        reasons.append("pupilas desiguais ou arreflexas")
    if s.aura_without_prior_migraine_dx:
        reasons.append("aura na ausência de diagnóstico prévio de enxaqueca")

    # Perfil/públicos especiais
    if profile.age_years < 12:
        reasons.append("criança <12 anos (urgente se rigidez de pescoço, febre ou exantema)")
    if profile.is_pregnant_or_gt20w:
        reasons.append("gestante (>20 semanas)")
    if profile.is_frail_elderly:
        reasons.append("idoso frágil")
    if profile.age_years > 50:
        reasons.append("primeiro episódio ou dor grave >50 anos")
    if profile.is_immunosuppressed:
        reasons.append("imunossuprimido")

    # Condições subjacentes
    if profile.underlying_conditions:
        reasons.append("associada a condição clínica (HAS, sinusite, trauma, glaucoma, câncer, SAOS, bruxismo, DPOC)")

    # Medicamentos e uso excessivo
    if mh.suspected_adr_drugs:
        reasons.append("suspeita de reação medicamentosa (ACO, BCC, nitratos)")
    if mh.previous_treatment_failure_or_adrs:
        reasons.append("falha terapêutica prévia/reações adversas")
    if mh.overuse_analgesic_nsaid_15dmo or mh.overuse_triptan_opioid_ergot_combo_10dmo:
        reasons.append("uso excessivo de analgésicos (cefaleia por abuso de medicação)")

    if reasons:
        return True, " | ".join(reasons)
    return False, ""

def suggest_non_pharm() -> str:
    return (
        "- Repouso em ambiente escuro e silencioso\n"
        "- Bolsa térmica (quente ou fria) na cabeça\n"
        "- Manter rotina regular de sono e alimentação\n"
        "- Técnicas de relaxamento\n"
    )

def suggest_pharm(profile: PatientProfile) -> str:
    lines = []
    # AINEs geralmente mais efetivos que paracetamol
    if not profile.has_htn_hf_renal_gi_asthma_bronchitis:
        lines.append("Preferir AINEs OTC: ibuprofeno, naproxeno; considerar AAS conforme tolerância.")
    else:
        lines.append("AINEs podem ser limitados por HAS/IC, renal, GI, asma/bronquite — considerar alternativas.")
    lines.append("Paracetamol pode ser menos efetivo que AINEs, mas é opção quando AINEs são contraindicados.")
    lines.append("Se resposta inadequada a monoterapia, considerar combinação com cafeína (analgésico/AINE + cafeína).")
    lines.append("Evitar uso excessivo: analgésicos/AINEs ≥15 dias/mês e triptanos/opioides/ergot/associações ≥10 dias/mês podem causar cefaleia por abuso.")
    lines.append("Vasoconstritores OTC podem ser usados conforme bula; avaliar riscos individuais.")
    return "- " + "\n- ".join(lines)

def triage(profile: PatientProfile, s: Symptoms, mh: MedicationHistory) -> TriageResult:
    red, why = has_red_flags(profile, s, mh)
    if red:
        return TriageResult(
            action="ENCAMINHAR",
            rationale=f"Encaminhar para avaliação profissional devido a: {why}.",
            non_pharm="- Pode usar medidas não farmacológicas até avaliação; enfatizar procura médica.",
            follow_up="Procurar serviço de saúde (urgência se sinais neurológicos/infecção)."
        )

    non_pharm = suggest_non_pharm()
    pharm = suggest_pharm(profile)
    return TriageResult(
        action="AUTOCUIDADO",
        rationale=(
            "Cefaleia autolimitada (≤7 dias), tipo tensão (bilateral em aperto, sensibilidade pericraniana, "
            "padrão estável ≥6 meses) ou enxaqueca conhecida (pulsátil, gradual e crescente com diagnóstico prévio)."
        ),
        non_pharm=non_pharm,
        pharm=pharm,
        follow_up=(
            "Reavaliar em até 72h. Identificar e evitar gatilhos (álcool, odores, chocolate, queijos, cafeína, aspartame, glutamato, castanhas, ruídos). "
            "Se padrão mudar, persistir >7 dias, aumentar frequência, ou surgirem sinais de alarme, procurar atendimento."
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
    print("=== Triagem de Dor de Cabeça (educacional) ===")
    idade = int(input("Idade (anos): ").strip())
    gest20 = ask_bool("Gestante (≥20 semanas)?")
    idoso_fragil = ask_bool("Idoso frágil (dependência/alta vulnerabilidade)?")
    imuno = ask_bool("Imunossuprimido(a)?")
    limita_nsaid = ask_bool("HAS/IC, insuficiência renal, doença GI, asma ou bronquite?")
    cond_subj = ask_bool("Há condição subjacente associada (HAS, sinusite, trauma, glaucoma, câncer, SAOS, bruxismo, DPOC)?")

    dur = int(input("Duração do episódio atual (dias): ").strip())
    freq = int(input("Frequência: quantos dias de dor por mês (número inteiro): ").strip())
    dur_4_72 = ask_bool("As crises costumam durar 4–72h e há outras características de alerta?")
    peri_explosiva = ask_bool("Dor unilateral, periorbitária/temporal, profunda, contínua e explosiva de início abrupto?")
    puls_no_dx = ask_bool("Dor pulsátil, início gradual e crescente, sem diagnóstico prévio de enxaqueca?")
    manha_piora = ask_bool("Inicia pela manhã, piora deitado e melhora ao longo do dia?")
    padrao_mudou = ask_bool("Mudança do padrão nos últimos 6 meses?")
    occipital_grave = ask_bool("Dor occipital grave?")
    incap = ask_bool("Dor moderada a grave que incapacita atividades?")

    bilateral_aper = ask_bool("Dor bilateral em aperto?")
    peri_sens = ask_bool("Aumento da sensibilidade pericraniana?")
    estavel6m = ask_bool("Padrão estável há ≥6 meses?")
    enxaqueca_conhecida = ask_bool("Enxaqueca conhecida (pulsátil, início gradual, padrão crescente, já diagnosticada)?")

    gatilhos = ask_bool("Há gatilhos (estresse, menstruação, clima, jejum, privação do sono, rotina alterada)?")
    alivio_escuro = ask_bool("Alivia em ambiente escuro e silencioso?")

    foto_fono = ask_bool("Há apenas fotofobia/fonofobia (sem outros sintomas de alerta)?")
    febre_calafrio = ask_bool("Febre ou calafrios?")
    sonol = ask_bool("Sonolência excessiva?")
    nausea_vom = ask_bool("Náuseas ou vômitos?")
    mialgia = ask_bool("Mialgias?")
    pa_alta = ask_bool("Pressão arterial elevada?")
    perda_peso = ask_bool("Perda de peso?")
    rigidez = ask_bool("Rigidez de nuca?")
    tont = ask_bool("Tontura?")
    confus = ask_bool("Confusão mental?")
    olhos = ask_bool("Lacrimejamento/vermelhidão ao redor dos olhos?")
    rino_sud_agit = ask_bool("Rinorreia, sudorese ou agitação?")
    neuro_focal = ask_bool("Sinais neurológicos focais?")
    palpebra = ask_bool("Edema palpebral, miose ou ptose?")
    visao = ask_bool("Visão turva ou dupla?")
    papil = ask_bool("Papiledema?")
    pupilas = ask_bool("Pupilas desiguais ou que não reagem à luz?")
    aura_sem_dx = ask_bool("Aura (visual/sensitiva/fala/parestesia) sem diagnóstico prévio de enxaqueca?")

    suspeita_adr = ask_bool("Suspeita de reação a medicamento (anticoncepcional, BCC, nitratos)?")
    falha_trat = ask_bool("Falha terapêutica prévia ou reação adversa importante?")
    abuso_analg = ask_bool("Uso de analgésicos/AINEs ≥15 dias/mês nos últimos 3 meses?")
    abuso_tript = ask_bool("Uso de triptanos/opioides/ergot/associações ≥10 dias/mês nos últimos 3 meses?")

    profile = PatientProfile(
        age_years=idade,
        is_pregnant_or_gt20w=gest20,
        is_frail_elderly=idoso_fragil,
        is_immunosuppressed=imuno,
        has_htn_hf_renal_gi_asthma_bronchitis=limita_nsaid,
        underlying_conditions=cond_subj
    )
    s = Symptoms(
        duration_days=dur,
        freq_days_per_month=freq,
        duration_4_to_72h=dur_4_72,
        unilateral_periorbital_temporal_explosive_abrupt=peri_explosiva,
        pulsatile_gradual_increase_no_prev_migraine_dx=puls_no_dx,
        morning_worse_lying_better_day=manha_piora,
        pattern_change_last_6_months=padrao_mudou,
        severe_occipital=occipital_grave,
        moderate_to_severe_incapacitating=incap,
        bilateral_tight_band=bilateral_aper,
        pericranial_tenderness=peri_sens,
        stable_6_months=estavel6m,
        known_migraine_with_pulsatile_gradual=enxaqueca_conhecida,
        triggers_present=gatilhos,
        relief_dark_quiet=alivio_escuro,
        photophobia_or_phonophobia_only=foto_fono,
        fever_chills=febre_calafrio,
        drowsiness=sonol,
        nausea_vomiting=nausea_vom,
        myalgia=mialgia,
        high_bp_measurement=pa_alta,
        weight_loss=perda_peso,
        neck_rigidity=rigidez,
        dizziness=tont,
        confusion=confus,
        tearing_redness_eye=olhos,
        rhinorrhea_sweating_agitation=rino_sud_agit,
        focal_neuro_signs=neuro_focal,
        eyelid_edema_miosis_ptosis=palpebra,
        blurred_or_double_vision=visao,
        papilledema=papil,
        unequal_or_nonreactive_pupils=pupilas,
        aura_without_prior_migraine_dx=aura_sem_dx
    )
    mh = MedicationHistory(
        suspected_adr_drugs=suspeita_adr,
        previous_treatment_failure_or_adrs=falha_trat,
        overuse_analgesic_nsaid_15dmo=abuso_analg,
        overuse_triptan_opioid_ergot_combo_10dmo=abuso_tript
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
