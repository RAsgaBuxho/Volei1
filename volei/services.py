from db import supabase

def adicionar_familia(user_id, nome, idade, responsavel, termo):
    return supabase.table("family").insert({
        "user_id": user_id,
        "nome": nome,
        "idade": idade,
        "responsavel_nome": responsavel,
        "termo_aceito": termo
    }).execute()

def listar_familia(user_id):
    return supabase.table("family") \
        .select("*") \
        .eq("user_id", user_id) \
        .execute()

def tem_familia(user_id):
    res = supabase.table("family") \
        .select("*") \
        .eq("user_id", user_id) \
        .execute()

    return len(res.data) > 0


# =========================
# CONVIDADOS
# =========================

def adicionar_convidado(nome, dia):
    """Adiciona um convidado (pessoa não cadastrada) à lista de espera"""
    return supabase.table("convidados").insert({
        "nome": nome,
        "dia": dia,
        "adicionado_fila": False
    }).execute()


def listar_convidados(dia):
    """Lista todos os convidados para um dia específico que ainda não foram adicionados à fila"""
    res = supabase.table("convidados") \
        .select("*") \
        .eq("dia", dia) \
        .eq("adicionado_fila", False) \
        .order("created_at") \
        .execute()
    
    return res.data


def remover_convidado(convidado_id):
    """Remove um convidado"""
    return supabase.table("convidados") \
        .delete() \
        .eq("id", convidado_id) \
        .execute()


def marcar_convidado_adicionado(convidado_id):
    """Marca um convidado como adicionado à fila"""
    return supabase.table("convidados") \
        .update({"adicionado_fila": True}) \
        .eq("id", convidado_id) \
        .execute()


def preencher_fila_com_convidados(dia):
    """
    Adiciona convidados automaticamente à fila quando há vagas disponíveis
    Usa user_id = null para diferenciar convidados de usuários cadastrados
    """
    from fila import entrar_fila, listar_fila
    
    limite = 24 if dia == "terça" else 18
    fila_atual = listar_fila(dia)
    vagas = limite - len(fila_atual)
    
    if vagas <= 0:
        return {"success": False, "message": "Nenhuma vaga disponível"}
    
    convidados = listar_convidados(dia)
    adicionados = 0
    
    for convidado in convidados[:vagas]:
        try:
            # Adiciona convidado à fila com user_id = None (ou uuid fixo para convidados)
            supabase.table("fila").insert({
                "user_id": None,
                "nome": convidado['nome'],
                "dia": dia,
                "is_convidado": True
            }).execute()
            
            marcar_convidado_adicionado(convidado['id'])
            adicionados += 1
        except Exception as e:
            print(f"Erro ao adicionar convidado {convidado['nome']}: {e}")
    
    return {"success": True, "adicionados": adicionados, "vagas_preenchidas": adicionados}