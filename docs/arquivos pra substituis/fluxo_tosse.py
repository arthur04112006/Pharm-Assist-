
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluxograma (CLI) para Tosse
---------------------------
Baseado no algoritmo clínico do PDF enviado: triagem de tosse com
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
    is_bedridden: bool = False
    is_immunocompromised: bool = False

@dataclass
class Symptoms:
    duration_days: int
    productive: bool
    dry: bool
    allergic_context: bool
    worsens_at_night_or_lying: bool
    incapacitates: bool

    purulent_or_bloody: bool
    nocturnal_recurrent: bool
    chest_pain_tightness: bool
    dyspnea: bool
    wheezing: bool
    fever: bool
    hemoptysis: bool
    hoarseness: bool
    anorexia: bool
    sore_throat_with_plaques_or_dysphagia: bool
    intense_pain_on_inspiration: bool
    gi_symptoms: bool  # vomiting, abdominal pain, diarrhea
    arthralgia: bool
    conjunctivitis_non_purulent: bool
    malaise: bool
    facial_pain_moderate_severe: bool
    epigastric_pain: bool
    acid_regurgitation: bool
    lymphadenopathy: bool
    hepatosplenomegaly: bool
    edema_lower_limbs: bool

@dataclass
class MedicationHistory:
    ace_inhibitors: bool
    recent_otc_failure: bool

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
    if s.duration_days >= 21:
        reasons.append("tosse ≥3 semanas")

    # Gravidade
    if s.incapacitates:
        reasons.append("sintoma incapacita atividades diárias")
    if s.purulent_or_bloody:
        reasons.append("tosse purulenta, com sangue e/ou odor fétido")
    if s.nocturnal_recurrent or s.worsens_at_night_or_lying:
        reasons.append("tosse noturna recorrente ou que piora ao deitar")
    if s.chest_pain_tightness or s.dyspnea or s.wheezing:
        reasons.append("dispneia, aperto/dor no peito ou sibilância")
    if s.fever:
        reasons.append("febre")
    if s.hemoptysis:
        reasons.append("hemoptise")
    if s.hoarseness:
        reasons.append("rouquidão")
    if s.anorexia:
        reasons.append("anorexia")
    if s.sore_throat_with_plaques_or_dysphagia:
        reasons.append("dor de garganta com placas/disfagia")
    if s.intense_pain_on_inspiration:
        reasons.append("dor intensa na inspiração")
    if s.gi_symptoms:
        reasons.append("manifestações gastrointestinais (vômito, dor abdominal, diarreia)")
    if s.arthralgia:
        reasons.append("artralgia")
    if s.conjunctivitis_non_purulent:
        reasons.append("conjuntivite não purulenta")
    if s.malaise:
        reasons.append("mal-estar geral")
    if s.facial_pain_moderate_severe:
        reasons.append("dor facial moderada a grave")
    if s.epigastric_pain:
        reasons.append("dor epigástrica")
    if s.acid_regurgitation:
        reasons.append("regurgitação ácida")
    if s.lymphadenopathy:
        reasons.append("linfadenopatia")
    if s.hepatosplenomegaly:
        reasons.append("hepatoesplenomegalia")
    if s.edema_lower_limbs:
        reasons.append("edema em membros inferiores")

    # Perfis especiais
    if profile.age_years < 2:
        reasons.append("criança <2 anos")
    if profile.is_pregnant_or_lactating:
        reasons.append("gestante/lactante")
    if profile.is_bedridden:
        reasons.append("paciente acamado")
    if profile.is_immunocompromised:
        reasons.append("imunocomprometido")
    if profile.is_frail_elderly or profile.age_years >= 75:
        reasons.append("idoso frágil (≥75 anos ou dependente)")

    # História farmacoterapêutica
    if mh.ace_inhibitors:
        reasons.append("uso de inibidores da ECA (podem causar tosse)")
    if mh.recent_otc_failure:
        reasons.append("sem melhora após 7 dias de tratamento OTC adequado")

    if reasons:
        return True, " | ".join(reasons)
    return False, ""

def suggest_non_pharm() -> str:
    return (
        "- Aumentar ingestão de líquidos (água, sucos, chás)\n"
        "- Ingerir mel (com cautela em pacientes diabéticos)\n"
        "- Usar umidificadores ou vaporizadores\n"
        "- Cessar tabagismo\n"
        "- Evitar exposição à poluição, poeira, fumaça e irritantes\n"
    )

def suggest_pharm(s: Symptoms) -> str:
    lines = []
    if s.dry:
        lines.append("Antitussígenos/sedativos da tosse seca: dextrometorfano, clobutinol, dropropizina, cloperastina")
    if s.productive:
        lines.append("Expectorantes: guaifenesina, ambroxol")
        lines.append("Mucolíticos: acetilcisteína, carbocisteína, bromexina")
    if s.allergic_context:
        lines.append("Antialérgicos: dexclorfeniramina, loratadina, desloratadina")
    lines.append("⚠️ Não se recomenda associar classes diferentes de medicamentos para tosse.")
    return "- " + "\n- ".join(lines)

def triage(profile: PatientProfile, s: Symptoms, mh: MedicationHistory) -> TriageResult:
    red, why = has_red_flags(profile, s, mh)
    if red:
        return TriageResult(
            action="ENCAMINHAR",
            rationale=f"Encaminhar para avaliação profissional devido a: {why}.",
            non_pharm="- Enquanto aguarda, manter hidratação, evitar irritantes, usar mel/umidificador.",
            follow_up="Procurar serviço de saúde (urgência se dispneia, dor torácica, hemoptise, febre alta)."
        )

    non_pharm = suggest_non_pharm()
    pharm = suggest_pharm(s)
    return TriageResult(
        action="AUTOCUIDADO",
        rationale=(
            "Tosse autolimitada (<3 semanas), seca ou produtiva, sem sinais de alerta, "
            "relacionada a irritantes/infecções leves/alergia, não incapacitando atividades."
        ),
        non_pharm=non_pharm,
        pharm=pharm,
        follow_up="Reavaliar em 7 dias. Se piorar, persistir ≥3 semanas ou surgirem sinais de alarme, procurar atendimento."
    )

# ----------------- CLI -----------------

def ask_bool(q: str) -> bool:
    while True:
        a = input(q + " [s/n]: ").strip().lower()
        if a in ("s","sim","y","yes"): return True
        if a in ("n","nao","não","no"): return False
        print("Responda com 's' ou 'n'.")

def run_cli():
    print("=== Triagem de Tosse (educacional) ===")
    idade = int(input("Idade (anos): ").strip())
    gest_lac = ask_bool("Gestante ou lactante?")
    idoso = ask_bool("Idoso frágil (dependente/≥75 anos)?")
    acamado = ask_bool("Paciente acamado?")
    imuno = ask_bool("Imunocomprometido(a)?")

    dur = int(input("Duração da tosse (dias): ").strip())
    prod = ask_bool("Tosse produtiva (com secreção)?")
    seca = ask_bool("Tosse seca?")
    alerg = ask_bool("Histórico de rinite/alergia na vigência da tosse?")
    noturna = ask_bool("Tosse noturna recorrente ou que piora ao deitar?")
    incap = ask_bool("A tosse incapacita atividades diárias?")

    purulenta = ask_bool("Tosse purulenta (amarela, verde, marrom), com sangue e/ou odor fétido?")
    dor_peito = ask_bool("Dor/pressão no peito ou falta de ar (dispneia)?")
    sib = ask_bool("Sibilância (chiado no peito)?")
    febre = ask_bool("Febre?")
    hemopt = ask_bool("Tosse com sangue (hemoptise)?")
    rouq = ask_bool("Rouquidão?")
    anorex = ask_bool("Anorexia (falta de apetite)?")
    dor_garganta = ask_bool("Dor de garganta com placas/disfagia?")
    dor_insp = ask_bool("Dor intensa ao inspirar?")
    gi = ask_bool("Sintomas gastrointestinais (vômito, dor abdominal, diarreia)?")
    artralgia = ask_bool("Artralgia (dor nas articulações)?")
    conjunt = ask_bool("Conjuntivite não purulenta?")
    mal = ask_bool("Mal-estar geral?")
    dor_facial = ask_bool("Dor facial moderada a grave?")
    dor_epi = ask_bool("Dor epigástrica?")
    regurg = ask_bool("Regurgitação ácida?")
    linfon = ask_bool("Linfonodomegalia (ínguas)?")
    hepatoespleno = ask_bool("Hepatoesplenomegalia?")
    edema_mmii = ask_bool("Edema em membros inferiores?")

    ieca = ask_bool("Uso de inibidores da ECA (ex.: captopril, enalapril, lisinopril)?")
    falha_otc = ask_bool("Sem melhora após 7 dias de tratamento OTC adequado?")

    profile = PatientProfile(
        age_years=idade,
        is_pregnant_or_lactating=gest_lac,
        is_frail_elderly=idoso,
        is_bedridden=acamado,
        is_immunocompromised=imuno
    )
    s = Symptoms(
        duration_days=dur,
        productive=prod,
        dry=seca,
        allergic_context=alerg,
        worsens_at_night_or_lying=noturna,
        incapacitates=incap,
        purulent_or_bloody=purulenta,
        nocturnal_recurrent=noturna,
        chest_pain_tightness=dor_peito,
        dyspnea=dor_peito,
        wheezing=sib,
        fever=febre,
        hemoptysis=hemopt,
        hoarseness=rouq,
        anorexia=anorex,
        sore_throat_with_plaques_or_dysphagia=dor_garganta,
        intense_pain_on_inspiration=dor_insp,
        gi_symptoms=gi,
        arthralgia=artralgia,
        conjunctivitis_non_purulent=conjunt,
        malaise=mal,
        facial_pain_moderate_severe=dor_facial,
        epigastric_pain=dor_epi,
        acid_regurgitation=regurg,
        lymphadenopathy=linfon,
        hepatosplenomegaly=hepatoespleno,
        edema_lower_limbs=edema_mmii
    )
    mh = MedicationHistory(
        ace_inhibitors=ieca,
        recent_otc_failure=falha_otc
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
