from db import supabase
from datetime import datetime, timedelta
import pytz

tz_br = pytz.timezone('America/Sao_Paulo')


def registrar_check_in_confirmado(user_id, nome, email, dia):
    """
    Registra quando um usuário faz check-in confirmado
    Atualiza o score do usuário
    """
    try:
        # Verifica se usuário já tem score registrado
        res = supabase.table("usuario_score") \
            .select("*") \
            .eq("user_id", user_id) \
            .execute()
        
        if res.data:
            # Atualiza contador de check-ins e data da última atividade
            usuario = res.data[0]
            novo_score = usuario.get("check_ins_confirmados", 0) + 1
            
            supabase.table("usuario_score") \
                .update({
                    "check_ins_confirmados": novo_score,
                    "ultima_atividade": datetime.now(tz_br).isoformat(),
                    "updated_at": datetime.now(tz_br).isoformat()
                }) \
                .eq("user_id", user_id) \
                .execute()
        else:
            # Cria novo registro de score
            supabase.table("usuario_score").insert({
                "user_id": user_id,
                "nome": nome,
                "email": email,
                "check_ins_confirmados": 1,
                "entradas_fila": 0,
                "ultima_atividade": datetime.now(tz_br).isoformat()
            }).execute()
        
        return {"success": True}
    except Exception as e:
        print(f"Erro ao registrar check-in: {e}")
        return {"success": False, "error": str(e)}


def registrar_entrada_fila(user_id, nome, email):
    """
    Registra quando um usuário entra na fila
    Incrementa contador de entradas
    """
    try:
        res = supabase.table("usuario_score") \
            .select("*") \
            .eq("user_id", user_id) \
            .execute()
        
        if res.data:
            usuario = res.data[0]
            nova_entrada = usuario.get("entradas_fila", 0) + 1
            
            supabase.table("usuario_score") \
                .update({"entradas_fila": nova_entrada}) \
                .eq("user_id", user_id) \
                .execute()
        else:
            supabase.table("usuario_score").insert({
                "user_id": user_id,
                "nome": nome,
                "email": email,
                "check_ins_confirmados": 0,
                "entradas_fila": 1
            }).execute()
        
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def calcular_score(usuario):
    """
    Calcula score baseado em:
    - Check-ins confirmados: 100 pontos cada
    - Taxa de presença: 50 pontos por 10% de presença
    - Atividade recente: 25 pontos se jogou no último mês
    """
    try:
        check_ins = usuario.get("check_ins_confirmados", 0)
        entradas = usuario.get("entradas_fila", 0)
        
        score = 0
        
        # Pontos por check-ins confirmados
        score += check_ins * 100
        
        # Pontos por taxa de presença
        if entradas > 0:
            taxa_presenca = (check_ins / entradas) * 100
            pontos_taxa = (taxa_presenca / 10) * 5  # 5 pontos por 10% de presença
            score += int(pontos_taxa)
        
        # Pontos por atividade recente
        if "ultima_atividade" in usuario:
            data_ult = datetime.fromisoformat(usuario["ultima_atividade"].replace('Z', '+00:00'))
            dias_atras = (datetime.now(tz_br) - data_ult).days
            
            if dias_atras <= 30:  # Jogou no último mês
                score += 25
            elif dias_atras <= 7:  # Jogou na última semana
                score += 50
        
        return max(score, 0)
    except:
        return 0


def listar_ranking(limite=10):
    """
    Lista ranking dos usuários com melhor score
    Apenas últimos 30 dias
    """
    try:
        res = supabase.table("usuario_score") \
            .select("*") \
            .order("check_ins_confirmados", desc=True) \
            .limit(limite) \
            .execute()
        
        ranking = []
        for i, usuario in enumerate(res.data, 1):
            score = calcular_score(usuario)
            taxa_presenca = 0
            
            if usuario.get("entradas_fila", 0) > 0:
                taxa_presenca = (usuario.get("check_ins_confirmados", 0) / usuario.get("entradas_fila", 0)) * 100
            
            ranking.append({
                "posicao": i,
                "nome": usuario.get("nome", "Desconhecido"),
                "check_ins": usuario.get("check_ins_confirmados", 0),
                "entradas": usuario.get("entradas_fila", 0),
                "taxa_presenca": taxa_presenca,
                "score": score
            })
        
        return ranking
    except Exception as e:
        print(f"Erro ao listar ranking: {e}")
        return []


def limpar_scores_inativos(dias=90):
    """
    Remove usuários que não aparecem há mais de X dias
    Economiza espaço no banco
    """
    try:
        res = supabase.table("usuario_score").select("*").execute()
        
        if not res.data:
            return {"success": True, "deletados": 0}
        
        data_limite = datetime.now(tz_br) - timedelta(days=dias)
        deletados = 0
        
        for usuario in res.data:
            try:
                if "ultima_atividade" in usuario:
                    data_ult = datetime.fromisoformat(usuario["ultima_atividade"].replace('Z', '+00:00'))
                    
                    if data_ult < data_limite:
                        supabase.table("usuario_score") \
                            .delete() \
                            .eq("id", usuario["id"]) \
                            .execute()
                        deletados += 1
            except:
                pass
        
        return {"success": True, "deletados": deletados}
    except Exception as e:
        return {"success": False, "error": str(e)}
