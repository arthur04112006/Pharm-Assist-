"""
Pacote de módulos de perguntas por sintoma para triagem farmacêutica.

Cada módulo expõe a função principal `iniciar_triangem(paciente)`.
"""

from . import (
    espirro_congestao_nasal,
    dor_lombar,
    dor_garganta,
    dismenorreia,
    febre,
    infeccoes_fungicas,
    dor_cabeca,
    azia_ma_digestao,
    queimadura_solar,
    constipacao,
    hemorroidas,
    diarreia,
    tosse,
)

__all__ = [
    "espirro_congestao_nasal",
    "dor_lombar",
    "dor_garganta",
    "dismenorreia",
    "febre",
    "infeccoes_fungicas",
    "dor_cabeca",
    "azia_ma_digestao",
    "queimadura_solar",
    "constipacao",
    "hemorroidas",
    "diarreia",
    "tosse",
]
