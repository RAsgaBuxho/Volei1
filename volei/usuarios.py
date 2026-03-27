"""
Modulo para gerenciar usuários cadastrados
"""

from db import supabase


def obter_usuario(user_id):
    """Obtém dados do usuário"""
    res = supabase.table("usuarios") \
        .select("*") \
        .eq("id", user_id) \
        .execute()
    
    if res.data:
        return res.data[0]
    return None


def listar_usuarios():
    """Lista todos os usuários cadastrados"""
    res = supabase.table("usuarios") \
        .select("*") \
        .order("nome") \
        .execute()
    
    return res.data


def atualizar_usuario(user_id, dados):
    """Atualiza dados do usuário (nome, telefone, etc)"""
    return supabase.table("usuarios") \
        .update(dados) \
        .eq("id", user_id) \
        .execute()


def obter_total_usuarios():
    """Retorna o total de usuários cadastrados"""
    res = supabase.table("usuarios") \
        .select("id", count="exact") \
        .execute()
    
    return len(res.data)
