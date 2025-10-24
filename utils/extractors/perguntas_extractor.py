#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilitário para extrair perguntas oficiais dos módulos em motor_de_perguntas.

Regras:
- Não altera textos/ordem/quantidade das perguntas.
- Usa AST para localizar, em run_cli(), as chamadas a ask_bool(...) e input(...).
- Inferência de tipo: ask_bool → boolean; int(input(...))/float(input(...)) → number; input(...) → string.
"""

import ast
import os
from typing import List, Dict, Optional, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MOTOR_DIR = os.path.join(BASE_DIR, 'services', 'triagem', 'motor_de_perguntas')


def _read_module_source(slug: str) -> str:
    path = os.path.join(MOTOR_DIR, f'{slug}.py')
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def _humanize_slug(slug: str) -> str:
    return slug.replace('_', ' ').strip().title()


def list_modules() -> List[Dict[str, str]]:
    """Lista módulos disponíveis no diretório motor_de_perguntas (exclui subpastas auxiliares)."""
    items: List[Dict[str, str]] = []
    for name in sorted(os.listdir(MOTOR_DIR)):
        if not name.endswith('.py'):
            continue
        if name == '__init__.py':
            continue
        # Ignorar subpastas auxiliares já que aqui só listamos arquivos .py
        slug = name[:-3]
        items.append({
            'slug': slug,
            'nome': _humanize_slug(slug)
        })
    return items


def get_patient_profile_from_cadastro(paciente_data: dict) -> dict:
    """Converte dados do cadastro do paciente para o formato usado pelos motores de perguntas."""
    profile = {
        'age_years': paciente_data.get('idade', 0),
        'age_months': paciente_data.get('idade', 0) * 12,  # conversão aproximada
        'is_pregnant_or_lactating': False,  # será inferido se necessário
        'is_frail_elderly': paciente_data.get('idade', 0) >= 75,
        'is_immunocompromised': False,  # não está no cadastro atual
        'sexo': paciente_data.get('sexo', ''),
        'peso': paciente_data.get('peso'),
        'altura': paciente_data.get('altura')
    }
    
    # Inferir gestação/lactação baseado no sexo e idade
    if paciente_data.get('sexo') == 'F' and 15 <= paciente_data.get('idade', 0) <= 50:
        # Para mulheres em idade fértil, assumir que não está grávida por padrão
        # O sistema pode perguntar especificamente se necessário
        profile['is_pregnant_or_lactating'] = False
    
    return profile


def _is_call_to(node: ast.AST, func_name: str) -> bool:
    return isinstance(node, ast.Call) and (
        (isinstance(node.func, ast.Name) and node.func.id == func_name) or
        (isinstance(node.func, ast.Attribute) and node.func.attr == func_name)
    )


def _find_run_cli_function(tree: ast.AST) -> Optional[ast.FunctionDef]:
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and n.name == 'run_cli':
            return n
    return None


def _extract_literal_from_call(call_node: ast.Call) -> Optional[str]:
    if not call_node.args:
        return None
    arg0 = call_node.args[0]
    if isinstance(arg0, ast.Constant) and isinstance(arg0.value, str):
        return arg0.value
    return None


def _find_calls_in_expr(expr: ast.AST) -> List[ast.Call]:
    """Coleta chamadas a ask_bool e input em uma expressão, preservando ordem de visita."""
    calls: List[ast.Call] = []

    class Visitor(ast.NodeVisitor):
        def visit_Call(self, node: ast.Call):
            # Coleta chamadas a ask_bool e input, mesmo se aninhadas (ex.: int(input(...)))
            if _is_call_to(node, 'ask_bool') or _is_call_to(node, 'input'):
                calls.append(node)
            # Continuar descendo para pegar input dentro de int(...)
            self.generic_visit(node)

    Visitor().visit(expr)
    return calls


def _infer_type_from_call(call_node: ast.Call) -> str:
    """Inferir tipo da pergunta com base no contexto próximo: boolean|number|string."""
    # ask_bool → boolean diretamente
    if _is_call_to(call_node, 'ask_bool'):
        return 'boolean'

    # input(...) → inspecionar se ancestral imediato é int(...) ou float(...)
    parent = getattr(call_node, '_parent', None)
    if isinstance(parent, ast.Call) and isinstance(parent.func, ast.Name):
        if parent.func.id in ('int', 'float'):
            return 'number'

    # Se a cadeia for algo como int(input(...).strip())
    # O pai direto pode ser Attribute (.strip), e o avô ser Call(int(...))
    if isinstance(parent, ast.Attribute):
        grand = getattr(parent, '_parent', None)
        if isinstance(grand, ast.Call) and isinstance(grand.func, ast.Name) and grand.func.id in ('int', 'float'):
            return 'number'

    return 'string'


def _attach_parents(node: ast.AST):
    for child in ast.iter_child_nodes(node):
        setattr(child, '_parent', node)
        _attach_parents(child)


def _is_unnecessary_question(texto: str) -> bool:
    """Verifica se a pergunta é desnecessária pois o dado já está no cadastro do paciente."""
    texto_lower = texto.lower()
    
    # Perguntas sobre idade
    if any(phrase in texto_lower for phrase in [
        'idade (anos)', 'idade em anos', 'idade em meses', 'anos', 'meses'
    ]):
        return True
    
    # Perguntas sobre gestação/lactação (pode ser inferido do sexo e idade)
    if any(phrase in texto_lower for phrase in [
        'gestante', 'lactante', 'gestação', 'lactação', 'puérpera'
    ]):
        return True
    
    # Perguntas sobre idoso frágil (pode ser inferido da idade ≥75)
    if any(phrase in texto_lower for phrase in [
        'idoso frágil', 'idoso', 'dependência', 'alta vulnerabilidade'
    ]):
        return True
    
    return False


def _get_question_weight(slug: str, question_text: str, order: int) -> Dict[str, object]:
    """Obtém informações de peso para uma pergunta específica"""
    from utils.scoring.triagem_scoring import scoring_system
    
    question_id = f"{slug}_{order}"
    
    # Buscar peso da pergunta no sistema de pontuação
    if question_id in scoring_system.question_weights:
        weight_info = scoring_system.question_weights[question_id]
        return {
            'peso': weight_info.weight,
            'categoria': weight_info.category,
            'critica': weight_info.critical,
            'indication': 'farmacologico' if weight_info.weight > 1.5 else 'nao_farmacologico'
        }
    
    # Valores padrão baseados no tipo de pergunta
    if 'duração' in question_text.lower() or 'dias' in question_text.lower():
        return {'peso': 2.0, 'categoria': 'duracao', 'critica': False, 'indication': 'farmacologico'}
    elif 'febre' in question_text.lower() or 'sangue' in question_text.lower() or 'dor' in question_text.lower():
        return {'peso': 2.5, 'categoria': 'gravidade', 'critica': True, 'indication': 'farmacologico'}
    elif 'histórico' in question_text.lower() or 'uso' in question_text.lower():
        return {'peso': 1.5, 'categoria': 'historico', 'critica': False, 'indication': 'farmacologico'}
    else:
        return {'peso': 1.0, 'categoria': 'sintoma', 'critica': False, 'indication': 'nao_farmacologico'}


def extract_questions_for_module(slug: str, filter_unnecessary: bool = True) -> List[Dict[str, object]]:
    """Extrai perguntas em ordem a partir de run_cli() de um módulo."""
    source = _read_module_source(slug)
    tree = ast.parse(source)
    _attach_parents(tree)
    run_cli_fn = _find_run_cli_function(tree)
    if not run_cli_fn:
        return []

    questions: List[Dict[str, object]] = []

    # Percorrer corpo em ordem e coletar chamadas relevantes
    for stmt in run_cli_fn.body:
        # Ex.: atribuicoes: var = ask_bool("...") ou var = int(input("..."))
        if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.AST):
            calls = _find_calls_in_expr(stmt.value)
        # Ex.: chamada isolada (raro): ask_bool("...")
        elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.AST):
            calls = _find_calls_in_expr(stmt.value)
        else:
            calls = []

        for call in calls:
            if not (_is_call_to(call, 'ask_bool') or _is_call_to(call, 'input')):
                continue
            texto = _extract_literal_from_call(call)
            if not texto:
                continue
            
            # Filtrar perguntas desnecessárias se solicitado
            if filter_unnecessary and _is_unnecessary_question(texto):
                continue
                
            qtype = _infer_type_from_call(call)
            order = len(questions) + 1
            
            # Obter informações de peso
            weight_info = _get_question_weight(slug, texto, order)
            
            questions.append({
                'id': f"{slug}_{order}",
                'modulo': slug,
                'ordem': order,
                'texto': texto,
                'tipo': qtype,
                'required': True,
                'placeholder': None,
                'opcoes': None,
                'grupo': 'etapa',
                'peso': weight_info['peso'],
                'categoria': weight_info['categoria'],
                'critica': weight_info['critica'],
                'indication': weight_info['indication']
            })

    return questions


if __name__ == '__main__':
    # Execução simples para depuração manual
    mods = list_modules()
    print(f"Módulos: {[m['slug'] for m in mods]}")
    for m in mods:
        qs = extract_questions_for_module(m['slug'])
        print(m['slug'], len(qs))



