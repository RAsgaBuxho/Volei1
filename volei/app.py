import streamlit as st
import time

from auth import login, signup, logout
from fila import entrar_fila, listar_fila, sair_fila, limpar_fila, limpar_fila_antigas, contar_fila
from times import gerar_times
from frontend import aplicar_estilo, desenhar_quadra, card_jogador, status_lista, botao_check_in, card_check_in, lista_presenca
from checkin import fazer_check_in, listar_check_ins, listar_check_ins_validados, get_check_in_usuario, limpar_check_ins_antigos
from services import adicionar_familia, listar_familia, tem_familia, adicionar_convidado, listar_convidados, preencher_fila_com_convidados
from score import registrar_check_in_confirmado, registrar_entrada_fila, listar_ranking, limpar_scores_inativos, calcular_score
from controle import get_status, criar_lista, fechar_lista
from usuarios import obter_usuario, listar_usuarios, atualizar_usuario, obter_total_usuarios
from authadmin import is_admin

# Importar QR Code com fallback
try:
    from qrcode_checkin import gerar_qrcode_checkin, fazer_checkin_por_qrcode
    QRCODE_DISPONIVEL = True
except ImportError as e:
    print(f"⚠️ Módulo QR Code não disponível: {e}")
    QRCODE_DISPONIVEL = False
    # Criar funções dummy
    def gerar_qrcode_checkin(dia):
        return {"sucesso": False, "erro": "QR Code não configurado"}
    def fazer_checkin_por_qrcode(user_id, token, dia):
        return {"sucesso": False, "erro": "QR Code não configurado"}


# =========================
# CONFIG
# =========================
aplicar_estilo()

# =========================
# SESSION STATE INIT
# =========================
if "checkin_requested" not in st.session_state:
    st.session_state.checkin_requested = False

if "user" not in st.session_state:
    st.session_state.user = None

if "times" not in st.session_state:
    st.session_state.times = None

if "limpeza_feita" not in st.session_state:
    st.session_state.limpeza_feita = False
    
    # Limpeza automática na inicialização (apenas uma vez)
    try:
        limpar_fila_antigas()
        limpar_check_ins_antigos(dias=7)
        limpar_scores_inativos(dias=90)
        st.session_state.limpeza_feita = True
    except:
        pass  # Silencioso se houver erro

if "nome_usuario" not in st.session_state:
    st.session_state.nome_usuario = None


# =========================
# HEADER
# =========================
import os

# Tentar carregar e exibir o escudo
escudo_path = "volei/assets/escudo_vila_linda.png"
aguia_path = "volei/assets/aguia_volei.png"

escudo_existe = os.path.exists(escudo_path)
aguia_existe = os.path.exists(aguia_path)

# Header com imagem
col_header_left, col_header_center, col_header_right = st.columns([1, 2, 1])

if escudo_existe:
    with col_header_left:
        st.image(escudo_path, width=150)

with col_header_center:
    st.markdown("""
    <div style="text-align: center; margin-top: 10px;">
        <h1 style="color: #ffd60a; text-shadow: 0 0 20px rgba(255, 214, 10, 0.4); margin: 0;">
            🏐 ESQUADRÃO DO VÓLEI 🏐
        </h1>
        <p style="color: #00d4aa; font-size: 1.3em; font-weight: bold; margin: 5px 0;">
            VILA LINDA
        </p>
    </div>
    """, unsafe_allow_html=True)

if escudo_existe:
    with col_header_right:
        st.image(escudo_path, width=150)

st.markdown("---")


# =========================
# LOGIN
# =========================
if not st.session_state.user:
    st.markdown("""
    <div style="text-align: center; padding: 40px 0;">
        <div style="font-size: 4em; margin-bottom: 20px;">🏐🔥⚡</div>
        <h2 style="color: #ffd60a; text-shadow: 0 0 20px rgba(255, 214, 10, 0.4);">
            Bem-vindo ao Gerenciador de Vôlei!
        </h2>
        <p style="color: #e39a03; font-size: 1.2em;">Faça login ou crie sua conta para começar</p>
    </div>
    """, unsafe_allow_html=True)
    
    aba = st.radio("Opção", ["🔐 LOGIN", "📝 CADASTRO"], horizontal=True, label_visibility="collapsed")

    email = st.text_input("📧 Email")
    senha = st.text_input("🔑 Senha", type="password")
    
    # Campo de nome só aparece na aba CADASTRO
    nome = ""
    if aba == "📝 CADASTRO":
        nome = st.text_input("👤 Nome Completo")

    if aba == "🔐 LOGIN":
        if st.button("🎯 ENTRAR"):
            user = login(email, senha)

            if user:
                # compat com supabase
                if hasattr(user, "user"):
                    user = user.user

                st.session_state.user = user
                
                # Recuperar nome do usuário do banco
                try:
                    meu_perfil = obter_usuario(user.id)
                    if meu_perfil and meu_perfil.get('nome'):
                        st.session_state.nome_usuario = meu_perfil['nome']
                    else:
                        # Fallback: usar email se nome não existir
                        st.session_state.nome_usuario = getattr(user, "email", "Usuário")
                except:
                    st.session_state.nome_usuario = getattr(user, "email", "Usuário")
                
                st.success("✅ Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("❌ Email ou senha incorretos!")

    else:
        if st.button("✅ CRIAR CONTA"):
            if not nome:
                st.error("❌ Por favor, preencha seu nome completo!")
            else:
                resultado = signup(email, senha, nome)
                if resultado:
                    st.success("🎉 Conta criada com sucesso! Agora faça login!")
                    # Aguardar um pouco e depois fazer rerun para voltar ao login
                    time.sleep(1)
                else:
                    st.error("❌ Falha ao criar a conta. Verifique os dados e tente novamente.")

    st.stop()


# =========================
# USER
# =========================
user = st.session_state.user
email_user = getattr(user, "email", "Sem email")
nome_usuario = st.session_state.nome_usuario or email_user.split('@')[0]  # Fallback para parte antes do @

col_top1, col_top2, col_top3 = st.columns([3, 1, 1])

with col_top1:
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(6, 168, 125, 0.2), rgba(0, 212, 170, 0.1));
        border: 2px solid #00d4aa;
        border-radius: 15px;
        padding: 15px;
        color: white;
        font-weight: 700;
        font-size: 1.1em;
    ">
        ✅ Logado como: <span style="color: #ffd60a;">{nome_usuario}</span>
    </div>
    """, unsafe_allow_html=True)

with col_top3:
    if st.button("🚪 SAIR"):
        logout()
        st.session_state.user = None
        st.rerun()

# Debug: Verificar se usuário é admin (APENAS PARA ADMINS)
is_admin_user = is_admin(user.id) if user else False

if is_admin_user:
    with st.expander("🔍 Debug - Verificar Status Admin"):
        user_id_str = str(user.id) if user else "Sem user"
        st.write(f"**Email:** {email_user}")
        st.write(f"**User ID:** {user_id_str}")
        st.write(f"**É Admin?** {is_admin_user}")
        st.success("✅ Você é um administrador do sistema!")

# ⚠️ Aviso de Segurança (APENAS PARA ADMINS)
if is_admin_user:
    with st.expander("🔒 SEGURANÇA DO BANCO DE DADOS"):
        st.warning("⚠️ **IMPORTANTE**: Seu banco de dados deve estar protegido com Row Level Security (RLS)")
        
        st.markdown("""
        ### 🚨 O que Pode Acontecer SEM Proteção?
        - ❌ Qualquer um na internet pode ver TODOS os dados
        - ❌ Roubar informações pessoais dos usuários
        - ❌ Editar ou deletar dados
        - ❌ Sabotage completa do sistema
        
        ### ✅ Como Proteger (3 passos rápidos)
        
        1. **Abra o arquivo** `SETUP_SEGURANCA_RLS.sql`
        2. **Copie TODO o conteúdo**
        3. **Cole no Supabase → SQL Editor**
        4. **Clique RUN** ▶️
        
        ### ✔️ Verificar se Está Protegido
        
        No Supabase → **Table Editor**:
        - Selecione uma tabela (ex: `fila`)
        - Vá em **Policies**
        - Se ver múltiplas políticas → ✅ Protegido!
        - Se estiver vazio → ❌ NÃO protegido!
        
        ### 📚 Documentação Completa
        
        Leia [GUIA_SEGURANCA.md](GUIA_SEGURANCA.md) para:
        - Explicação detalhada de cada política
        - Matriz de permissões
        - Testes de segurança
        - Melhores práticas
        """)


# =========================
# PERFIL DO USUÁRIO
# =========================
st.markdown("---")

# Adicionar escudo antes do perfil
if escudo_existe:
    col_esc1, col_esc2, col_esc3 = st.columns([1, 1, 1])
    with col_esc2:
        st.image(escudo_path, width=250)

st.subheader("👤 MEU PERFIL 👤")

try:
    meu_perfil = obter_usuario(user.id)
    
    if meu_perfil:
        col_perfil1, col_perfil2 = st.columns([2, 1])
        
        with col_perfil1:
            st.write(f"**Nome:** {meu_perfil['nome']}")
            st.write(f"**Email:** {meu_perfil['email']}")
            if meu_perfil.get('telefone'):
                st.write(f"**Telefone:** {meu_perfil['telefone']}")
        
        with col_perfil2:
            if meu_perfil.get('data_cadastro'):
                st.write(f"**Cadastro:** {meu_perfil['data_cadastro'][:10]}")
        
        with st.expander("✏️ Editar Meu Perfil"):
            novo_nome = st.text_input("Nome", value=meu_perfil['nome'])
            novo_telefone = st.text_input("Telefone", value=meu_perfil.get('telefone', '') or '')
            
            if st.button("💾 Salvar Alterações", use_container_width=True):
                try:
                    atualizar_usuario(user.id, {
                        "nome": novo_nome,
                        "telefone": novo_telefone if novo_telefone else None
                    })
                    st.success("✅ Perfil atualizado com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erro ao atualizar: {e}")
    else:
        st.warning("⚠️ Dados de perfil não encontrados. Verifique se SETUP_USUARIOS.sql foi executado.")
except Exception as e:
    st.info(f"ℹ️ Seção de perfil indisponível (execute SETUP_USUARIOS.sql no Supabase)")


# =========================
# SEÇÕES REORGANIZADAS - VER ABAIXO
# =========================



# =========================
# DIA CORRETO - CARREGA PRIMEIRO
# =========================
st.markdown("---")
st.subheader("📅 SELECIONE O DIA")
dia = st.selectbox("", ["terça-feira 🔴", "quinta-feira 🔵 REI DA QUADRA"], label_visibility="collapsed")

# =========================
# VERIFICA STATUS DA LISTA
# =========================
dia_key = dia.split()[0]  # "terça" ou "quinta"
status_lista_atual = get_status(dia_key)

# Mostra status visual
if status_lista_atual is None:
    st.warning("⚠️ A lista para este dia ainda não foi criada por um administrador.")
elif status_lista_atual:
    st.success("✅ A lista está ABERTA! Você pode se inscrever na lista de convocação.")
else:
    st.error("🔒 A lista está FECHADA. Não há mais vagas disponíveis.")

st.divider()

# =========================
# INSCRIÇÃO NA LISTA
# =========================
st.markdown("---")
st.subheader("✍️ INSCREVER-SE NA LISTA ✍️")

if status_lista_atual is None:
    st.error("❌ A lista para este dia ainda não foi criada por um administrador. Aguarde...")
elif not status_lista_atual:
    st.error("🔒 A lista está FECHADA. Não é possível fazer novas inscrições.")
else:
    # Adicionar imagem da águia
    if aguia_existe:
        col_img1, col_img2, col_img3 = st.columns([1, 1, 1])
        with col_img2:
            st.image(aguia_path, width=250)
    
    dia_acao = "🔵 REI DA QUADRA" if dia.split()[0] == "quinta" else "🔴 TERÇA-FEIRA"
    st.caption(f"Preparando para: {dia_acao}")

    col_form1, col_form2 = st.columns(2)
    
    with col_form1:
        nome_escolhido = st.text_input("🎯 Seu nome na lista", value=nome_usuario)
        eh_levantador = st.checkbox("🤚 Sou levantador/levantadora")
    
    with col_form2:
        limite_lev_str = "4" if dia.split()[0] == "terça" else "3"
        st.markdown(f"**Limite de levantadores:** {limite_lev_str}")
        st.markdown("")  # Espaço
    
    # Opção para adicionar familiares
    familia_list = listar_familia(user.id).data if listar_familia(user.id).data else []
    familiares_selecionados = []
    
    if familia_list:
        st.markdown("**👥 Adicionar familiares à inscrição:**")
        familiares_selecionados = st.multiselect(
            "Selecione familiares que também vão jogar",
            options=[f"{m['nome']} ({m['idade']} anos)" for m in familia_list],
            key=f"familia_select_{dia}"
        )
    
    # Botão para inscrição
    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn1:
        if st.button("➕ INSCREVER-SE AGORA", use_container_width=True, key="inscrever_btn"):
            if not nome_escolhido:
                st.error("❌ Digite seu nome para se inscrever!")
            else:
                try:
                    is_admin_user = is_admin(user.id)
                    if not is_admin_user:
                        fila_atual = listar_fila(dia)
                        pessoas_usuario = [p for p in fila_atual if p.get("user_id") == user.id]
                        total_pessoas_selecionadas = 1 + len(familiares_selecionados)
                        total_com_existentes = len(pessoas_usuario) + total_pessoas_selecionadas
                        
                        if total_com_existentes > 2:
                            st.error(f"❌ Limite excedido! Máx 2 pessoas por dia.")
                        else:
                            res = entrar_fila(user.id, nome_escolhido, dia, levantador=eh_levantador)
                            if isinstance(res, dict) and res.get("error"):
                                st.error(f"❌ {res['error']}")
                            else:
                                if familiares_selecionados and familia_list:
                                    for fam_selecionado in familiares_selecionados:
                                        membro = next((m for m in familia_list if f"{m['nome']} ({m['idade']} anos)" == fam_selecionado), None)
                                        if membro:
                                            try:
                                                entrar_fila(user.id, membro['nome'], dia, levantador=False)
                                            except:
                                                pass
                                
                                total_inscrito = 1 + len(familiares_selecionados)
                                st.success(f"✅ {total_inscrito} pessoa(s) inscrita(s) com sucesso!")
                                try:
                                    registrar_entrada_fila(user.id, nome_escolhido, email_user)
                                except:
                                    pass
                                st.rerun()
                    else:
                        res = entrar_fila(user.id, nome_escolhido, dia, levantador=eh_levantador)
                        if isinstance(res, dict) and res.get("error"):
                            st.error(f"❌ {res['error']}")
                        else:
                            if familiares_selecionados and familia_list:
                                for fam_selecionado in familiares_selecionados:
                                    membro = next((m for m in familia_list if f"{m['nome']} ({m['idade']} anos)" == fam_selecionado), None)
                                    if membro:
                                        try:
                                            entrar_fila(user.id, membro['nome'], dia, levantador=False)
                                        except:
                                            pass
                            
                            total_inscrito = 1 + len(familiares_selecionados)
                            st.success(f"✅ {total_inscrito} pessoa(s) inscrita(s)!")
                            try:
                                registrar_entrada_fila(user.id, nome_escolhido, email_user)
                            except:
                                pass
                            st.rerun()
                except Exception as e:
                    st.error(f"❌ Erro: {e}")
    
    with col_btn2:
        if st.button("❌ SAIR", use_container_width=True):
            try:
                sair_fila(user.id, dia)
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erro: {e}")

st.divider()

# =========================
# LISTA DE CONVOCAÇÃO
# =========================
st.markdown("---")
st.subheader("📋 LISTA DE CONVOCAÇÃO 📋")

dia_display = "🔵 REI DA QUADRA" if dia.split()[0] == "quinta" else "🔴 TERÇA-FEIRA"
limite_display = "18" if dia.split()[0] == "quinta" else "24"
st.markdown(f"**{dia_display} - Limite de {limite_display} pessoas**")

try:
    fila = listar_fila(dia)
except Exception as e:
    st.error(f"❌ Erro ao buscar lista: {e}")
    fila = []

if fila:
    # Mostrar em cards lado a lado (2 colunas)
    cols = st.columns(2)
    for i, jogador in enumerate(fila):
        nome = jogador["nome"]
        levantador = jogador.get("levantador", False)
        with cols[i % 2]:
            card_jogador(i + 1, nome, levantador=levantador)
else:
    st.info("📭 A lista está vazia! Seja o primeiro a se inscrever!")

st.divider()

# =========================
# CHECK-IN
# =========================
st.markdown("---")
st.subheader("📍 CHECK-IN DE CHEGADA 📍")
st.markdown("Registre sua chegada para confirmar sua presença")

is_admin_user = is_admin(user.id)

# ADMIN: Gerar QR Code
if is_admin_user:
    if QRCODE_DISPONIVEL:
        with st.expander("🔐 ADMIN - Gerar QR Code para Check-in", expanded=False):
            st.info("ℹ️ Gere um QR Code para que os usuários façam check-in escaneando")
            
            if st.button("📱 GERAR QR CODE PARA ESTE DIA", use_container_width=True, key="gerar_qr"):
                resultado = gerar_qrcode_checkin(dia.split()[0])
                
                if resultado.get("sucesso"):
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, rgba(6, 168, 125, 0.3), rgba(0, 212, 170, 0.1));
                        border: 2px solid #06a87d;
                        border-radius: 15px;
                        padding: 15px;
                        text-align: center;
                    ">
                        <div style="color: #06a87d; font-weight: 900; margin-bottom: 10px;">✅ QR Code Gerado!</div>
                        <div style="font-size: 0.9em; color: #00d4aa;">Token: <code>{resultado.get('token')}</code></div>
                        <div style="font-size: 0.85em; color: #e39a03; margin-top: 8px;">Compartilhe com os jogadores</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.image(resultado.get("img_bytes"), width=300, caption="Escaneie para fazer check-in")
                else:
                    st.error(f"❌ Erro: {resultado.get('erro', 'Desconhecido')}")
    else:
        st.info("ℹ️ Sistema de QR Code não disponível")

st.markdown("---")
st.markdown("**Opções de Check-in:**")

col_checkin1, col_checkin2 = st.columns(2)

with col_checkin1:
    st.markdown("#### 1️⃣ Geolocalização (Automático)")
    botao_check_in()

with col_checkin2:
    if QRCODE_DISPONIVEL:
        st.markdown("#### 2️⃣ QR Code (Se GPS não funcionar)")
        if st.button("📱 ESCANEAR QR CODE", use_container_width=True, key="escanear_qr"):
            st.session_state.modo_qr = True
        
        if st.session_state.get("modo_qr"):
            token_manual = st.text_input("Cole o token do admin:", key="token_qr_input")
            if st.button("✅ CONFIRMAR", use_container_width=True):
                if token_manual:
                    resultado = fazer_checkin_por_qrcode(user.id, token_manual, dia.split()[0])
                    if resultado.get("sucesso"):
                        st.success("✅ Check-in realizado!")
                        st.balloons()
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(f"❌ {resultado.get('erro')}")
                else:
                    st.warning("⚠️ Digite o token")
    else:
        st.info("ℹ️ QR Code não disponível")

# Status do Check-in
check_in_atual = get_check_in_usuario(user.id, dia.split()[0])

if check_in_atual:
    hora_chegada = check_in_atual["hora_chegada"].split("T")[1][:5] if check_in_atual.get("hora_chegada") else "N/A"
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(6, 168, 125, 0.3), rgba(0, 212, 170, 0.1));
        border: 2px solid #06a87d;
        border-radius: 15px;
        padding: 15px;
        color: white;
        text-align: center;
        margin-top: 15px;
    ">
        <div style="font-size: 1.2em; font-weight: 900; color: #06a87d; margin-bottom: 8px;">✅ Check-in Realizado!</div>
        <div>🕐 Hora: <span style="color: #ffd60a; font-weight: bold;">{hora_chegada}</span></div>
        <div style="font-size: 0.9em; color: #00d4aa; margin-top: 8px;">✨ Você está confirmado para jogar!</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("ℹ️ Você ainda não fez check-in")

st.divider()

# =========================
# PAINEL DO ADMIN (APENAS ADMINS)
# =========================
if is_admin_user:
    st.markdown("---")
    st.subheader("🔐 PAINEL DO ADMINISTRADOR 🔐")
    
    # Seção 1: Gerenciar Lista
    st.markdown("#### ➕ Gerenciar Lista")
    col_admin1, col_admin2, col_admin3 = st.columns(3)
    
    with col_admin1:
        if status_lista_atual is None:
            if st.button("➕ CRIAR LISTA", use_container_width=True):
                try:
                    criar_lista(dia_key)
                    st.success(f"✅ Lista criada!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erro: {e}")
        else:
            st.info(f"✓ Lista: {'Aberta' if status_lista_atual else 'Fechada'}")
    
    with col_admin2:
        if status_lista_atual:
            if st.button("🔒 FECHAR LISTA", use_container_width=True):
                try:
                    fechar_lista(dia_key)
                    try:
                        resultado = preencher_fila_com_convidados(dia)
                        if resultado['success'] and resultado['adicionados'] > 0:
                            st.info(f"✅ {resultado['adicionados']} convidado(s) adicionados!")
                    except:
                        pass
                    st.success("✅ Lista fechada!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erro: {e}")
    
    with col_admin3:
        if st.button("🧹 LIMPAR FILA", use_container_width=True):
            try:
                limpar_fila(dia)
                st.session_state.times = None
                st.success("✅ Fila limpa!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erro: {e}")
    
    st.divider()
    
    # Seção 2: Convidados
    st.markdown("#### 👥 Gerenciar Convidados")
    
    convidados = listar_convidados(dia)
    limite = 24 if dia.split()[0] == "terça" else 18
    fila_atual = listar_fila(dia)
    vagas = limite - len(fila_atual)
    
    col_cong1, col_cong2 = st.columns(2)
    
    with col_cong1:
        st.markdown(f"**Vagas:** {vagas} | **Convidados:** {len(convidados)}")
        if convidados:
            for i, convidado in enumerate(convidados):
                st.markdown(f"• {convidado['nome']}")
        else:
            st.info("Nenhum convidado")
    
    with col_cong2:
        st.markdown("**Adicionar:**")
        nome_convidado = st.text_input("Nome", key="nome_convidado")
        if st.button("➕ ADICIONAR", use_container_width=True):
            if nome_convidado:
                try:
                    adicionar_convidado(nome_convidado, dia)
                    st.success(f"✅ {nome_convidado} adicionado!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erro: {e}")
            else:
                st.warning("⚠️ Digite um nome!")
    
    st.divider()
    
    # Seção 3: Estatísticas
    st.markdown("#### 📊 Estatísticas")
    
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    
    with col_stat1:
        fila_count = contar_fila(dia)
        limite_str = "24" if dia.split()[0] == "terça" else "18"
        st.metric("Inscritos", f"{fila_count}/{limite_str}")
    
    with col_stat2:
        fila_com_lev = listar_fila(dia)
        total_lev = len([p for p in fila_com_lev if p.get("levantador", False)])
        limite_lev = "4" if dia.split()[0] == "terça" else "3"
        st.metric("🤚 Levantadores", f"{total_lev}/{limite_lev}")
    
    with col_stat3:
        if st.button("🧹 Limpeza Manual", use_container_width=True):
            try:
                limpar_fila_antigas()
                limpar_check_ins_antigos(dias=7)
                limpar_scores_inativos(dias=90)
                st.success("✅ Limpeza concluída!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erro: {e}")
    
    st.divider()

# =========================
# SORTEIO DE TIMES
# =========================
st.markdown("---")
st.subheader("🎲 SORTEIO DE TIMES 🎲")

dia_titulo = "🔵 REI DA QUADRA" if dia.split()[0] == "quinta" else "🔴 TERÇA-FEIRA"
st.markdown(f"**Sorteios para: {dia_titulo}**")

col_sorteio1, col_sorteio2, col_sorteio3 = st.columns([1, 2, 1])

with col_sorteio2:
    if st.button("🎲 SORTEAR TIMES AGORA 🎲", use_container_width=True, key="sortear"):
        try:
            st.session_state.times = gerar_times(dia)
            st.balloons()
        except Exception as e:
            st.error(f"❌ Erro ao gerar times: {e}")

# =========================
# EXIBIR TIMES
# =========================
if st.session_state.times:
    times = st.session_state.times
    
    if isinstance(times, dict):
        st.error(f"❌ {times.get('error', 'Erro ao gerar times')}")
    else:
        st.markdown("---")
        st.subheader(f"🏟️ TIMES FORMADOS 🏟️")
        
        for i in range(0, len(times), 2):
            if i + 1 < len(times):
                desenhar_quadra(times[i], times[i + 1])
            else:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, rgba(51, 65, 85, 0.6), rgba(30, 41, 59, 0.6));
                    border: 2px solid #ffd60a;
                    border-radius: 18px;
                    padding: 20px;
                    color: white;
                    font-weight: 700;
                ">
                    <h3 style="color: #ffd60a; text-align: center;">🏐 Time Extra 🏐</h3>
                """, unsafe_allow_html=True)
                for jogador in times[i]:
                    st.write(f"🎯 {jogador}")
                st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# =========================
# PRESENÇA & CHECK-INS
# =========================
st.markdown("---")
st.subheader("📊 PRESENÇA & CHECK-INS 📊")

dia_clean = dia.split()[0]
check_ins_validados = listar_check_ins_validados(dia_clean, raio_metros=50)
lista_presenca(check_ins_validados)

# Admin: Seção de usuários cadastrados
if is_admin(user.id):
    st.divider()
    st.subheader("👥 USUÁRIOS CADASTRADOS 👥")
    
    try:
        total_usuarios = obter_total_usuarios()
        st.metric("Total de Usuários", total_usuarios)
        
        with st.expander("📋 Ver Lista de Usuários"):
            usuarios_lista = listar_usuarios()
            if usuarios_lista:
                for idx, usr in enumerate(usuarios_lista, 1):
                    col1, col2, col3 = st.columns([2, 2, 1])
                    with col1:
                        st.write(f"**{usr['nome']}**")
                    with col2:
                        st.write(f"📧 {usr['email']}")
                    with col3:
                        if usr['telefone']:
                            st.write(f"☎️ {usr['telefone']}")
            else:
                st.info("Nenhum usuário cadastrado ainda")
    except Exception as e:
        st.warning(f"⚠️ Erro ao carregar usuários: {e}\n\nExecute SETUP_USUARIOS.sql no Supabase")


# =========================
# RANKING & SCORE
# =========================
st.divider()
st.subheader("🏆 RANKING DE CONFIABILIDADE 🏆")

st.markdown("""
**Ranking baseado em:**
- ✅ Check-ins confirmados
- 📊 Taxa de presença (check-ins / entradas na fila)
- 🎯 Atividade recente

**Objetivo:** Valorizar quem entra na fila E realmente comparece!
""")

ranking = listar_ranking(limite=10)

if ranking:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🥇 Melhor Score", f"{ranking[0]['score']} pts", f"{ranking[0]['nome']}", delta_color="off")
    
    with col2:
        if len(ranking) > 1:
            st.metric("🥈 2º Lugar", f"{ranking[1]['score']} pts", f"{ranking[1]['nome']}", delta_color="off")
        else:
            st.metric("🥈 2º Lugar", "---", delta_color="off")
    
    with col3:
        if len(ranking) > 2:
            st.metric("🥉 3º Lugar", f"{ranking[2]['score']} pts", f"{ranking[2]['nome']}", delta_color="off")
        else:
            st.metric("🥉 3º Lugar", "---", delta_color="off")
    
    st.divider()
    
    st.markdown("**📋 TOP 10 RANKING:**")
    
    for i, jogador in enumerate(ranking[:10], 1):
        medalha = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}️⃣ "
        
        col_rank1, col_rank2, col_rank3, col_rank4, col_rank5 = st.columns([0.5, 2, 1.5, 1.5, 1])
        
        with col_rank1:
            st.markdown(f"**{medalha}**")
        
        with col_rank2:
            st.markdown(f"**{jogador['nome']}**")
        
        with col_rank3:
            st.markdown(f"✅ {jogador['check_ins']} check-ins")
        
        with col_rank4:
            st.markdown(f"📊 {jogador['taxa_presenca']:.0f}% presença")
        
        with col_rank5:
            st.markdown(f"⭐ {jogador['score']} pts", help="Score total")
else:
    st.info("📈 Nenhum jogador com score ainda. Comece a jogar e fazer check-ins!")

st.divider()

# =========================
# SORTEIO DE TIMES
# =========================
st.markdown("---")
st.subheader("🎲 SORTEIO DE TIMES 🎲")

dia_titulo = "🔵 REI DA QUADRA" if dia.split()[0] == "quinta" else "🔴 TERÇA-FEIRA"
st.markdown(f"**Sorteios para: {dia_titulo}**")

col_sorteio1, col_sorteio2, col_sorteio3 = st.columns([1, 2, 1])

with col_sorteio2:
    if st.button("🎲 SORTEAR TIMES AGORA 🎲", use_container_width=True, key="sortear"):
        try:
            st.session_state.times = gerar_times(dia)
            st.balloons()
        except Exception as e:
            st.error(f"❌ Erro ao gerar times: {e}")

# =========================
# EXIBIR TIMES
# =========================
if st.session_state.times:
    times = st.session_state.times
    
    if isinstance(times, dict):
        st.error(f"❌ {times.get('error', 'Erro ao gerar times')}")
    else:
        st.markdown("---")
        st.subheader(f"🏟️ TIMES FORMADOS 🏟️")
        
        for i in range(0, len(times), 2):
            if i + 1 < len(times):
                desenhar_quadra(times[i], times[i + 1])
            else:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, rgba(51, 65, 85, 0.6), rgba(30, 41, 59, 0.6));
                    border: 2px solid #ffd60a;
                    border-radius: 18px;
                    padding: 20px;
                    color: white;
                    font-weight: 700;
                ">
                    <h3 style="color: #ffd60a; text-align: center;">🏐 Time Extra 🏐</h3>
                """, unsafe_allow_html=True)
                for jogador in times[i]:
                    st.write(f"🎯 {jogador}")
                st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# =========================
# PRESENÇA & CHECK-INS
# =========================
st.markdown("---")
st.subheader("📊 PRESENÇA & CHECK-INS 📊")

dia_clean = dia.split()[0]
check_ins_validados = listar_check_ins_validados(dia_clean, raio_metros=50)
lista_presenca(check_ins_validados)

# Admin: Seção de usuários cadastrados
if is_admin(user.id):
    st.divider()
    st.subheader("👥 USUÁRIOS CADASTRADOS 👥")
    
    try:
        total_usuarios = obter_total_usuarios()
        st.metric("Total de Usuários", total_usuarios)
        
        with st.expander("📋 Ver Lista de Usuários"):
            usuarios_lista = listar_usuarios()
            if usuarios_lista:
                for idx, usr in enumerate(usuarios_lista, 1):
                    col1, col2, col3 = st.columns([2, 2, 1])
                    with col1:
                        st.write(f"**{usr['nome']}**")
                    with col2:
                        st.write(f"📧 {usr['email']}")
                    with col3:
                        if usr['telefone']:
                            st.write(f"☎️ {usr['telefone']}")
            else:
                st.info("Nenhum usuário cadastrado ainda")
    except Exception as e:
        st.warning(f"⚠️ Erro ao carregar usuários: {e}\n\nExecute SETUP_USUARIOS.sql no Supabase")