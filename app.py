import streamlit as st
import pandas as pd
import datetime
import zoneinfo
import firebase_admin
from firebase_admin import credentials, firestore
import json
import qrcode
import io

# ==================================================================
# 1. CONEXIÓN CON FIREBASE Y CONFIGURACIÓN MAESTRA DE PÁGINA
# ==================================================================
st.set_page_config(layout="wide", page_title="Flores Antivero Cosecha")

if not firebase_admin._apps:
    try:
        if "text_key" in st.secrets:
            firebase_info = dict(st.secrets["text_key"])
            cred = credentials.Certificate(firebase_info)
            firebase_admin.initialize_app(cred)
        else:
            cred = credentials.Certificate("llave_firebase.json")
            firebase_admin.initialize_app(cred)
    except Exception as e_secrets:
        try:
            cred = credentials.Certificate("llave_firebase.json")
            firebase_admin.initialize_app(cred)
        except Exception as e_local:
            st.error(f"Error crítico: {e_local}")

db = firestore.client()

# ==================================================================
# 4.B TERMINAL EXPRESS CON LECTOR QR ASOCIADO (DISEÑO EXACTO FOTO)
# ==================================================================
def dibujar_teclado_maqueta_antivero():
    st.html("""
        <style>
            .cuadro-teclado-oficial { max-width: 350px; margin: 10px auto; box-sizing: border-box; }
            .cuadro-teclado-oficial [data-testid="stHorizontalBlock"] { flex-direction: row !important; display: flex !important; gap: 8px !important; margin-bottom: 8px !important; }
            .cuadro-teclado-oficial div[data-testid="column"] { margin-bottom: 0 !important; }
            
            .cuadro-teclado-oficial button {
                background-color: #1e293b !important; color: #f8fafc !important;
                border: 1px solid #334155 !important; border-radius: 8px !important;
                font-size: 22px !important; font-weight: bold !important; height: 56px !important;
            }
            .cuadro-teclado-oficial button:active { background-color: #38bdf8 !important; color: #0f172a !important; }
            
            /* 🟥 Barra Roja Horizontal de Borrado Total */
            .cuadro-teclado-oficial .barra-roja-clear button { background-color: #ef4444 !important; border: 1px solid #dc2626 !important; height: 52px !important; }
            .cuadro-teclado-oficial .barra-roja-clear button p { color: #ffffff !important; font-weight: bold !important; font-size: 18px !important; }
            
            /* 🟦 Barra Azul Horizontal de ENTER */
            .cuadro-teclado-oficial .barra-azul-enter button { background-color: #2563eb !important; border: 1px solid #1d4ed8 !important; height: 54px !important; }
            .cuadro-teclado-oficial .barra-azul-enter button p { color: #ffffff !important; font-weight: bold !important; font-size: 16px !important; }
        </style>
    """)
    
    st.subheader("📌 Lector de Ficha Express")
    st.caption("Digite el ID de 3 dígitos (100-200) o presione la cámara para leer el QR:")

    if "id_express_cosecha" not in st.session_state: 
        st.session_state.id_express_cosecha = ""
    id_crudo = st.session_state.id_express_cosecha

    # Forzamos la zona horaria chilena para validar únicamente las fichas de hoy
    tz_cl = zoneinfo.ZoneInfo("America/Santiago")
    fecha_hoy_str = datetime.datetime.now(tz_cl).strftime("%Y-%m-%d")
    
    ficha_es_valida = False
    if id_crudo.isdigit() and 100 <= int(id_crudo) <= 200:
        try:
            doc_ficha = db.collection("credenciales_activas_dia").document(id_crudo).get()
            if doc_ficha.exists:
                datos_f = doc_ficha.to_dict()
                # Filtro estricto: solo sirve si se enroló en la fecha actual de Chile
                if datos_f.get("FechaFiltro") == fecha_hoy_str:
                    ficha_es_valida = True
                    st.session_state.rut_cosechador = datos_f.get("RutCosechador", "")
                    st.session_state.cc_activo_meson = datos_f.get("CentroCosto", "")
                    st.session_state.contratista_activo_meson = datos_f.get("Contratista", "")
        except Exception: 
            ficha_es_valida = False

    icono_verificacion = "✅" if ficha_es_valida else "🛑"
    
    st.markdown('<div class="cuadro-teclado-oficial">', unsafe_allow_html=True)
    
    # Cabecera interactiva con Visor e ícono de cámara QR de tu fotografía
    col_v_txt, col_v_ico = st.columns(2)
    with col_v_txt:
        st.markdown(f'<div class="rut-display-box" style="font-size:24px; min-height:50px; margin-bottom:0; background-color:#0f172a;">#{id_crudo if id_crudo else "---"}</div>', unsafe_allow_html=True)
    with col_v_ico:
        # 🚀 CÁMARA POP-OVER CON MOTOR WEBRTC Y ENFOQUE CONTINUO FORZADO 🚀
        with st.popover("📷 SCAN QR", use_container_width=True):
            import streamlit.components.v1 as components
            
            components.html("""
            <div style="background-color: #0f172a; padding: 10px; border-radius: 8px; font-family: sans-serif; color: white; text-align: center;">
                <video id="video-stream-terminal" style="width: 100%; max-width: 300px; height: auto; border-radius: 6px; background-color: #000;" autoplay playsinline></video>
                <div id="status-scan-terminal" style="margin-top: 8px; font-weight: bold; color: #38bdf8; font-size: 14px;">📷 Acerque el QR del Balde</div>
            </div>
            
            <script src="https://jsdelivr.net"></script>
            <script>
                const video = document.getElementById('video-stream-terminal');
                const statusDiv = document.getElementById('status-scan-terminal');
                let trackActivo = null;
                
                // Forzamos resolución media para que el procesador de la tablet enfoque el macro al instante
                navigator.mediaDevices.getUserMedia({ 
                    video: { 
                        facingMode: "environment", 
                        width: { ideal: 640 }, 
                        height: { ideal: 480 } 
                    } 
                })
                .then(function(stream) {
                    video.srcObject = stream;
                    video.setAttribute("playsinline", true);
                    video.play();
                    
                    // 🧠 SISTEMA ANTI-DESENFOQUE DE HARDWARE
                    trackActivo = stream.getVideoTracks()[0];
                    const capabilities = trackActivo.getCapabilities ? trackActivo.getCapabilities() : {};
                    
                    // Si el dispositivo soporta enfoque continuo o macro, lo obligamos a fijarlo por código
                    let constraints = {};
                    if (capabilities.focusMode && capabilities.focusMode.includes('continuous')) {
                        constraints.focusMode = 'continuous';
                    }
                    if (Object.keys(constraints).length > 0) {
                        trackActivo.applyConstraints({ advanced: [constraints] }).catch(e => console.log(e));
                    }
                    
                    requestAnimationFrame(tick);
                })
                .catch(function(err) {
                    statusDiv.innerHTML = "🛑 Sin acceso al lente.";
                });

                function tick() {
                    if (video.readyState === video.HAVE_ENOUGH_DATA) {
                        const canvas = document.createElement("canvas");
                        canvas.width = video.videoWidth;
                        canvas.height = video.videoHeight;
                        const ctx = canvas.getContext("2d");
                        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                        
                        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                        const code = jsQR(imageData.data, imageData.width, imageData.height, { inversionAttempts: "dontInvert" });
                        
                        if (code && code.data) {
                            const idDetectado = code.data.trim();
                            // Validamos que el QR del balde sea un número express limpio (100-200)
                            if (!isNaN(idDetectado) && parseInt(idDetectado) >= 100 && parseInt(idDetectado) <= 200) {
                                statusDiv.innerHTML = "✅ Balde #" + idDetectado + " Leído";
                                statusDiv.style.color = "#10b981";
                                
                                // Mandamos el ID al instante a la memoria base de Streamlit
                                window.parent.postMessage({ type: "ANTIVERO_QR_TERMINAL", id_express: idDetectado }, "*");
                            }
                        }
                    }
                    requestAnimationFrame(tick);
                }
            </script>
            """, height=310)

        # 🚀 RECEPTOR INTERNO EN PYTHON: Carga el número en la caja express y libera el mesón
        st.html("""
        <script>
            window.addEventListener('message', function(e) {
                if (e.data && e.data.type === 'ANTIVERO_QR_TERMINAL') {
                    const inputs = window.parent.document.querySelectorAll('input');
                    inputs.forEach(input => {
                        // Inyectamos el ID express directo en la memoria caché de la terminal
                        if (input.getAttribute('key') === 'input_recup_manual' || (input.getAttribute('aria-label') && input.getAttribute('aria-label').includes('ID'))) {
                            input.value = e.data.id_express;
                            input.dispatchEvent(new Event('input', { bubbles: true }));
                        }
                    });
                }
            });
        </script>
        """)


    st.write("")
    
    # Matriz Numérica del 1 al 9
    filas_num = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"]]
    for fila in filas_num:
        cols = st.columns(3)
        for idx, digito in enumerate(fila):
            with cols[idx]:
                if st.button(digito, key=f"btn_term_fijo_{digito}", use_container_width=True):
                    if len(st.session_state.id_express_cosecha) < 3:
                        st.session_state.id_express_cosecha += digito
                        st.rerun()
                        
    # Hilera Inferior: K, 0 y botón gris ← para borrar un solo dígito
    col_inf1, col_inf2, col_inf3 = st.columns(3)
    with col_inf1:
        if st.button("K", key="btn_term_K_fijo", use_container_width=True):
            if len(st.session_state.id_express_cosecha) < 3:
                st.session_state.id_express_cosecha += "K"
                st.rerun()
    with col_inf2:
        if st.button("0", key="btn_term_0_fijo", use_container_width=True):
            if len(st.session_state.id_express_cosecha) < 3:
                st.session_state.id_express_cosecha += "0"
                st.rerun()
    with col_inf3:
        if st.button("←", key="btn_term_RETRO_1_fijo", use_container_width=True):
            st.session_state.id_express_cosecha = st.session_state.id_express_cosecha[:-1]
            st.rerun()
            
    # 🟥 Línea Roja Horizontal de Borrado Total
    st.write("")
    st.markdown('<div class="barra-roja-clear">', unsafe_allow_html=True)
    if st.button("borrar", key="btn_term_CLEAR_M_fijo", use_container_width=True):
        st.session_state.id_express_cosecha = ""
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 🟦 Línea Azul Horizontal de ENTER
    st.write("")
    st.markdown('<div class="barra-azul-enter">', unsafe_allow_html=True)
    if st.button("enter", key="btn_term_ENTER_M_fijo", use_container_width=True):
        if ficha_es_valida: st.success("🔓 Ficha Cargada")
        else: st.error("❌ Ficha Vacía")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.session_state.rut_bloqueado_operacion = not ficha_es_valida
# ==================================================================
# 4.C FUNCIÓN ESPEJO: ENROLAMIENTO MATINAL (DISEÑO EXACTO FOTO)
# ==================================================================
def dibujar_teclado_enrolamiento_antivero():
    st.html("""
        <style>
            .cuadro-teclado-enrol { max-width: 350px; margin: 10px auto; box-sizing: border-box; }
            .cuadro-teclado-enrol [data-testid="stHorizontalBlock"] { flex-direction: row !important; display: flex !important; gap: 8px !important; margin-bottom: 8px !important; }
            .cuadro-teclado-enrol div[data-testid="column"] { margin-bottom: 0 !important; }
            
            .cuadro-teclado-enrol button {
                background-color: #1e293b !important; color: #f8fafc !important;
                border: 1px solid #334155 !important; border-radius: 8px !important;
                font-size: 22px !important; font-weight: bold !important; height: 56px !important;
            }
            .cuadro-teclado-enrol button:active { background-color: #38bdf8 !important; color: #0f172a !important; }
            
            /* 🟥 Barra Roja Horizontal de Borrado Total (C) */
            .cuadro-teclado-enrol .barra-roja-clear-enrol button { background-color: #ef4444 !important; border: 1px solid #dc2626 !important; height: 52px !important; }
            .cuadro-teclado-enrol .barra-roja-clear-enrol button p { color: #ffffff !important; font-weight: bold !important; font-size: 18px !important; }
            
            /* 🟦 Barra Azul Horizontal de ENTER */
            .cuadro-teclado-enrol .barra-azul-enter-enrol button { background-color: #2563eb !important; border: 1px solid #1d4ed8 !important; height: 54px !important; }
            .cuadro-teclado-enrol .barra-azul-enter-enrol button p { color: #ffffff !important; font-weight: bold !important; font-size: 16px !important; }
        </style>
    """)
    
    st.subheader("📍 Identificación de Campo (Matinal)")
    
    # Conectamos el selector matinal directo a la lista dinámica de Firebase
    cc_manana = st.selectbox(
        "Origen (Centro de Costo)", 
        ["Seleccione Centro de Costo...", *lista_cc_dinamica], 
        key="cc_selector_agricola_enrol_fijo"
    )
    
    # Conectamos el contratista matinal directo a la lista dinámica de Firebase
    contratista_manana = st.selectbox(
        "Contratista Destino (Kame B2B)", 
        ["Seleccione Contratista...", *lista_b2b_dinamica], 
        key="contratista_selector_b2b_enrol_fijo"
    )


    st.write("")
    st.markdown("<label>👤 RUT Cosechador a Enrolar</label>", unsafe_allow_html=True)

    if "rut_asistencia_matinal" not in st.session_state: 
        st.session_state.rut_asistencia_matinal = ""
    rut_crudo = st.session_state.rut_asistencia_matinal
    rut_visible = f"{rut_crudo[:-1]}-{rut_crudo[-1]}".upper() if len(rut_crudo) > 1 else rut_crudo.upper()
    if not rut_crudo: rut_visible = "00.000.000-0"
    
    import __main__ as main
    rut_es_valido = main.validar_rut_chileno(rut_crudo) if (rut_crudo and hasattr(main, 'validar_rut_chileno')) else False
    icono_verificacion = "✅" if rut_es_valido else "🛑"
    
    st.markdown('<div class="cuadro-teclado-enrol">', unsafe_allow_html=True)
    
    col_visor_texto, col_visor_icono = st.columns([3, 1])
    with col_visor_texto:
        st.markdown(f'<div class="rut-display-box" style="font-size:22px; min-height:48px; margin-bottom:0; background-color:#1e293b;">{rut_visible}</div>', unsafe_allow_html=True)
    with col_visor_icono:
        st.markdown(f'<div class="rut-display-box" style="font-size:22px; min-height:48px; margin-bottom:0; background-color:#1e293b; text-align:center;">{icono_verificacion}</div>', unsafe_allow_html=True)
        
    st.write("")
    
    # Matriz del 1 al 9
    filas_maqueta = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"]]
    for fila in filas_maqueta:
        cols_n = st.columns(3)
        for idx, digito in enumerate(fila):
            with cols_n[idx]:
                if st.button(digito, key=f"btn_enrol_{digito}", use_container_width=True):
                    if len(st.session_state.rut_asistencia_matinal) < 9:
                        st.session_state.rut_asistencia_matinal += digito
                        st.rerun()
                        
    # Hilera Inferior: K, 0 y botón gris ← para borrar un solo dígito
    col_inf1, col_inf2, col_inf3 = st.columns(3)
    with col_inf1:
        if st.button("K", key="btn_enrol_K", use_container_width=True):
            if len(st.session_state.rut_asistencia_matinal) < 9:
                st.session_state.rut_asistencia_matinal += "K"
                st.rerun()
    with col_inf2:
        if st.button("0", key="btn_enrol_0", use_container_width=True):
            if len(st.session_state.rut_asistencia_matinal) < 9:
                st.session_state.rut_asistencia_matinal += "0"
                st.rerun()
    with col_inf3:
        if st.button("←", key="btn_enrol_RETRO_1", use_container_width=True):
            st.session_state.rut_asistencia_matinal = st.session_state.rut_asistencia_matinal[:-1]
            st.rerun()
            
    # 🟥 Barra Roja Horizontal de Borrado Total (C)
    st.write("")
    st.markdown('<div class="barra-roja-clear-enrol">', unsafe_allow_html=True)
    if st.button("C", key="btn_enrol_CLEAR_M", use_container_width=True):
        st.session_state.rut_asistencia_matinal = ""
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 🟦 Barra Azul Horizontal de ENTER (Validar Ingreso)
    st.write("")
    st.markdown('<div class="barra-azul-enter-enrol">', unsafe_allow_html=True)
    bloqueo_enrol = not rut_es_valido or cc_manana == "Seleccione Centro de Costo..." or contratista_manana == "Seleccione Contratista..."
    
    if st.button("💾 ENTER (Validar Ingreso)", key="btn_enrol_ENTER_M", use_container_width=True, disabled=bloqueo_enrol):
        try:
            tz_cl = zoneinfo.ZoneInfo("America/Santiago")
            ahora_cl = datetime.datetime.now(tz_cl)
            fecha_hoy_str = ahora_cl.strftime("%Y-%m-%d")
            
            # Consultamos la base para buscar el ID express disponible hoy
            ya_enrolados = db.collection("credenciales_activas_dia").where("FechaFiltro", "==", fecha_hoy_str).stream()
            numeros_ocupados = [int(doc.to_dict().get("id_express")) for doc in ya_enrolados if doc.to_dict().get("id_express")]
            
            id_express = 100
            for num in range(100, 201):
                if num not in numeros_ocupados:
                    id_express = num
                    break
                    
            rut_limpio = rut_crudo.replace(".", "").replace("-", "").strip().lower()
            
            # 🚀 CÓDIGO LARGO HISTÓRICO DE AUDITORÍA PERFECTO 🚀
            codigo_largo_auditoria = f"{ahora_cl.strftime('%Y%m%d')}-{rut_limpio}-{id_express}"
            
            db.collection("credenciales_activas_dia").document(str(id_express)).set({
                "id_express": str(id_express),
                "RutCosechador": rut_limpio,
                "CentroCosto": cc_manana,
                "Contratista": contratista_manana,
                "CodigoLargoAuditoria": codigo_largo_auditoria,
                "FechaEnrolamiento": ahora_cl,
                "FechaFiltro": fecha_hoy_str
            })
            
            qr = qrcode.QRCode(version=1, box_size=8, border=1)
            qr.add_data(str(id_express))
            qr.make(fit=True)
            
            buf = io.BytesIO()
            qr.make_image(fill_color="black", back_color="white").save(buf, format="PNG")
            
            st.session_state.qr_render_actual = buf.getvalue()
            st.session_state.id_render_actual = id_express
            st.session_state.rut_asistencia_matinal = ""
            st.rerun()
        except Exception as ex:
            st.error(f"❌ Error en el enrolamiento: {ex}")
            
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Despliegue del Ticket QR impreso en pantalla con Botón de Impresión al Costado
    qr_activo = st.session_state.get("qr_render_actual", None)
    if "imprimir_ficha_trigger" not in st.session_state:
        st.session_state.imprimir_ficha_trigger = False
        
    if qr_activo:
        st.write("")
        with st.container(border=True):
            # Dividimos la tarjeta en 2 columnas simétricas
            col_ticket_qr, col_ticket_btn = st.columns([1.5, 1.5])
            
            with col_ticket_qr:
                st.image(qr_activo, caption=f"Ficha #{st.session_state.id_render_actual} Generada", width=160)
                
            with col_ticket_btn:
                st.write("")
                st.write("")
                # Botón de impresión instantánea al costado del QR
                if st.button("🖨️ IMPRIMIR FICHA", key="btn_print_ficha_matinal", use_container_width=True, type="primary"):
                    st.session_state.imprimir_ficha_trigger = True
                    st.rerun()
                    
                st.write("")
                if st.button("🗑️ Siguiente Operario", key="clear_qr_view", use_container_width=True):
                    st.session_state.qr_render_actual = None
                    st.session_state.imprimir_ficha_trigger = False
                    st.rerun()
                    
            # Disparador JavaScript que envía la orden física directa a la ticketera térmica
            if st.session_state.imprimir_ficha_trigger:
                st.session_state.imprimir_ficha_trigger = False
                st.html("""
                    <script>
                        setTimeout(function() {
                            window.parent.print();
                        }, 150);
                    </script>
                """)
# ==================================================================
# 2. CONFIGURACIÓN VISUAL MAESTRA INTERFAZ TABLET FLORES ANTIVERO
# ==================================================================
st.set_page_config(layout="wide", page_title="Flores Antivero Cosecha")
st.html("""
    <style>
        :root {
            --bg-dark: #0f172a;
            --panel-bg: #1e293b;
            --text-light: #f8fafc;
            --text-muted: #94a3b8;
            --border-color: #334155;
            --accent-blue: #38bdf8;
        }
        .stApp { background-color: var(--bg-dark) !important; color: var(--text-light) !important; }
        .antivero-header { background: var(--panel-bg); padding: 15px 20px; border-radius: 12px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border: 1px solid var(--border-color); }
        .antivero-header h1 { margin: 0; font-size: 22px; color: var(--accent-blue) !important; font-weight: bold; }
        .stSelectbox label, .stTextInput label { font-weight: 700 !important; font-size: 12px !important; color: var(--text-muted) !important; text-transform: uppercase !important; }
        .rut-display-box { background: var(--bg-dark); border: 2px solid #475569; border-radius: 8px; padding: 12px; text-align: center; font-size: 26px; font-weight: bold; color: var(--accent-blue); min-height: 58px; margin-bottom: 10px; }
        
        /* 🚀 1. REPARACIÓN DEFECTOS PESTAÑAS MÁSTER SUPERIORES EN TABLET (TEXTO BLANCO) 🚀 */
        .stApp [data-testid="stTabs"] [role="tablist"] button {
            min-width: 180px !important;
            flex-grow: 1 !important;
            text-align: center !important;
            font-size: 15px !important;
            padding: 12px 16px !important;
            background-color: #1e293b !important;
            border: 1px solid #334155 !important;
            border-radius: 8px 8px 0 0 !important;
            color: #ffffff !important; /* FORZAMOS TEXTO BLANCO BRILLANTE PARA LAS INACTIVAS */
            opacity: 0.9 !important;
        }
        .stApp [data-testid="stTabs"] [role="tablist"] button p {
            color: #ffffff !important; /* Escudo doble para navegadores móviles */
        }
        .stApp [data-testid="stTabs"] [role="tablist"] button[aria-selected="true"] {
            background-color: #38bdf8 !important;
            color: #0f172a !important;
            font-weight: bold !important;
            opacity: 1 !important;
        }
        .stApp [data-testid="stTabs"] [role="tablist"] button[aria-selected="true"] p {
            color: #0f172a !important; /* Texto oscuro para la pestaña que está activa */
        }


        /* 🚀 2. REPARACIÓN DEL RUT VERDE CON FONDO BLANCO EN EL MESÓN DE CARGA 🚀 */
        code, span[data-testid="stMarkdownMutedText"] {
            background-color: #0f172a !important;
            color: #38bdf8 !important;
            padding: 4px 8px !important;
            border-radius: 4px !important;
            font-size: 16px !important;
            font-weight: bold !important;
            border: 1px solid #334155 !important;
        }

        /* Estilos base para los botones del sistema */
        div[data-testid="stButton"] button { 
            background-color: var(--panel-bg) !important; 
            color: var(--text-light) !important; 
            border: 1px solid var(--border-color) !important; 
            font-weight: bold !important; 
            font-size: 15px !important; 
        }
        div[data-testid="stButton"] button p { color: var(--text-light) !important; }
        div[data-testid="stButton"] button:active, div[data-testid="stButton"] button:focus { background-color: var(--accent-blue) !important; color: var(--bg-dark) !important; border-color: var(--accent-blue) !important; }
        div[data-testid="stButton"] button:active p, div[data-testid="stButton"] button:focus p { color: var(--bg-dark) !important; }
        
        @media (max-width: 768px) {
            .stMainBlock > div > [data-testid="stHorizontalBlock"] { flex-direction: column !important; }
            .stMainBlock > div > [data-testid="stHorizontalBlock"] > div[data-testid="column"] { width: 100% !important; margin-left: 0 !important; margin-bottom: 15px !important; }
            .antivero-header h1 { font-size: 18px; }
        }
        div[data-testid="stElementToolbar"] { display: none !important; }
        div[data-testid="stDataFrameGridContainer"] button { display: none !important; }
    </style>
""")


# ==================================================================
# CONFIGURACIÓN DEL ENCABEZADO CON FECHA Y HORA OFICIAL DE CHILE
# ==================================================================
zona_chile = zoneinfo.ZoneInfo("America/Santiago")
ahora_chile = datetime.datetime.now(zona_chile)
hora_actual = ahora_chile.strftime("%H:%M")
fecha_actual = ahora_chile.strftime("%d/%m/%Y")

st.html(f"""
<div class="antivero-header">
    <div>
        <h1>🚜 Flores Antivero — Terminal de Cosecha v2.0</h1>
        <div style="font-size: 13px; color: #94a3b8; margin-top: 4px;">Fecha de Campo: {fecha_actual}</div>
    </div>
    <div style="font-weight: bold; font-size: 24px; color: #38bdf8;">{hora_actual}</div>
</div>
""")

# Inicialización segura de estados globales en Session State
if "usuario_conectado" not in st.session_state:
    st.session_state.usuario_conectado = False
if "rol_usuario" not in st.session_state:
    st.session_state.rol_usuario = "operario"
if "rut_cosechador" not in st.session_state:
    st.session_state.rut_cosechador = ""
if "id_usuario_activo" not in st.session_state:
    st.session_state.id_usuario_activo = ""

# ==================================================================
# SINCRONIZACIÓN AUTOMÁTICA EN VIVO DEL CATÁLOGO DESDE FIREBASE
# ==================================================================
# 1. Lectura de Centros de Costo con respaldo estático original
try:
    docs_cc = db.collection("config_centros").order_by("nombre").stream()
    lista_cc_dinamica = [doc.to_dict().get("nombre") for doc in docs_cc if doc.to_dict().get("nombre")]
    if not lista_cc_dinamica:
        lista_cc_dinamica = ["Las Rosas (CC 01)", "Chipana (CC 02)"]
except Exception:
    lista_cc_dinamica = ["Las Rosas (CC 01)", "Chipana (CC 02)"]

# 2. Lectura de Contratistas con respaldo estático original
try:
    docs_b2b = db.collection("config_contratistas").order_by("fecha_creacion", direction=firestore.Query.DESCENDING).stream()
    lista_b2b_dinamica = [doc.to_dict().get("formato_kame") for doc in docs_b2b if doc.to_dict().get("formato_kame")]
    if not lista_b2b_dinamica:
        lista_b2b_dinamica = [
            "76.543.210-K | Servicios Agrícolas del Maule",
            "77.123.456-7 | Agrícola San Fernando Limitada",
            "76.999.888-2 | Mano de Obra Terreno SpA"
        ]
except Exception:
    lista_b2b_dinamica = [
        "76.543.210-K | Servicios Agrícolas del Maule",
        "77.123.456-7 | Agrícola San Fernando Limitada",
        "76.999.888-2 | Mano de Obra Terreno SpA"
    ]

# 3. Lectura de Flores y Variedades del Catálogo (Clasificación Botánica Estricta)
diccionario_flores_dinamico = {
    "Ranunculo Romance": [], 
    "Ranunculo Elegance": [], 
    "Peonía": [], 
    "Delphinium": []
}
try:
    docs_flores = db.collection("config_flores").stream()
    for doc in docs_flores:
        dat = doc.to_dict()
        fam_cruda = str(dat.get("familia", "")).strip().lower()
        cod_f = dat.get("codigo")
        nom_f = dat.get("nombre", "Sin Nombre")
        color_f = dat.get("color", "#94a3b8")
        
        if cod_f is not None and nom_f != "Sin Nombre":
            objeto_flor = {"codigo": int(cod_f), "nombre": str(nom_f), "color": str(color_f)}
            
            # Clasificación por hilos de texto exactos de la especie
            if "romance" in fam_cruda:
                diccionario_flores_dinamico["Ranunculo Romance"].append(objeto_flor)
            elif "elegance" in fam_cruda:
                diccionario_flores_dinamico["Ranunculo Elegance"].append(objeto_flor)
            elif "peon" in fam_cruda:
                diccionario_flores_dinamico["Peonía"].append(objeto_flor)
            elif "delphi" in fam_cruda:
                diccionario_flores_dinamico["Delphinium"].append(objeto_flor)
except Exception as e_cat_flores:
    st.caption(f"⚠️ Alerta catálogo: {e_cat_flores}")


except Exception:
    pass

# GATILLO DE TERRENO: Descarga automática de registros bajo huso horario estricto chileno
lista_datos_dia = []
try:
    inicio_hoy = datetime.datetime.combine(datetime.date.today(), datetime.time.min, tzinfo=zona_chile)
    fin_hoy = datetime.datetime.combine(datetime.date.today(), datetime.time.max, tzinfo=zona_chile)
    docs_hoy = db.collection("cosecha_diaria").where("FechaRegistro", ">=", inicio_hoy).where("FechaRegistro", "<=", fin_hoy).stream()
    lista_datos_dia = [doc.to_dict() for doc in docs_hoy]
    st.session_state.lista_datos_dia_cache = lista_datos_dia
except Exception as e_consulta_automatica:
    st.caption(f"⚠️ Nota de sincronización: {e_consulta_automatica}")
# ==================================================================
# 3. PORTAL DE ACCESO CON ENMASCARAMIENTO TOTAL ANTI-CONTRASURAS
# ==================================================================
if "usuario_conectado" not in st.session_state:
    st.session_state.usuario_conectado = False

if not st.session_state.usuario_conectado:
    # Inyección de estilos extremos para evitar autocompletado e inyecciones de Opera/Chrome
    st.html("""
    <style>
        /* Desactiva por completo los iconos flotantes de llaveros de contraseñas */
        input::-webkit-credentials-auto-fill-button,
        input::-webkit-contacts-auto-fill-button,
        div[data-testid="stTextInput"] iframe, 
        .password-icon {
            visibility: hidden !important;
            pointer-events: none !important;
            display: none !important;
        }
        /* Forzamos tipografía de círculos si el navegador intenta renderizar texto plano */
        .mascara-pass input {
            -webkit-text-security: disc !important;
            text-security: disc !important;
        }
    </style>
    <script>
        // Mutación forzada cada 300ms sobre el DOM real del dispositivo móvil/tablet
        setInterval(function() {
            const inputs = window.parent.document.querySelectorAll('input');
            inputs.forEach(input => {
                // Eliminamos cualquier rastro que active el gestor de contraseñas
                input.removeAttribute('name');
                input.removeAttribute('id');
                if (input.getAttribute('type') === 'password') {
                    // Si el navegador forzó un tipo password, lo degradamos a texto enmascarado por CSS
                    input.setAttribute('type', 'text');
                }
                input.setAttribute('autocomplete', 'new-password-off-' + Math.random().toString(36).substring(5));
                input.setAttribute('autocorrect', 'off');
                input.setAttribute('autocapitalize', 'off');
                input.setAttribute('spellcheck', 'false');
            });
        }, 300);
    </script>
    """)

    st.markdown("<h3 style='text-align: center; color: #38bdf8;'>Acceso Cosecha Flores</h3>", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("### Iniciar Sesión")
        
        input_usuario = st.text_input(
            "INGRESA TU RUT:", 
            key="campo_neutro_user",
            placeholder="Ej: 12345678k"
        ).strip().lower()
        
        # Usamos text_input común (tipo texto plano para el navegador) con clase de enmascaramiento CSS
        st.markdown('<div class="mascara-pass">', unsafe_allow_html=True)
        input_clave = st.text_input(
            "CONTRASEÑA DE ACCESO:", 
            key="campo_neutro_pass",
            placeholder="••••••••"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.write("")
        if st.button("Ingresar al Sistema", key="btn_auth_login_submit", use_container_width=True, type="primary"):
            if input_usuario and input_clave:
                try:
                    user_ref = db.collection("usuarios").document(input_usuario).get()
                    if user_ref.exists and user_ref.to_dict().get("password") == input_clave:
                        st.session_state.usuario_conectado = True
                        st.session_state.rol_usuario = user_ref.to_dict().get("rol", "operario")
                        st.session_state.id_usuario_activo = input_usuario
                        st.rerun()
                    else:
                        st.error("La contraseña o el usuario ingresado son incorrectos.")
                except Exception as e:
                    st.error(f"Error de conexión con el servidor de Google: {e}")
            else:
                st.warning("Por favor, complete ambos campos.")
                
    # ==============================================================
    # RESTAURACIÓN MÁSTER: RECUPERACIÓN DE CLAVES EXTRAS DE TERRENO 
    # ==============================================================
    st.write("---")
    with st.expander("¿Olvidó su Contraseña o RUT Inválido?", expanded=False):
        st.caption("Solicite un cambio express. El administrador aprobará su nueva clave desde el Panel de Auditoría.")
        with st.form("form_recuperacion_express_clave", clear_on_submit=True):
            rut_olvido = st.text_input(
                "Ingrese su RUT para Alerta (Sin puntos ni guñón):", 
                placeholder="Ej: 174031711", 
                key="recup_rut_input"
            ).strip().lower()
            
            if st.form_submit_button("Enviar Alerta Express de Cambio", use_container_width=True):
                if rut_olvido and len(rut_olvido) >= 7:
                    try:
                        db.collection("solicitudes_clave").document(rut_olvido).set({
                            "usuario": rut_olvido,
                            "estado": "pendiente",
                            "fecha_solicitud": datetime.datetime.now(zoneinfo.ZoneInfo("America/Santiago"))
                        })
                        st.success(f"Alerta enviada con éxito para el RUT {rut_olvido}. Dé aviso al supervisor de turno.")
                    except Exception as e_sol:
                        st.error(f"Error al conectar la alerta: {e_sol}")
                else:
                    st.warning("Ingrese un RUT válido de campo.")
    st.stop()



# ==================================================================
# 3. INTERFAZ PRINCIPAL (USUARIO AUTENTICADO Y SEGURIZADO)
# ==================================================================
with st.sidebar:
    st.markdown(f" **Usuario Activo:** `{st.session_state.id_usuario_activo.upper()}`")
    st.markdown(f" **Rol:** `{st.session_state.rol_usuario.upper()}`")
    st.write("---")
    
    with st.expander(" Cambiar mi Contraseña", expanded=False):
        with st.form("form_cambio_clave_universal", clear_on_submit=True):
            nueva_p1 = st.text_input("Nueva Contraseña:", type="password", key="univ_p1")
            nueva_p2 = st.text_input("Confirmar Contraseña:", type="password", key="univ_p2")
            if st.form_submit_button("Guardar Nueva Clave", use_container_width=True):
                if nueva_p1 and nueva_p1 == nueva_p2 and len(nueva_p1) >= 4:
                    try:
                        db.collection("usuarios").document(st.session_state.id_usuario_activo).update({"password": nueva_p1})
                        st.success("¡Contraseña actualizada con éxito!")
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.error("Las claves no coinciden o tienen menos de 4 caracteres.")

    if st.session_state.rol_usuario == "admin":
        st.write("---")
        st.markdown("### Herramientas de Administrador")
        with st.expander(" Registrar Nuevo Operario", expanded=False):
            with st.form("form_registro_interno_admin", clear_on_submit=True):
                reg_rut = st.text_input("RUT Cosechador:", placeholder="Ej: 123456789", key="admin_reg_rut").strip().lower()
                reg_clave = st.text_input("Contraseña inicial:", type="password", key="admin_reg_pass")
                if st.form_submit_button("Crear Operario", use_container_width=True):
                    if reg_rut and len(reg_clave) >= 4:
                        try:
                            if db.collection("usuarios").document(reg_rut).get().exists:
                                st.error(" Este RUT ya existe en los registros.")
                            else:
                                db.collection("usuarios").document(reg_rut).set({"password": reg_clave, "rol": "operario"})
                                st.success(f"¡RUT {reg_rut} creado con éxito!")
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.warning(" Datos inválidos o clave muy corta.")
        with st.expander("🗑️ Eliminar Cuenta de Operario", expanded=False):
            with st.form("form_eliminar_operario", clear_on_submit=True):
                rut_a_borrar = st.text_input("RUT a eliminar (Sin puntos ni guión):", placeholder="Ej: 123456789", key="del_rut").strip().lower()
                confirmar_check = st.checkbox("Confirmo que deseo borrar permanentemente este usuario.")
                if st.form_submit_button("Eliminar de la Nube", use_container_width=True):
                    if rut_a_borrar and confirmar_check:
                        try:
                            doc_ref = db.collection("usuarios").document(rut_a_borrar)
                            if doc_ref.get().exists:
                                doc_ref.delete()
                                st.success(f"¡El usuario {rut_a_borrar} fue eliminado!")
                            else:
                                st.error("❌ El RUT ingresado no existe.")
                        except Exception as e:
                            st.error(f"Error al eliminar: {e}")
                    else:
                        st.warning("⚠️ Debes rellenar el campo y marcar la casilla de confirmación.")

        with st.expander("🚨 Alertas de Clave Olvidada", expanded=False):
            try:
                solicitudes = db.collection("solicitudes_clave").where("estado", "==", "pendiente").stream()
                lista_sol = [s.to_dict() for s in solicitudes]
                if not lista_sol:
                    st.caption("No hay alertas pendientes.")
                else:
                    for s in lista_sol:
                        st.warning(f"⚠️ Usuario: {s['usuario']}")
                        nueva_clave_express = st.text_input(f"Nueva clave para {s['usuario']}:", type="password", key=f"express_{s['usuario']}")
                        if st.button(f"Forzar cambio para {s['usuario']}", key=f"btn_exp_{s['usuario']}", use_container_width=True):
                            if len(nueva_clave_express) >= 4:
                                db.collection("usuarios").document(s["usuario"]).update({"password": nueva_clave_express})
                                db.collection("solicitudes_clave").document(s["usuario"]).update({"estado": "resuelto"})
                                st.success("¡Clave reconfigurada con éxito!")
                                st.rerun()
            except Exception as e:
                st.caption(f"Error al leer alertas: {e}")

    st.write("---")
    if st.button("🚪 Cerrar Sesión", use_container_width=True, type="secondary"):
        st.session_state.usuario_conectado = False
        st.session_state.rol_usuario = "operario"
        st.session_state.id_usuario_activo = ""
        st.rerun()

# ==================================================================
# ALGORITMO DE VALIDACIÓN DE RUT CHILENO (INTEGRADO EN LA RAÍZ)
# ==================================================================
def validar_rut_chileno(rut_str):
    rut_limpio = rut_str.replace(".", "").replace("-", "").strip().upper()
    if len(rut_limpio) < 2: return False
    cuerpo = rut_limpio[:-1]
    dv_ingresado = rut_limpio[-1]
    if not cuerpo.isdigit(): return False
    suma = 0
    multiplicador = 2
    for c in reversed(cuerpo):
        suma += int(c) * multiplicador
        multiplicador = 2 if multiplicador == 7 else multiplicador + 1
    remat = 11 - (suma % 11)
    dv_esperado = "0" if remat == 11 else ("K" if remat == 10 else str(remat))
    return dv_ingresado == dv_esperado

# ==================================================================
# FORMATEADOR MAESTRO DE RUT DIARIO (PUNTOS Y GUION AUTOMÁTICOS)
# ==================================================================
def formatear_rut_chileno_completo(rut_str):
    rut_limpio = rut_str.replace(".", "").replace("-", "").strip().upper()
    if len(rut_limpio) < 2:
        return rut_limpio
    cuerpo = rut_limpio[:-1]
    dv = rut_limpio[-1]
    if cuerpo.isdigit():
        cuerpo_int = int(cuerpo)
        return f"{cuerpo_int:,}-{dv}".replace(",", ".")
    else:
        return f"{cuerpo}-{dv}"

# ==================================================================
# 5. ENRUTADOR DE PESTAÑAS AGRÍCOLAS REFORZADO (3 CASILLAS)
# ==================================================================
if st.session_state.rol_usuario == "admin":
    tab_terminal, tab_credenciales, tab_auditoria = st.tabs([
        "🚜 Terminal de Cosecha", 
        "📋 Credenciales del Día (Fichas express)", 
        "📊 Panel de Control y Auditoría"
    ])
else:
    tab_terminal, tab_credenciales = st.tabs([
        "🚜 Terminal de Cosecha", 
        "📋 Credenciales del Día (Fichas express)"
    ])
    tab_auditoria = None
    with st.expander("🗑️ Eliminar Cuenta de Operario", expanded=False):
        with st.form("form_eliminar_operario", clear_on_submit=True):
            rut_a_borrar = st.text_input("RUT a eliminar (Sin puntos ni guión):", placeholder="Ej: 123456789", key="del_rut").strip().lower()
            confirmar_check = st.checkbox("Confirmo que deseo borrar permanentemente este usuario SpA.")
            if st.form_submit_button("Eliminar de la Nube", use_container_width=True):
                if rut_a_borrar and confirmar_check:
                    try:
                        doc_ref = db.collection("usuarios").document(rut_a_borrar)
                        if doc_ref.get().exists:
                            doc_ref.delete()
                            st.success(f"¡El usuario {rut_a_borrar} fue eliminado de FirebaseSpA!")
                        else:
                            st.error("❌ El RUT ingresado no existe.")
                    except Exception as e:
                        st.error(f"Error al eliminar: {e}")
                else:
                    st.warning("⚠️ Debes rellenar el campo y marcar la casilla de confirmación.")

                        
        with st.expander("🚨 Alertas de Clave Olvidada", expanded=False):
            try:
                solicitudes = db.collection("solicitudes_clave").where("estado", "==", "pendiente").stream()
                lista_sol = [s.to_dict() for s in solicitudes]
                if not lista_sol:
                    st.caption("No hay alertas pendientes.")
                else:
                    for s in lista_sol:
                        st.warning(f"⚠️ Usuario: {s['usuario']}")
                        nueva_clave_express = st.text_input(f"Nueva clave para {s['usuario']}:", type="password", key=f"express_{s['usuario']}")
                        if st.button(f"Forzar cambio para {s['usuario']}", key=f"btn_exp_{s['usuario']}", use_container_width=True):
                            if len(nueva_clave_express) >= 4:
                                db.collection("usuarios").document(s["usuario"]).update({"password": nueva_clave_express})
                                db.collection("solicitudes_clave").document(s["usuario"]).update({"estado": "resuelto"})
                                st.success("¡Clave reconfigurada con éxito!")
                                st.rerun()
            except Exception as e:
                st.caption(f"Error al leer alertas: {e}")
                
    st.write("---")
    if st.button("🚪 Cerrar Sesión", use_container_width=True, type="secondary"):
        st.session_state.usuario_conectado = False
        st.session_state.rol_usuario = "operario"
        st.session_state.id_usuario_activo = ""
        st.rerun()

# ==================================================================
# ALGORITMO DE VALIDACIÓN DE RUT CHILENO (INTEGRADO EN LA RAÍZ)
# ==================================================================
def validar_rut_chileno(rut_str):
    rut_limpio = rut_str.replace(".", "").replace("-", "").strip().upper()
    if len(rut_limpio) < 2: return False
    cuerpo = rut_limpio[:-1]
    dv_ingresado = rut_limpio[-1]
    if not cuerpo.isdigit(): return False
    suma = 0
    multiplicador = 2
    for c in reversed(cuerpo):
        suma += int(c) * multiplicador
        multiplicador = 2 if multiplicador == 7 else multiplicador + 1
    remat = 11 - (suma % 11)
    dv_esperado = "0" if remat == 11 else ("K" if remat == 10 else str(remat))
    return dv_ingresado == dv_esperado

# ==================================================================
# FORMATEADOR MAESTRO DE RUT DIARIO (PUNTOS Y GUION AUTOMÁTICOS)
# ==================================================================
def formatear_rut_chileno_completo(rut_str):
    rut_limpio = rut_str.replace(".", "").replace("-", "").strip().upper()
    if len(rut_limpio) < 2:
        return rut_limpio
    cuerpo = rut_limpio[:-1]
    dv = rut_limpio[-1]
    if cuerpo.isdigit():
        cuerpo_int = int(cuerpo)
        return f"{cuerpo_int:,}-{dv}".replace(",", ".")
    else:
        return f"{cuerpo}-{dv}"

# --- CONTENIDO DE LA PESTAÑA CENTRAL: REGISTRO DE CREDENCIALES ---
with tab_credenciales:
    st.markdown("<h2 style='color:#38bdf8;'>📋 Registro y Enrolamiento de Fichas Express</h2>", unsafe_allow_html=True)
    st.caption("Configure el contratista, digite el RUT en el teclado espejo para otorgar un ID con QR.")
    
    col_enrol_izq, col_enrol_der = st.columns([1.3, 2.7])
    with col_enrol_izq:
        dibujar_teclado_enrolamiento_antivero()
    with col_enrol_der:
        st.markdown("### 📷 Escáner QR de Cédula de Identidad (Mesón)")
        st.caption("Enfoque el código QR del carnet (reverso). El sistema procesará el RUT de forma automática:")
        
        # 🚀 INYECCIÓN HTML5 WEBRTC DIRECTA CON AUTOENFOQUE CONTINUO CRÍTICO 🚀
        import streamlit.components.v1 as components
        components.html("""
        <div style="background-color: #1e293b; padding: 12px; border-radius: 10px; border: 1px solid #334155; font-family: sans-serif; color: #f8fafc; text-align: center;">
            <p style="margin-top:0; font-size:14px; color:#94a3b8;">Lector QR Directo por Cámara (Enfoque Continuo)</p>
            <video id="video-stream-matinal" style="width: 100%; max-width: 320px; height: auto; border-radius: 8px; background:#0f172a;" autoplay playsinline></video>
            <div id="status-lector-qr" style="margin-top: 10px; font-weight: bold; color: #38bdf8; font-size: 15px;">📷 Buscando Código QR...</div>
        </div>
        <script src="https://jsdelivr.net"></script>
        <script>
            const video = document.getElementById('video-stream-matinal');
            const statusDiv = document.getElementById('status-lector-qr');
            let trackActivo = null;
            
            // 🧠 RESOLUCIÓN OPTIMIZADA: 640x480 reduce la distorsión y facilita el enfoque macro en Android
            navigator.mediaDevices.getUserMedia({ 
                video: { facingMode: "environment", width: { ideal: 640 }, height: { ideal: 480 } } 
            })
            .then(function(stream) {
                video.srcObject = stream;
                video.setAttribute("playsinline", true);
                video.play();
                
                // 🧠 CONSTREÑIMIENTO DE ENFOQUE CONTINUO NATIVO
                trackActivo = stream.getVideoTracks()[0];
                setTimeout(() => {
                    const capabilities = trackActivo.getCapabilities ? trackActivo.getCapabilities() : {};
                    let constraints = {};
                    if (capabilities.focusMode && capabilities.focusMode.includes('continuous')) {
                        constraints.focusMode = 'continuous';
                    }
                    if (Object.keys(constraints).length > 0) {
                        trackActivo.applyConstraints({ advanced: [constraints] }).catch(e => console.log(e));
                    }
                }, 500); // Pequeño retraso para dar tiempo a la inicialización del sensor
                
                requestAnimationFrame(tick);
            }).catch(function(err) {
                statusDiv.innerHTML = "🛑 Permiso de cámara denegado o hardware ocupado.";
                statusDiv.style.color = "#ef4444";
            });

            function tick() {
                if (video.readyState === video.HAVE_ENOUGH_DATA) {
                    const canvas = document.createElement("canvas");
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                    const ctx = canvas.getContext("2d");
                    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                    const code = jsQR(imageData.data, imageData.width, imageData.height, { inversionAttempts: "dontInvert" });
                    
                    if (code && code.data.includes("RUN=")) {
                        statusDiv.innerHTML = "🎯 ¡Cédula Detectada con Éxito!";
                        statusDiv.style.color = "#10b981";
                        const urlParams = new URLSearchParams(code.data.split('?'));
                        const r = urlParams.get('RUN');
                        if (r) {
                            window.parent.postMessage({ type: 'QR_CARNET_DETECTADO', rut: r.replace("-", "").trim().toLowerCase() }, '*');
                        }
                    }
                }
                requestAnimationFrame(tick);
            }
        </script>
        """, height=340)


        # 🚀 OÍDOR DE EVENTOS EN PYTHON: Atrapa el RUT enviado por JavaScript y actualiza la app
        st.html("""
        <script>
            window.addEventListener('message', function(e) {
                if (e.data && e.data.type === 'ANTIVERO_QR_CARNET') {
                    // Buscamos la caja de texto del RUT matinal en la columna izquierda y le inyectamos el valor
                    const inputs = window.parent.document.querySelectorAll('input');
                    inputs.forEach(input => {
                        // Buscamos el widget asociado a la clave de la mañana
                        if (input.getAttribute('aria-label') && input.getAttribute('aria-label').includes('RUT')) {
                            input.value = e.data.rut;
                            input.dispatchEvent(new Event('input', { bubbles: true }));
                        }
                    });
                }
            });
        </script>
        """)


        # --- TABLA DE CONTROL EN VIVO DE CREDENCIALES DEL DÍA ---
        try:
            tz_local = zoneinfo.ZoneInfo("America/Santiago")
            fecha_filtro_hoy = datetime.datetime.now(tz_local).strftime("%Y-%m-%d")
            
            # Consultamos las fichas que corresponden a la fecha de hoy en Chile
            docs_enrolados = db.collection("credenciales_activas_dia").where("FechaFiltro", "==", fecha_filtro_hoy).stream()
            lista_enrolados_dia = [doc.to_dict() for doc in docs_enrolados]
            
            if lista_enrolados_dia:
                df_enrolados = pd.DataFrame(lista_enrolados_dia)
                import __main__ as main
                if "RutCosechador" in df_enrolados.columns and hasattr(main, "formatear_rut_chileno_completo"):
                    df_enrolados["RutCosechador"] = df_enrolados["RutCosechador"].apply(main.formatear_rut_chileno_completo)
                
                columnas_asistencia = ["id_express", "RutCosechador", "CentroCosto", "CodigoLargoAuditoria"]
                df_asistencia_render = df_enrolados[columnas_asistencia].sort_values(by="id_express")
                
                # 1. TABLA FLUIDA Y ESTABLE (CERO RECARGAS FANTASMAS)
                st.dataframe(df_asistencia_render, use_container_width=True, hide_index=True)
                
                # 🚀 LA CORRECCIÓN: Declaramos la lista de IDs de hoy directo desde los datos de Firebase 🚀
                lista_ids_hoy = [str(x) for x in df_asistencia_render["id_express"].tolist()]
                
                # 🚀 REGENERADOR INDEPENDIENTE LIBRE DE ERRORES DE INSTANCIACIÓN
                st.write("")
                st.markdown("<h4 style='color:#38bdf8;'>🖨️ Módulo de Reimpresión de Fichas Extraviadas</h4>", unsafe_allow_html=True)
                
                id_a_recuperar = st.text_input(
                    "Digite el número de ID Express a recuperar (Ej: 105):",
                    placeholder="Escriba el número aquí...",
                    key="input_recuperador_manual_express"
                ).strip()
                
                if st.button("🔄 Regenerar y Cargar QR a la Izquierda", key="btn_ejecutar_reimpresion_limpio", use_container_width=True):
                    if id_a_recuperar in lista_ids_hoy:
                        try:
                            qr_reimp = qrcode.QRCode(version=1, box_size=8, border=1)
                            qr_reimp.add_data(str(id_a_recuperar))
                            qr_reimp.make(fit=True)
                            
                            buf_reimp = io.BytesIO()
                            qr_reimp.make_image(fill_color="black", back_color="white").save(buf_reimp, format="PNG")
                            
                            st.session_state.qr_render_actual = buf_reimp.getvalue()
                            st.session_state.id_render_actual = id_a_recuperar
                            
                            st.toast(f"🎟️ Ficha #{id_a_recuperar} cargada con éxito a la izquierda.")
                            st.fragment(lambda: None)
                            st.rerun()
                        except Exception as e_reimp:
                            st.error(f"❌ Error al reconstruir el código QR: {e_reimp}")
                    elif id_a_recuperar == "":
                        st.warning("⚠️ Por favor, ingrese un número de ID express válido antes de presionar el botón.")
                    else:
                        st.error(f"❌ El ID #{id_a_recuperar} no ha sido enrolado el día de hoy en este fundo.")



            else:
                st.info("📝 No hay operarios matriculados hoy.")
        except Exception as e_t:
            st.caption(f"Nota de visualización de asistencia: {e_t}")


# --- CONTENIDO DE LA PESTAÑA A: TERMINAL DE COSECHA AGRÍCOLA ---
with tab_terminal:
    col_panel_izq, col_panel_central_derecho = st.columns([1.2, 2.8])
    with col_panel_izq:
        # Llamamos al teclado de lectura express de tu fotografía
        dibujar_teclado_maqueta_antivero()
        
    with col_panel_central_derecho:
        if "flor_seleccionada_meson" not in st.session_state:
            st.session_state.flor_seleccionada_meson = None
        if "cantidad_varas_meson" not in st.session_state:
            st.session_state.cantidad_varas_meson = 30
            
        col_centro_flujo, col_derecha_consolidacion = st.columns([1.6, 1.2])
        with col_centro_flujo:
            st.markdown("<h3 style='margin:0 0 5px 0; color:#38bdf8;'>🌸 Selección de Familia de Flores</h3>", unsafe_allow_html=True)
            st.caption("Toque una familia en la grilla para desplegar sus variedades en el mesón:")
            
            bloqueo_activo = st.session_state.get("rut_bloqueado_operacion", True)
            
            # Inicializamos la memoria de la familia activa si no existe
            if "familia_activa_meson" not in st.session_state:
                st.session_state.familia_activa_meson = "Ranunculo Romance"
                
            # Estilos CSS corregidos y aislados para que no alteren los colores del mesón
            st.html("""
                <style>
                    /* Botones máster de Familias en la grilla de a dos */
                    button[key^="btn_grid_fam_"] {
                        border-radius: 8px !important;
                        padding: 12px !important;
                        font-weight: bold !important;
                        font-size: 15px !important;
                    }
                    /* Tarjeta en relieve fucsia para las variedades */
                    .tarjeta-flor-antivero { 
                        background-color: #1e293b !important; 
                        border: 1px solid #334155 !important; 
                        border-left: 6px solid #ec4899 !important; 
                        border-radius: 10px !important; 
                        padding: 14px 18px !important; 
                        width: 100% !important; 
                        text-align: left !important; 
                        min-height: 85px; 
                        pointer-events: none !important;
                    }
                    .punto-color-flor { 
                        display: inline-block !important; 
                        width: 14px !important; 
                        height: 14px !important; 
                        border-radius: 50% !important; 
                        margin-right: 10px !important; 
                        vertical-align: middle !important; 
                    }
                    /* Botón invisible sobre la tarjeta */
                    button[key^="btn_tarjeta_act_"] {
                        background-color: transparent !important;
                        border: none !important;
                        height: 85px !important;
                        width: 100% !important;
                        box-shadow: none !important;
                    }
                </style>
            """)

            # 🚀 LECTURA DINÁMICA DE FAMILIAS REGISTRADAS EN FIREBASE 🚀
            # Obtenemos las llaves del diccionario en tiempo real (Ranunculo Romance, Ranunculo Elegance, Peonía, Delphinium, etc.)
            familias_lista = list(diccionario_flores_dinamico.keys())
            if not familias_lista:
                familias_lista = ["Ranunculo Romance", "Ranunculo Elegance", "Peonía", "Delphinium"]
            
            # Generamos de forma automática los botones de familias organizados estrictamente en bloques de a dos hacia abajo
            for i in range(0, len(familias_lista), 2):
                par_familias = familias_lista[i:i+2]
                cols_fam = st.columns(2)
                for idx, fam_item in enumerate(par_familias):
                    with cols_fam[idx]:
                        # Si la familia es la seleccionada, se ilumina con tu color azul brillante
                        es_activa = (st.session_state.familia_activa_meson == fam_item)
                        tipo_boton = "primary" if es_activa else "secondary"
                        
                        prefix_icono = "🌹 " if "Romance" in fam_item else ("🌸 " if "Elegance" in fam_item else ("🌺 " if "Peon" in fam_item else "🌿 "))
                        
                        if st.button(f"{prefix_icono}{fam_item}", key=f"btn_grid_fam_{fam_item.replace(' ', '_')}", use_container_width=True, type=tipo_boton):
                            st.session_state.familia_activa_meson = fam_item
                            st.rerun()
            
            st.markdown("<hr style='margin:15px 0; border-color:#334155;'>", unsafe_allow_html=True)
            
            # DESPLIEGUE EXCLUSIVO DE LAS VARIADADES DE LA FAMILIA QUE ESTÁ PINCHADA
            familia_actual = st.session_state.familia_activa_meson
            lista_flores_render = diccionario_flores_dinamico.get(familia_actual, [])
            
            # Respaldos estáticos de tus páginas del PDF si Firebase está offline momentáneamente
            if not lista_flores_render and familia_actual == "Ranunculo Romance":
                lista_flores_render = [
                    {"codigo": 228, "nombre": "Ranunculo Romance Seine", "color": "#3b82f6"},
                    {"codigo": 230, "nombre": "Ranunculo Romance Montenvers", "color": "#a855f7"},
                    {"codigo": 226, "nombre": "Ranunculo Romance Nohan", "color": "#10b981"},
                    {"codigo": 227, "nombre": "Ranunculo Romance GetLucky", "color": "#f97316"}
                ]
            
            if lista_flores_render:
                st.markdown(f"<p style='color:#94a3b8; font-size:13px; margin-bottom:12px;'>Variedades activas en {familia_actual}:</p>", unsafe_allow_html=True)
                for i in range(0, len(lista_flores_render), 2):
                    bloque_par = lista_flores_render[i:i+2]
                    cols_f = st.columns(2)
                    for idx, flor in enumerate(bloque_par):
                        with cols_f[idx]:
                            cod_f = flor["codigo"]
                            nom_f = flor["nombre"]
                            color_punto = flor.get("color", "#94a3b8")
                            nombre_limpio = nom_f.replace(familia_actual + " ", "").replace("Peonía ", "").replace("Delphinium ", "").strip()
                            
                            if st.button("", key=f"btn_tarjeta_act_{cod_f}", use_container_width=True, disabled=bloqueo_activo):
                                st.session_state.flor_seleccionada_meson = {"codigo": cod_f, "nombre": nom_f}
                                st.session_state.cantidad_varas_meson = 30
                                st.rerun()
                                
                            st.html(f"""
                                <div class="tarjeta-flor-antivero" style="margin-top: -68px;">
                                    <div style="font-size: 18px; font-weight: bold; color: #f8fafc; margin-bottom: 4px;">
                                        <span class="punto-color-flor" style="background-color: {color_punto} !important;"></span>
                                        {nombre_limpio}
                                    </div>
                                    <div style="font-size: 13px; color: #94a3b8;">Código KAME: {cod_f}</div>
                                </div>
                            """)


        # ==============================================================
        # COLUMNA DERECHA REFORZADA: MESÓN DE CARGA ACTUAL (PÁGINA 44)
        # ==============================================================
        with col_derecha_consolidacion:
            st.markdown("<h2 style='color:#f8fafc;'>📥 Mesón de Carga Actual</h2>", unsafe_allow_html=True)
            
            rut_aux_meson = st.session_state.get("rut_cosechador", "")
            rut_final_meson = f"{rut_aux_meson[:-1]}-{rut_aux_meson[-1]}".upper() if len(rut_aux_meson) > 1 else rut_aux_meson.upper()
            if not rut_aux_meson: rut_final_meson = "00.000.000-0"
            
            with st.container(border=True):
                st.markdown(f"**RUT Cosechador:** `{rut_final_meson}`")
                flor_actual = st.session_state.get("flor_seleccionada_meson", None)
                flor_nom = flor_actual["nombre"] if flor_actual else "Ninguna"
                st.markdown(f"**Flor:** <span style='color:#38bdf8; font-weight:bold;'>{flor_nom}</span>", unsafe_allow_html=True)
                
                st.write("")
                st.caption("⚙️ ¿Saldo de hilera? Edita varas:")
                
                st.html("""
                    <style>
                        div[data-testid="stNumberInput"] input {
                            background-color: #0f172a !important;
                            color: #38bdf8 !important;
                            border: 1px solid #334155 !important;
                            border-radius: 8px !important;
                            font-size: 24px !important;
                            font-weight: bold !important;
                            text-align: center !important;
                            height: 52px !important;
                        }
                        input[type=number]::-webkit-inner-spin-button, 
                        input[type=number]::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }
                        input[type=number] { -moz-appearance: textfield; }
                        div[data-testid="stNumberInput"] label { display: none !important; }
                    </style>
                """)

                col_m1, col_m2, col_m3 = st.columns([1, 1.6, 1])
                with col_m1:
                    if st.button("-5", key="btn_meson_menos_5", use_container_width=True):
                        st.session_state.cantidad_varas_meson = max(0, st.session_state.cantidad_varas_meson - 5)
                        st.rerun()
                        
                with col_m2:
                    varas_digitadas = st.number_input(
                        "Cantidad Varas:", min_value=0, max_value=500,
                        value=int(st.session_state.cantidad_varas_meson), step=1, key="input_editable_varas_meson"
                    )
                    if varas_digitadas != st.session_state.cantidad_varas_meson:
                        st.session_state.cantidad_varas_meson = int(varas_digitadas)
                        st.rerun()
                        
                with col_m3:
                    if st.button("+5", key="btn_meson_mas_5", use_container_width=True):
                        st.session_state.cantidad_varas_meson += 5
                        st.rerun()
                
                st.write("")
                sin_flor = (st.session_state.get("flor_seleccionada_meson", None) is None)
                cc_seleccionado = st.session_state.get("cc_activo_meson", "")
                contratista_seleccionado = st.session_state.get("contratista_activo_meson", "")
                
                bloqueo_final = bloqueo_activo or sin_flor or not cc_seleccionado or not contratista_seleccionado
                
                if st.button("✅ Confirmar e Inyectar a Firebase", key="btn_confirmar_inyeccion_meson", use_container_width=True, disabled=bloqueo_final):
                    partes_contratista = contratista_seleccionado.split(" | ")
                    tz_chile = zoneinfo.ZoneInfo("America/Santiago")
                    
                    nuevo_registro = {
                        "CentroCosto": cc_seleccionado,
                        "RutContratista": partes_contratista[0].strip() if len(partes_contratista) > 0 else "",
                        "ContratistaNombre": partes_contratista[1].strip() if len(partes_contratista) > 1 else "",
                        "RutCosechador": st.session_state.rut_cosechador,
                        "CodigoArticulo": int(st.session_state.flor_seleccionada_meson["codigo"]),
                        "DescripcionArticulo": st.session_state.flor_seleccionada_meson["nombre"],
                        "CantidadVaras": int(st.session_state.cantidad_varas_meson),
                        "FechaRegistro": datetime.datetime.now(tz_chile),
                        "IdExpressUsado": st.session_state.id_express_cosecha
                    }
                    try:
                        db.collection("cosecha_diaria").add(nuevo_registro)
                        st.success("✅ Carga inyectada con éxito.")
                        st.session_state.flor_seleccionada_meson = None
                        st.session_state.cantidad_varas_meson = 30
                        st.rerun()
                    except Exception as e_fb:
                        st.error(f"❌ Error Firebase: {e_fb}")

            # 2. HISTORIAL DIARIO DE TERRENO ACTUALIZADO AUTOMÁTICAMENTE
            st.write("")
            st.markdown("<h3 style='color:#f8fafc;'>📋 Historial del Día (Servidor Google Cloud)</h3>", unsafe_allow_html=True)
            
            lista_operario_real = st.session_state.get("lista_datos_dia_cache", [])
            if lista_operario_real:
                try:
                    df_op = pd.DataFrame(lista_operario_real)
                    import __main__ as main
                    if "RutCosechador" in df_op.columns and hasattr(main, "formatear_rut_chileno_completo"):
                        df_op["RutCosechador"] = df_op["RutCosechador"].apply(main.formatear_rut_chileno_completo)
                        
                    columnas_seguras = ["RutCosechador", "DescripcionArticulo", "CantidadVaras"]
                    df_op_render = df_op[columnas_seguras].groupby(["RutCosechador", "DescripcionArticulo"], as_index=False)["CantidadVaras"].sum()
                    st.dataframe(df_op_render, use_container_width=True, hide_index=True)
                except Exception as e_tabla:
                    st.caption(f"⚠️ Nota de visualización: {e_tabla}")
            else:
                st.info("📝 No hay registros cargados hoy en este mesón.")


# --- CONTENIDO DE LA PESTAÑA B: PANEL DE AUDITORÍA Y CONTROL (ADMINISTRADOR) ---
if st.session_state.rol_usuario == "admin" and tab_auditoria is not None:
    with tab_auditoria:
        st.markdown("<h2 style='color:#38bdf8;'> Bars Ventana de Auditoría y Control de Registros</h2>", unsafe_allow_html=True)
        st.caption("Espacio exclusivo para administradores. Filtre por día, por RUT o combine ambos para auditar Google Firebase.")
        
        col_f_fecha, col_f_cc, col_f_b2b, col_f_rut = st.columns(4)
        with col_f_fecha:
            filtro_fecha = st.date_input("📅 Filtrar por Día:", value=datetime.date.today(), key="admin_audit_date")
            historico_completo = st.checkbox("Ignorar fecha", value=False, key="chk_audit_hist")
        with col_f_cc:
            filtro_cc = st.selectbox("🏬 Centro de Costo:", ["Las Rosas (CC 01)", "Chipana (CC 02)"], key="audit_filter_cc")
            ignorar_cc = st.checkbox("Ignorar Centro Costo", value=True, key="chk_audit_cc")
        with col_f_b2b:
            filtro_b2b = st.selectbox("🤝 Contratista B2B:", [
                "76.543.210-K | Servicios Agrícolas del Maule",
                "77.123.456-7 | Agrícola San Fernando Limitada",
                "76.999.888-2 | Mano de Obra Terreno SpA"
            ], key="audit_filter_b2b")
            ignorar_b2b = st.checkbox("Ignorar Contratista SpA", value=True, key="chk_audit_b2b")
        with col_f_rut:
            filtro_rut = st.text_input("🔍 RUT Cosechador:", placeholder="Ej: 123456789", key="admin_audit_rut").strip().lower()
            
        if "resultado_auditoria_nube" not in st.session_state:
            st.session_state.resultado_auditoria_nube = []
            
        if st.button("🚀 Ejecutar Búsqueda en la Nube", key="btn_ejecutar_busqueda_audit", use_container_width=True, type="primary"):
            try:
                tz_local = zoneinfo.ZoneInfo("America/Santiago")
                inicio_dia = datetime.datetime.combine(filtro_fecha, datetime.time.min, tzinfo=tz_local)
                fin_dia = datetime.datetime.combine(filtro_fecha, datetime.time.max, tzinfo=tz_local)
                
                query = db.collection("cosecha_diaria")
                if not historico_completo:
                    query = query.where("FechaRegistro", ">=", inicio_dia).where("FechaRegistro", "<=", fin_dia)
                if filtro_rut:
                    query = query.where("RutCosechador", "==", filtro_rut.replace(".", "").replace("-", "").strip().lower())
                if not ignorar_cc:
                    query = query.where("CentroCosto", "==", filtro_cc)
                if not ignorar_b2b:
                    nombre_b2b_limpio = filtro_b2b.split(" | ")[1].strip() if " | " in filtro_b2b else filtro_b2b
                    query = query.where("ContratistaNombre", "==", nombre_b2b_limpio)
                
                docs_filtrados = query.order_by("FechaRegistro", direction=firestore.Query.DESCENDING).stream()
                st.session_state.resultado_auditoria_nube = [(doc.id, doc.to_dict()) for doc in docs_filtrados]
                if not st.session_state.resultado_auditoria_nube:
                    st.info("📋 No se encontraron registros con los criterios seleccionados.")
                else:
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Error en consulta Firebase: {e}")
        if st.session_state.resultado_auditoria_nube:
            st.write(f"📋 Se encontraron {len(st.session_state.resultado_auditoria_nube)} registros:")
            for doc_id, datos in st.session_state.resultado_auditoria_nube:
                with st.container(border=True):
                    c_info, c_edit, c_acc = st.columns([1.8, 1, 1.2])
                    with c_info:
                        rut_tarjeta_crudo = datos.get('RutCosechador', '')
                        import __main__ as main
                        rut_tarjeta_estetico = main.formatear_rut_chileno_completo(rut_tarjeta_crudo) if hasattr(main, 'formatear_rut_chileno_completo') else rut_tarjeta_crudo.upper()
                        
                        fecha_registro_raw = datos.get("FechaRegistro", None)
                        fecha_registro_estetica = fecha_registro_raw.strftime("%d/%m/%Y a las %H:%M hrs") if hasattr(fecha_registro_raw, "strftime") else "Sin fecha"
                        
                        cc_origen_real = datos.get("CentroCosto", "S/C")
                        contratista_real = datos.get("ContratistaNombre", "S/C")
                        
                        st.markdown(f"👤 **Cosechador:** `{rut_tarjeta_estetico}`")
                        st.caption(f"📦 Variedad: {datos.get('DescripcionArticulo', 'S/V')}")
                        st.markdown(f"<div style='font-size:12px; color:#94a3b8;'>🏬 <b>Origen:</b> {cc_origen_real}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='font-size:12px; color:#94a3b8;'>🤝 <b>Empresa:</b> {contratista_real}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='font-size:12px; color:#38bdf8; margin-top:4px;'>📅 <b>Registro:</b> {fecha_registro_estetica}</div>", unsafe_allow_html=True)
                    
                    with c_edit:
                        nueva_cantidad = st.number_input("Varas:", min_value=0, value=int(datos.get("CantidadVaras", 0)), step=1, key=f"audit_mod_{doc_id}")
                    with c_acc:
                        st.write("")
                        if st.button("💾 Guardar", key=f"audit_btn_upd_{doc_id}", use_container_width=True):
                            try:
                                db.collection("cosecha_diaria").document(doc_id).update({"CantidadVaras": int(nueva_cantidad)})
                                st.session_state.resultado_auditoria_nube = [] 
                                st.success("¡Modificado!")
                                st.rerun()
                            except Exception as ex: st.error(f"Error: {ex}")
                        if st.button("🗑️ Borrar", key=f"audit_btn_del_{doc_id}", use_container_width=True, type="secondary"):
                            try:
                                db.collection("cosecha_diaria").document(doc_id).delete()
                                st.session_state.resultado_auditoria_nube = [] 
                                st.success("Eliminado.")
                                st.rerun()
                            except Exception as ex: st.error(f"Error: {ex}")

        # ==================================================================
        # E. PANEL DE CONFIGURACIÓN DEL CATÁLOGO DIRECTO EN LA NUBE
        # ==================================================================
        st.write("---")
        st.markdown("<h2 style='color:#38bdf8;'>⚙️ Panel de Configuración del Catálogo</h2>", unsafe_allow_html=True)
        s_cc, s_b2b, s_flores = st.tabs(["🏬 Centros de Costo", "🤝 Contratistas B2B", "💐 Flores y Variedades"])
        
        with s_cc:
            with st.form("form_add_cc", clear_on_submit=True):
                nuevo_cc_nombre = st.text_input("Nombre del nuevo Centro de Costo:", placeholder="Ej: Fundo El Quillay (CC 03)").strip()
                if st.form_submit_button("Registrar Centro de Costo", use_container_width=True):
                    if nuevo_cc_nombre:
                        try:
                            db.collection("config_centros").add({"nombre": nuevo_cc_nombre, "fecha_creacion": datetime.datetime.now()})
                            st.success(f"✅ Centro de Costo '{nuevo_cc_nombre}' inyectado.")
                        except Exception as e: st.error(f"Error: {e}")
                    else: st.warning("El campo no puede estar vacío.")
                    
        with s_b2b:
            with st.form("form_add_contratista", clear_on_submit=True):
                new_rut_b2b = st.text_input("RUT Contratista (Con puntos y guión):", placeholder="Ej: 76.888.999-K").strip()
                new_nom_b2b = st.text_input("Razón Social / Nombre Contratista:", placeholder="Ej: Cosechas del Valle SpA").strip()
                if st.form_submit_button("Registrar Contratista B2B", use_container_width=True):
                    if new_rut_b2b and new_nom_b2b:
                        try:
                            cadena_kame = f"{new_rut_b2b} | {new_nom_b2b}"
                            db.collection("config_contratistas").add({"formato_kame": cadena_kame, "fecha_creacion": datetime.datetime.now()})
                            st.success(f"✅ Contratista '{cadena_kame}' configurado.")
                        except Exception as e: st.error(f"Error: {e}")
                    else: st.warning("Ambos campos son obligatorios.")

        with s_flores:
            with st.form("form_add_flor_catalogo_libre", clear_on_submit=True):
                nueva_familia_libre = st.text_input("Escribe la Familia Agrícola / Especie:", placeholder="Ej: Rosas, Peonía").strip()
                nuevo_cod_flor = st.number_input("Código de Artículo único (Kame ERP):", min_value=1, value=225, step=1, key="admin_add_cod_int")
                nuevo_nom_flor = st.text_input("Nombre de la Variedad / Color comercial:", placeholder="Ej: Ranunculo Romance Rosado", key="admin_add_nom_str").strip()
                
                # 🎨 EL CLON DE WORD: Selector de color interactivo táctil para el administrador
                nuevo_color_hex = st.color_picker(
                    "🎨 Seleccione el color visual para el círculo de la tarjeta:", 
                    value="#38bdf8", 
                    key="admin_add_color_picker"
                )
                
                if st.form_submit_button("Registrar Flor en el Catálogo", use_container_width=True):
                    if nuevo_nom_flor and nuevo_cod_flor:
                        try:
                            # Inyectamos el registro con su color hexadecimal real amarrado
                            db.collection("config_flores").add({
                                "familia": nueva_familia_libre, 
                                "codigo": int(nuevo_cod_flor), 
                                "nombre": nuevo_nom_flor,
                                "color": str(nuevo_color_hex).lower(),
                                "fecha_creacion": datetime.datetime.now(zoneinfo.ZoneInfo("America/Santiago"))
                            })
                            st.success(f"¡Variedad '{nuevo_nom_flor}' registrada con éxito con el color {nuevo_color_hex}!")
                            st.fragment(lambda: None)
                            st.rerun()
                        except Exception as e: 
                            st.error(f"❌ Error al registrar flor en la nube: {e}")
                    else: 
                        st.warning("⚠️ El nombre de la variedad es obligatorio.")



        # ==================================================================
        # F. EXPORTACIÓN ERP Y EMISIÓN DE VALES FORMALES EN TICKET CHILE
        # ==================================================================
        st.write("---")
        st.markdown("<h2 style='color:#38bdf8;'>🧾 Exportación y Comprobantes de Cosecha</h2>", unsafe_allow_html=True)
        
        tz_local = zoneinfo.ZoneInfo("America/Santiago")
        inicio_dia = datetime.datetime.combine(filtro_fecha, datetime.time.min, tzinfo=tz_local)
        fin_dia = datetime.datetime.combine(filtro_fecha, datetime.time.max, tzinfo=tz_local)
        
        col_admin_kame, col_admin_vale = st.columns(2)
        with col_admin_kame:
            st.markdown("### Planilla Contable")
            if st.button("Procesar y Preparar .CSV", key="btn_kame_process", use_container_width=True, type="primary"):
                try:
                    query = db.collection("cosecha_diaria").where("FechaRegistro", ">=", inicio_dia).where("FechaRegistro", "<=", fin_dia)
                    if filtro_rut: 
                        query = query.where("RutCosechador", "==", filtro_rut.replace(".", "").replace("-", "").strip().lower())
                    docs = query.order_by("FechaRegistro", direction=firestore.Query.DESCENDING).stream()
                    lista_datos = [doc.to_dict() for doc in docs]
                    if not lista_datos: 
                        st.warning("⚠️ No se encontraron registros.")
                    else:
                        df_admin = pd.DataFrame(lista_datos)
                        columnas_kame = ["CentroCosto", "RutContratista", "ContratistaNombre", "RutCosechador", "CodigoArticulo", "DescripcionArticulo", "CantidadVaras"]
                        csv_kame = df_admin[columnas_kame].groupby(["CentroCosto", "RutContratista", "ContratistaNombre", "RutCosechador", "CodigoArticulo", "DescripcionArticulo"], as_index=False)["CantidadVaras"].sum().to_csv(index=False, sep=";").encode('utf-8')
                        st.success("Planilla generada con éxito.")
                        st.download_button(label="📥 DESCARGAR PLANILLA KAME", data=csv_kame, file_name=f"KAME_Cosecha_{filtro_fecha}.csv", mime="text/csv", use_container_width=True)
                except Exception as e: st.error(f"Error: {e}")
                
        with col_admin_vale:
            st.markdown("### Vale Físico de Cosecha")
            col_v_btn1, col_v_btn2 = st.columns(2)
            if "html_vale_actual" not in st.session_state: st.session_state.html_vale_actual = ""
            if "mostrar_trigger_impresion" not in st.session_state: st.session_state.mostrar_trigger_impresion = False
            
            with col_v_btn1:
                if st.button("Generar Vista Previa", key="btn_vale_process", use_container_width=True):
                    try:
                        query = db.collection("cosecha_diaria").where("FechaRegistro", ">=", inicio_dia).where("FechaRegistro", "<=", fin_dia)
                        if filtro_rut: 
                            query = query.where("RutCosechador", "==", filtro_rut.replace(".", "").replace("-", "").strip().lower())
                        docs = query.order_by("FechaRegistro", direction=firestore.Query.DESCENDING).stream()
                        lista_datos = [doc.to_dict() for doc in docs]
                        if not lista_datos:
                            st.warning("⚠️ No existen registros.")
                            st.session_state.html_vale_actual = ""
                        else:
                            df_vale = pd.DataFrame(lista_datos).groupby(["RutCosechador", "DescripcionArticulo"], as_index=False)["CantidadVaras"].sum()
                            import __main__ as main
                            rut_vale = main.formatear_rut_chileno_completo(filtro_rut) if (filtro_rut and hasattr(main, "formatear_rut_chileno_completo")) else "TODOS LOS COSECHADORES"
                            cc_vale = filtro_cc if not ignorar_cc else "TODOS LOS CENTROS"
                            b2b_vale = filtro_b2b.split(" | ")[1] if not ignorar_b2b else "TODOS LOS CONTRATISTAS"
                            
                            filas_html = "".join([f"<tr><td style='padding:4px;'>{r['DescripcionArticulo']}</td><td style='text-align:right; font-weight:bold;'>{r['CantidadVaras']}</td></tr>" for _, r in df_vale.iterrows()])
                            st.session_state.html_vale_actual = f"""
                            <div style='background-color:white; color:black; padding:20px; font-family:monospace; border:1px solid #ccc;'>
                                <h3 style='text-align:center; margin:0;'>FLORES ANTIVERO</h3>
                                <p style='text-align:center; margin:5px 0; font-size:12px;'>COMPROBANTE DE COSECHA DIARIA</p>
                                <hr style='border-top:1px dashed black;'>
                                <p style='margin:3px 0;'><b>Fecha:</b> {filtro_fecha.strftime('%d/%m/%Y')}</p>
                                <p style='margin:3px 0;'><b>Origen:</b> {cc_vale}</p>
                                <p style='margin:3px 0;'><b>Empresa:</b> {b2b_vale}</p>
                                <p style='margin:3px 0;'><b>Cosechador:</b> {rut_vale}</p>
                                <hr style='border-top:1px dashed black;'>
                                <table style='width:100%; border-collapse:collapse;'>
                                    <thead><tr><th style='text-align:left;'>Variedad</th><th style='text-align:right;'>Varas</th></tr></thead>
                                    <tbody>{filas_html}</tbody>
                                </table>
                                <hr style='border-top:1px dashed black;'>
                                <h3 style='display:flex; justify-content:space-between; margin:0;'><span>TOTAL:</span> <span>{df_vale['CantidadVaras'].sum()} Varas</span></h3>
                            </div>"""
                            st.session_state.mostrar_trigger_impresion = False
                            st.rerun()
                    except Exception as e: st.error(f"Error: {e}")
            with col_v_btn2:
                if st.button("Imprimir Voucher", key="btn_vale_print_trigger", use_container_width=True, type="primary", disabled=(st.session_state.html_vale_actual == "")):
                    st.session_state.mostrar_trigger_impresion = True
                    st.rerun()
            if st.session_state.html_vale_actual: 
                st.html(st.session_state.html_vale_actual)
            if st.session_state.mostrar_trigger_impresion:
                st.session_state.mostrar_trigger_impresion = False
                st.html("<script>setTimeout(function() { window.parent.print(); }, 200);</script>")
