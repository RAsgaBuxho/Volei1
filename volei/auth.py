from db import supabase

def login(email, senha):
    res = supabase.auth.sign_in_with_password({
        "email": email,
        "password": senha
    })

    if res and res.user:
        return res.user  # 🔥 AQUI A CORREÇÃO
    return None

def signup(email, senha):
    try:
        res = supabase.auth.sign_up({
            "email": email,
            "password": senha
        })
        return res
    except Exception as e:
        print("ERRO SIGNUP:", e)
        return None


def logout():
    try:
        supabase.auth.sign_out()
    except:
        pass