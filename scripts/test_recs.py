#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys

try:
    import recomendacoes_farmacologicas as r
except Exception as e:
    print(f"Erro ao importar recomendacoes_farmacologicas: {e}")
    sys.exit(1)


class SR:
    pass


def main():
    mods = [
        "dor_garganta",
        "hemorroidas",
        "diarreia",
        "espirro_congestao_nasal",
        "tosse",
        "febre",
        "dor_cabeca",
        "azia_ma_digestao",
        "constipacao",
        "dor_lombar",
    ]

    respostas = {
        "dor_garganta": [{"pergunta_id": "dor_garganta_1", "resposta": "sim"}],
        "hemorroidas": [{"pergunta_id": "hemorroida_1", "resposta": "sim"}],
        "diarreia": [{"pergunta_id": "diarreia_1", "resposta": "sim"}],
        "espirro_congestao_nasal": [{"pergunta_id": "congestao_1", "resposta": "sim"}],
        "tosse": [{"pergunta_id": "tosse_3", "resposta": "sim"}],
        "febre": [{"pergunta_id": "febre_1", "resposta": "sim"}],
        "dor_cabeca": [{"pergunta_id": "dor_cabeca_1", "resposta": "sim"}],
        "azia_ma_digestao": [{"pergunta_id": "azia_1", "resposta": "sim"}],
        "constipacao": [{"pergunta_id": "constipacao_1", "resposta": "sim"}],
        "dor_lombar": [{"pergunta_id": "dor_lombar_1", "resposta": "sim"}],
    }

    sr = SR()
    perfil = {"age_years": 30}

    out = {}
    for m in mods:
        try:
            recs = r.sistema_recomendacoes.gerar_recomendacoes(
                m, respostas.get(m, []), sr, perfil
            )
            out[m] = [
                {
                    "medicamento": x.medicamento,
                    "principio_ativo": x.principio_ativo,
                    "indicacao": x.indicacao,
                    "observacoes": x.observacoes,
                }
                for x in recs
            ]
        except Exception as e:
            out[m] = {"error": str(e)}

    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()


