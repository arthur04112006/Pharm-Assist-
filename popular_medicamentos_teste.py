#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para popular o banco de dados com medicamentos de teste
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Medicamento

def popular_medicamentos_teste():
    """Popula o banco com medicamentos de teste"""
    with app.app_context():
        # Verificar se já existem medicamentos
        medicamentos_existentes = Medicamento.query.count()
        if medicamentos_existentes > 0:
            print(f"Já existem {medicamentos_existentes} medicamentos no banco.")
            return
        
        medicamentos_teste = [
            # Medicamentos para tosse
            Medicamento(
                nome_comercial="Vick 44",
                nome_generico="Dextrometorfano",
                descricao="Antitussígeno para tosse seca",
                indicacao="Tosse seca e irritativa, antitussígeno, supressão da tosse",
                contraindicacao="Não usar em crianças menores de 2 anos, gestantes e lactantes",
                tipo="farmacologico",
                ativo=True
            ),
            Medicamento(
                nome_comercial="Mucosolvan",
                nome_generico="Ambroxol",
                descricao="Expectorante e mucolítico",
                indicacao="Tosse produtiva, expectorante, mucolítico, bronquiolite",
                contraindicacao="Hipersensibilidade ao ambroxol",
                tipo="farmacologico",
                ativo=True
            ),
            Medicamento(
                nome_comercial="Claritin",
                nome_generico="Loratadina",
                descricao="Antialérgico",
                indicacao="Tosse alérgica, rinite alérgica, antihistamínico, antialérgico",
                contraindicacao="Hipersensibilidade à loratadina",
                tipo="farmacologico",
                ativo=True
            ),
            Medicamento(
                nome_comercial="Bisolvon",
                nome_generico="Bromexina",
                descricao="Mucolítico e expectorante",
                indicacao="Tosse com secreção, mucolítico, expectorante, bronquite",
                contraindicacao="Hipersensibilidade à bromexina",
                tipo="farmacologico",
                ativo=True
            ),
            Medicamento(
                nome_comercial="Benalet",
                nome_generico="Clobutinol",
                descricao="Antitussígeno",
                indicacao="Tosse seca, antitussígeno, supressão da tosse",
                contraindicacao="Hipersensibilidade ao clobutinol",
                tipo="farmacologico",
                ativo=True
            ),
            Medicamento(
                nome_comercial="Xarope de Guaifenesina",
                nome_generico="Guaifenesina",
                descricao="Expectorante",
                indicacao="Tosse produtiva, expectorante, mucolítico",
                contraindicacao="Hipersensibilidade à guaifenesina",
                tipo="farmacologico",
                ativo=True
            ),
            
            # Medicamentos para febre
            Medicamento(
                nome_comercial="Tylenol",
                nome_generico="Paracetamol",
                descricao="Analgésico e antipirético",
                indicacao="Febre, dor, antipirético, analgésico, cefaleia",
                contraindicacao="Hepatite grave, insuficiência hepática",
                tipo="farmacologico",
                ativo=True
            ),
            Medicamento(
                nome_comercial="Advil",
                nome_generico="Ibuprofeno",
                descricao="Anti-inflamatório, analgésico e antipirético",
                indicacao="Febre, dor, inflamação, antipirético, anti-inflamatório",
                contraindicacao="Úlcera péptica, insuficiência cardíaca grave",
                tipo="farmacologico",
                ativo=True
            ),
            Medicamento(
                nome_comercial="Novalgina",
                nome_generico="Dipirona",
                descricao="Analgésico e antipirético",
                indicacao="Febre, dor, antipirético, analgésico, cefaleia",
                contraindicacao="Anemia aplástica, agranulocitose",
                tipo="farmacologico",
                ativo=True
            ),
            Medicamento(
                nome_comercial="Aspirina",
                nome_generico="Ácido Acetilsalicílico",
                descricao="Anti-inflamatório, analgésico e antipirético",
                indicacao="Febre, dor, inflamação, antipirético, anti-inflamatório",
                contraindicacao="Úlcera péptica, hemorragia, crianças com varicela",
                tipo="farmacologico",
                ativo=True
            ),
            
            # Medicamentos para dor de cabeça
            Medicamento(
                nome_comercial="Dorflex",
                nome_generico="Dipirona + Orfenadrina",
                descricao="Analgésico e relaxante muscular",
                indicacao="Dor de cabeça, dor muscular, analgésico, relaxante muscular",
                contraindicacao="Anemia aplástica, glaucoma, miastenia gravis",
                tipo="farmacologico",
                ativo=True
            ),
            Medicamento(
                nome_comercial="Voltaren",
                nome_generico="Diclofenaco",
                descricao="Anti-inflamatório",
                indicacao="Dor de cabeça, dor, inflamação, anti-inflamatório",
                contraindicacao="Úlcera péptica, insuficiência cardíaca grave",
                tipo="farmacologico",
                ativo=True
            ),
            
            # Medicamentos para diarreia
            Medicamento(
                nome_comercial="Imodium",
                nome_generico="Loperamida",
                descricao="Antidiarreico",
                indicacao="Diarreia aguda, antidiarreico, cólicas intestinais",
                contraindicacao="Diarreia com sangue, febre alta, crianças menores de 2 anos",
                tipo="farmacologico",
                ativo=True
            ),
            Medicamento(
                nome_comercial="Floratil",
                nome_generico="Saccharomyces boulardii",
                descricao="Probiótico",
                indicacao="Diarreia, probiótico, restauração da flora intestinal",
                contraindicacao="Hipersensibilidade ao produto",
                tipo="farmacologico",
                ativo=True
            ),
            Medicamento(
                nome_comercial="Smecta",
                nome_generico="Diosmectita",
                descricao="Antidiarreico e protetor gástrico",
                indicacao="Diarreia, cólicas, protetor gástrico",
                contraindicacao="Hipersensibilidade à diosmectita",
                tipo="farmacologico",
                ativo=True
            ),
            
            # Medicamentos para dor de garganta
            Medicamento(
                nome_comercial="Strepsils",
                nome_generico="Benzocaína + Amilmetacresol",
                descricao="Analgésico tópico",
                indicacao="Dor de garganta, analgésico tópico, anestésico local",
                contraindicacao="Hipersensibilidade aos componentes",
                tipo="farmacologico",
                ativo=True
            ),
            Medicamento(
                nome_comercial="Cepacol",
                nome_generico="Benzocaína + Cetylpiridinium",
                descricao="Analgésico tópico e antisséptico",
                indicacao="Dor de garganta, analgésico tópico, antisséptico",
                contraindicacao="Hipersensibilidade aos componentes",
                tipo="farmacologico",
                ativo=True
            ),
            
            # Medicamentos para azia
            Medicamento(
                nome_comercial="Pepsamar",
                nome_generico="Hidróxido de Alumínio + Magnésio",
                descricao="Antiácido",
                indicacao="Azia, queimação, antiácido, refluxo gastroesofágico",
                contraindicacao="Insuficiência renal grave",
                tipo="farmacologico",
                ativo=True
            ),
            Medicamento(
                nome_comercial="Omeprazol",
                nome_generico="Omeprazol",
                descricao="Inibidor de bomba de prótons",
                indicacao="Azia, refluxo gastroesofágico, úlcera péptica",
                contraindicacao="Hipersensibilidade ao omeprazol",
                tipo="farmacologico",
                ativo=True
            ),
            
            # Medicamentos para constipação
            Medicamento(
                nome_comercial="Lactulona",
                nome_generico="Lactulose",
                descricao="Laxante",
                indicacao="Constipação, laxante, prisão de ventre",
                contraindicacao="Obstrução intestinal, galactosemia",
                tipo="farmacologico",
                ativo=True
            ),
            Medicamento(
                nome_comercial="Bisacodil",
                nome_generico="Bisacodil",
                descricao="Laxante estimulante",
                indicacao="Constipação, laxante estimulante, prisão de ventre",
                contraindicacao="Obstrução intestinal, apendicite",
                tipo="farmacologico",
                ativo=True
            ),
            
            # Medicamentos para hemorroidas
            Medicamento(
                nome_comercial="Proctyl",
                nome_generico="Hidrocortisona + Lidocaína",
                descricao="Anti-inflamatório tópico",
                indicacao="Hemorroidas, anti-inflamatório tópico, anestésico local",
                contraindicacao="Hipersensibilidade aos componentes",
                tipo="farmacologico",
                ativo=True
            ),
            Medicamento(
                nome_comercial="Anusol",
                nome_generico="Óxido de Zinco + Bálsamo",
                descricao="Protetor e cicatrizante",
                indicacao="Hemorroidas, fissuras, protetor, cicatrizante",
                contraindicacao="Hipersensibilidade aos componentes",
                tipo="farmacologico",
                ativo=True
            ),
            
            # Medicamentos para dor lombar
            Medicamento(
                nome_comercial="Ciclobenzaprina",
                nome_generico="Ciclobenzaprina",
                descricao="Relaxante muscular",
                indicacao="Dor lombar, relaxante muscular, espasmos musculares",
                contraindicacao="Glaucoma, miastenia gravis, arritmias cardíacas",
                tipo="farmacologico",
                ativo=True
            ),
            Medicamento(
                nome_comercial="Tramadol",
                nome_generico="Tramadol",
                descricao="Analgésico opioide",
                indicacao="Dor lombar intensa, analgésico opioide, dor crônica",
                contraindicacao="Epilepsia, depressão respiratória, gravidez",
                tipo="farmacologico",
                ativo=True
            ),
            
            # Medicamentos para congestão nasal
            Medicamento(
                nome_comercial="Sorine",
                nome_generico="Cloridrato de Naftazolina",
                descricao="Descongestionante nasal",
                indicacao="Congestão nasal, descongestionante, rinite",
                contraindicacao="Hipersensibilidade à naftazolina",
                tipo="farmacologico",
                ativo=True
            ),
            Medicamento(
                nome_comercial="Allegra",
                nome_generico="Fexofenadina",
                descricao="Antihistamínico",
                indicacao="Congestão nasal alérgica, rinite alérgica, antihistamínico",
                contraindicacao="Hipersensibilidade à fexofenadina",
                tipo="farmacologico",
                ativo=True
            ),
            Medicamento(
                nome_comercial="Rinosoro",
                nome_generico="Soro Fisiológico",
                descricao="Lavagem nasal",
                indicacao="Congestão nasal, lavagem nasal, higiene nasal",
                contraindicacao="Hipersensibilidade ao soro fisiológico",
                tipo="farmacologico",
                ativo=True
            )
        ]
        
        # Inserir medicamentos no banco
        for medicamento in medicamentos_teste:
            db.session.add(medicamento)
        
        db.session.commit()
        print(f"✅ {len(medicamentos_teste)} medicamentos inseridos no banco de dados!")

if __name__ == "__main__":
    popular_medicamentos_teste()
