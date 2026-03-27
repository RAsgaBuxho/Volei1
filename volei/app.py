import streamlit as st

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


# =========================
# HEADER
# =========================
st.title("🏐 GERENCIADOR DE VÔLEI 🏐")


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
    
    aba = st.radio("", ["🔐 LOGIN", "📝 CADASTRO"], horizontal=True)

    email = st.text_input("📧 Email")
    senha = st.text_input("🔑 Senha", type="password")

    if aba == "🔐 LOGIN":
        if st.button("🎯 ENTRAR"):
            user = login(email, senha)

            if user:
                # compat com supabase
                if hasattr(user, "user"):
                    user = user.user

                st.session_state.user = user
                st.success("✅ Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("❌ Email ou senha incorretos!")

    else:
        if st.button("✅ CRIAR CONTA"):
            signup(email, senha)
            st.success("🎉 Conta criada com sucesso! Agora faça login!")

    st.stop()


# =========================
# USER
# =========================
user = st.session_state.user
email_user = getattr(user, "email", "Sem email")

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
        ✅ Logado como: <span style="color: #ffd60a;">{email_user}</span>
    </div>
    """, unsafe_allow_html=True)

with col_top3:
    if st.button("🚪 SAIR"):
        logout()
        st.session_state.user = None
        st.rerun()

# Debug: Verificar se usuário é admin
with st.expander("🔍 Debug - Verificar Status Admin"):
    user_id_str = str(user.id) if user else "Sem user"
    is_admin_user = is_admin(user.id) if user else False
    st.write(f"**Email:** {email_user}")
    st.write(f"**User ID:** {user_id_str}")
    st.write(f"**É Admin?** {is_admin_user}")
    if not is_admin_user:
        st.error("❌ Você não está registrado como admin!")
        st.markdown("""
        ### Como se tornar Admin:
        
        1. **Copie seu User ID acima** (o UUID mostrado em **User ID**)
        2. **Abra o Supabase** e vá para **SQL Editor**
        3. **Execute este comando:**
        ```sql
        INSERT INTO roles (user_id, role) VALUES ('COLE_SEU_USER_ID_AQUI', 'admin');
        ```
        4. **Volte aqui e atualize** (F5 ou Ctrl+R)
        5. ✅ Você verá "É Admin? True"
        """)

# ⚠️ Aviso de Segurança
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
# FAMILIA
# =========================
st.markdown("---")
st.subheader("👨‍👩‍👧‍👦 GERENCIAR FAMÍLIA 👨‍👩‍👧‍👦")

familia_list = listar_familia(user.id).data if listar_familia(user.id).data else []
max_familia = float('inf') if is_admin(user.id) else 2

col_fam1, col_fam2 = st.columns(2)

with col_fam1:
    st.markdown(f"**Membros da família: {len(familia_list)}/{int(max_familia) if max_familia != float('inf') else '∞'}**")
    
    if familia_list:
        for membro in familia_list:
            st.write(f"👤 {membro['nome']} ({membro['idade']} anos) - Responsável: {membro['responsavel_nome']}")
    else:
        st.info("Nenhum membro da família registrado")

with col_fam2:
    if len(familia_list) < max_familia:
        st.markdown("**Adicionar novo membro:**")
        nome_fam = st.text_input("Nome", key="nome_fam")
        idade_fam = st.number_input("Idade", min_value=1, max_value=120, key="idade_fam")
        responsavel_fam = st.text_input("Responsável", key="responsavel_fam")
        termo_fam = st.checkbox("Aceito o termo")
        
        if st.button("➕ ADICIONAR MEMBRO", use_container_width=True):
            if nome_fam and responsavel_fam:
                try:
                    adicionar_familia(user.id, nome_fam, idade_fam, responsavel_fam, termo_fam)
                    st.success("✅ Membro adicionado com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erro ao adicionar: {e}")
            else:
                st.warning("⚠️ Preencha todos os campos!")
    else:
        st.warning(f"⚠️ Limite de {int(max_familia)} membros atingido!")


# =========================
# DIA CORRETO - CARREGA PRIMEIRO
# =========================
st.markdown("**📅 Qual dia você quer?**")
dia = st.selectbox("", ["terça-feira 🔴", "quinta-feira 🔵 REI DA QUADRA"], label_visibility="collapsed")

# =========================
# VERIFICA STATUS DA LISTA
# =========================
dia_key = dia.split()[0]  # "terça" ou "quinta"
status_lista_atual = get_status(dia_key)

# Mostra status visual
if status_lista_atual is None:
    st.warning("⚠️ A lista para este dia ainda não foi criada.")
elif status_lista_atual:
    st.success("✅ Lista aberta! Você pode entrar na fila.")
else:
    st.error("🔒 Lista fechada. Não há mais vagas.")

st.divider()

# Banner que monitora dados em localStorage
st.markdown("""
<script>
// Monitora continuamente se há dados de geolocalização
function monitorarGeolocation() {
    const lat = localStorage.getItem('latitude');
    const lon = localStorage.getItem('longitude');
    
    if (lat && lon) {
        // Dados foram capturados - Streamlit vai detectar
        const div = document.createElement('div');
        div.style.cssText = `
            position: fixed;
            top: 60px;
            right: 10px;
            background: linear-gradient(135deg, #06a87d, #00d4aa);
            border: 2px solid #06a87d;
            border-radius: 10px;
            padding: 15px;
            color: white;
            font-weight: 700;
            z-index: 10000;
            box-shadow: 0 5px 20px rgba(6, 168, 125, 0.4);
            animation: slideIn 0.5s ease;
        `;
        div.innerHTML = `
            <div style="font-size: 0.9em;">✅ Dados capturados!</div>
            <div style="font-size: 0.8em; margin-top: 5px;">📍 Processando localização...</div>
        `;
        document.body.appendChild(div);
        
        console.log("✅ Localização capturada: ", lat, lon);
    }
}

// Verifica a cada 500ms
setInterval(monitorarGeolocation, 500);
</script>
""", unsafe_allow_html=True)

# Aviso visual se detectar dados de geolocalização pendentes
st.markdown("""
<script>
if (localStorage.getItem('latitude') && localStorage.getItem('longitude')) {
    console.log("✅ Dados de geolocalização detectados!");
    const lat = localStorage.getItem('latitude');
    const lon = localStorage.getItem('longitude');
    console.log("Lat:", lat, "Lon:", lon);
}
</script>
""", unsafe_allow_html=True)


# =========================
# CHECK-IN
# =========================
st.markdown("---")
st.subheader("📍 CHECK-IN DE CHEGADA 📍")

col_checkin1, col_checkin2 = st.columns(2)

with col_checkin1:
    st.markdown("**Clique no botão para registrar sua chegada com localização**")
    botao_check_in()
    
    # Script que monitora localStorage e preenche os campos automaticamente
    st.markdown("""
    <script>
    // Função para preencher campos quando localização é capturada
    function verificarLocalizacaoCapturada() {
        const latitude = localStorage.getItem('latitude');
        const longitude = localStorage.getItem('longitude');
        
        if (latitude && longitude) {
            console.log("🎯 Localização capturada detectada!");
            console.log("Latitude:", latitude);
            console.log("Longitude:", longitude);
            
            // Streamlit vai detectar automaticamente
            // Aqui apenas confirmamos que temos os dados
        }
    }
    
    // Verifica ao carregar e periodicamente
    verificarLocalizacaoCapturada();
    setInterval(verificarLocalizacaoCapturada, 500);
    </script>
    """, unsafe_allow_html=True)

with col_checkin2:
    # Alternativa: Input manual (caso a geolocalização não funcione)
    st.markdown("**Ou insira manualmente (alternativa):**")
    
    col_lat, col_lon = st.columns(2)
    with col_lat:
        lat_manual = st.number_input("Latitude", format="%.6f", min_value=-90.0, max_value=90.0, key="lat_input")
    with col_lon:
        lon_manual = st.number_input("Longitude", format="%.6f", min_value=-180.0, max_value=180.0, key="lon_input")
    
    if st.button("✅ CONFIRMAR CHECK-IN MANUAL", use_container_width=True):
        if lat_manual != 0 and lon_manual != 0:
            res = fazer_check_in(user.id, lat_manual, lon_manual, dia.split()[0])
            if isinstance(res, dict) and res.get("error"):
                st.error(f"❌ Erro: {res['error']}")
            else:
                # Exibe mensagem de sucesso com detalhes da localização
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, rgba(6, 168, 125, 0.3), rgba(0, 212, 170, 0.1));
                    border: 3px solid #06a87d;
                    border-radius: 15px;
                    padding: 20px;
                    color: white;
                    text-align: center;
                ">
                    <div style="font-size: 2em; margin-bottom: 15px;">✅</div>
                    <div style="font-size: 1.3em; font-weight: 900; color: #06a87d; margin-bottom: 15px;">Check-in Registrado com Sucesso!</div>
                    <div style="background: rgba(0, 0, 0, 0.2); border-radius: 10px; padding: 15px; font-size: 0.95em;">
                        <div style="margin: 8px 0;"><strong>📍 Latitude:</strong> {lat_manual:.6f}</div>
                        <div style="margin: 8px 0;"><strong>📍 Longitude:</strong> {lon_manual:.6f}</div>
                        <div style="margin: 8px 0;"><strong>🗓️ Dia:</strong> {dia}</div>
                        <div style="margin: 8px 0;"><strong>⏰ Horário:</strong> Registrado em tempo real</div>
                    </div>
                    <div style="font-size: 0.9em; color: #00d4aa; margin-top: 15px;">✨ Você está confirmado para jogar!</div>
                </div>
                """, unsafe_allow_html=True)
                st.balloons()
                
                # Registra check-in confirmado para o score
                try:
                    registrar_check_in_confirmado(user.id, email_user, email_user, dia.split()[0])
                except:
                    pass  # Silencioso se não conseguir registrar score
                
                st.session_state.checkin_feito = True
                st.rerun()
        else:
            st.warning("⚠️ Insira latitude e longitude válidas")
    
    # Status monitor (debug)
    with st.expander("🔍 DEBUG - Status da Geolocalização"):
        st.markdown("""
        <script>
        // Monitora status do localStorage
        function verificarStatus() {
            const lat = localStorage.getItem('latitude');
            const lon = localStorage.getItem('longitude');
            const status = localStorage.getItem('geolocation_success');
            
            console.log("📊 STATUS:");
            console.log("- Latitude:", lat);
            console.log("- Longitude:", lon);
            console.log("- Sucesso:", status);
            console.log("- UserAgent:", navigator.userAgent);
            console.log("- Geolocation suportada:", !!navigator.geolocation);
        }
        
        verificarStatus();
        console.log("✅ Script de debug carregado. Abra o Console (F12) para mais detalhes.");
        </script>
        """, unsafe_allow_html=True)
        
        st.info("💡 **Como debugar:**")
        st.write("1. Abra o Console do navegador: **F12** ou **Ctrl+Shift+I**")
        st.write("2. Clique no botão de geolocalização")
        st.write("3. Veja as mensagens no console")
        st.write("4. Se ver **'❌ Erro'**, mostre a mensagem")
        st.write("5. Se estiver em HTTP (não HTTPS), use https://localhost:8501")
    
    # Exibe o check-in atual do usuário
    check_in_atual = get_check_in_usuario(user.id, dia.split()[0])
    
    if check_in_atual:
        hora_chegada = check_in_atual["hora_chegada"].split("T")[1][:5] if check_in_atual.get("hora_chegada") else "N/A"
        st.markdown(f"""
        <div class="card" style="background: linear-gradient(135deg, rgba(6, 168, 125, 0.3), rgba(0, 212, 170, 0.1));">
            <div style="color: #00d4aa; font-weight: 900; margin-bottom: 10px;">✅ Você já fez check-in!</div>
            <div>🕐 Hora: <span style="color: #ffd60a;">{hora_chegada}</span></div>
            <div style="font-size: 0.9em; margin-top: 8px;">📍 Localização registrada</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("ℹ️ Você ainda não fez check-in. Clique no botão para registrar sua chegada!")


# =========================
# LAYOUT
# =========================
col1, col2 = st.columns(2)


# =========================
# FILA
# =========================
with col1:
    dia_display = "🔵 REI DA QUADRA" if dia.split()[0] == "quinta" else "🔴 TERÇA-FEIRA"
    limite_display = "18" if dia.split()[0] == "quinta" else "24"
    st.subheader(f"📋 FILA DE ESPERA {dia_display} 📋")
    st.caption(f"Limite: {limite_display} pessoas")

    try:
        fila = listar_fila(dia)
    except Exception as e:
        st.error(f"❌ Erro ao buscar fila: {e}")
        fila = []

    if fila:
        for i, jogador in enumerate(fila):
            nome = jogador["nome"]
            levantador = jogador.get("levantador", False)
            card_jogador(i + 1, nome, levantador=levantador)
    else:
        st.info("🟡 A fila está vazia! Seja o primeiro a entrar!")


# =========================
# AÇÕES
# =========================
with col2:
    st.subheader("⚙️ VAMOS JOGAR ⚙️")
    
    dia_acao = "🔵 REI DA QUADRA" if dia.split()[0] == "quinta" else "🔴 TERÇA-FEIRA"
    st.caption(f"Preparando para: {dia_acao}")

    nome_escolhido = st.text_input("🎯 Seu nome na lista")
    
    # Pergunta se é levantador
    eh_levantador = st.checkbox("🤚 Sou levantador")
    limite_lev_str = "4" if dia.split()[0] == "terça" else "3"
    st.caption(f"Limite de levantadores: {limite_lev_str} por dia")
    
    # Opção para adicionar familiares
    familia_list = listar_familia(user.id).data if listar_familia(user.id).data else []
    familiares_selecionados = []
    
    if familia_list:
        st.markdown("**Adicionar familiares à fila:**")
        familiares_selecionados = st.multiselect(
            "Selecione familiares",
            options=[f"{m['nome']} ({m['idade']} anos)" for m in familia_list],
            key=f"familia_select_{dia}"
        )

    # Verifica se a lista foi criada antes de mostrar botão de entrar
    if status_lista_atual is None:
        st.error("❌ A lista ainda não foi criada por um admin.")
    elif status_lista_atual:
        if st.button("➕ ENTRAR NA FILA"):
            if not nome_escolhido:
                st.warning("⚠️ Digite um nome para continuar!")
            else:
                try:
                    # Validar limite de pessoas para o usuário
                    is_admin_user = is_admin(user.id)
                    if not is_admin_user:
                        # Contar quantas pessoas o usuário já tem na fila
                        fila_atual = listar_fila(dia)
                        pessoas_usuario = [p for p in fila_atual if p.get("user_id") == user.id]
                        total_pessoas_selecionadas = 1 + len(familiares_selecionados)
                        total_com_existentes = len(pessoas_usuario) + total_pessoas_selecionadas
                        
                        if total_com_existentes > 2:
                            st.error(f"❌ Limite excedido! Você pode adicionar no máximo 2 pessoas por dia. Você já tem {len(pessoas_usuario)} pessoa(s) e quer adicionar {total_pessoas_selecionadas}.")
                        else:
                            # Adiciona o usuário na fila
                            res = entrar_fila(user.id, nome_escolhido, dia, levantador=eh_levantador)

                            if isinstance(res, dict) and res.get("error"):
                                st.error(f"❌ {res['error']}")
                            else:
                                # Adiciona familiares à fila também
                                if familiares_selecionados and familia_list:
                                    erro_familiares = False
                                    for fam_selecionado in familiares_selecionados:
                                        membro = next((m for m in familia_list if f"{m['nome']} ({m['idade']} anos)" == fam_selecionado), None)
                                        if membro:
                                            try:
                                                entrar_fila(user.id, membro['nome'], dia, levantador=False)
                                            except Exception as e:
                                                erro_familiares = True
                                                st.warning(f"⚠️ Erro ao adicionar {membro['nome']}: {e}")
                                
                                st.success("✅ Você entrou na fila! Boa sorte!")
                                
                                # Registra entrada na fila para o score
                                try:
                                    registrar_entrada_fila(user.id, nome_escolhido, email_user)
                                except:
                                    pass
                                
                                st.rerun()
                    else:
                        # Admin pode adicionar ilimitadamente
                        res = entrar_fila(user.id, nome_escolhido, dia, levantador=eh_levantador)

                        if isinstance(res, dict) and res.get("error"):
                            st.error(f"❌ {res['error']}")
                        else:
                            # Adiciona familiares à fila também
                            if familiares_selecionados and familia_list:
                                for fam_selecionado in familiares_selecionados:
                                    membro = next((m for m in familia_list if f"{m['nome']} ({m['idade']} anos)" == fam_selecionado), None)
                                    if membro:
                                        try:
                                            entrar_fila(user.id, membro['nome'], dia, levantador=False)
                                        except:
                                            pass
                            
                            st.success("✅ Você entrou na fila! Boa sorte!")
                            
                            # Registra entrada na fila para o score (admin)
                            try:
                                registrar_entrada_fila(user.id, nome_escolhido, email_user)
                            except:
                                pass
                            
                            st.rerun()

                except Exception as e:
                    st.error(f"❌ Erro ao entrar: {e}")

    if st.button("❌ SAIR DA FILA"):
        try:
            sair_fila(user.id, dia)
            st.rerun()
        except Exception as e:
            st.error(f"❌ Erro ao sair: {e}")

    st.divider()

    # ADMIN SIMPLES
    if is_admin(user.id):
        st.markdown("**🔐 PAINEL DO ADMIN 🔐**")

        # Botão para CRIAR LISTA (se ainda não foi criada)
        if status_lista_atual is None:
            if st.button("➕ CRIAR LISTA"):
                try:
                    criar_lista(dia_key)
                    st.success(f"✅ Lista para {dia} foi criada!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erro ao criar lista: {e}")
        else:
            st.info(f"ℹ️ Lista já foi criada ({('Aberta' if status_lista_atual else 'Fechada')})")

        # Botão para FECHAR LISTA
        if status_lista_atual:
            if st.button("🔒 FECHAR LISTA"):
                try:
                    fechar_lista(dia_key)
                    
                    # Automaticamente adiciona convidados quando fecha a lista
                    try:
                        resultado = preencher_fila_com_convidados(dia)
                        if resultado['success'] and resultado['adicionados'] > 0:
                            st.info(f"✅ {resultado['adicionados']} convidado(s) adicionado(s) à fila!")
                    except Exception as e:
                        st.warning(f"⚠️ Erro ao adicionar convidados: {e}")
                    
                    st.success("✅ Lista fechada!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erro ao fechar lista: {e}")
            
            st.rerun()

        if st.button("🧹 LIMPAR FILA"):
            try:
                limpar_fila(dia)
                st.session_state.times = None
                st.success("✅ Fila limpa com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erro ao limpar: {e}")
        
        # Seção de Convidados
        st.divider()
        st.markdown("**👥 GERENCIAR CONVIDADOS 👥**")
        
        convidados = listar_convidados(dia)
        limite = 24 if dia.split()[0] == "terça" else 18
        fila_atual = listar_fila(dia)
        vagas = limite - len(fila_atual)
        
        st.caption(f"Vagas disponíveis: {vagas} | Convidados pendentes: {len(convidados)}")
        
        col_cong1, col_cong2 = st.columns(2)
        
        with col_cong1:
            st.markdown("**Convidados aguardando vaga:**")
            if convidados:
                for i, convidado in enumerate(convidados):
                    st.write(f"{i+1}. {convidado['nome']} 👤")
            else:
                st.info("ℹ️ Nenhum convidado na espera")
        
        with col_cong2:
            st.markdown("**Adicionar novo convidado:**")
            nome_convidado = st.text_input("Nome do convidado", key="nome_convidado")
            
            if st.button("➕ ADICIONAR CONVIDADO", use_container_width=True):
                if nome_convidado:
                    try:
                        adicionar_convidado(nome_convidado, dia)
                        st.success(f"✅ {nome_convidado} adicionado à lista de convidados!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erro ao adicionar: {e}")
                else:
                    st.warning("⚠️ Digite o nome do convidado!")
        
        # Informações sobre economia de espaço
        st.divider()
        st.markdown("**💾 ECONOMIA DE ESPAÇO 💾**")
        
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            fila_atual_count = contar_fila(dia)
            st.metric("Pessoas na fila (hoje)", fila_atual_count, delta="máx: 24" if dia.split()[0] == "terça" else "máx: 18")
            
            # Mostrar levantadores
            fila_com_levantadores = listar_fila(dia)
            total_levantadores = len([p for p in fila_com_levantadores if p.get("levantador", False)])
            limite_lev = 4 if dia.split()[0] == "terça" else 3
            st.metric("🤚 Levantadores", total_levantadores, delta=f"máx: {limite_lev}")
        
        with col_info2:
            st.markdown("""
            **🗑️ Limpeza Automática:**
            - Filas: deletadas após 3 dias
            - Check-ins: deletados após 7 dias
            
            ✅ Economiza espaço no banco (versão gratuita)
            """)
        
        # Botão para forçar limpeza manual
        if st.button("🧹 FORÇAR LIMPEZA MANUAL AGORA", use_container_width=True):
            try:
                res_fila = limpar_fila_antigas()
                res_check = limpar_check_ins_antigos(dias=7)
                res_scores = limpar_scores_inativos(dias=90)
                
                msg = f"✅ Limpeza concluída!\n\n"
                if res_fila['success']:
                    msg += f"🗂️ Fila: {res_fila['deletados']} registro(s) deletado(s)\n"
                if res_check['success']:
                    msg += f"📍 Check-ins: {res_check['deletados']} registro(s) deletado(s)\n"
                if res_scores['success']:
                    msg += f"🏆 Scores: {res_scores['deletados']} jogador(es) inativo(s) removido(s)"
                
                st.success(msg)
            except Exception as e:
                st.error(f"❌ Erro na limpeza: {e}")


# =========================
# GERAR TIMES
# =========================
st.divider()

dia_titulo = "🔵 REI DA QUADRA" if dia.split()[0] == "quinta" else "🔴 TERÇA-FEIRA"
st.markdown(f"### 🎯 Sorteio para {dia_titulo}")

col_sorteio1, col_sorteio2, col_sorteio3 = st.columns([1, 2, 1])

with col_sorteio2:
    if st.button("🎲 SORTEAR TIMES AGORA 🎲", key="sortear"):
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
        dia_times = "🔵 REI DA QUADRA" if dia.split()[0] == "quinta" else "🔴 TERÇA-FEIRA"
        st.subheader(f"🏟️ TIMES FORMADOS {dia_times} 🏟️")

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


# =========================
# PRESENÇA
# =========================
st.divider()

# Extrai o dia (terça ou quinta)
dia_clean = dia.split()[0]
dia_presenca = "🔵 REI DA QUADRA" if dia_clean == "quinta" else "🔴 TERÇA-FEIRA"

st.subheader(f"📊 PRESENÇA & CHECK-INS {dia_presenca} 📊")

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
    
    # Tabela completa do ranking
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