import streamlit as st
print("frontend carregado")
def aplicar_estilo():
    st.set_page_config(
        page_title="🏐 Gerenciador de Vôlei",
        page_icon="🏐",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    st.markdown("""
    <style>
    
    * {
        margin: 0;
        padding: 0;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        min-height: 100vh;
    }

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }

    .main {
        background: transparent;
    }

    h1 {
        color: #ffd60a;
        font-weight: 900;
        font-size: 3.5em;
        text-shadow: 0 0 20px rgba(255, 214, 10, 0.4);
        margin-bottom: 0.3em;
        text-align: center;
    }

    h2 {
        color: #ffd60a;
        font-weight: 800;
        font-size: 1.8em;
        text-shadow: 0 0 10px rgba(255, 214, 10, 0.3);
    }

    h3 {
        color: #e39a03;
        font-weight: 700;
        font-size: 1.3em;
    }

    /* BOTÕES - ESTILO VÔLEI */
    .stButton > button {
        background: linear-gradient(135deg, #ffd60a 0%, #ffb703 100%);
        color: #000;
        border-radius: 15px;
        height: 3.2em;
        width: 100%;
        font-weight: 900;
        font-size: 1.1em;
        border: 2px solid #fb5607;
        box-shadow: 0 8px 20px rgba(255, 214, 10, 0.3);
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #ffb703 0%, #ffd60a 100%);
        box-shadow: 0 12px 30px rgba(255, 214, 10, 0.5);
        transform: translateY(-2px);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    /* INPUT FIELDS */
    input, .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 2px solid #ffd60a !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 12px !important;
        font-weight: 600 !important;
    }

    input::placeholder {
        color: rgba(255, 255, 255, 0.6) !important;
    }

    /* CARDS - JOGADOR */
    .card {
        background: linear-gradient(135deg, rgba(51, 65, 85, 0.6), rgba(30, 41, 59, 0.6));
        padding: 18px;
        border-radius: 18px;
        margin-bottom: 12px;
        border: 2px solid #ffd60a;
        box-shadow: 0 8px 25px rgba(255, 214, 10, 0.15);
        color: white;
        font-weight: 700;
        transition: all 0.3s ease;
    }

    .card:hover {
        background: linear-gradient(135deg, rgba(51, 65, 85, 0.8), rgba(30, 41, 59, 0.8));
        box-shadow: 0 12px 35px rgba(255, 214, 10, 0.25);
        transform: translateX(5px);
    }

    /* STATUS */
    .status-open {
        background: linear-gradient(135deg, #06a77d 0%, #04986f 100%);
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        color: #ffffff;
        font-weight: 900;
        font-size: 1.2em;
        box-shadow: 0 8px 20px rgba(6, 168, 125, 0.3);
        border: 2px solid #00d4aa;
    }

    .status-closed {
        background: linear-gradient(135deg, #d62828 0%, #af2416 100%);
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        color: #ffffff;
        font-weight: 900;
        font-size: 1.2em;
        box-shadow: 0 8px 20px rgba(214, 40, 40, 0.3);
        border: 2px solid #ff4444;
    }

    /* DIVIDERS */
    hr {
        border: 2px solid #ffd60a;
        border-radius: 2px;
        margin: 2em 0;
    }

    /* SELECTBOX E RADIO */
    .stRadio > label, .stSelectbox > label {
        color: #ffd60a !important;
        font-weight: 700 !important;
        font-size: 1.1em !important;
    }

    /* MENSAGENS */
    .stSuccess {
        background-color: rgba(6, 168, 125, 0.2) !important;
        border-left: 4px solid #06a77d !important;
    }

    .stError {
        background-color: rgba(214, 40, 40, 0.2) !important;
        border-left: 4px solid #d62828 !important;
    }

    .stWarning {
        background-color: rgba(255, 214, 10, 0.15) !important;
        border-left: 4px solid #ffd60a !important;
    }

    .stInfo {
        background-color: rgba(59, 130, 246, 0.15) !important;
        border-left: 4px solid #3b82f6 !important;
    }

    /* QUADRA */
    .quadra-container {
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 214, 10, 0.4); }
        50% { box-shadow: 0 0 0 10px rgba(255, 214, 10, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 214, 10, 0); }
    }

    </style>
    """, unsafe_allow_html=True)


# =========================
# CARD JOGADOR
# =========================
def card_jogador(posicao, nome, levantador=False):
    cores = ["🔴", "🟠", "🟡", "🟢", "🔵", "🟣"]
    cor = cores[(posicao - 1) % len(cores)]
    badge_lev = "🤚" if levantador else ""
    
    st.markdown(f"""
    <div class="card">
        <div style="display: flex; align-items: center; gap: 15px; font-size: 1.2em;">
            <span style="font-size: 1.8em;">{cor}</span>
            <span style="background: linear-gradient(90deg, #ffd60a, #ffb703); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900;">
                {posicao}º lugar
            </span>
            <span style="color: #e39a03; font-size: 1.3em; flex: 1;">
                🏐 {nome} {badge_lev}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# =========================
# STATUS LISTA
# =========================
def status_lista(aberta):
    if aberta:
        st.markdown('<div class="status-open">🟢 Lista ABERTA</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-closed">🔴 Lista FECHADA</div>', unsafe_allow_html=True)


# =========================
# QUADRA PROFISSIONAL
# =========================
def desenhar_quadra(time1, time2):
    def montar_time(time):
        grid = [""] * 6
        for i, jogador in enumerate(time[:6]):
            grid[i] = jogador

        posicoes = [
            ("🥅<br/>Levantador", grid[0]),
            ("🎯<br/>Ponta", grid[1]),
            ("⚔️<br/>Central", grid[2]),
            ("🛡️<br/>Central", grid[3]),
            ("🌟<br/>Ponta", grid[4]),
            ("🔥<br/>Líbero", grid[5]),
        ]

        cells_html = ""
        for i, (label, nome) in enumerate(posicoes):
            cells_html += f"""
            <div style="
                background: linear-gradient(135deg, rgba(255, 214, 10, 0.1), rgba(255, 183, 3, 0.05));
                border: 2px solid rgba(255, 214, 10, 0.3);
                border-radius: 12px;
                padding: 12px;
                text-align: center;
                color: white;
                font-weight: 700;
                min-height: 80px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                transition: all 0.3s ease;
            " onmouseover="this.style.background='linear-gradient(135deg, rgba(255, 214, 10, 0.25), rgba(255, 183, 3, 0.15))'; this.style.transform='scale(1.05)';" onmouseout="this.style.background='linear-gradient(135deg, rgba(255, 214, 10, 0.1), rgba(255, 183, 3, 0.05))'; this.style.transform='scale(1)';">
                <div style="font-size: 1.4em; margin-bottom: 5px;">{label.split('<br/>')[0]}</div>
                <div style="font-size: 0.85em; color: #ffd60a; margin-bottom: 8px;">{label.split('<br/>')[1]}</div>
                <div style="font-size: 1.1em; color: #00d4aa; font-weight: 900; word-break: break-word;">{nome}</div>
            </div>
            """

        return f"""
        <div style="
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
        ">
            {cells_html}
        </div>
        """

    html = f"""
    <div class="quadra-container" style="
        background: linear-gradient(135deg, #065f46 0%, #047857 100%);
        border: 4px solid #ffd60a;
        border-radius: 25px;
        padding: 30px;
        display: flex;
        justify-content: space-between;
        gap: 30px;
        color: white;
        font-weight: bold;
        margin: 20px 0;
        box-shadow: 0 15px 50px rgba(0, 0, 0, 0.4);
    ">
        <div style="width: 48%; display: flex; flex-direction: column;">
            <h3 style="
                text-align: center;
                color: #ffd60a;
                font-size: 1.8em;
                margin-bottom: 20px;
                text-shadow: 0 0 10px rgba(255, 214, 10, 0.3);
            ">🔥 TIME A 🔥</h3>
            {montar_time(time1)}
        </div>

        <div style="
            width: 3px;
            background: linear-gradient(180deg, transparent, #ffd60a, transparent);
            border-radius: 2px;
        "></div>

        <div style="width: 48%; display: flex; flex-direction: column;">
            <h3 style="
                text-align: center;
                color: #00d4aa;
                font-size: 1.8em;
                margin-bottom: 20px;
                text-shadow: 0 0 10px rgba(0, 212, 170, 0.3);
            ">⚡ TIME B ⚡</h3>
            {montar_time(time2)}
        </div>
    </div>
    <div style="text-align: center; color: #ffd60a; font-weight: 900; font-size: 1.3em; margin-top: 15px;">
        🏆 QUE VENCE O MELHOR! 🏆
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)


# =========================
# CHECK-IN
# =========================
def botao_check_in():
    """
    Cria uma interface para fazer check-in com geolocalização
    """
    st.markdown("""
    <style>
    .checkin-container {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 50%, #ff6b6b 100%);
        border: 3px solid #ff1744;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(255, 107, 107, 0.4);
    }
    
    .checkin-button-text {
        color: white;
        font-weight: 900;
        font-size: 1.1em;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Cria um espaço para o botão de check-in
    col_btn1, col_btn2, col_btn3 = st.columns([0.2, 0.6, 0.2])
    
    with col_btn2:
        if st.button("📍 FAZER CHECK-IN COM GEOLOCALIZAÇÃO 📍", key="checkin_btn", use_container_width=True):
            st.session_state.checkin_requested = True
            st.rerun()
    
    # Se foi solicitado o check-in, executa JavaScript para capturar localização
    if st.session_state.get("checkin_requested"):
        st.info("⏳ Solicitando sua localização... Por favor, aceite a permissão que aparecerá no navegador!")
        
        st.markdown("""
        <script>
        // Função para obter localização e armazenar
        function obterLocalizacao() {
            if (!navigator.geolocation) {
                alert("❌ Seu navegador não suporta geolocalização.\\nUse um navegador moderno (Chrome, Firefox, Edge, Safari).");
                return;
            }
            
            console.log("🔍 Iniciando requisição de geolocalização...");
            
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    console.log("✅ Sucesso! Coordenadas obtidas:");
                    console.log("Latitude:", position.coords.latitude);
                    console.log("Longitude:", position.coords.longitude);
                    console.log("Precisão:", position.coords.accuracy, "metros");
                    
                    // Armazena no localStorage
                    localStorage.setItem('latitude', position.coords.latitude);
                    localStorage.setItem('longitude', position.coords.longitude);
                    localStorage.setItem('accuracy', position.coords.accuracy);
                    localStorage.setItem('timestamp', new Date().toISOString());
                    localStorage.setItem('geolocation_success', 'true');
                    
                    // Sinaliza sucesso e recarrega
                    alert("✅ Sucesso!\\nLatitude: " + position.coords.latitude.toFixed(6) + "\\nLongitude: " + position.coords.longitude.toFixed(6) + "\\nPrecisão: " + position.coords.accuracy.toFixed(1) + "m");
                    setTimeout(function() { window.location.reload(); }, 500);
                },
                function(error) {
                    let mensagem = "❌ Erro ao obter localização.\\n\\n";
                    
                    if (error.code === error.PERMISSION_DENIED) {
                        mensagem += "PERMISSÃO NEGADA.\\nClique no ícone de localização na barra de endereço ou veja as configurações do site.";
                    } else if (error.code === error.POSITION_UNAVAILABLE) {
                        mensagem += "Posição indisponível. Tente novamente ou use entrada manual.";
                    } else if (error.code === error.TIMEOUT) {
                        mensagem += "Tempo limite excedido. Sua localização está desativada ou leva muito tempo.";
                    } else {
                        mensagem += "Erro: " + error.message;
                    }
                    
                    alert(mensagem);
                    console.error("❌ Erro na geolocalização:", error);
                    
                    // Marca como falha
                    localStorage.setItem('geolocation_success', 'false');
                },
                {
                    enableHighAccuracy: true,  // Usa GPS quando possível
                    timeout: 15000,             // 15 segundos de espera
                    maximumAge: 0               // Não usa cache
                }
            );
        }
        
        console.log("📍 Script de geolocalização carregado. Chamando obterLocalizacao()...");
        obterLocalizacao();
        </script>
        """, unsafe_allow_html=True)
    
    return None


def card_check_in(nome, hora, distancia_metros=None, status="confirmado"):
    """
    Exibe um card de check-in formatado com validação
    status pode ser: "confirmado", "fora_area", "pendente"
    """
    emojis_status = {
        "confirmado": "✅",
        "fora_area": "❌",
        "pendente": "⏳"
    }
    
    emoji = emojis_status.get(status, "✅")
    cor_status = {
        "confirmado": "#06a77d",
        "fora_area": "#d62828",
        "pendente": "#ffd60a"
    }.get(status, "#06a77d")
    
    labels_status = {
        "confirmado": "Confirmado ✅",
        "fora_area": "Fora da área ❌",
        "pendente": "Pendente ⏳"
    }
    
    label = labels_status.get(status, "Confirmado")
    
    distancia_html = ""
    if distancia_metros is not None:
        distancia_html = f"<div style='color: #ff9f43; font-size: 0.9em; margin-top: 8px;'>📍 {distancia_metros:.1f}m da quadra</div>"
    
    st.markdown(f"""
    <div class="card" style="border-left: 4px solid {cor_status};">
        <div style="display: flex; align-items: center; gap: 15px;">
            <span style="font-size: 2em;">{emoji}</span>
            <div style="flex: 1;">
                <div style="font-size: 1.1em; color: #ffd60a;">{nome}</div>
                <div style="font-size: 0.95em; color: {cor_status}; margin-top: 5px; font-weight: 700;">📊 {label}</div>
                <div style="font-size: 0.9em; color: #e39a03; margin-top: 3px;">🕐 {hora}</div>
                {distancia_html}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def lista_presenca(check_ins):
    """
    Exibe uma lista de presença formatada com status de validação
    check_ins deve vir de listar_check_ins_validados()
    """
    if not check_ins:
        st.info("📊 Nenhum check-in registrado ainda")
        return
    
    confirmados = sum(1 for ci in check_ins if ci.get("validado", False))
    fora_area = sum(1 for ci in check_ins if not ci.get("validado", True) and ci.get("distancia_metros"))
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(51, 65, 85, 0.3), rgba(30, 41, 59, 0.3));
        border: 2px solid #ffd60a;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
    ">
        <h3 style="color: #ffd60a; text-align: center; margin-bottom: 20px;">
            📊 PRESENÇA DO DIA - {len(check_ins)} Jogadores
        </h3>
        <div style="display: flex; justify-content: space-around; margin-bottom: 15px; gap: 10px;">
            <div style="text-align: center;">
                <div style="font-size: 1.5em; color: #06a77d; font-weight: 900;">{confirmados}</div>
                <div style="color: #06a77d; font-size: 0.9em;">✅ Confirmados</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 1.5em; color: #d62828; font-weight: 900;">{fora_area}</div>
                <div style="color: #d62828; font-size: 0.9em;">❌ Fora da Área</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    for i, check_in in enumerate(check_ins, 1):
        hora = check_in.get("hora_chegada", "").split("T")[1][:5] if check_in.get("hora_chegada") else "N/A"
        distancia = check_in.get("distancia_metros")
        status_val = "confirmado" if check_in.get("validado", False) else "fora_area"
        
        # Pega nome do user_id ou usa ID truncado
        nome_display = f"{i}º - {check_in['user_id'][:8]}"
        
        card_check_in(nome_display, hora, distancia, status_val)
    
    st.markdown("</div>", unsafe_allow_html=True)