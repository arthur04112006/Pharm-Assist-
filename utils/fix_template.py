#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrigir o botão Voltar no template admin_usuarios.html
"""

# Ler o arquivo template
with open('templates/admin_usuarios.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Substituir o botão Voltar para ir para index ao invés de admin
content = content.replace(
    'href="{{ url_for(\'admin\') }}"',
    'href="{{ url_for(\'index\') }}"'
)

# Salvar o arquivo corrigido
with open('templates/admin_usuarios.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Botão Voltar corrigido no admin_usuarios.html!")

