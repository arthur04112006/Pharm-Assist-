#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluxograma (CLI) para Infecções Fúngicas Superficiais
-----------------------------------------------------
Baseado no algoritmo clínico do PDF enviado: triagem de micoses superficiais
(tineas, intertrigo por fungo, etc.) com anamnese, checagem de sinais de alerta
(encaminhar) e orientações de manejo não farmacológico e farmacológico (apenas MIPs/OTC).

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
    is_immunosuppressed: bool = False  # HIV/transplante
    uses_immunosuppressant_or_corticosteroid: bool = False

@dataclass
class Symptoms:
    duration_days: int
    large_body_area_involved: bool
    pruritus: bool
    humidity_or_poor_hygiene: bool
    plaque_erythematous_or_brown_with_scale_and_active_borders: bool
    central_clearing: bool

    # Alertas/gravidade/associação
    bleeding: bool
    rapid_growth: bool
    hyperchromic_asymmetric_lesion: bool
    fissure: bool
    pus_or_discharge: bool
    pain: bool
    blisters: bool
    papules_or_pustules: bool
    loss_of_sensation: bool

    trauma_burn_abrasion_or_venomous_bite: bool
    worsens_with_sun_exposure: bool
    open_wound_or_exposed_muscle: bool
    nodule_fistula_or_cyst: bool

    suspected_anaphylaxis_signs: bool  # angioedema, fechamento de glote, respiração curta, bolhas extensas ou rash difuso

@dataclass
class MedicationHistory:
    correct_otc_use_failure: bool

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
    if s.duration_days > 30:
        reasons.append("lesão há mais de 1 mês")

    # Intensidade/Extensão
    if s.large_body_area_involved:
        reasons.append("áreas extensas acometidas / intensidade importante")

    # Características preocupantes da lesão
    if s.open_wound_or_exposed_muscle:
        reasons.append("ferida aberta/exposição de tecido muscular")
    if s.nodule_fistula_or_cyst:
        reasons.append("nódulo/fístula/cisto")
    if s.trauma_burn_abrasion_or_venomous_bite:
        reasons.append("decorrente de trauma/queimadura/escoriação/picada peçonhenta")
    if s.worsens_with_sun_exposure:
        reasons.append("piora com exposição solar")
    if s.bleeding:
        reasons.append("sangramento")
    if s.rapid_growth:
        reasons.append("crescimento rápido")
    if s.hyperchromic_asymmetric_lesion:
        reasons.append("lesão hipercrômica assimétrica")
    if s.fissure:
        reasons.append("fissura")
    if s.pus_or_discharge:
        reasons.append("presença de pus/secreção")
    if s.pain:
        reasons.append("dor")
    if s.blisters:
        reasons.append("bolhas")
    if s.papules_or_pustules:
        reasons.append("pápulas/pústulas")
    if s.loss_of_sensation:
        reasons.append("perda de sensibilidade")
    if s.suspected_anaphylaxis_signs:
        reasons.append("sinais de anafilaxia (angioedema/fechamento de glote/dispneia/rash difuso)")

    # Perfil
    if profile.age_years < 2:
        reasons.append("criança <2 anos")
    if profile.is_pregnant_or_lactating:
        reasons.append("gestante/lactante")
    if profile.is_immunosuppressed:
        reasons.append("imunossupressão (HIV/transplante)")

    # Hist. farmacoterapêutica
    if profile.uses_immunosuppressant_or_corticosteroid:
        reasons.append("uso de imunossupressor/corticosteroide")
    if mh.correct_otc_use_failure:
        reasons.append("falha com uso correto de antifúngico OTC")

    if reasons:
        return True, " | ".join(reasons)
    return False, ""

def suggest_non_pharm() -> str:
    return (
        "- Lavar e secar o corpo com toalha diferente daquela usada para pés\n"
        "- Evitar contato próximo com indivíduos afetados até cura\n"
        "- Evitar brincar/manipular cães/gatos desconhecidos\n"
        "- Perder peso para reduzir áreas intertriginosas (se aplicável)\n"
        "- Secar-se bem após o banho, especialmente dobras (sob mamas, abdome)\n"
        "- Manter a área afetada seca e arejada\n"
    )

def suggest_pharm(profile: PatientProfile) -> str:
    lines = []
    if profile.age_years >= 2:
        # Adultos e crianças >=2 anos
        lines.append("Crianças ≥2 anos: oxiconazol, miconazol (tópicos).")
        lines.append("Adultos: butenafina, terbinafina, clotrimazol, cetoconazol (tópicos).")
    else:
        lines.append("Menores de 2 anos: avaliar com profissional de saúde (não recomendar OTC tópico neste algoritmo).")
    lines.append("Aplicar 1–2x/dia por 2–4 semanas ou conforme bula, estendendo 1–2 semanas após resolução clínica.")
    lines.append("Higiene e secagem adequadas são fundamentais para evitar recidiva.")
    return "- " + "\n- ".join(lines)

def triage(profile: PatientProfile, s: Symptoms, mh: MedicationHistory) -> TriageResult:
    red, why = has_red_flags(profile, s, mh)
    if red:
        return TriageResult(
            action="ENCAMINHAR",
            rationale=f"Encaminhar para avaliação profissional devido a: {why}.",
            non_pharm="- Enquanto aguarda, manter área limpa, seca e arejada; evitar coçar e compartilhar toalhas/roupas.",
            follow_up="Procurar serviço de saúde (dermato/UBS/PA) conforme gravidade."
        )

    # Critérios de problema autolimitado (coluna verde, adaptado)
    non_pharm = suggest_non_pharm()
    pharm = suggest_pharm(profile)
    return TriageResult(
        action="AUTOCUIDADO",
        rationale=(
            "Lesão cutânea superficial escamosa com bordas ativas e clareamento central, com prurido, "
            "sem sinais de alarme e <1 mês de evolução."
        ),
        non_pharm=non_pharm,
        pharm=pharm,
        follow_up=(
            "Reavaliar em 2–4 semanas. Se não houver melhora, houver piora, ou surgirem sinais de alerta, "
            "procurar atendimento."
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
    print("=== Triagem de Infecções Fúngicas Superficiais (educacional) ===")
    idade = float(input("Idade em anos (ex.: 25): ").strip())
    gest_lac = ask_bool("Gestante ou lactante?")
    imuno = ask_bool("Imunossuprimido(a) (HIV/transplante)?")
    uso_imunossup = ask_bool("Uso de imunossupressor ou corticosteroide?")

    dur = int(input("Duração da(s) lesão(ões) (dias): ").strip())
    area_extensa = ask_bool("Grandes áreas do corpo acometidas?")
    prurido = ask_bool("Prurido (coceira) presente?")
    umidade = ask_bool("Ambiente úmido/falta de higiene adequada contribuem?")
    placa = ask_bool("Placa eritematosa/acastanhada, superficial e escamosa, com bordas ativas?")
    centro_claro = ask_bool("Clareamento central (bordas mais ativas)?")

    sangramento = ask_bool("Sangramento?")
    crescimento_rapido = ask_bool("Crescimento rápido da lesão?")
    hipercr = ask_bool("Lesão hipercrômica assimétrica?")
    fissura = ask_bool("Fissura?")
    pus = ask_bool("Pus/secreção?")
    dor = ask_bool("Dor local?")
    bolhas = ask_bool("Bolhas?")
    papulas = ask_bool("Pápulas/pústulas?")
    perda_sens = ask_bool("Perda de sensibilidade no local?")

    trauma_queimadura = ask_bool("Resultado de trauma/queimadura/escoriação ou picada peçonhenta?")
    piora_sol = ask_bool("Lesão piora com exposição solar?")
    ferida_aberta = ask_bool("Ferida aberta ou exposição de tecido muscular?")
    nodulo_fistula_cisto = ask_bool("Nódulo, fístula ou cisto?")

    anafilaxia = ask_bool("Sinais de anafilaxia (angioedema, falta de ar, bolhas extensas/rash difuso)?")

    falha_otc = ask_bool("Houve falha com uso correto de antifúngico tópico OTC?")

    profile = PatientProfile(
        age_years=idade,
        is_pregnant_or_lactating=gest_lac,
        is_immunosuppressed=imuno,
        uses_immunosuppressant_or_corticosteroid=uso_imunossup
    )
    s = Symptoms(
        duration_days=dur,
        large_body_area_involved=area_extensa,
        pruritus=prurido,
        humidity_or_poor_hygiene=umidade,
        plaque_erythematous_or_brown_with_scale_and_active_borders=placa,
        central_clearing=centro_claro,
        bleeding=sangramento,
        rapid_growth=crescimento_rapido,
        hyperchromic_asymmetric_lesion=hipercr,
        fissure=fissura,
        pus_or_discharge=pus,
        pain=dor,
        blisters=bolhas,
        papules_or_pustules=papulas,
        loss_of_sensation=perda_sens,
        trauma_burn_abrasion_or_venomous_bite=trauma_queimadura,
        worsens_with_sun_exposure=piora_sol,
        open_wound_or_exposed_muscle=ferida_aberta,
        nodule_fistula_or_cyst=nodulo_fistula_cisto,
        suspected_anaphylaxis_signs=anafilaxia
    )
    mh = MedicationHistory(correct_otc_use_failure=falha_otc)

    result = triage(profile, s, mh)

    print("\n=== Resultado ===")
    print(f"Ação: {result.action}")
    print(f"Motivo: {result.rationale}")
    if result.non_pharm:
        print("\nMedidas não farmacológicas:")
        print(result.non_pharm)
    if result.pharm:
        print("\nOpções farmacológicas (MIP/OTC) – tópicos:")
        print(result.pharm)
    if result.follow_up:
        print("\nAcompanhamento:")
        print(result.follow_up)

if __name__ == "__main__":
    run_cli()

def iniciar_triagem(paciente):
    """
    Fluxo de perguntas e decisões para infecções fúngicas.
    Será implementado conforme diretrizes da ANVISA.
    """
    raise NotImplementedError("Fluxo de infeccoes_fungicas ainda não implementado")
