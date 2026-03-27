import random
from db import supabase


def gerar_times(dia):
    # busca jogadores daquele dia
    res = supabase.table("fila") \
        .select("*") \
        .eq("dia", dia) \
        .order("created_at") \
        .execute()

    jogadores = [p["nome"] for p in res.data]

    # validações
    if not jogadores:
        return {"error": "Nenhum jogador na fila"}

    if len(jogadores) < 6:
        return {"error": "Poucos jogadores para montar um time"}

    # embaralha
    random.shuffle(jogadores)

    # cria times de 6
    times = []
    for i in range(0, len(jogadores), 6):
        grupo = jogadores[i:i+6]

        if len(grupo) == 6:
            times.append(grupo)

    if not times:
        return {"error": "Não foi possível formar times completos"}

    return times