from db import supabase
from authadmin import is_admin
from datetime import datetime, timedelta


def entrar_fila(user_id, nome, dia, levantador=False):
    # Limite por dia
    limite = 24 if dia == "terça" else 18
    
    # Limite de levantadores
    limite_levantadores = 4 if dia == "terça" else 3

    res = supabase.table("fila") \
        .select("*") \
        .eq("dia", dia) \
        .execute()

    if len(res.data) >= limite and not is_admin(user_id):
        return {"error": "Lista cheia"}
    
    # Se é levantador, valida limite de levantadores
    if levantador:
        levantadores_atuais = len([p for p in res.data if p.get("levantador", False)])
        if levantadores_atuais >= limite_levantadores and not is_admin(user_id):
            return {"error": f"Limite de {limite_levantadores} levantadores atingido para {dia}"}
    
    # Validar limite de pessoas por usuário (2 para usuários normais, ilimitado para admins)
    if not is_admin(user_id):
        res_user = supabase.table("fila") \
            .select("*") \
            .eq("user_id", user_id) \
            .eq("dia", dia) \
            .execute()
        
        if len(res_user.data) >= 2:
            return {"error": "Você atingiu o limite de 2 pessoas por dia (admins podem adicionar mais)"}

    return supabase.table("fila").insert({
        "user_id": user_id,
        "nome": nome,
        "dia": dia,
        "levantador": levantador
    }).execute()


def listar_fila(dia):
    res = supabase.table("fila")\
        .select("*")\
        .eq("dia", dia)\
        .execute()

    return res.data

def sair_fila(user_id, dia):
    return supabase.table("fila") \
        .delete() \
        .eq("user_id", user_id) \
        .eq("dia", dia) \
        .execute()

def limpar_fila(dia):
    return supabase.table("fila") \
        .delete() \
        .eq("dia", dia) \
        .execute()


def limpar_fila_antigas():
    """
    Limpa filas muito antigas (mais de 3 dias)
    para economizar espaço no banco de dados
    """
    try:
        # Busca todas as filas
        res = supabase.table("fila").select("*").execute()
        
        if not res.data:
            return {"success": True, "deletados": 0}
        
        data_limite = datetime.now() - timedelta(days=3)
        deletados = 0
        
        for registro in res.data:
            try:
                # Converte created_at para datetime
                if hasattr(registro, 'created_at'):
                    data_criacao = datetime.fromisoformat(registro['created_at'].replace('Z', '+00:00'))
                    
                    # Se tem mais de 3 dias, deleta
                    if data_criacao < data_limite:
                        supabase.table("fila").delete().eq("id", registro['id']).execute()
                        deletados += 1
            except:
                pass
        
        return {"success": True, "deletados": deletados}
    except Exception as e:
        return {"success": False, "error": str(e)}


def contar_fila(dia):
    """Retorna a quantidade de pessoas na fila"""
    res = supabase.table("fila")\
        .select("*")\
        .eq("dia", dia)\
        .execute()
    
    return len(res.data)
def limpar_fila(dia):
    return supabase.table("fila") \
        .delete() \
        .eq("dia", dia) \
        .execute()