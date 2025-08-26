from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from sqlalchemy.orm import Session
from db import Base, engine, get_db
from models import Patient, Encounter
from schemas import PatientIn, EncounterIn
from auth import require_auth
from rules import compute_bmi, generate_suggestions
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime

app = Flask(__name__)
CORS(app)
Base.metadata.create_all(bind=engine)

# depois de Base.metadata.create_all(bind=engine)
from sqlalchemy import text
with engine.connect() as conn:
    # adicionar coluna cpf se não existir
    cols = [row[1] for row in conn.execute(text("PRAGMA table_info(patients)"))]
    if "cpf" not in cols:
        conn.execute(text("ALTER TABLE patients ADD COLUMN cpf TEXT"))
    # índice único para cpf (evita duplicados)
    conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS idx_patients_cpf ON patients(cpf)"))
    conn.commit()

import re

def only_digits(s: str) -> str:
    return re.sub(r"\D+", "", s or "")

def cpf_is_valid_digits(cpf: str) -> bool:
    # valida 11 dígitos sem ser tudo igual; (checagem simples, sem DV matemático para MVP)
    if not re.fullmatch(r"\d{11}", cpf): return False
    if cpf == cpf[0]*11: return False
    return True


from flask_cors import CORS
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})


from flask import request

# atende qualquer pré-flight CORS (OPTIONS) com 204
@app.route("/<path:anypath>", methods=["OPTIONS"])
def any_options(anypath):
    return ("", 204)


@app.post("/auth/login")
def login():
    body = request.get_json() or {}
    # mock: aceita qualquer email/senha
    return jsonify({"token":"demo","user":{"email":body.get("email","user@demo")}})

@app.get("/patients")
@require_auth
def list_patients():
    with next(get_db()) as db:  # type: Session
        q = db.query(Patient).order_by(Patient.created_at.desc()).all()
        out = []
        for p in q:
            out.append({
              "id": p.id, "name": p.name, "imc": p.imc,
              "height_m": p.height_m, "weight_kg": p.weight_kg
            })
        return jsonify(out)

@app.post("/patients")
@require_auth
def create_patient():
    data = request.get_json() or {}
    # normaliza cpf para apenas dígitos
    data["cpf"] = only_digits(data.get("cpf"))
    p = PatientIn(**data)

    if not cpf_is_valid_digits(p.cpf):
        return jsonify({"error":"invalid_cpf","detail":"CPF deve ter 11 dígitos válidos"}), 400

    with next(get_db()) as db:
        # checar duplicidade
        exists = db.query(Patient).filter(Patient.cpf == p.cpf).first()
        if exists:
            return jsonify({"error":"duplicate_cpf","detail":"Já existe paciente com este CPF"}), 409

        imc = compute_bmi(p.height_m, p.weight_kg)
        m = Patient(
            name=p.name, cpf=p.cpf, birth_date=p.birth_date,
            height_m=p.height_m, weight_kg=p.weight_kg, imc=imc,
            allergies=[a for a in p.allergies],
            meds=[m.model_dump() for m in p.meds]
        )
        db.add(m); db.commit(); db.refresh(m)
        return jsonify({"id": m.id}), 201


@app.get("/patients/<pid>")
@require_auth
def get_patient(pid):
    with next(get_db()) as db:
        p = db.get(Patient, pid)
        if not p: return jsonify({"error":"not found"}), 404
        return jsonify({
            "id": p.id, "name": p.name, "cpf": p.cpf,
            "birth_date": str(p.birth_date) if p.birth_date else None,
            "height_m": p.height_m, "weight_kg": p.weight_kg, "imc": p.imc,
            "allergies": p.allergies or [], "meds": p.meds or []
        })

@app.delete("/patients/<pid>")
@require_auth
def delete_patient(pid):
    with next(get_db()) as db:
        p = db.get(Patient, pid)
        if not p: return jsonify({"error":"not found"}), 404
        db.delete(p)  # encounters caem em cascata
        db.commit()
        return jsonify({"ok": True})


@app.put("/patients/<pid>")
@require_auth
def update_patient(pid):
    data = request.get_json() or {}
    with next(get_db()) as db:
        p = db.get(Patient, pid)
        if not p: return jsonify({"error":"not found"}), 404

        if "cpf" in data and only_digits(data["cpf"]) != p.cpf:
            return jsonify({"error":"immutable_field","detail":"CPF não pode ser alterado"}), 400

        for k in ("name","birth_date","height_m","weight_kg","allergies","meds"):
            if k in data: setattr(p, k, data[k])
        p.imc = compute_bmi(p.height_m, p.weight_kg)
        db.commit()
        return jsonify({"ok": True})

@app.post("/patients/<pid>/encounters")
@require_auth
def start_encounter(pid):
    with next(get_db()) as db:
        p = db.get(Patient, pid)
        if not p: return jsonify({"error":"patient not found"}), 404
        e = Encounter(patient_id=pid, data={}, suggestions={})
        db.add(e); db.commit(); db.refresh(e)
        return jsonify({"id": e.id}), 201

@app.put("/encounters/<eid>")
@require_auth
def save_encounter(eid):
    body = request.get_json() or {}
    enc_in = EncounterIn(**body)
    with next(get_db()) as db:
        e = db.get(Encounter, eid)
        if not e: return jsonify({"error":"not found"}), 404
        e.data = enc_in.data
        db.commit()
        return jsonify({"ok": True})

@app.post("/encounters/<eid>/finalize")
@require_auth
def finalize_encounter(eid):
    with next(get_db()) as db:
        e = db.get(Encounter, eid)
        if not e: return jsonify({"error":"not found"}), 404
        p = db.get(Patient, e.patient_id)
        e.suggestions = generate_suggestions(p, e.data or {})
        db.commit(); db.refresh(e)
        return jsonify({"id": e.id, "patient_id": e.patient_id, "data": e.data, "suggestions": e.suggestions})

def _pdf_bytes(title, lines):
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    y = height - 50
    c.setFont("Helvetica-Bold", 14); c.drawString(40, y, title); y -= 20
    c.setFont("Helvetica", 10)
    for line in lines:
        if y < 60: c.showPage(); y = height - 50
        c.drawString(40, y, line); y -= 14
    c.showPage(); c.save(); buf.seek(0); return buf

@app.get("/pdf/patient/<pid>")
@require_auth
def pdf_patient(pid):
    with next(get_db()) as db:
        p = db.get(Patient, pid)
        if not p: return jsonify({"error":"not found"}), 404
        lines = [
            f"Paciente: {p.name}",
            f"Altura: {p.height_m} m   Peso: {p.weight_kg} kg   IMC: {p.imc}",
            f"Alergias: {', '.join(p.allergies or []) or '—'}",
            f"Medicamentos: {', '.join([m.get('nome','') for m in (p.meds or [])]) or '—'}",
        ]
        return send_file(_pdf_bytes("Prontuário - Cadastro", lines),
                         mimetype="application/pdf", as_attachment=True,
                         download_name=f"prontuario_{p.id}.pdf")

@app.get("/pdf/encounter/<eid>")
@require_auth
def pdf_encounter(eid):
    with next(get_db()) as db:
        e = db.get(Encounter, eid)
        if not e: return jsonify({"error":"not found"}), 404
        p = db.get(Patient, e.patient_id)
        sug = e.suggestions or {}
        lines = [
            f"Paciente: {p.name}",
            f"Respostas: {e.data}",
            f"Sugestões não farmacológicas: {', '.join(sug.get('nao_farmacologicas',[])) or '—'}",
            f"Sugestões farmacológicas: {', '.join(sug.get('farmacologicas',[])) or '—'}",
            f"Alertas: {', '.join(sug.get('alertas',[])) or '—'}",
        ]
        return send_file(_pdf_bytes("Resumo do Atendimento", lines),
                         mimetype="application/pdf", as_attachment=True,
                         download_name=f"atendimento_{e.id}.pdf")

@app.get("/patients/<pid>/encounters")
@require_auth
def list_encounters(pid):
    with next(get_db()) as db:
        p = db.get(Patient, pid)
        if not p:
            return jsonify({"error":"patient not found"}), 404
        out = []
        for e in p.encounters:
            out.append({
                "id": e.id,
                "patient_id": e.patient_id,
                "created_at": str(e.created_at),
                "has_suggestions": bool(e.suggestions)
            })
        # ordenar desc por data
        out.sort(key=lambda x: x["created_at"], reverse=True)
        return jsonify(out)

@app.get("/encounters/<eid>")
@require_auth
def get_encounter(eid):
    with next(get_db()) as db:
        e = db.get(Encounter, eid)
        if not e:
            return jsonify({"error":"not found"}), 404
        return jsonify({
            "id": e.id,
            "patient_id": e.patient_id,
            "data": e.data or {},
            "suggestions": e.suggestions or {},
            "created_at": str(e.created_at)
        })

import csv
from datetime import datetime

@app.get("/export/patients.csv")
@require_auth
def export_patients_csv():
    with next(get_db()) as db:
        pts = db.query(Patient).order_by(Patient.created_at.desc()).all()
        from io import StringIO, BytesIO
        sio = StringIO()
        w = csv.writer(sio, delimiter=';')
        w.writerow(["id","nome","altura_m","peso_kg","imc","alergias","medicamentos","criado_em"])
        for p in pts:
            alergias = ", ".join(p.allergies or [])
            meds = ", ".join([m.get("nome","") for m in (p.meds or [])])
            w.writerow([p.id, p.name, p.height_m or "", p.weight_kg or "", p.imc or "", alergias, meds, p.created_at])
        data = sio.getvalue().encode("utf-8")
        bio = BytesIO(data); bio.seek(0)
        fname = f"pacientes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        return send_file(bio, mimetype="text/csv", as_attachment=True, download_name=fname)
    
@app.route("/encounters/<eid>/feedback", methods=["POST", "OPTIONS"])
@require_auth
def save_feedback(eid):
    try:
        body = request.get_json(force=True, silent=False) or {}
        label = (body.get("label") or "").strip().lower()   # "agree" | "disagree"
        note  = (body.get("note") or "").strip() or None

        if label not in {"agree", "disagree"}:
            return jsonify({"error": "label must be 'agree' or 'disagree'"}), 400

        with next(get_db()) as db:
            e = db.get(Encounter, eid)
            if not e:
                return jsonify({"error":"not found"}), 404

            # se não houver suggestions, gera agora
            if not e.suggestions or not isinstance(e.suggestions, dict) or len(e.suggestions) == 0:
                p = db.get(Patient, e.patient_id)
                e.suggestions = generate_suggestions(p, e.data or {})

            s = e.suggestions or {}
            s["feedback"] = {
                "label": label,
                "note": note,
                "ts": datetime.utcnow().isoformat() + "Z"
            }
            e.suggestions = s
            db.commit(); db.refresh(e)
            return jsonify({"ok": True, "suggestions": e.suggestions}), 200
    except Exception as ex:
        app.logger.exception("feedback failed")
        return jsonify({"error":"feedback_failed","detail":str(ex)}), 500


if __name__ == "__main__":
    app.run(debug=True)





