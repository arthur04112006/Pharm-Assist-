
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluxograma (CLI) para Hemorroidas
---------------------------------
Baseado no algoritmo clínico do PDF enviado: triagem de hemorroidas com
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
    is_child_leq12: bool = False
    is_immunocompromised: bool = False
    has_portal_hypertension: bool = False
    has_inflammatory_bowel_disease: bool = False  # DII

@dataclass
class Symptoms:
    duration_days: int
    frequency_per_month: int
    pain_intensity_moderate_severe: bool
    bleeding_bright_red_end_or_drips: bool  # típico da coluna verde
    bleeding_dark_red_or_worsened_by_strain: bool
    abundant_bleeding: bool
    prolapse_requires_manual_reduction: bool
    mild_pruritus: bool
    anal_pain: bool
    anal_pruritus: bool
    mucous_secretion_or_mild_fecal_incontinence: bool
    stool_pattern_change: bool
    stool_caliber_frequency_consistency_change: bool
    melena_history: bool
    rectal_bleeding_without_prior_hemmorhoids_dx: bool
    constitutional_symptoms: bool  # mal-estar, febre, hipotensão postural, cansaço persistente
    anemia_symptoms: bool  # fraqueza, cefaleia, irritabilidade, fadiga, intolerância ao exercício

@dataclass
class ClinicalHistory:
    family_history_crc_or_ibd_first_degree: bool
    personal_history_colorectal_polyps: bool

@dataclass
class MedicationHistory:
    anticoagulants_or_antiplatelets: bool
    used_otc_treatment_recently: bool
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
    if s.duration_days > 10:
        reasons.append("sintomas por >10 dias")
    if s.frequency_per_month > 1:
        reasons.append("episódios recorrentes (>1/mês)")

    # Gravidade/intensidade e sangramento
    if s.abundant_bleeding:
        reasons.append("sangramento abundante")
    if mh.anticoagulants_or_antiplatelets and (s.abundant_bleeding or s.bleeding_dark_red_or_worsened_by_strain):
        reasons.append("sangramento volumoso/persistente em uso de anticoagulante/antiagregante")
    if s.pain_intensity_moderate_severe:
        reasons.append("dor intensa que compromete atividades diárias")
    if s.bleeding_dark_red_or_worsened_by_strain:
        reasons.append("sangramento vermelho escuro/agravado por esforço")
    if s.prolapse_requires_manual_reduction:
        reasons.append("prolapso importante exigindo manobras/conduta clínica")

    # Sinais/sintomas associados sugestivos de malignidade
    if s.constitutional_symptoms:
        reasons.append("sintomas constitucionais (mal-estar/febre/hipotensão postural/cansaço)")
    if s.anemia_symptoms:
        reasons.append("sinais/sintomas de anemia por deficiência de ferro")
    if s.stool_pattern_change or s.stool_caliber_frequency_consistency_change:
        reasons.append("alteração do padrão/calibre/frequência/consistência das fezes")
    if s.melena_history:
        reasons.append("histórico de melena")

    # Perfis especiais
    if profile.age_years > 40 and s.rectal_bleeding_without_prior_hemmorhoids_dx:
        reasons.append(">40 anos com sangramento retal sem diagnóstico prévio de hemorroidas")
    if profile.is_child_leq12:
        reasons.append("criança ≤12 anos")
    if profile.is_pregnant_or_lactating:
        reasons.append("gestante/lactante")
    if profile.is_immunocompromised:
        reasons.append("imunocomprometido")
    if profile.has_portal_hypertension:
        reasons.append("hipertensão portal")
    if profile.has_inflammatory_bowel_disease:
        reasons.append("doença inflamatória intestinal")

    # História clínica/familiar
    if ch.personal_history_colorectal_polyps:
        reasons.append("história pessoal de pólipos colorretais")
    if ch.family_history_crc_or_ibd_first_degree:
        reasons.append("história familiar de DII ou câncer colorretal (1º grau)")

    # História farmacoterapêutica
    if s.mucous_secretion_or_mild_fecal_incontinence:
        reasons.append("incontinência fecal leve com secreção de muco")
    if mh.otc_failure_or_adrs:
        reasons.append("falha/reações com tratamentos OTC prévios")

    if reasons:
        return True, " | ".join(reasons)
    return False, ""

def suggest_non_pharm() -> str:
    return (
        "- Ingerir 20–30 g/dia de **fibras insolúveis** + 1,5–2 L/dia de líquidos (pode levar até 6 semanas para perceber o efeito)\n"
        "- **Banhos de assento** 2–3x/dia e após evacuações (15 min em água morna)\n"
        "- **Atividade física** regular\n"
    )

def suggest_pharm() -> str:
    return (
        "- Pomadas/supositórios analgésicos/anti-inflamatórios/antipruriginosos:\n"
        "   • Hidrocortisona acetato + lidocaína\n"
        "   • Fluocortolona pivalato + lidocaína\n"
        "   • Hidrocortisona + lidocaína + subgalato de bismuto + óxido de zinco\n"
        "- Pomadas/supositórios anestésicos e adstringentes: policresuleno + cinchocaína\n"
        "- Pomada anestésica + vasoconstritora: Hamamelis virginiana L + Davilla rugosa P + Atropa belladonna L + mentol + lidocaína\n"
        "- Analgésicos e AINEs (conforme bula)\n"
        "- Laxantes **formadores de massa (fibras)** para manter equilíbrio intestinal\n"
        "⚠️ Atenção: somente medicamentos **isentos de prescrição** neste algoritmo.\n"
    )

def triage(profile: PatientProfile, s: Symptoms, ch: ClinicalHistory, mh: MedicationHistory) -> TriageResult:
    red, why = has_red_flags(profile, s, ch, mh)
    if red:
        return TriageResult(
            action="ENCAMINHAR",
            rationale=f"Encaminhar para avaliação profissional devido a: {why}.",
            non_pharm="- Enquanto aguarda avaliação, manter fibras/líquidos, banhos de assento e higiene local.",
            follow_up="Procurar serviço de saúde (UBS/PA/Proctologia) conforme gravidade."
        )

    non_pharm = suggest_non_pharm()
    pharm = suggest_pharm()
    return TriageResult(
        action="AUTOCUIDADO",
        rationale=(
            "Quadro compatível com doença hemorroidária autolimitada: dor leve-moderada, prurido e "
            "sangramento vermelho vivo cobrindo as fezes no final da defecação ou pingando no vaso, "
            "sinais proeminentes durante a evacuação, sem outros sinais de alerta."
        ),
        non_pharm=non_pharm,
        pharm=pharm,
        follow_up=(
            "Reavaliar em 7–10 dias. Se houver piora, persistência >10 dias, sangramento volumoso, alteração do padrão das fezes "
            "ou quaisquer sinais de alerta, procurar atendimento."
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
    print("=== Triagem de Hemorroidas (educacional) ===")
    idade = int(input("Idade (anos): ").strip())
    gest_lac = ask_bool("Gestante ou lactante?")
    crianca = ask_bool("Criança ≤12 anos?")
    imuno = ask_bool("Imunocomprometido(a)?")
    h_portal = ask_bool("Hipertensão portal?")
    dii = ask_bool("Doença inflamatória intestinal (DII)?")

    dur = int(input("Duração dos sintomas (dias): ").strip())
    freq = int(input("Frequência de episódios por mês (número inteiro): ").strip())

    dor_mod_grave = ask_bool("Dor moderada a intensa que compromete atividades?")
    sang_vermelho_vivo = ask_bool("Sangramento vermelho vivo que cobre as fezes no final da evacuação ou pinga no vaso?")
    sang_escuro_esforco = ask_bool("Sangramento vermelho escuro e/ou agravado por esforço?")
    sang_abundante = ask_bool("Sangramento abundante?")
    prolapso_importante = ask_bool("Prolapso importante que necessita manobras para retorno?")
    prurido_leve = ask_bool("Prurido anal leve?")
    dor_anal = ask_bool("Dor anal presente?")
    prurido_anal = ask_bool("Prurido anal presente?")
    incontinencia_muco = ask_bool("Incontinência fecal leve com secreção de muco?")

    alt_rotina = ask_bool("Houve mudanças de rotina (viagens, estresse, dieta) quando começaram os sintomas?")
    alteracao_habito_intestinal = ask_bool("Houve alteração do hábito intestinal?")
    mudanca_padroes_fezes = ask_bool("Mudança no calibre/frequência/consistência das fezes?")
    melena = ask_bool("Histórico de melena?")
    sang_ret_sem_dx = ask_bool("Sangramento colorretal sem diagnóstico prévio de hemorroidas?")

    sintomas_constitucionais = ask_bool("Mal-estar, febre, hipotensão postural e/ou cansaço persistente?")
    sintomas_anemia = ask_bool("Fraqueza, dor de cabeça, irritabilidade, fadiga ou intolerância ao exercício (sugestivos de anemia)?")

    hist_pessoal_polipos = ask_bool("História pessoal de pólipos colorretais?")
    hist_familiar_crc_dii = ask_bool("História familiar (1º grau) de câncer colorretal ou DII?")

    anticoag_antiagreg = ask_bool("Uso de anticoagulantes e/ou antiagregantes plaquetários?")
    usou_otc = ask_bool("Já tentou pomadas/supositórios OTC recentemente?")
    falha_otc = ask_bool("Houve falha terapêutica ou reação adversa com OTC?")

    profile = PatientProfile(
        age_years=idade,
        is_pregnant_or_lactating=gest_lac,
        is_child_leq12=crianca,
        is_immunocompromised=imuno,
        has_portal_hypertension=h_portal,
        has_inflammatory_bowel_disease=dii
    )
    s = Symptoms(
        duration_days=dur,
        frequency_per_month=freq,
        pain_intensity_moderate_severe=dor_mod_grave,
        bleeding_bright_red_end_or_drips=sang_vermelho_vivo,
        bleeding_dark_red_or_worsened_by_strain=sang_escuro_esforco,
        abundant_bleeding=sang_abundante,
        prolapse_requires_manual_reduction=prolapso_importante,
        mild_pruritus=prurido_leve,
        anal_pain=dor_anal,
        anal_pruritus=prurido_anal,
        mucous_secretion_or_mild_fecal_incontinence=incontinencia_muco,
        stool_pattern_change=alteracao_habito_intestinal,
        stool_caliber_frequency_consistency_change=mudanca_padroes_fezes,
        melena_history=melena,
        rectal_bleeding_without_prior_hemmorhoids_dx=sang_ret_sem_dx,
        constitutional_symptoms=sintomas_constitucionais,
        anemia_symptoms=sintomas_anemia
    )
    ch = ClinicalHistory(
        family_history_crc_or_ibd_first_degree=hist_familiar_crc_dii,
        personal_history_colorectal_polyps=hist_pessoal_polipos
    )
    mh = MedicationHistory(
        anticoagulants_or_antiplatelets=anticoag_antiagreg,
        used_otc_treatment_recently=usou_otc,
        otc_failure_or_adrs=falha_otc
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
