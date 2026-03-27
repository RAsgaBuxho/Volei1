from db import supabase
from datetime import datetime
import pytz

# Timezone de Brasília
tz_br = pytz.timezone('America/Sao_Paulo')

def fazer_check_in(user_id, latitude, longitude, dia):
    """
    Registra o check-in do usuário com localização e hora
    """
    try:
        hora_chegada = datetime.now(tz_br).isoformat()
        
        # Verifica se já fez check-in hoje
        res_existe = supabase.table("check_ins") \
            .select("*") \
            .eq("user_id", user_id) \
            .eq("dia", dia) \
            .execute()
        
        if res_existe.data:
            # Atualiza check-in existente
            return supabase.table("check_ins") \
                .update({
                    "latitude": latitude,
                    "longitude": longitude,
                    "hora_chegada": hora_chegada,
                    "updated_at": hora_chegada
                }) \
                .eq("user_id", user_id) \
                .eq("dia", dia) \
                .execute()
        else:
            # Cria novo check-in
            return supabase.table("check_ins").insert({
                "user_id": user_id,
                "latitude": latitude,
                "longitude": longitude,
                "hora_chegada": hora_chegada,
                "dia": dia
            }).execute()
    
    except Exception as e:
        print(f"Erro ao fazer check-in: {e}")
        return {"error": str(e)}


def listar_check_ins(dia):
    """
    Lista todos os check-ins do dia
    """
    try:
        res = supabase.table("check_ins") \
            .select("*") \
            .eq("dia", dia) \
            .order("hora_chegada", desc=False) \
            .execute()
        
        return res.data
    except Exception as e:
        print(f"Erro ao listar check-ins: {e}")
        return []


def get_check_in_usuario(user_id, dia):
    """
    Pega o check-in de um usuário específico para um dia
    """
    try:
        res = supabase.table("check_ins") \
            .select("*") \
            .eq("user_id", user_id) \
            .eq("dia", dia) \
            .execute()
        
        return res.data[0] if res.data else None
    except Exception as e:
        print(f"Erro ao pegar check-in do usuário: {e}")
        return None


def get_check_in_admin(dia):
    """
    Obtém o check-in do admin para usar como referência da quadra
    O admin é identificado pelo email 'admin@email.com'
    """
    try:
        from fila import listar_fila
        
        # Tenta obter informação do admin de uma tabela de usuários se existir
        # Alternativa: busca no histórico o primeiro check-in (geralmente é o admin)
        res = supabase.table("check_ins") \
            .select("*") \
            .eq("dia", dia) \
            .order("hora_chegada", desc=False) \
            .execute()
        
        if not res.data:
            return None
        
        # Retorna o primeiro check-in do dia (usualmente o admin)
        # ou pode ser customizado para buscar especificamente o admin
        primeiro_check_in = res.data[0]
        
        return primeiro_check_in
    
    except Exception as e:
        print(f"Erro ao obter check-in do admin: {e}")
        return None


def validar_localizacao_quadra(latitude, longitude, dia, raio_metros=50):
    """
    Valida se o usuário está próximo ao check-in do admin
    Usa a localização do admin como referência da quadra
    raio_metros: raio de tolerância em metros (padrão 50m)
    
    Args:
        latitude: Latitude do check-in do usuário
        longitude: Longitude do check-in do usuário
        dia: Dia do jogo (para buscar check-in do admin)
        raio_metros: Tolerância em metros
    
    Returns:
        (validar: bool, distancia_metros: float)
    """
    # Obtém localização do admin (referência da quadra)
    check_in_admin = get_check_in_admin(dia)
    
    if not check_in_admin:
        print("⚠️ Admin ainda não fez check-in neste dia")
        return False, None
    
    lat_quadra = check_in_admin["latitude"]
    lon_quadra = check_in_admin["longitude"]
    
    # Calcula distância em metros
    distancia_km = calcular_distancia(latitude, longitude, lat_quadra, lon_quadra)
    distancia_metros = distancia_km * 1000
    
    # Valida se está dentro do raio
    esta_valido = distancia_metros <= raio_metros
    
    return esta_valido, distancia_metros


def listar_check_ins_validados(dia, raio_metros=50):
    """
    Lista check-ins do dia validando proximidade à quadra (check-in do admin)
    Retorna check-ins com status de validação
    """
    check_ins = listar_check_ins(dia)
    check_ins_validados = []
    
    for check_in in check_ins:
        validar, distancia = validar_localizacao_quadra(
            check_in["latitude"],
            check_in["longitude"],
            dia,
            raio_metros
        )
        
        check_in_com_status = {
            **check_in,
            "validado": validar,
            "distancia_metros": distancia,
            "status": "✅ Confirmado" if validar else "❌ Fora da área"
        }
        check_ins_validados.append(check_in_com_status)
    
    return check_ins_validados


def listar_presenca(dia):
    """
    Lista presença formatada para o dia
    """
    check_ins = listar_check_ins(dia)
    
    if not check_ins:
        return []
    
    presenca = []
    for check_in in check_ins:
        presenca.append({
            "user_id": check_in["user_id"],
            "hora": check_in["hora_chegada"],
            "latitude": check_in["latitude"],
            "longitude": check_in["longitude"]
        })
    
    return presenca


def limpar_check_ins_antigos(dias=7):
    """
    Limpa check-ins com mais de X dias
    Default: 7 dias
    Economiza espaço no banco de dados
    """
    try:
        from datetime import timedelta
        
        # Busca todos os check-ins
        res = supabase.table("check_ins").select("*").execute()
        
        if not res.data:
            return {"success": True, "deletados": 0}
        
        data_limite = datetime.now(tz_br) - timedelta(days=dias)
        deletados = 0
        
        for registro in res.data:
            try:
                # Converte created_at para datetime
                if 'created_at' in registro:
                    # Remove 'Z' e converte para datetime com timezone
                    data_str = registro['created_at'].replace('Z', '+00:00')
                    data_criacao = datetime.fromisoformat(data_str)
                    
                    # Se tem mais de X dias, deleta
                    if data_criacao < data_limite:
                        supabase.table("check_ins").delete().eq("id", registro['id']).execute()
                        deletados += 1
            except Exception as e:
                print(f"Erro ao processar check-in {registro.get('id')}: {e}")
                pass
        
        return {"success": True, "deletados": deletados}
    except Exception as e:
        return {"success": False, "error": str(e)}
