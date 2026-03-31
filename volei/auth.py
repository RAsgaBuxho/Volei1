from db import supabase
import time
import streamlit as st

def login(email, senha):
    """
    Faz login do usuário usando email e senha
    Retorna o objeto user se bem-sucedido, None caso contrário
    """
    try:
        if not email or not senha:
            st.error("❌ Email e senha são obrigatórios!")
            return None
        
        print(f"📝 Tentando login para: {email}")
        
        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": senha
        })

        if res and res.user:
            print(f"✅ Login bem-sucedido para: {email}")
            return res.user
        else:
            print(f"⚠️  Resposta vazia ao fazer login para: {email}")
            st.error("❌ Resposta inválida do servidor")
            return None
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ ERRO NO LOGIN: {error_msg}")
        
        # Tentar extrair mais detalhes do erro
        if "invalid login credentials" in error_msg.lower():
            st.error("❌ Email ou senha incorretos")
        elif "email not confirmed" in error_msg.lower():
            st.error("❌ Email não foi confirmado. Verifique seu email")
        elif "auth" in error_msg.lower() or "redacted" in error_msg.lower():
            st.error("❌ Erro de autenticação. Verifique suas credenciais")
            st.info("💡 Se você criou a conta agora, aguarde alguns segundos e tente novamente")
        else:
            st.error(f"❌ Erro: {error_msg[:100]}")
        
        return None

def signup(email, senha):
    """
    Cria uma nova conta de usuário
    """
    try:
        if not email or not senha:
            st.error("❌ Email e senha são obrigatórios!")
            return False
        
        if len(senha) < 6:
            st.error("❌ Senha deve ter pelo menos 6 caracteres")
            return False
            
        print(f"📝 Tentando criar conta para: {email}")
        
        res = supabase.auth.sign_up({
            "email": email,
            "password": senha,
            "options": {
                "data": {
                    "nome": email.split('@')[0]  # Nome padrão = parte antes do @
                }
            }
        })
        
        if res and res.user:
            print(f"✅ Conta criada com sucesso para: {email}")
            
            # Aguardar um pouco para o trigger inserir em usuarios
            print("⏳ Processando dados (aguarde 2 segundos)...")
            time.sleep(2)
            
            # Verificar se foi inserido na tabela usuarios
            try:
                user_check = supabase.table("usuarios").select("*").eq("id", res.user.id).execute()
                if user_check.data and len(user_check.data) > 0:
                    print(f"✅ Registro de usuário criado no banco: {email}")
                else:
                    print(f"⚠️  Usuário criado mas registro em 'usuarios' ainda não foi criado")
            except Exception as check_error:
                print(f"⚠️  Não foi possível verificar registro em usuarios: {check_error}")
            
            return True
        else:
            print(f"⚠️  Resposta vazia ao criar conta")
            st.error("❌ Não foi possível criar a conta")
            return False
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ ERRO NO SIGNUP: {error_msg}")
        
        # Tratamento de erros comuns
        if "user already exists" in error_msg.lower():
            st.error("❌ Este email já está cadastrado")
        elif "invalid email" in error_msg.lower():
            st.error("❌ Email inválido")
        elif "password" in error_msg.lower():
            st.error("❌ Requisitos de senha não atendidos")
        else:
            st.error(f"❌ Erro ao criar conta: {error_msg[:100]}")
        
        return False

def logout():
    """
    Faz logout do usuário
    """
    try:
        supabase.auth.sign_out()
        print("✅ Logout realizado com sucesso")
    except Exception as e:
        print(f"⚠️  Erro ao fazer logout: {e}")