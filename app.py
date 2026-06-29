import streamlit as st
import pandas as pd
import datetime
import zoneinfo
import firebase_admin
from firebase_admin import credentials, firestore
import json

# ==================================================================
# 1. CONEXIÓN SECRETA Y SEGURA CON GOOGLE FIREBASE CLOUD (HÍBRIDA)
# ==================================================================
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
            st.error(f"❌ Error crítico al cargar credenciales de Firebase: {e_local}")

db = firestore.client()

# ==================================================================
# 4.B DEFINICIÓN TECLADO MAQUETA CON MARCO PROTECTOR INDESTRUCTIBLE
# ==================================================================
def dibujar_teclado_maqueta_antivero():
    # 🛡️ ESCUDO GEOMÉTRICO: Obliga a la tablet a mantener la cuadrícula 3x4 en vertical u horizontal
    st.html("""
        <style>
            /* Creamos el cuadro contenedor perimetral rígido que solicitaste */
            .recuadro-protector-campo {
                background-color: #1e293b !important;
                border: 2px solid #334155 !important;
                border-radius: 12px !important;
                padding: 18px !important;
                max-width: 340px !important;
                margin: 10px auto !important;
                box-sizing: border-box !important;
            }
            /* Bloqueo Flexbox: Prohíbe terminantemente que los números se apilen hacia abajo */
            .recuadro-protector-campo [data-testid="stHorizontalBlock"] {
                flex-direction: row !important;
                display: flex !important;
                gap: 8px !important;
                margin-bottom: 8px !important;
            }
            .recuadro-protector-campo [data-testid="stHorizontalBlock"] div[data-testid="column"] {
                width: 33.333% !important;
                flex: 1 1 33.333% !important;
                max-width: 33.333% !important;
                margin-bottom: 0 !important;
            }
            .recuadro-protector-campo button {
                background-color: #0f172a !important;
                color: #f8fafc !important;
                border: 1px solid #334155 !important;
                border-radius: 6px !important;
                font-size: 20px !important;
                font-weight: bold !important;
                height: 52px !important;
            }
            .recuadro-protector-campo button:active { background-color: #38bdf8 !important; color: #0f172a !important; }
            .recuadro-protector-campo button[key="btn_k_RETROCESO"] p { color: #ef4444 !important; }
            .recuadro-protector-campo .barra-borrar-real button { background-color: #ef4444 !important; border: 1px solid #b91c1c !important; height: 46px !important; }
            .recuadro-protector-campo .barra-borrar-real button p { color: #ffffff !important; font-weight: bold !important; }
            .recuadro-protector-campo .barra-borrar-real button:active { background-color: #dc2626 !important; }
            .recuadro-protector-campo .columna-enter-vertical button { background-color: #1e293b !important; color: #38bdf8 !important; border: 2px solid #334155 !important; height: 232px !important; font-size: 18px !important; }
        </style>
    """)
    
    st.subheader("📍 Identificación de Campo")
    st.session_state.cc_activo_meson = st.selectbox(
        "Origen (Centro de Costo)",
        ["Seleccione Centro de Costo...", "Las Rosas (CC 01)", "Chipana (CC 02)"],
        key="cc_selector_agricola"
    )
    st.session_state.contratista_activo_meson = st.selectbox(
        "Contratista Destino (Kame B2B)",
        [
            "Seleccione Contratista...",
            "76.543.210-K | Servicios Agrícolas del Maule",
            "77.123.456-7 | Agrícola San Fernando Limitada",
            "76.999.888-2 | Mano de Obra Terreno SpA"
        ],
        key="contratista_selector_b2b"
    )
    rut_crudo = st.session_state.rut_cosechador
    rut_visible = f"{rut_crudo[:-1]}-{rut_crudo[-1]}".upper() if len(rut_crudo) > 1 else rut_crudo.upper()
    if not rut_crudo: rut_visible = "00.000.000-0"
    
    import __main__ as main
    rut_es_valido = main.validar_rut_chileno(rut_crudo) if (rut_crudo and hasattr(main, 'validar_rut_chileno')) else False
    icono_verificacion = "✅" if rut_es_valido else "🛑"
    
    col_visor_texto, col_visor_icono = st.columns([4, 1])
    with col_visor_texto:
        st.markdown(f'<div class="rut-display-box" style="font-size:22px; min-height:48px; margin-bottom:0; background-color:#1e293b;">{rut_visible}</div>', unsafe_allow_html=True)
    with col_visor_icono:
        st.markdown(f'<div class="rut-display-box" style="font-size:22px; min-height:48px; margin-bottom:0; background-color:#1e293b; text-align:center;">{icono_verificacion}</div>', unsafe_allow_html=True)
        
    st.markdown('<div class="cuadro-maqueta-rut">', unsafe_allow_html=True)
    col_bloque_numeros, col_bloque_enter = st.columns([3, 1])
    with col_bloque_numeros:
        filas_maqueta = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"], ["0", "K", "←"]]
        for fila in filas_maqueta:
            cols_n = st.columns(3)
            for idx, digito in enumerate(fila):
                with cols_n[idx]:
                    if digito == "←":
                        if st.button("←", key="btn_k_RETROCESO", use_container_width=True):
                            st.session_state.rut_cosechador = st.session_state.rut_cosechador[:-1]
                            st.rerun()
                    else:
                        if st.button(digito, key=f"btn_k_{digito}", use_container_width=True):
                            if len(st.session_state.rut_cosechador) < 9:
                                st.session_state.rut_cosechador += digito
                                st.rerun()
                                
        st.markdown('<div class="barra-borrar-real">', unsafe_allow_html=True)
        if st.button("borrar", key="btn_k_BORRAR_TODO", use_container_width=True):
            st.session_state.rut_cosechador = ""
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_bloque_enter:
        st.markdown('<div class="columna-enter-vertical">', unsafe_allow_html=True)
        if st.button("E\nN\nT\nE\nR", key="btn_k_ENTER_CONFIRM", use_container_width=True):
            if rut_es_valido: st.success("🔓 Confirmado")
            else: st.error("❌ Inválido")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.session_state.rut_bloqueado_operacion = not rut_es_valido


# ==================================================================
# 2. CONFIGURACIÓN VISUAL OPTIMIZADA PARA GIROS Y DISPOSITIVOS
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
        /* Forzamos estilos oscuros en la interfaz */
        .stApp {
            background-color: var(--bg-dark) !important;
            color: var(--text-light) !important;
        }
        .antivero-header {
            background: var(--panel-bg);
            padding: 15px 20px;
            border-radius: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            border: 1px solid var(--border-color);
        }
        .antivero-header h1 {
            margin: 0;
            font-size: 22px;
            color: var(--accent-blue) !important;
            font-weight: bold;
        }
        .stSelectbox label, .stTextInput label {
            font-weight: 700 !important;
            font-size: 12px !important;
            color: var(--text-muted) !important;
            text-transform: uppercase !important;
        }
        .rut-display-box {
            background: var(--bg-dark);
            border: 2px solid #475569;
            border-radius: 8px;
            padding: 12px;
            text-align: center;
            font-size: 26px;
            font-weight: bold;
            color: var(--accent-blue);
            min-height: 58px;
            margin-bottom: 10px;
        }
        /* REGLAS CRÍTICAS PARA VISIBILIDAD DE BOTONES TÁCTILES EN TABLETS */
        div[data-testid="stButton"] button {
            background-color: var(--panel-bg) !important;
            color: var(--text-light) !important;
            border: 1px solid var(--border-color) !important;
            font-weight: bold !important;
            font-size: 15px !important;
        }
        div[data-testid="stButton"] button p {
            color: var(--text-light) !important;
        }
        div[data-testid="stButton"] button:active, div[data-testid="stButton"] button:focus {
            background-color: var(--accent-blue) !important;
            color: var(--bg-dark) !important;
            border-color: var(--accent-blue) !important;
        }
        div[data-testid="stButton"] button:active p, div[data-testid="stButton"] button:focus p {
            color: var(--bg-dark) !important;
        }
        /* RESPONSIVIDAD DINÁMICA: DETECTA CELULAR VERTICAL O GIROS EN TERRENO */
        @media (max-width: 768px) {
            .stMainBlock > div > [data-testid="stHorizontalBlock"] {
                flex-direction: column !important;
            }
            .stMainBlock > div > [data-testid="stHorizontalBlock"] > div[data-testid="column"] {
                width: 100% !important;
                margin-left: 0 !important;
                margin-bottom: 15px !important;
            }
            .antivero-header h1 {
                font-size: 18px;
            }
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

# 🚀 GATILLO DE TERRENO: Descarga automática del día para el historial en vivo del operario 🚀
lista_datos_dia = []
try:
    inicio_hoy = datetime.datetime.combine(datetime.date.today(), datetime.time.min, tzinfo=zoneinfo.ZoneInfo("America/Santiago"))
    fin_hoy = datetime.datetime.combine(datetime.date.today(), datetime.time.max, tzinfo=zoneinfo.ZoneInfo("America/Santiago"))
    docs_hoy = db.collection("cosecha_diaria").where("FechaRegistro", ">=", inicio_hoy).where("FechaRegistro", "<=", fin_hoy).stream()
    lista_datos_dia = [doc.to_dict() for doc in docs_hoy]
    st.session_state.lista_datos_dia_cache = lista_datos_dia
except Exception as e_consulta_automatica:
    st.caption(f"⚠️ Nota de sincronización: {e_consulta_automatica}")

# ==================================================================
# 3. PORTAL DE ACCESO ÚNICO CON ESCUDO DE CAMPOS TRAMPA ANTI-AUTOCOMPLETADO
# ==================================================================
if not st.session_state.usuario_conectado:
    st.html("""
        <form style="display:none;" autocomplete="off">
            <input type="text" name="username_fake" autocomplete="new-username" />
            <input type="password" name="password_fake" autocomplete="new-password" />
        </form>
        <style>
            input:-webkit-autofill, input:-webkit-autofill:hover, input:-webkit-autofill:focus {
                -webkit-text-fill-color: #f8fafc !important;
                transition: background-color 5000s ease-in-out 0s;
            }
        </style>
    """)
    st.markdown("<h3 style='text-align: center; color: #38bdf8;'>🔐 Acceso Cosecha Flores Antivero</h3>", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("### Iniciar Sesión")
        input_usuario = st.text_input("INGRESA TU RUT O CORREO ADMINISTRADOR:", placeholder="Ej: admin@antivero.cl", key="auth_login_user").strip().lower()
        input_clave = st.text_input("CONTRASEÑA DE ACCESO:", type="password", placeholder="••••••••", key="auth_login_password")
        
        st.html("""
        <script>
        setTimeout(function() {
            const inputs = window.parent.document.querySelectorAll('input');
            inputs.forEach(input => {
                input.setAttribute('autocomplete', 'off');
                input.setAttribute('id', 'nocache_' + Math.random().toString(36).substring(7));
                input.removeAttribute('name');
            });
        }, 250);
        </script>
        """)
        if st.button("🔑 Ingresar al Sistema", key="btn_auth_login_submit", use_container_width=True, type="primary"):
            if input_usuario and input_clave:
                try:
                    user_ref = db.collection("usuarios").document(input_usuario).get()
                    if user_ref.exists:
                        datos_user = user_ref.to_dict()
                        if datos_user.get("password") == input_clave:
                            st.session_state.usuario_conectado = True
                            st.session_state.rol_usuario = datos_user.get("rol", "operario")
                            st.session_state.id_usuario_activo = input_usuario
                            st.success(f"✅ Acceso concedido como: {st.session_state.rol_usuario.upper()}")
                            st.fragment(lambda: None)
                            st.rerun()
                        else:
                            st.error("❌ La contraseña ingresada es incorrecta.")
                    else:
                        st.error("❌ El usuario ingresado no está registrado en el sistema agrícola.")
                except Exception as e:
                    st.error(f"❌ Error de conexión con el servidor de Google: {e}")
            else:
                st.warning("⚠️ Por favor, complete ambos campos.")

    # 🔒 EL ESCUDO MÁSTER: Detiene la ejecución absoluta para que NO se dibuje la terminal abajo si no se ha logueado
    st.stop()

# ==================================================================
# 3. INTERFAZ PRINCIPAL (USUARIO AUTENTICADO Y SEGURIZADO)
# ==================================================================
with st.sidebar:
    st.markdown(f"👤 **Usuario Activo:** `{st.session_state.id_usuario_activo.upper()}`")
    st.markdown(f"⚙️ **Rol:** `{st.session_state.rol_usuario.upper()}`")
    st.write("---")
    
    # FORMULARIO UNIVERSAL: Cambiar contraseña de la cuenta en uso
    with st.expander("🔒 Cambiar mi Contraseña", expanded=False):
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

    # SECCIÓN EXCLUSIVA PARA ADMINISTRADORES: GESTIÓN DE PERSONAL
    if st.session_state.rol_usuario == "admin":
        st.write("---")
        st.markdown("### 🛠️ Herramientas de Administrador")
        
        with st.expander("👤 Registrar Nuevo Operario", expanded=False):
            with st.form("form_registro_interno_admin", clear_on_submit=True):
                reg_rut = st.text_input("RUT Cosechador:", placeholder="Ej: 123456789", key="admin_reg_rut").strip().lower()
                reg_clave = st.text_input("Contraseña inicial:", type="password", key="admin_reg_pass")
                if st.form_submit_button("Crear Operario", use_container_width=True):
                    if reg_rut and len(reg_clave) >= 4:
                        try:
                            if db.collection("usuarios").document(reg_rut).get().exists:
                                st.error("❌ Este RUT ya existe en los registros.")
                            else:
                                db.collection("usuarios").document(reg_rut).set({"password": reg_clave, "rol": "operario"})
                                st.success(f"¡RUT {reg_rut} creado con éxito!")
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.warning("⚠️ Datos inválidos o clave muy corta.")
                        
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

# ==================================================================
# 5. MAQUETADO EN COLUMNAS (IDENTIFICACIÓN Y FLUJO CENTRAL)
# ==================================================================
if "admin_tab_filtro_rut" not in st.session_state:
    st.session_state.admin_tab_filtro_rut = ""

if st.session_state.rol_usuario == "admin":
    tab_terminal, tab_auditoria = st.tabs(["🚜 Terminal de Cosecha", "📊 Panel de Control y Auditoría"])
else:
    tab_terminal = st.container()
    tab_auditoria = None

# --- CONTENIDO DE LA PESTAÑA A: TERMINAL DE COSECHA AGRÍCOLA ---
with tab_terminal:
    col_panel_izq, col_panel_central_derecho = st.columns([1.2, 2.8])
    
    with col_panel_izq:
        # Llamamos al teclado maqueta blindado por su marco protector rígido
        dibujar_teclado_maqueta_antivero()

    with col_panel_central_derecho:
        if "flor_seleccionada_meson" not in st.session_state:
            st.session_state.flor_seleccionada_meson = None
        if "cantidad_varas_meson" not in st.session_state:
            st.session_state.cantidad_varas_meson = 30
            
        col_centro_flujo, col_derecha_consolidacion = st.columns([1.6, 1.2])
        
        with col_centro_flujo:
            st.subheader("🌸 Selección de Familia de Flores")
            capa_familias = st.tabs(["🌹 Rosas / Romance / Elegance", "🌸 Peonías", "🌿 Delphinium"])
            
            # Candado inteligente en vivo leyendo el Session State de la fila izquierda
            bloqueo_activo = st.session_state.get("rut_bloqueado_operacion", True)
            
            with capa_familias[0]:
                st.markdown("<p style='color:#94a3b8; font-size:13px;'>Seleccione variedad para el mesón:</p>", unsafe_allow_html=True)
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    if st.button("Rosas Romance\n(Cód: 220)", key="btn_prod_220", use_container_width=True, disabled=bloqueo_activo):
                        st.session_state.flor_seleccionada_meson = {"codigo": 220, "nombre": "Rosas Romance"}
                        st.session_state.cantidad_varas_meson = 30
                        st.rerun()
                with col_f2:
                    if st.button("Rosas Elegance\n(Cód: 221)", key="btn_prod_221", use_container_width=True, disabled=bloqueo_activo):
                        st.session_state.flor_seleccionada_meson = {"codigo": 221, "nombre": "Rosas Elegance"}
                        st.session_state.cantidad_varas_meson = 30
                        st.rerun()
                        
            with capa_familias[1]:
                st.markdown("<p style='color:#94a3b8; font-size:13px;'>Seleccione Peonía:</p>", unsafe_allow_html=True)
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    if st.button("Sarah Bernhardt\n(Cód: 222)", key="btn_prod_222", use_container_width=True, disabled=bloqueo_activo):
                        st.session_state.flor_seleccionada_meson = {"codigo": 222, "nombre": "Peonía Sarah Bernhardt"}
                        st.session_state.cantidad_varas_meson = 30
                        st.rerun()
                with col_p2:
                    if st.button("Festiva Maxima\n(Cód: 223)", key="btn_prod_223", use_container_width=True, disabled=bloqueo_activo):
                        st.session_state.flor_seleccionada_meson = {"codigo": 223, "nombre": "Peonía Festiva Maxima"}
                        st.session_state.cantidad_varas_meson = 30
                        st.rerun()
                        
            with capa_familias[2]:
                st.markdown("<p style='color:#94a3b8; font-size:13px;'>Seleccione Delphinium:</p>", unsafe_allow_html=True)
                if st.button("Guardian Mix\n(Cód: 224)", key="btn_prod_224", use_container_width=True, disabled=bloqueo_activo):
                    st.session_state.flor_seleccionada_meson = {"codigo": 224, "nombre": "Delphinium Guardian Mix"}
                    st.session_state.cantidad_varas_meson = 30
                    st.rerun()
        with col_derecha_consolidacion:
            st.markdown("<h2 style='color:#f8fafc;'>📥 Mesón de Carga Actual</h2>", unsafe_allow_html=True)
            
            # 1. VISOR DE RECOLECCIÓN ACTIVA EN LA INTERFAZ DEL MESÓN
            rut_aux_meson = st.session_state.rut_cosechador
            rut_final_meson = f"{rut_aux_meson[:-1]}-{rut_aux_meson[-1]}".upper() if len(rut_aux_meson) > 1 else rut_aux_meson.upper()
            if not rut_aux_meson: rut_final_meson = "00.000.000-0"
            
            with st.container(border=True):
                st.markdown(f"**RUT Cosechador:** `{rut_final_meson}`")
                flor_actual = st.session_state.get("flor_seleccionada_meson", None)
                flor_nom = flor_actual["nombre"] if flor_actual else "Ninguna"
                st.markdown(f"**Flor:** <span style='color:#38bdf8; font-weight:bold;'>{flor_nom}</span>", unsafe_allow_html=True)
                
                st.write("")
                st.caption("⚙️ ¿Saldo de hilera? Edita varas:")
                
                # Inyectamos el CSS local de alta prioridad que mimetiza la caja editable con tu diseño
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
                        input[type=number]::-webkit-outer-spin-button { 
                            -webkit-appearance: none; 
                            margin: 0; 
                        }
                        input[type=number] { -moz-appearance: textfield; }
                        div[data-testid="stNumberInput"] label { display: none !important; }
                    </style>
                """)

                # Creamos la sub-distribución proporcional para colocar la caja editable y sus botones laterales
                col_m1, col_m2, col_m3 = st.columns([1, 1.6, 1])
                with col_m1:
                    if st.button("-5", key="btn_meson_menos_5", use_container_width=True):
                        st.session_state.cantidad_varas_meson = max(0, st.session_state.cantidad_varas_meson - 5)
                        st.rerun()
                        
                with col_m2:
                    # Caja de texto numérica 100% editable al tacto en la tablet de campo
                    varas_digitadas = st.number_input(
                        "Cantidad Varas:",
                        min_value=0,
                        max_value=500,
                        value=int(st.session_state.cantidad_varas_meson),
                        step=1,
                        key="input_editable_varas_meson"
                    )
                    if varas_digitadas != st.session_state.cantidad_varas_meson:
                        st.session_state.cantidad_varas_meson = int(varas_digitadas)
                        st.rerun()
                        
                with col_m3:
                    if st.button("+5", key="btn_meson_mas_5", use_container_width=True):
                        st.session_state.cantidad_varas_meson += 5
                        st.rerun()
                
                st.write("")
                # 🚨 CANDADO MULTIPLE DE CONTROL TOTAL ACTUALIZADO 🚨
                rut_invalido = st.session_state.get("rut_bloqueado_operacion", True)
                sin_flor = (st.session_state.get("flor_seleccionada_meson", None) is None)
                
                cc_seleccionado = st.session_state.get("cc_activo_meson", "Seleccione Centro de Costo...")
                contratista_seleccionado = st.session_state.get("contratista_activo_meson", "Seleccione Contratista...")
                
                sin_cc = (cc_seleccionado == "Seleccione Centro de Costo...")
                sin_contratista = (contratista_seleccionado == "Seleccione Contratista...")
                
                bloqueo_final = rut_invalido or sin_flor or sin_cc or sin_contratista
                
                if st.button("✅ Confirmar e Inyectar a Firebase", key="btn_confirmar_inyeccion_meson", use_container_width=True, disabled=bloqueo_final):
                    partes_contratista = contratista_seleccionado.split(" | ")
                    nuevo_registro = {
                        "CentroCosto": cc_seleccionado,
                        "RutContratista": partes_contratista[0].strip() if len(partes_contratista) > 0 else "",
                        "ContratistaNombre": partes_contratista[1].strip() if len(partes_contratista) > 1 else "",
                        "RutCosechador": st.session_state.rut_cosechador.replace(".", "").replace("-", "").strip().lower(),
                        "CodigoArticulo": int(st.session_state.flor_seleccionada_meson["codigo"]),
                        "DescripcionArticulo": st.session_state.flor_seleccionada_meson["nombre"],
                        "CantidadVaras": int(st.session_state.cantidad_varas_meson),
                        "FechaRegistro": datetime.datetime.now(zoneinfo.ZoneInfo("America/Santiago"))
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
        st.markdown("<h2 style='color:#38bdf8;'>📊 Ventana de Auditoría y Control de Registros</h2>", unsafe_allow_html=True)
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
                    # Filtramos por el nombre de la empresa limpio extraído del string
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

        # Guardamos la referencia para el mesón
        locals()["lista_datos_dia"] = [d for _, d in st.session_state.resultado_auditoria_nube]

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
                            except Exception as ex:
                                st.error(f"Error: {ex}")
                        if st.button("🗑️ Borrar", key=f"audit_btn_del_{doc_id}", use_container_width=True, type="secondary"):
                            try:
                                db.collection("cosecha_diaria").document(doc_id).delete()
                                st.session_state.resultado_auditoria_nube = [] 
                                st.success("Eliminado.")
                                st.rerun()
                            except Exception as ex:
                                st.error(f"Error: {ex}")

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
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.warning("El campo no puede estar vacío.")
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
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.warning("Ambos campos son obligatorios.")
                    
        with s_flores:
            with st.form("form_add_flor_catalogo_libre", clear_on_submit=True):
                nueva_familia_libre = st.text_input("Escribe la Familia Agrícola / Especie:", placeholder="Ej: Rosas, Peonías").strip()
                nuevo_cod_flor = st.number_input("Código de Artículo único (Kame ERP):", min_value=1, value=225, step=1, key="admin_add_cod_int")
                nuevo_nom_flor = st.text_input("Nombre de la Variedad / Color:", placeholder="Ej: Red Naomi, Coral Sunset").strip()
                if st.form_submit_button("Registrar Flor en el Catálogo", use_container_width=True):
                    if nueva_familia_libre and nuevo_nom_flor and nuevo_cod_flor:
                        try:
                            db.collection("config_flores").add({
                                "familia": nueva_familia_libre, 
                                "codigo": int(nuevo_cod_flor), 
                                "nombre": nuevo_nom_flor,
                                "fecha_creacion": datetime.datetime.now(zoneinfo.ZoneInfo("America/Santiago"))
                            })
                            st.success(f"¡Variedad '{nuevo_nom_flor}' registrada con éxito!")
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.warning("Todos los campos son obligatorios.")

        # ==================================================================
        # F. EXPORTACIÓN ERP Y EMISIÓN DE VALES FORMALES EN TICKET CHILE
        # ==================================================================
        st.write("---")
        st.markdown("<h2 style='color:#38bdf8;'>🧾 Exportación y Comprobantes de Cosecha</h2>", unsafe_allow_html=True)
        
        tz_local = zoneinfo.ZoneInfo("America/Santiago")
        inicio_dia = datetime.datetime.combine(filtro_fecha, datetime.time.min, tzinfo=tz_local)
        fin_dia = datetime.datetime.combine(filtro_fecha, datetime.time.max, tzinfo=zoneinfo.ZoneInfo("America/Santiago"))
        
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
                        st.success("Planilla generada.")
                        st.download_button(label="📥 DESCARGAR PLANILLA KAME", data=csv_kame, file_name=f"KAME_Cosecha_{filtro_fecha}.csv", mime="text/csv", use_container_width=True)
                except Exception as e:
                    st.error(f"Error: {e}")
                
        with col_admin_vale:
            st.markdown("### Vale Físico de Cosecha")
            col_v_btn1, col_v_btn2 = st.columns(2)
            if "html_vale_actual" not in st.session_state:
                st.session_state.html_vale_actual = ""
            if "mostrar_trigger_impresion" not in st.session_state:
                st.session_state.mostrar_trigger_impresion = False
            
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
                    except Exception as e:
                        st.error(f"Error: {e}")
            with col_v_btn2:
                if st.button("Imprimir Voucher", key="btn_vale_print_trigger", use_container_width=True, type="primary", disabled=(st.session_state.html_vale_actual == "")):
                    st.session_state.mostrar_trigger_impresion = True
                    st.rerun()
            if st.session_state.html_vale_actual:
                st.html(st.session_state.html_vale_actual)
            if st.session_state.mostrar_trigger_impresion:
                st.session_state.mostrar_trigger_impresion = False
                st.html("<script>setTimeout(function() { window.parent.print(); }, 200);</script>")
