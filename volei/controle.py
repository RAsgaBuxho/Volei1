from db import supabase

def get_status(dia):
    """Retorna o status da lista (True=aberta, False=fechada, None=não existe)"""
    res = supabase.table("controle_lista") \
        .select("*") \
        .eq("dia", dia) \
        .execute()

    if not res.data:
        return None  # Lista não existe - precisa ser criada por admin
    
    return res.data[0]["aberta"]


def criar_lista(dia):
    """Admin cria uma nova lista"""
    return supabase.table("controle_lista").insert({
        "dia": dia,
        "aberta": True
    }).execute()


def abrir_lista(dia):
    return supabase.table("controle_lista") \
        .update({"aberta": True}) \
        .eq("dia", dia) \
        .execute()


def fechar_lista(dia):
    return supabase.table("controle_lista") \
        .update({"aberta": False}) \
        .eq("dia", dia) \
        .execute()