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
# LECTURA DINÁMICA AVANZADA PARA FILTROS DE AUDITORÍA
# ==================================================================
lista_contratistas_dinamica = []       # Para el enrolamiento (solo nombres)
lista_centros_costo_dinamica = []      # Para el enrolamiento (solo nombres)

# Nuevas listas con formato exacto para los selectores de Auditoría
opciones_auditoria_cc = []             # Formato: "Nombre (Código)"
opciones_auditoria_contratista = []    # Formato: "RUT | Nombre"

try:
    # 1. Procesar Contratistas
    docs_contratistas = db.collection("config_contratistas").stream()
    for doc in docs_contratistas:
        datos = doc.to_dict()
        nom = datos.get("nombre")
        rut = datos.get("rut")
        cod = datos.get("codigo")
        
        if nom:
            lista_contratistas_dinamica.append(nom)
            if rut:
                # Mantiene la estética: "RUT | Nombre"
                opciones_auditoria_contratista.append(f"{rut} | {nom}")
            else:
                opciones_auditoria_contratista.append(nom)

    # 2. Procesar Centros de Costo
    docs_cc = db.collection("config_centros_costo").stream()
    for doc in docs_cc:
        datos = doc.to_dict()
        nom = datos.get("nombre")
        cod = datos.get("codigo")
        
        if nom:
            lista_centros_costo_dinamica.append(nom)
            if cod:
                # Mantiene la estética: "Nombre (Código)"
                opciones_auditoria_cc.append(f"{nom} ({cod})")
            else:
                opciones_auditoria_cc.append(nom)

    # Ordenar todas las listas alfabéticamente
    lista_contratistas_dinamica.sort()
    lista_centros_costo_dinamica.sort()
    opciones_auditoria_contratista.sort()
    opciones_auditoria_cc.sort()

except Exception as e:
    st.error(f"Error cargando datos para filtros de auditoría: {e}")
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
# LECTURA DINÁMICA CORREGIDA DESDE FIRESTORE
# ==================================================================
lista_contratistas_dinamica = []
lista_centros_costo_dinamica = []

try:
    # Leer Contratistas (Guardamos el campo 'nombre')
    docs_contratistas = db.collection("config_contratistas").stream()
    lista_contratistas_dinamica = [doc.to_dict().get("nombre") for doc in docs_contratistas if doc.to_dict().get("nombre")]
    
    # Leer Centros de Costo (Guardamos el campo 'nombre')
    docs_cc = db.collection("config_centros_costo").stream()
    lista_centros_costo_dinamica = [doc.to_dict().get("nombre") for doc in docs_cc if doc.to_dict().get("nombre")]
    
    # Ordenamos alfabéticamente para mantener la estética limpia en las tablets
    lista_contratistas_dinamica.sort()
    lista_centros_costo_dinamica.sort()

except Exception as e:
    st.error(f"Error cargando configuraciones operacionales: {e}")

# ==================================================================
# CONSTRUCCIÓN DEL DICCIONARIO DESDE DOCUMENTOS PLANOS DE FIRESTORE
# ==================================================================
diccionario_flores_dinamico = {}

try:
    docs = db.collection("config_flores").stream()
    for doc in docs:
        data = doc.to_dict()
        fam = data.get("familia", "Sin Familia")
        
        # Estructura interna de cada variedad
        flor_item = {
            "codigo": data.get("codigo", ""),
            "nombre": data.get("nombre", ""),
            "color": data.get("color", "#38bdf8")
        }
        
        # Agrupamos por el campo 'familia'
        if fam not in diccionario_flores_dinamico:
            diccionario_flores_dinamico[fam] = []
            
        diccionario_flores_dinamico[fam].append(flor_item)

except Exception as e:
    st.error(f"Error al cargar config_flores desde Firestore: {e}")

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

# ---------------------------------------------------------
# PARTE 1: DETECTOR DE CLIC EN LAS TARJETAS (Poner al inicio)
# ---------------------------------------------------------
params = st.query_params
if "sel_meson_cod" in params:
    cod_seleccionado = params["sel_meson_cod"]
    familia_actual = st.session_state.get("familia_activa_meson")
    lista_flores = diccionario_flores_dinamico.get(familia_actual, []) if diccionario_flores_dinamico else []
    flor_encontrada = next((f for f in lista_flores if f["codigo"] == cod_seleccionado), None)
    if flor_encontrada:
        st.session_state.flor_seleccionada_meson = {
            "codigo": flor_encontrada["codigo"],
            "nombre": flor_encontrada["nombre"],
            "color": flor_encontrada.get("color", "#ec4899")
        }
        st.session_state.cantidad_varas_meson = 30
    st.query_params.clear()
    st.rerun()

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
        /* Forzamos tipografía de círculos para enmascarar la contraseña de forma nativa */
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
                    input.setAttribute('type', 'text');
                }
                input.setAttribute('autocomplete', 'new-password-off-' + Math.random().toString(36).substring(5));
                input.setAttribute('autocorrect', 'off');
                input.setAttribute('autocapitalize', 'off');
                input.setAttribute('spellcheck', 'false');
                input.setAttribute('data-lpignore', 'true');
                input.setAttribute('data-form-type', 'other');
            });
        }, 300);
    </script>
    """)

    st.markdown("<h3 style='text-align: center; color: #38bdf8;'>Acceso Cosecha Flores</h3>", unsafe_allow_html=True)
    
    @st.fragment
    def render_login_form():
        with st.container(border=True):
            st.markdown("### Iniciar Sesión")
            
            input_usuario = st.text_input(
                "INGRESA TU RUT O MAIL:", 
                key="campo_neutro_user",
                placeholder="Ej: 12345678k",
                autocomplete="off"
            ).strip().lower()
            
            # 🛡️ CONTRASEÑA BLINDADA: Usamos text_input común con clase CSS de enmascaramiento para evitar menús desplegables
            st.markdown('<div class="mascara-pass">', unsafe_allow_html=True)
            input_clave = st.text_input(
                "CONTRASEÑA DE ACCESO:", 
                key="campo_neutro_pass",
                placeholder="••••••••",
                autocomplete="off"
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

    render_login_form()
         
    # ==============================================================
    # RESTAURACIÓN MÁSTER: RECUPERACIÓN DE CLAVES EXTRAS DE TERRENO 
    # ==============================================================
    st.write("---")
    
    @st.fragment
    def render_recovery_form():
        with st.expander("¿Olvidó su Contraseña o RUT Inválido?", expanded=False):
            st.caption("Solicite un cambio express. El administrador aprobará su nueva clave desde el Panel de Auditoría.")
            with st.form("form_recuperacion_express_clave", clear_on_submit=True):
                rut_olvido = st.text_input(
                    "Ingrese su RUT para Alerta (Sin puntos ni guñón):", 
                    placeholder="Ej: 174031711", 
                    key="recup_rut_input",
                    autocomplete="off"
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

    render_recovery_form()
    st.stop()

# ==================================================================
# 3. INTERFAZ PRINCIPAL (USUARIO AUTENTICADO Y SEGURIZADO)
# ==================================================================
with st.sidebar:
    st.markdown(f" **Usuario Activo:** `{st.session_state.id_usuario_activo.upper()}`")
    st.markdown(f" **Rol:** `{st.session_state.rol_usuario.upper()}`")
    st.write("---")
    
    @st.fragment
    def render_sidebar_password_change():
        with st.expander(" Cambiar mi Contraseña", expanded=False):
            with st.form("form_cambio_clave_universal", clear_on_submit=True):
                # También protegemos el cambio de clave en el menú lateral
                st.markdown('<div class="mascara-pass">', unsafe_allow_html=True)
                nueva_p1 = st.text_input("Nueva Contraseña:", key="univ_p1", autocomplete="off", placeholder="••••••••")
                nueva_p2 = st.text_input("Confirmar Contraseña:", key="univ_p2", autocomplete="off", placeholder="••••••••")
                st.markdown('</div>', unsafe_allow_html=True)
                
                if st.form_submit_button("Guardar Nueva Clave", use_container_width=True):
                    if nueva_p1 and nueva_p1 == nueva_p2 and len(nueva_p1) >= 4:
                        try:
                            db.collection("usuarios").document(st.session_state.id_usuario_activo).update({"password": nueva_p1})
                            st.success("¡Contraseña actualizada con éxito!")
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.error("Las claves no coinciden o tienen menos de 4 caracteres.")

    render_sidebar_password_change()

    if st.session_state.rol_usuario == "admin":
        st.write("---")
        st.markdown("### Herramientas de Administrador")
        
        @st.fragment
        def render_admin_tools():
            with st.expander(" Registrar Nuevo Operario", expanded=False):
                with st.form("form_registro_interno_admin", clear_on_submit=True):
                    reg_rut = st.text_input("RUT Cosechador:", placeholder="Ej: 123456789", key="admin_reg_rut", autocomplete="off").strip().lower()
                    
                    st.markdown('<div class="mascara-pass">', unsafe_allow_html=True)
                    reg_clave = st.text_input("Contraseña inicial:", key="admin_reg_pass", autocomplete="off", placeholder="••••••••")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
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
                    rut_a_borrar = st.text_input("RUT a eliminar (Sin puntos ni guión):", placeholder="Ej: 123456789", key="del_rut", autocomplete="off").strip().lower()
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
                            
                            st.markdown('<div class="mascara-pass">', unsafe_allow_html=True)
                            nueva_clave_express = st.text_input(f"Nueva clave para {s['usuario']}:", key=f"express_{s['usuario']}", autocomplete="off", placeholder="••••••••")
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            if st.button(f"Forzar cambio para {s['usuario']}", key=f"btn_exp_{s['usuario']}", use_container_width=True):
                                if len(nueva_clave_express) >= 4:
                                    db.collection("usuarios").document(s["usuario"]).update({"password": nueva_clave_express})
                                    db.collection("solicitudes_clave").document(s["usuario"]).update({"estado": "resuelto"})
                                    st.success("¡Clave reconfigurada con éxito!")
                                    st.rerun()
                except Exception as e:
                    st.caption(f"Error al leer alertas: {e}")

        render_admin_tools()

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
# ==================================================================
# 4.C FUNCIÓN ESPEJO: ENROLAMIENTO MATINAL (DISEÑO EXACTO FOTO)
# =================================================================
import streamlit as st
import datetime
import io
import qrcode
import zoneinfo
import pandas as pd

def validar_rut_chileno_local(rut_limpio):
    """
    Valida matemáticamente un RUT chileno limpio (ej: '000000000').
    Retorna True si el dígito verificador es correcto.
    """
    if not rut_limpio or len(rut_limpio) < 2:
        return False
    try:
        cuerpo = rut_limpio[:-1]
        dv = rut_limpio[-1].upper()
        
        suma = 0
        multiplicador = 2
        for c in reversed(cuerpo):
            if not c.isdigit():
                return False
            suma += int(c) * multiplicador
            multiplicador = 2 if multiplicador == 7 else multiplicador + 1
            
        dv_esperado = 11 - (suma % 11)
        if dv_esperado == 11:
            dv_correcto = "0"
        elif dv_esperado == 10:
            dv_correcto = "K"
        else:
            dv_correcto = str(dv_esperado)
            
        return dv == dv_correcto
    except Exception:
        return False

@st.fragment
def dibujar_teclado_enrolamiento_antivero():
    st.html("""
        <style>
            .cuadro-teclado-enrol { max-width: 350px; margin: 10px auto; box-sizing: border-box; }
            .cuadro-teclado-enrol [data-testid="stHorizontalBlock"] { flex-direction: row !important; display: flex !important; gap: 8px !important; margin-bottom: 8px !important; }
            .cuadro-teclado-enrol div[data-testid="column"] { margin-bottom: 0 !important; }
            
            /* Visor Estilizado */
            .rut-display-box {
                color: #38bdf8 !important; font-weight: bold !important;
                border: 1px solid #334155 !important; border-radius: 8px !important;
                padding: 10px; text-align: center; display: flex; align-items: center; justify-content: center;
                box-sizing: border-box;
            }
            
            /* Estilo Barra Azul Horizontal de ENTER original */
            .cuadro-teclado-enrol .barra-azul-enter-enrol button { background-color: #2563eb !important; border: 1px solid #1d4ed8 !important; height: 54px !important; }
            .cuadro-teclado-enrol .barra-azul-enter-enrol button p { color: #ffffff !important; font-weight: bold !important; font-size: 16px !important; }
        </style>
    """)
    
    st.subheader("📍 Identificación de Campo (Matinal)")
    
    opciones_cc = list(lista_centros_costo_dinamica)
    if "Seleccione Centro de Costo..." not in opciones_cc:
        opciones_cc.insert(0, "Seleccione Centro de Costo...")
        
    opciones_contratista = list(lista_contratistas_dinamica)
    if "Seleccione Contratista..." not in opciones_contratista:
        opciones_contratista.insert(0, "Seleccione Contratista...")

    def formatear_centro_costo(opcion):
        if opcion == "Seleccione Centro de Costo...":
            return opcion
        if isinstance(opcion, dict):
            return f"{opcion.get('nombre', 'Sin Nombre')} ({opcion.get('codigo', 'CC 00')})"
        try:
            docs = db.collection("config_centros_costo").where("nombre", "==", opcion).limit(1).get()
            if docs:
                d = docs[0].to_dict()
                return f"{opcion} ({d.get('codigo', 'CC 00')})"
        except Exception:
            pass
        return str(opcion)

    def formatear_contratista(opcion):
        if opcion == "Seleccione Contratista...":
            return opcion
        if isinstance(opcion, dict):
            return f"{opcion.get('rut', '00.000.000-0')} | {opcion.get('nombre', 'Sin Nombre')} ( {opcion.get('codigo', 'xxxx')} )"
        try:
            docs = db.collection("config_contratistas").where("nombre", "==", opcion).limit(1).get()
            if docs:
                d = docs[0].to_dict()
                return f"{d.get('rut', '00.000.000-0')} | {opcion} ( {d.get('codigo', 'xxxx')} )"
        except Exception:
            pass
        return str(opcion)
    
    cc_manana = st.selectbox(
        "Centro de Costo / Cuartel:",
        options=opciones_cc,
        index=0,
        format_func=formatear_centro_costo,
        key="enrol_centro_costo"
    )
    
    contratista_manana = st.selectbox(
        "Empresa / Contratista:",
        options=opciones_contratista,
        index=0,
        format_func=formatear_contratista,
        key="enrol_contratista"
    )

    st.write("")
    st.markdown("<label>👤 RUT o Escaneo QR Cosechador</label>", unsafe_allow_html=True)

    rut_ingresado_fisico = st.text_input(
        "DIGITE O ESCANEE EL QR AQUÍ...",
        value="",
        key="input_unico_fisico_antivero",
        placeholder="Ej: 12345678-9 o URL del carnet"
    )

    rut_procesar = rut_ingresado_fisico.strip()
    nombre_extraido_qr = ""

    if "run=" in rut_procesar.lower() or "rut=" in rut_procesar.lower() or "http" in rut_procesar.lower():
        try:
            from urllib.parse import parse_qs, urlparse
            parsed_url = urlparse(rut_procesar)
            query_params = parse_qs(parsed_url.query)
            
            for param in ["run", "rut", "RUN", "RUT"]:
                if param in query_params:
                    rut_procesar = query_params[param][0]
                    break
            
            for param_nom in ["nombre", "nombres", "name", "NOMBRE"]:
                if param_nom in query_params:
                    nombre_extraido_qr = query_params[param_nom][0].replace("+", " ").title()
                    break
        except Exception:
            pass

    if nombre_extraido_qr and "input_nombre_operario" in st.session_state:
        st.session_state["input_nombre_operario"] = nombre_extraido_qr

    rut_crudo = "".join([c for c in rut_procesar.upper() if c.isdigit() or c == "K"])
    
    if len(rut_crudo) > 1:
        cuerpo = rut_crudo[:-1]
        dv = rut_crudo[-1]
        cuerpo_puntos = ""
        for i, char in enumerate(reversed(cuerpo)):
            if i > 0 and i % 3 == 0:
                cuerpo_puntos = "." + cuerpo_puntos
            cuerpo_puntos = char + cuerpo_puntos
        rut_visible = f"{cuerpo_puntos}-{dv}"
    else:
        rut_visible = rut_crudo if rut_crudo else "00.000.000-0"
    
    rut_es_valido = validar_rut_chileno_local(rut_crudo)
    icono_verificacion = "✅" if rut_es_valido else "🛑"
    
    st.markdown('<div class="cuadro-teclado-enrol">', unsafe_allow_html=True)
    
    col_visor_texto, col_visor_icono = st.columns([3, 1])
    with col_visor_texto:
        st.markdown(f'<div class="rut-display-box" style="font-size:20px; min-height:52px; margin-bottom:0; background-color:#1e293b;">{rut_visible}</div>', unsafe_allow_html=True)
    with col_visor_icono:
        st.markdown(f'<div class="rut-display-box" style="font-size:24px; min-height:52px; margin-bottom:0; background-color:#1e293b; text-align:center;">{icono_verificacion}</div>', unsafe_allow_html=True)
        
    st.write("")

    nombre_operario = st.text_input(
        "Nombre del Operario:",
        value="",
        key="input_nombre_operario",
        placeholder="Se llena automático con QR o escriba manual"
    )
    
    st.write("")
    
    st.markdown('<div class="barra-azul-enter-enrol">', unsafe_allow_html=True)
    bloqueo_enrol = (
        not rut_es_valido or 
        not nombre_operario.strip() or
        cc_manana == "Seleccione Centro de Costo..." or 
        contratista_manana == "Seleccione Contratista..."
    )
    
    if st.button("💾 ENTER (Validar Ingreso)", key="btn_enrol_ENTER_M", use_container_width=True, disabled=bloqueo_enrol):
        try:
            tz_cl = zoneinfo.ZoneInfo("America/Santiago")
            ahora_cl = datetime.datetime.now(tz_cl)
            fecha_hoy_str = ahora_cl.strftime("%d/%m/%Y")
            rut_limpio = rut_crudo.lower()
            nombre_limpio = nombre_operario.strip().title()
            
            contratista_nombre_val = contratista_manana.get("nombre") if isinstance(contratista_manana, dict) else contratista_manana
            contratista_rut_val = "Sin RUT"
            contratista_codigo_val = "Sin Código"
            
            try:
                docs_c = db.collection("config_contratistas").where("nombre", "==", contratista_nombre_val).limit(1).get()
                if docs_c:
                    d_c = docs_c[0].to_dict()
                    contratista_rut_val = d_c.get("rut", "Sin RUT")
                    contratista_codigo_val = d_c.get("codigo", "Sin Código")
            except Exception:
                pass

            duplicados = db.collection("credenciales_activas_dia")\
                .where("RutCosechador", "==", rut_limpio)\
                .limit(1).get()
                
            if duplicados:
                datos_existentes = duplicados[0].to_dict()
                id_existente = datos_existentes.get("id_express")
                nombre_registrado = datos_existentes.get("NombreCosechador", nombre_limpio)
                st.warning(f"⚠️ El operario {nombre_registrado} (RUT {rut_visible}) ya cuenta con la Ficha #{id_existente} asignada previamente. Se recupera su credencial.")
                
                qr = qrcode.QRCode(version=1, box_size=8, border=1)
                qr.add_data(str(id_existente))
                qr.make(fit=True)
                buf = io.BytesIO()
                qr.make_image(fill_color="black", back_color="white").save(buf, format="PNG")
                
                st.session_state.qr_render_actual = buf.getvalue()
                st.session_state.id_render_actual = id_existente
                st.session_state.nombre_render_actual = nombre_registrado
                st.rerun()
            
            ya_enrolados = db.collection("credenciales_activas_dia").stream()
            numeros_ocupados = [int(doc.to_dict().get("id_express")) for doc in ya_enrolados if doc.to_dict().get("id_express")]
            
            id_express = 100
            for num in range(100, 201):
                if num not in numeros_ocupados:
                    id_express = num
                    break
                
            codigo_largo_auditoria = f"{ahora_cl.strftime('%d/%m/%Y')}-{rut_limpio}-{id_express}"
            cc_valor = cc_manana.get("nombre") if isinstance(cc_manana, dict) else cc_manana

            db.collection("credenciales_activas_dia").document(str(id_express)).set({
                "id_express": str(id_express),
                "RutCosechador": rut_limpio,
                "NombreCosechador": nombre_limpio,
                "CentroCosto": cc_valor,
                "Contratista": contratista_nombre_val,
                "RutContratista": contratista_rut_val,
                "CodigoContratista": contratista_codigo_val,
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
            st.session_state.nombre_render_actual = nombre_limpio
            st.rerun()
        except Exception as ex:
            st.error(f"❌ Error en el enrolamiento: {ex}")
            
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    qr_activo = st.session_state.get("qr_render_actual", None)
    if "imprimir_zebra_trigger" not in st.session_state:
        st.session_state.imprimir_zebra_trigger = False
    if "imprimir_windows_trigger" not in st.session_state:
        st.session_state.imprimir_windows_trigger = False
        
    if qr_activo:
        st.write("")
        import base64
        qr_b64 = base64.b64encode(qr_activo).decode("utf-8")
        id_actual_str = str(st.session_state.get("id_render_actual", ""))
        nombre_actual_str = str(st.session_state.get("nombre_render_actual", ""))
        
        with st.container(border=True):
            col_ticket_qr, col_ticket_btn = st.columns([1.3, 1.7])
            with col_ticket_qr:
                st.image(qr_activo, caption=f"Ficha #{id_actual_str}\n{nombre_actual_str}", width=150)
            with col_ticket_btn:
                st.write("### Opciones de Impresión")
                
                if st.button("🚀 IMPRESIÓN DIRECTA (ZEBRA ZM400)", key="btn_print_zebra", use_container_width=True, type="primary"):
                    st.session_state.imprimir_zebra_trigger = True
                    st.rerun()
                    
                if st.button("🖨️ IMPRIMIR CON WINDOWS (Elegir...)", key="btn_print_windows", use_container_width=True):
                    st.session_state.imprimir_windows_trigger = True
                    st.rerun()
                    
                if st.button("🗑️ Siguiente Operario", key="clear_qr_view", use_container_width=True):
                    st.session_state.qr_render_actual = None
                    st.session_state.id_render_actual = None
                    st.session_state.nombre_render_actual = None
                    st.session_state.imprimir_zebra_trigger = False
                    st.session_state.imprimir_windows_trigger = False
                    st.rerun()
                    
        if st.session_state.imprimir_windows_trigger:
            st.session_state.imprimir_windows_trigger = False
            
            st.components.v1.html(f"""
                <div id="ticket-imprimible-exclusivo" style="text-align: center; font-family: sans-serif; background: #ffffff !important; color: #000000 !important; padding: 20px; position: fixed; left: -9999px;">
                    <h3 style="margin-top: 0px; margin-bottom: 5px; font-size: 16px; color: #000000 !important;">Flores Antivero Cosecha</h3>
                    <img src="data:image/png;base64,{qr_b64}" style="width: 180px; height: 180px;" />
                    <h2 style="margin-top: 10px; margin-bottom: 2px; font-size: 26px; color: #000000 !important;">FICHA #{id_actual_str}</h2>
                    <div style="font-size: 20px; font-weight: bold; color: #000000 !important; margin-top: 5px;">{nombre_actual_str}</div>
                </div>
                
                <script>
                    const parentDoc = window.parent.document;
                    
                    const viejoEstilo = parentDoc.getElementById("estilo-impresion-dinamico");
                    if (viejoEstilo) viejoEstilo.remove();
                    
                    const viejoContenedor = parentDoc.getElementById("ticket-imprimible-exclusivo");
                    if (viejoContenedor) viejoContenedor.remove();
                    
                    var estilo = parentDoc.createElement('style');
                    estilo.id = "estilo-impresion-dinamico";
                    estilo.innerHTML = `
                        @media print {{
                            html, body, [data-testid="stAppViewContainer"] {{
                                background-color: #ffffff !important;
                                color: #000000 !important;
                                background: #ffffff !important;
                            }}
                            body * {{ 
                                visibility: hidden !important; 
                            }}
                            #ticket-imprimible-exclusivo, #ticket-imprimible-exclusivo * {{ 
                                visibility: visible !important; 
                            }}
                            #ticket-imprimible-exclusivo {{ 
                                position: absolute !important; 
                                left: 0 !important; 
                                top: 0 !important; 
                                width: 100% !important; 
                                text-align: center !important; 
                                background: #ffffff !important;
                                display: block !important;
                            }}
                        }}
                    `;
                    parentDoc.head.appendChild(estilo);
                    
                    var divTemporal = parentDoc.createElement('div');
                    divTemporal.id = "ticket-imprimible-exclusivo";
                    divTemporal.style.cssText = "position:absolute; left:0; top:0; width:100%; text-align:center; background:#ffffff; z-index:999999; display:none;";
                    divTemporal.innerHTML = `
                        <h3 style="margin-top: 0px; margin-bottom: 5px; font-size: 16px; color: #000000 !important;">Flores Antivero Cosecha</h3>
                        <img src="data:image/png;base64,{qr_b64}" style="width: 180px; height: 180px;" />
                        <h2 style="margin-top: 10px; margin-bottom: 2px; font-size: 26px; color: #000000 !important;">FICHA #{id_actual_str}</h2>
                        <div style="font-size: 20px; font-weight: bold; color: #000000 !important; margin-top: 5px;">{nombre_actual_str}</div>
                    `;
                    parentDoc.body.appendChild(divTemporal);
                    
                    setTimeout(function() {{
                        window.parent.print();
                    }}, 250);
                </script>
            """, height=0, width=0)

        if st.session_state.imprimir_zebra_trigger:
            st.session_state.imprimir_zebra_trigger = False
            zpl_code = f"^XA^FO100,30^BQN,2,5^FDQA,{id_actual_str}^FS^FO100,180^A0N,30,30^FDID: {id_actual_str}^FS^FO100,220^A0N,25,25^FD{nombre_actual_str}^FS^XZ"
            
            st.components.v1.html(f"""
                <script>
                    if (typeof qz !== 'undefined' && qz.websocket.isActive()) {{
                        var config = qz.configs.create("Zebra ZM400");
                        var data = ['{zpl_code}'];
                        qz.print(config, data).catch(function(e) {{ console.error(e); }});
                    }} else {{
                        var iframe = window.parent.parent.document.createElement('iframe');
                        iframe.style.display = 'none';
                        window.parent.parent.document.body.appendChild(iframe);
                        iframe.contentWindow.document.write('{zpl_code}');
                        iframe.contentWindow.print();
                    }}
                </script>
            """, height=0, width=0)

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
            
            navigator.mediaDevices.getUserMedia({ 
                video: { facingMode: "environment", width: { ideal: 640 }, height: { ideal: 480 } } 
            })
            .then(function(stream) {
                video.srcObject = stream;
                video.setAttribute("playsinline", true);
                video.play();
                
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
                }, 500);
                
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

        # 🚀 OÍDOR DE EVENTOS EN PYTHON: Atrapa el RUT enviado por JavaScript
        st.html("""
        <script>
            window.addEventListener('message', function(e) {
                if (e.data && e.data.type === 'ANTIVERO_QR_CARNET') {
                    const inputs = window.parent.document.querySelectorAll('input');
                    inputs.forEach(input => {
                        if (input.getAttribute('aria-label') && input.getAttribute('aria-label').includes('RUT')) {
                            input.value = e.data.rut;
                            input.dispatchEvent(new Event('input', { bubbles: true }));
                        }
                    });
                }
            });
        </script>
        """)

        st.write("---")
        
        # ==================================================================
        # TABLA EDITABLE ÚNICA (Ubicada exactamente en la columna derecha)
        # ==================================================================
        st.subheader("📋 Listado de Enrolados del Día (Modificable)")
        st.caption("Modifique los campos directamente en la tabla y presione el botón inferior para guardar los cambios en Firebase.")

        try:
            docs_registros = db.collection("credenciales_activas_dia").stream()
            lista_docs = []
            for d in docs_registros:
                row_data = d.to_dict()
                row_data["doc_id"] = d.id  
                lista_docs.append(row_data)

            if lista_docs:
                df_enrolados = pd.DataFrame(lista_docs)
                
                columnas_ordenadas = [
                    "id_express", 
                    "NombreCosechador", 
                    "RutCosechador", 
                    "Contratista", 
                    "RutContratista", 
                    "CodigoContratista", 
                    "CentroCosto"
                ]
                
                for col in columnas_ordenadas:
                    if col not in df_enrolados.columns:
                        df_enrolados[col] = ""

                df_display = df_enrolados[columnas_ordenadas + ["doc_id"]].copy()

                df_editado = st.data_editor(
                    df_display,
                    column_config={
                        "doc_id": None, 
                        "id_express": st.column_config.TextColumn("ID Ficha", disabled=True),
                        "NombreCosechador": st.column_config.TextColumn("Nombre Operario"),
                        "RutCosechador": st.column_config.TextColumn("RUT Operario"),
                        "Contratista": st.column_config.TextColumn("Nombre Contratista"),
                        "RutContratista": st.column_config.TextColumn("RUT Contratista"),
                        "CodigoContratista": st.column_config.TextColumn("Código Contratista"),
                        "CentroCosto": st.column_config.TextColumn("Centro de Costo")
                    },
                    hide_index=True,
                    key="tabla_enrolados_editable_derecha_principal"
                )

                if st.button("💾 Guardar Cambios Modificados en Firebase", key="btn_guardar_cambios_tabla_derecha", type="primary"):
                    try:
                        batch = db.batch()
                        for index, row in df_editado.iterrows():
                            doc_id = str(row["doc_id"])
                            doc_ref = db.collection("credenciales_activas_dia").document(doc_id)
                            
                            actualizacion = {
                                "NombreCosechador": str(row["NombreCosechador"]),
                                "RutCosechador": str(row["RutCosechador"]),
                                "Contratista": str(row["Contratista"]),
                                "RutContratista": str(row["RutContratista"]),
                                "CodigoContratista": str(row["CodigoContratista"]),
                                "CentroCosto": str(row["CentroCosto"])
                            }
                            batch.update(doc_ref, actualizacion)
                        
                        batch.commit()
                        st.success("✅ ¡Los cambios se han actualizado y guardado correctamente en Firebase!")
                    except Exception as e_firebase:
                        st.error(f"❌ Error al guardar en Firebase: {e_firebase}")
            else:
                st.info("No hay registros de enrolamiento activos para mostrar en la tabla.")
        except Exception as e_load:
            st.error(f"Error al cargar registros desde la base de datos: {e_load}")

        st.write("---")

        # ==================================================================
        # MÓDULO DE REIMPRESIÓN DE FICHAS EXTRAVIADAS
        # ==================================================================
        st.markdown("<h4 style='color:#38bdf8;'>🖨️ Módulo de Reimpresión de Fichas Extraviadas</h4>", unsafe_allow_html=True)
        
        id_a_recuperar = st.text_input(
            "Digite el número de ID Express a recuperar (Ej: 105):",
            placeholder="Escriba el número aquí...",
            key="input_recuperador_manual_express"
        ).strip()
        
        if st.button("🔄 Regenerar y Cargar QR a la Izquierda", key="btn_ejecutar_reimpresion_limpio", use_container_width=True):
            if id_a_recuperar:
                try:
                    doc_ref = db.collection("credenciales_activas_dia").document(id_a_recuperar).get()
                    
                    if doc_ref.exists:
                        datos_credencial = doc_ref.to_dict()
                        nombre_encontrado = datos_credencial.get("NombreCosechador", "Sin Nombre")
                        
                        qr_reimp = qrcode.QRCode(version=1, box_size=8, border=1)
                        qr_reimp.add_data(str(id_a_recuperar))
                        qr_reimp.make(fit=True)
                        
                        buf_reimp = io.BytesIO()
                        qr_reimp.make_image(fill_color="black", back_color="white").save(buf_reimp, format="PNG")
                        
                        st.session_state.qr_render_actual = buf_reimp.getvalue()
                        st.session_state.id_render_actual = id_a_recuperar
                        st.session_state.nombre_render_actual = nombre_encontrado
                        
                        st.toast(f"🎟️ Ficha #{id_a_recuperar} de {nombre_encontrado} cargada con éxito a la izquierda.")
                        st.rerun()
                    else:
                        st.error(f"❌ El ID #{id_a_recuperar} no existe registrado en la base de datos.")
                except Exception as e_reimp:
                    st.error(f"❌ Error al reconstruir el código QR: {e_reimp}")
            else:
                st.warning("⚠️ Por favor, ingrese un número de ID express válido antes de presionar el botón.")

# --- CONTENIDO DE LA PESTAÑA A: TERMINAL DE COSECHA AGRÍCOLA ---
with tab_terminal:
    # Inicialización segura de estados para el Mesón si no existen
    if "familia_activa_meson" not in st.session_state:
        st.session_state.familia_activa_meson = "DELPHINIUM"
    if "rut_cosechador" not in st.session_state:
        st.session_state.rut_cosechador = ""
    if "rut_bloqueado_operacion" not in st.session_state:
        st.session_state.rut_bloqueado_operacion = True
    if "id_express_cosecha" not in st.session_state:
        st.session_state.id_express_cosecha = ""
    if "cc_activo_meson" not in st.session_state:
        st.session_state.cc_activo_meson = ""
    if "contratista_activo_meson" not in st.session_state:
        st.session_state.contratista_activo_meson = ""

    # Candado inteligente global heredable
    bloqueo_activo = st.session_state.rut_bloqueado_operacion
    
    # 🚀 CONTENEDOR 1: División máster horizontal de la pantalla de la tablet
    col_panel_izq, col_panel_central_derecho = st.columns([1.2, 2.8])
    
    with col_panel_izq:
        @st.fragment
        def fragmento_lector_ficha_express():
            st.markdown("<h3 style='margin:0 0 5px 0; color:#38bdf8;'>📌 Lector de Ficha Express</h3>", unsafe_allow_html=True)
            st.caption("Digite el ID de 3 dígitos (100-200) o use la cámara de la tablet:")

            id_ingresado_fisico = st.text_input(
                "DIGITE EL ID DIRECTAMENTE AQUÍ...",
                value="",
                key="input_id_express_terminal_unico",
                placeholder="Ej: 101",
                label_visibility="collapsed"
            )

            id_filtrado_manual = "".join([c for c in id_ingresado_fisico if c.isdigit()])
            
            st.markdown("<p style='color:#94a3b8; font-size:13px; margin-bottom:5px;'>📷 Escáner de Ficha por Cámara:</p>", unsafe_allow_html=True)
            
            id_filtrado_camara = ""
            foto_qr = st.camera_input("Capturar QR", label_visibility="collapsed", key="lector_camara_nativo")
            
            if foto_qr is not None:
                try:
                    from PIL import Image
                    try:
                        from pyzbar.pyzbar import decode
                        img = Image.open(foto_qr)
                        resultados = decode(img)
                        if resultados:
                            texto_qr = resultados[0].data.decode("utf-8")
                            id_filtrado_camara = "".join([c for c in texto_qr if c.isdigit()])
                    except ImportError:
                        import cv2
                        import numpy as np
                        file_bytes = np.asarray(bytearray(foto_qr.read()), dtype=np.uint8)
                        opencv_img = cv2.imdecode(file_bytes, 1)
                        detector = cv2.QRCodeDetector()
                        texto_qr, _, _ = detector.detectAndDecode(opencv_img)
                        if texto_qr:
                            id_filtrado_camara = "".join([c for c in texto_qr if c.isdigit()])
                except Exception as e_cam:
                    st.caption(f"Ajustando enfoque de cámara... ({e_cam})")

            id_final_a_procesar = id_filtrado_camara if id_filtrado_camara else id_filtrado_manual
            id_visible = f"#{id_final_a_procesar}" if id_final_a_procesar else "#---"
            
            st.markdown(
                f'<div style="color: #38bdf8; font-weight: bold; border: 1px solid #334155; '
                f'border-radius: 8px; padding: 12px; font-size: 26px; text-align: center; '
                f'background-color: #1e293b; margin-bottom: 15px;">{id_visible}</div>', 
                unsafe_allow_html=True
            )

            if id_final_a_procesar and len(id_final_a_procesar) >= 3:
                if st.session_state.get("id_express_cosecha", "") != str(id_final_a_procesar):
                    try:
                        id_num = int(id_final_a_procesar)
                        if 100 <= id_num <= 250:
                            doc_ref = db.collection("credenciales_activas_dia").document(str(id_num)).get()
                            
                            if doc_ref.exists:
                                datos_operario = doc_ref.to_dict()
                                
                                rut_raw = datos_operario.get("RutCosechador", "")
                                rut_encontrado = str(rut_raw).strip().upper()
                                
                                cc_encontrado = datos_operario.get("CentroCosto", "CC_TERRENO")
                                contratista_encontrado = datos_operario.get("Contratista", "INDEPENDIENTE")

                                st.session_state.rut_cosechador = rut_encontrado
                                st.session_state.id_express_cosecha = str(id_num)
                                st.session_state.cc_activo_meson = str(cc_encontrado)
                                st.session_state.contratista_activo_meson = str(contratista_encontrado)
                                
                                st.session_state.rut_bloqueado_operacion = False
                                st.toast(f"✅ Ficha #{id_num} cargada con éxito.", icon="👤")
                                st.rerun()
                            else:
                                st.error("⚠️ Ficha Express no registrada en el sistema.")
                    except Exception as e:
                        st.error(f"Error en validación: {e}")

        fragmento_lector_ficha_express()

        # --- BOTONES DE MERMA CON FAMILIA Y VARIEDAD (ESTILO FLORES) ---
        st.markdown("<hr style='margin:15px 0; border-color:#334155;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='margin:0 0 5px 0; color:#f87171;'>🗑️ Registro de Mermas</h4>", unsafe_allow_html=True)
        
        # Inicializar estado para la familia de mermas si no existe
        if "familia_activa_merma" not in st.session_state:
            st.session_state.familia_activa_merma = ""

        tiene_rut_merma = st.session_state.get("rut_cosechador", "") != ""

        # Consultar mermas desde Firestore y agruparlas por familia
        try:
            mermas_docs = db.collection("merma").stream()
            lista_mermas_db = [doc.to_dict() for doc in mermas_docs]
        except Exception:
            lista_mermas_db = []

        # Estructurar las mermas en un diccionario por familia dinámicamente
        diccionario_mermas_dinamico = {}
        for m in lista_mermas_db:
            fam = m.get("familia", "GENERAL").strip().upper()
            if not fam:
                fam = "GENERAL"
            if fam not in diccionario_mermas_dinamico:
                diccionario_mermas_dinamico[fam] = []
            diccionario_mermas_dinamico[fam].append({
                "codigo": m.get("codigo", "M00"),
                "nombre": m.get("merma", "Merma Huerto"),
                "variedad": m.get("variedad", "")
            })

        # Fallback si no hay registros en la base de datos
        if not diccionario_mermas_dinamico:
            diccionario_mermas_dinamico = {
                "CALIDAD": [{"codigo": "M01", "nombre": "Merma Huerto", "variedad": "Estándar"}],
                "ROTURA": [{"codigo": "M02", "nombre": "Merma Huerto", "variedad": "Física"}]
            }

        # Seleccionar la primera familia por defecto si la actual no es válida
        familias_mermas_lista = list(diccionario_mermas_dinamico.keys())
        if st.session_state.familia_activa_merma not in familias_mermas_lista and familias_mermas_lista:
            st.session_state.familia_activa_merma = familias_mermas_lista[0]

        st.caption("Seleccione la familia de merma:")
        
        # Renderizado de Botones de Familia de Mermas (en columnas de 2)
        for i in range(0, len(familias_mermas_lista), 2):
            par_fam_mermas = familias_mermas_lista[i:i+2]
            cols_fm = st.columns(2)
            for idx_fm, fam_m_item in enumerate(par_fam_mermas):
                with cols_fm[idx_fm]:
                    es_activa_m = (st.session_state.familia_activa_merma == fam_m_item)
                    tipo_b_m = "primary" if es_activa_m else "secondary"
                    
                    if st.button(f"🗑️ {fam_m_item}", key=f"btn_grid_fam_merma_{fam_m_item.replace(' ', '_')}", use_container_width=True, type=tipo_b_m):
                        st.session_state.familia_activa_merma = fam_m_item
                        st.rerun()

        st.markdown("<hr style='margin:10px 0; border-color:#334155;'>", unsafe_allow_html=True)

        # --- RENDERIZADO DE VARIEDADES DE MERMA DE LA FAMILIA ACTIVA ---
        familia_merma_actual = st.session_state.familia_activa_merma
        lista_mermas_brutas = diccionario_mermas_dinamico.get(familia_merma_actual, [])
        
        # Ordenamos alfabéticamente por nombre/variedad
        lista_mermas_render = sorted(lista_mermas_brutas, key=lambda x: str(x.get("nombre", "")).lower())

        if lista_mermas_render:
            st.markdown(f"<p style='color:#94a3b8; font-size:12px; margin-bottom:8px;'>Variedades en {familia_merma_actual}:</p>", unsafe_allow_html=True)
            
            for i in range(0, len(lista_mermas_render), 2):
                bloque_par_m = lista_mermas_render[i:i+2]
                cols_mm = st.columns(2)
                for idx_mm, m_item in enumerate(bloque_par_m):
                    indice_abs_mm = i + idx_mm
                    with cols_mm[idx_mm]:
                        cod_m = m_item.get("codigo", "M00")
                        nom_m = m_item.get("nombre", "Merma General")
                        var_m = m_item.get("variedad", "")
                        
                        texto_mostrar = f"{nom_m} - {var_m}" if var_m else nom_m

                        st.html(f"""
                        <div style="background-color: #2a1b1b; border: 1px solid #7f1d1d; border-radius: 10px; padding: 10px 12px; margin-bottom: 4px; border-left: 6px solid #ef4444;">
                            <div style="color: #fca5a5; font-size: 13px; font-weight: bold; font-family: system-ui, -apple-system, sans-serif;">{texto_mostrar}</div>
                            <div style="color: #94a3b8; font-size: 11px; font-family: system-ui, -apple-system, sans-serif;">Cód. Merma: {cod_m}</div>
                        </div>
                        """)

                        if st.button("Seleccionar", key=f"btn_merma_express_{cod_m}_{indice_abs_mm}", use_container_width=True, disabled=not tiene_rut_merma):
                            st.session_state.flor_seleccionada_meson = {
                                "codigo": cod_m, 
                                "nombre": f"Merma: {texto_mostrar}", 
                                "color": "#ef4444",
                                "es_merma": True
                            }
                            st.session_state.cantidad_varas_meson = 30
                            st.rerun()
with col_panel_central_derecho:
        if "flor_seleccionada_meson" not in st.session_state: 
            st.session_state.flor_seleccionada_meson = None
        if "cantidad_varas_meson" not in st.session_state: 
            st.session_state.cantidad_varas_meson = 30
            
        col_centro_flujo, col_derecha_consolidacion = st.columns([1.6, 1.2])
        
        with col_centro_flujo:
            st.markdown("<h3 style='margin:0 0 5px 0; color:#38bdf8;'>🌸 Selección de Familia de Flores</h3>", unsafe_allow_html=True)
            st.caption("Toque una familia para desplegar sus variedades en el mesón:")
            
            st.html("<style>button[key^='btn_grid_fam_'] { border-radius:8px !important; padding:12px !important; font-weight:bold !important; font-size:15px !important; }</style>")
            
            familias_lista = list(diccionario_flores_dinamico.keys()) if diccionario_flores_dinamico else ["RANÚNCULO", "PEONÍA", "DELPHINIUM", "SNAPDRAGON"]
            
            for i in range(0, len(familias_lista), 2):
                par_familias = familias_lista[i:i+2]
                cols_fam = st.columns(2)
                for idx, fam_item in enumerate(par_familias):
                    with cols_fam[idx]:
                        es_activa = (st.session_state.familia_activa_meson == fam_item)
                        tipo_b = "primary" if es_activa else "secondary"
                        prefix = "🌿 " if "DELPHINIUM" in fam_item else "🌸 "
                        
                        if st.button(f"{prefix}{fam_item}", key=f"btn_grid_fam_{fam_item.replace(' ', '_')}", use_container_width=True, type=tipo_b):
                            st.session_state.familia_activa_meson = fam_item
                            st.rerun()
            
            st.markdown("<hr style='margin:15px 0; border-color:#334155;'>", unsafe_allow_html=True)
            
            # --- RENDERIZADO UNIFICADO DE VARIEDADES DE FLORES (Ordenadas Alfabéticamente) ---
            familia_actual = st.session_state.familia_activa_meson
            lista_flores_brutas = diccionario_flores_dinamico.get(familia_actual, []) if diccionario_flores_dinamico else []
            
            # 🔤 Ordenamos la lista de diccionarios alfabéticamente por su nombre
            lista_flores_render = sorted(lista_flores_brutas, key=lambda x: str(x.get("nombre", "")).lower())
            
            if lista_flores_render:
                st.markdown(f"<p style='color:#94a3b8; font-size:13px; margin-bottom:12px;'>Variedades activas en {familia_actual}:</p>", unsafe_allow_html=True)
                
                for i in range(0, len(lista_flores_render), 2):
                    bloque_par = lista_flores_render[i:i+2]
                    cols_f = st.columns(2)
                    for idx_f, flor in enumerate(bloque_par):
                        indice_absoluto = i + idx_f
                        with cols_f[idx_f]:
                            cod_f, nom_f = flor["codigo"], flor["nombre"]
                            color_real = flor.get("color", "#ec4899")
                            
                            tiene_rut = st.session_state.get("rut_cosechador", "") != ""
                            
                            # 1. Tarjeta visual limpia con el color de Firebase y el código KAME debajo
                            st.html(f"""
                            <div style="background-color: #1e2530; border: 1px solid #2d3748; border-radius: 12px; padding: 12px 14px; margin-bottom: 4px; border-left: 6px solid {color_real};">
                                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 3px;">
                                    <span style="display: inline-block; width: 12px; height: 12px; background-color: {color_real}; border-radius: 50%; box-shadow: 0 0 5px {color_real}; flex-shrink: 0;"></span>
                                    <span style="color: #ffffff; font-size: 15px; font-weight: bold; font-family: system-ui, -apple-system, sans-serif;">{nom_f}</span>
                                </div>
                                <div style="color: #94a3b8; font-size: 12px; margin-left: 20px; font-family: system-ui, -apple-system, sans-serif;">Código KAME: {cod_f}</div>
                            </div>
                            """)
                            
                            # 2. Botón limpio para seleccionar la variedad
                            if st.button(f"Seleccionar {nom_f}", key=f"btn_var_real_{cod_f}_{indice_absoluto}", use_container_width=True, disabled=not tiene_rut):
                                st.session_state.flor_seleccionada_meson = {"codigo": cod_f, "nombre": nom_f, "color": color_real, "es_merma": False}
                                st.session_state.cantidad_varas_meson = 30
                                st.rerun()


with col_derecha_consolidacion:
            st.markdown("<h2 style='color:#f8fafc; margin-top:0;'>📥 Mesón</h2>", unsafe_allow_html=True)
            rut_aux = st.session_state.get("rut_cosechador", "")
                
            if rut_aux and len(rut_aux) > 1:
                rut_final = f"{rut_aux[:-1]}-{rut_aux[-1]}".upper()
            else:
                rut_final = "00.000.000-0"
                
            st.html("<style>.columna-meson button { background-color:#0f172a !important; border:2px solid #475569 !important; } .columna-meson button p { color:#f8fafc !important; font-weight:bold !important; } .columna-meson .btn-verde button { background-color:#10b981 !important; border:2px solid #047857 !important; height:50px !important; } .columna-meson .btn-verde button p { color:#0f172a !important; font-size:16px !important; }</style>")
            st.markdown('<div class="columna-meson">', unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown(f"**RUT:** `{rut_final}`")
                        
                # 🎨 Mostramos un punto coloreado dinámico también en el resumen del mesón
                if st.session_state.flor_seleccionada_meson:
                    f_sel = st.session_state.flor_seleccionada_meson
                    color_meson = f_sel.get("color", "#38bdf8")
                    st.markdown(f"**Item:** <span style='color:{color_meson}; font-weight:bold;'>● {f_sel['nombre']}</span>", unsafe_allow_html=True)
                else:
                    st.markdown("**Item:** <span style='color:#94a3b8; font-weight:bold;'>Ninguno</span>", unsafe_allow_html=True)
                        
                # 📍 Selector de Fecha de Registro / Inyección (Por defecto: Día Actual en Chile)
                import datetime
                import zoneinfo
                
                tz_cl = zoneinfo.ZoneInfo("America/Santiago")
                fecha_actual_chile = datetime.datetime.now(tz_cl).date()
                
                fecha_ingreso_meson = st.date_input(
                    "📅 Fecha de Registro:",
                    value=fecha_actual_chile,
                    key="input_fecha_ingreso_meson"
                )

                # 📍 Apartado para seleccionar el Origen de Huerto desde Firebase (config_origen_huerto)
                huertos_disponibles = []
                try:
                    docs_huertos = db.collection("config_origen_huerto").stream()
                    for doc in docs_huertos:
                        d_h = doc.to_dict()
                        nombre_h = d_h.get("nombre")
                        if nombre_h:
                            huertos_disponibles.append(nombre_h)
                    
                    # 🔤 Ordenar alfabéticamente la lista obtenida de Firebase
                    huertos_disponibles.sort()
                    
                except Exception:
                    pass
                
                # Respaldo por si la colección está vacía inicialmente
                if not huertos_disponibles:
                    huertos_disponibles = ["Sin huertos registrados"]

                huerto_seleccionado_meson = st.selectbox("📍 Seleccionar Origen de Huerto:", options=huertos_disponibles, key="select_huerto_meson")

                st.caption("⚙️ Edita varas:")
                        
                col_m1, col_m2, col_m3 = st.columns([1.2, 2.2, 1.2])
                with col_m1:
                    if st.button("-5", key="btn_m_menos_5_final_fijo", use_container_width=True):
                        st.session_state.cantidad_varas_meson = max(0, st.session_state.get("cantidad_varas_meson", 30) - 5)
                        st.rerun()
                                
                with col_m2:
                    varas_puente = st.number_input(
                        "Varas:", min_value=0, max_value=500,
                        value=int(st.session_state.get("cantidad_varas_meson", 30)),
                        step=1, label_visibility="collapsed"
                    )
                    if varas_puente != st.session_state.get("cantidad_varas_meson", 30):
                        st.session_state.cantidad_varas_meson = int(varas_puente)
                        st.fragment(lambda: None)
                        st.rerun()
                                
                with col_m3:
                    if st.button("+5", key="btn_m_mas_5_final_fijo", use_container_width=True):
                        st.session_state.cantidad_varas_meson = min(500, st.session_state.get("cantidad_varas_meson", 30) + 5)
                        st.rerun()

                st.write("")
                        
                tiene_rut = st.session_state.get("rut_cosechador", "") != ""
                tiene_flor = st.session_state.flor_seleccionada_meson is not None
                bloq_f = not (tiene_rut and tiene_flor)

                # 🎯 VALIDACIÓN DE SEGURIDAD OPERATIVA
                st.markdown('<div class="btn-verde">', unsafe_allow_html=True)
                if st.button("✅ Confirmar e Inyectar", key="btn_inj", use_container_width=True, disabled=bloq_f):
                    try:
                        # A. Recuperamos datos del estado de la tablet
                        cc_nombre = st.session_state.get("cc_activo_meson", "Chipana")
                        contratista_nombre = st.session_state.get("contratista_activo_meson", "INDEPENDIENTE")
                                
                        # 🔍 Buscamos de forma automática el nombre del cosechador registrado previamente en el día
                        rut_limpio_busqueda = st.session_state.get("rut_cosechador", "").strip().lower()
                        nombre_cosechador_encontrado = "Sin Nombre"

                        try:
                            fecha_hoy_busqueda_str = datetime.datetime.now(tz_cl).strftime("%d/%m/%Y")
                            
                            credenciales_query = db.collection("credenciales_activas_dia")\
                                .where("FechaFiltro", "==", fecha_hoy_busqueda_str)\
                                .where("RutCosechador", "==", rut_limpio_busqueda)\
                                .limit(1).get()
                                    
                            if credenciales_query:
                                nombre_cosechador_encontrado = credenciales_query[0].to_dict().get("NombreCosechador", "Sin Nombre")
                        except Exception:
                            pass

                        # B. Buscamos el CÓDIGO real del Centro de Costo en Firestore
                        codigo_cc_real = "n/a"
                        try:
                            cc_docs = db.collection("config_centros_costo").stream()
                            for doc in cc_docs:
                                d_cc = doc.to_dict()
                                if str(d_cc.get("nombre", "")).strip().lower() == cc_nombre.strip().lower():
                                    codigo_cc_real = d_cc.get("codigo", "n/a")
                                    break
                        except Exception:
                            pass
                                    
                        # C. Buscamos el RUT y CÓDIGO real del Contratista en Firestore
                        rut_contratista_real = "0-0"
                        codigo_contratista_real = "n/a"
                        try:
                            contra_docs = db.collection("config_contratistas").stream()
                            for doc in contra_docs:
                                d_cont = doc.to_dict()
                                if str(d_cont.get("nombre", "")).strip().lower() == contratista_nombre.strip().lower():
                                    rut_contratista_real = d_cont.get("rut", "0-0")
                                    codigo_contratista_real = d_cont.get("codigo", "n/a")
                                    break
                        except Exception:
                            pass

                        # C.1. Buscamos el CÓDIGO real del Origen de Huerto seleccionado en Firestore
                        codigo_huerto_real = "n/a"
                        try:
                            huerto_docs = db.collection("config_origen_huerto").stream()
                            for doc in huerto_docs:
                                d_huerto = doc.to_dict()
                                if str(d_huerto.get("nombre", "")).strip().lower() == huerto_seleccionado_meson.strip().lower():
                                    codigo_huerto_real = d_huerto.get("codigo", "n/a")
                                    break
                        except Exception:
                            pass

                        # D. Verificamos si es merma o flor normal
                        item_seleccionado = st.session_state.flor_seleccionada_meson
                        es_merma_actual = item_seleccionado.get("es_merma", False)

                        if es_merma_actual:
                            familia_final = "Merma"
                            variedad_final = item_seleccionado["nombre"].replace("Merma: ", "")
                            codigo_articulo = str(item_seleccionado["codigo"])
                        else:
                            familia_final = st.session_state.get("familia_activa_meson", "Delphinium Guardian")
                            variedad_final = item_seleccionado["nombre"]
                            codigo_articulo = str(item_seleccionado["codigo"])
                                    
                        # E. Construcción de fecha combinando la fecha seleccionada en el componente y la hora actual chilena
                        hora_actual_chile = datetime.datetime.now(tz_cl).time()
                        ahora_envio = datetime.datetime.combine(fecha_ingress_meson := fecha_ingreso_meson, hora_actual_chile).replace(tzinfo=tz_cl)
                        
                        db.collection("cosecha_diaria").add({
                            "fecha_registro": ahora_envio,
                            "FechaFiltro": ahora_envio.strftime("%d/%m/%Y"),
                            "rut_cosechador": st.session_state.rut_cosechador.upper(),
                            "nombre_cosechador": nombre_cosechador_encontrado,
                            "origen_huerto": huerto_seleccionado_meson,
                            "codigo_origen_huerto": codigo_huerto_real,

                            "contratista_nombre": contratista_nombre,
                            "rut_contratista": rut_contratista_real,
                            "codigo_contratista": codigo_contratista_real,
                                    
                            "centro_costo": cc_nombre,
                            "codigo_centro_costo": codigo_cc_real,
                                    
                            "familia_flor": familia_final,
                            "variedad_flor": variedad_final,
                            "codigo_flor": codigo_articulo,
                                    
                            "cantidad_varas": int(st.session_state.cantidad_varas_meson),
                            "es_merma": bool(es_merma_actual)
                        })
                                    
                        st.success("✅ ¡Inyectado con éxito con formato estandarizado!")
                                    
                        # Reseteo de mesón para el siguiente flujo
                        st.session_state.flor_seleccionada_meson = None
                        st.session_state.cantidad_varas_meson = 30
                        st.session_state.rut_cosechador = ""
                        st.session_state.id_express_cosecha = ""
                        st.session_state.cc_activo_meson = ""
                        st.session_state.contratista_activo_meson = ""
                        st.session_state.rut_bloqueado_operacion = True
                        
                        # Limpiamos caché del historial para forzar actualización automática instantánea
                        if "lista_datos_dia_cache" in st.session_state:
                            del st.session_state["lista_datos_dia_cache"]

                        st.rerun()
                    except Exception as e: 
                        st.error(f"Error al inyectar datos: {e}")
                st.markdown('</div>', unsafe_allow_html=True)

# --- Historial Diario de Terreno ---
            st.write("")
            st.markdown(
                "<h3 style='color:#f8fafc;'>📋 Historial del Día (Servidor Google Cloud)</h3>",
                unsafe_allow_html=True,
            )

            @st.fragment
            def fragmento_historial_dia_terreno():
                import datetime
                import zoneinfo

                tz_local = zoneinfo.ZoneInfo("America/Santiago")
                fecha_hoy_chile = datetime.datetime.now(tz_local).date()

                # 1. Selector de fecha en Streamlit para el usuario
                filtro_fecha = st.date_input(
                    "Selecciona la fecha para el historial:", 
                    value=fecha_hoy_chile, 
                    key="filtro_fecha_historial_meson"
                )

                # 2. Convertimos la fecha seleccionada al formato 'dd/mm/yyyy' para que coincida con Firestore
                filtro_fecha_str = filtro_fecha.strftime("%d/%m/%Y")

                # 3. Consulta directa y en tiempo real a Firestore (sin caché estática) para reflejar los datos nuevos al instante
                lista_operario_real = []
                try:
                    docs_hoy = (
                        db.collection("cosecha_diaria")
                        .where("FechaFiltro", "==", filtro_fecha_str)
                        .stream()
                    )
                    lista_operario_real = [doc.to_dict() for doc in docs_hoy]
                except Exception as e_carga:
                    lista_operario_real = []

                if lista_operario_real:
                    try:
                        df_op = pd.DataFrame(lista_operario_real)

                        col_rut = (
                            "rut_cosechador"
                            if "rut_cosechador" in df_op.columns
                            else ("RutCosechador" if "RutCosechador" in df_op.columns else None)
                        )
                        col_nombre = (
                            "nombre_cosechador"
                            if "nombre_cosechador" in df_op.columns
                            else ("NombreCosechador" if "NombreCosechador" in df_op.columns else None)
                        )
                        col_huerto = "origen_huerto" if "origen_huerto" in df_op.columns else ("nave" if "nave" in df_op.columns else None)
                        col_familia = (
                            "familia_flor" if "familia_flor" in df_op.columns else None
                        )
                        col_variedad = (
                            "variedad_flor"
                            if "variedad_flor" in df_op.columns
                            else (
                                "DescripcionArticulo"
                                if "DescripcionArticulo" in df_op.columns
                                else None
                            )
                        )
                        col_varas = (
                            "cantidad_varas"
                            if "cantidad_varas" in df_op.columns
                            else ("CantidadVaras" if "CantidadVaras" in df_op.columns else None)
                        )
                        col_es_merma = "es_merma" if "es_merma" in df_op.columns else None
                        col_fecha_reg = "fecha_registro" if "fecha_registro" in df_op.columns else None

                        if col_rut and col_variedad and col_varas:
                            import __main__ as main

                            if hasattr(main, "formatear_rut_chileno_completo"):
                                df_op[col_rut] = df_op[col_rut].apply(
                                    lambda x: main.formatear_rut_chileno_completo(x)
                                    if pd.notnull(x)
                                    else x
                                )

                            df_op_render = df_op.copy()

                            columnas_a_mostrar = []
                            renombre_columnas = {}

                            if col_rut:
                                columnas_a_mostrar.append(col_rut)
                                renombre_columnas[col_rut] = "RUT Cosechador"
                            if col_nombre and col_nombre in df_op_render.columns:
                                columnas_a_mostrar.append(col_nombre)
                                renombre_columnas[col_nombre] = "Nombre Cosechador"
                            if col_huerto and col_huerto in df_op_render.columns:
                                columnas_a_mostrar.append(col_huerto)
                                renombre_columnas[col_huerto] = "Origen de Huerto"
                            if col_familia and col_familia in df_op_render.columns:
                                columnas_a_mostrar.append(col_familia)
                                renombre_columnas[col_familia] = "Familia"
                            if col_variedad:
                                columnas_a_mostrar.append(col_variedad)
                                renombre_columnas[col_variedad] = "Variedad / Detalle"
                            if col_varas:
                                columnas_a_mostrar.append(col_varas)
                                renombre_columnas[col_varas] = "Cantidad Varas"
                            if col_es_merma and col_es_merma in df_op_render.columns:
                                columnas_a_mostrar.append(col_es_merma)
                                renombre_columnas[col_es_merma] = "¿Es Merma?"

                            df_op_render = df_op_render[columnas_a_mostrar].rename(columns=renombre_columnas)

                            if col_fecha_reg in df_op.columns:
                                df_op_render = df_op_render.iloc[df_op[col_fecha_reg].argsort()[::-1]]

                            st.dataframe(df_op_render, use_container_width=True, hide_index=True)
                        else:
                            st.warning(
                                "⚠️ No se encontraron las columnas esperadas en los datos del servidor."
                            )

                    except Exception as e_tabla:
                        st.caption(f"⚠️ Nota de visualización: {e_tabla}")
                else:
                    st.info(f"📝 No hay registros cargados para la fecha {filtro_fecha_str} en este mesón.")

            fragmento_historial_dia_terreno()

# Pestaña C: Panel de Control y Auditoría (Actualizado)

with tab_auditoria:
    st.markdown("<h3 style='color:#38bdf8;'>🔍 Panel de Auditoría y Control de Registros</h3>", unsafe_allow_html=True)
    st.caption("Espacio exclusivo para administradores. Filtre, edite directamente en la tabla y guarde las correcciones en Google Firebase.")

    # 1. Recuperamos tus filtros visuales en columnas (Añadido selector para Origen de Huerto)
    col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns(5)
    
    with col_f1:
        filtro_fecha = st.date_input("📅 FILTRAR POR DÍA:", value=datetime.date.today(), key="filtro_fecha_auditoria")
        ignorar_fecha = st.checkbox("Ignorar fecha", value=False, key="chk_ignorar_fecha")
        
    with col_f2:
        lista_cc_cargada = []
        try:
            cc_docs = db.collection("config_centros_costo").stream()
            for doc in cc_docs:
                d = doc.to_dict()
                nombre_cc = d.get('nombre', '')
                codigo_cc = d.get('codigo', '')
                lista_cc_cargada.append(f"{nombre_cc} ({codigo_cc})")
        except:
            pass
        
        # 🔤 Ordenamos alfabéticamente y ponemos "Todos" al principio
        lista_cc_selector = ["Todos"] + sorted(lista_cc_cargada, key=lambda x: x.lower())
        if len(lista_cc_selector) == 1:
            lista_cc_selector = ["Todos", "Chipana (CC 02)"]
            
        cc_seleccionado_filtro = st.selectbox("🏭 CENTRO DE COSTO:", options=lista_cc_selector, key="select_cc_auditoria")
        ignorar_cc = st.checkbox("Ignorar Centro Costo", value=True, key="chk_ignorar_cc")
        
        # 📋 Tipo de Registro movido aquí abajo de Centro de Costo
        filtro_tipo_registro = st.selectbox("📋 TIPO DE REGISTRO:", options=["Todos", "Solo Producción", "Solo Merma"], key="select_tipo_registro_auditoria")
                
    with col_f3:
        lista_huerto_cargada = []
        try:
            huerto_docs = db.collection("config_origen_huerto").stream()
            for doc in huerto_docs:
                d = doc.to_dict()
                nombre_h = d.get('nombre', '')
                codigo_h = d.get('codigo', '')
                lista_huerto_cargada.append(f"{nombre_h} ({codigo_h})")
        except:
            pass
            
        # 🔤 Ordenamos alfabéticamente y ponemos "Todos" al principio
        lista_huerto_selector = ["Todos"] + sorted(lista_huerto_cargada, key=lambda x: x.lower())
        
        huerto_seleccionado_filtro = st.selectbox("📍 ORIGEN HUERTO:", options=lista_huerto_selector, key="select_huerto_auditoria")
        ignorar_huerto = st.checkbox("Ignorar Huerto", value=True, key="chk_ignorar_huerto")

        # ⚡ Nuevo filtro de ID Express ubicado a su lado / debajo
        filtro_id_express = st.text_input("⚡ ID EXPRESS:", placeholder="ID exacto...", key="input_id_express_audit")

    with col_f4:
        lista_cont_cargada = []
        try:
            cont_docs = db.collection("config_contratistas").stream()
            for doc in cont_docs:
                d = doc.to_dict()
                rut_c = d.get('rut', '')
                nombre_c = d.get('nombre', '')
                lista_cont_cargada.append(f"{rut_c} | {nombre_c}")
        except:
            pass
            
        # 🔤 Ordenamos alfabéticamente y ponemos "Todos" al principio
        lista_cont_selector = ["Todos"] + sorted(lista_cont_cargada, key=lambda x: x.lower())
            
        contratista_seleccionado_filtro = st.selectbox("🤝 CONTRATISTA B2B:", options=lista_cont_selector, key="select_cont_auditoria")
        ignorar_contratista = st.checkbox("Ignorar Contratista SpA", value=True, key="chk_ignorar_cont")
        
    with col_f5:
        filtro_rut_cosechador = st.text_input("🔍 RUT COSECHADOR:", placeholder="Ej: 123456789", key="input_rut_audit")
        filtro_rut = filtro_rut_cosechador

    # 2. El Botón de Ejecutar Búsqueda en la Nube
    if st.button("🚀 Ejecutar Búsqueda en la Nube", key="btn_ejecutar_busqueda_nube"):
        try:
            ref_cosecha = db.collection("cosecha_diaria")
            
            import zoneinfo
            tz_local = zoneinfo.ZoneInfo("America/Santiago")
            
            if not ignorar_fecha:
                inicio_dia = datetime.datetime.combine(filtro_fecha, datetime.time.min, tzinfo=tz_local)
                fin_dia = datetime.datetime.combine(filtro_fecha, datetime.time.max, tzinfo=tz_local)
                query = ref_cosecha.where("fecha_registro", ">=", inicio_dia).where("fecha_registro", "<=", fin_dia)
            else:
                query = ref_cosecha
                
            docs_cosecha = query.limit(500).stream()
                
            registros_lista = []
            for d in docs_cosecha:
                r_dict = d.to_dict()
                r_dict["id_documento_firebase"] = d.id
                registros_lista.append(r_dict)
                
            if registros_lista:
                df_auditoria = pd.DataFrame(registros_lista)
                
                # --- APLICACIÓN DE FILTROS EN MEMORIA ---
                if not ignorar_cc and cc_seleccionado_filtro != "Todos":
                    nombre_cc_buscado = cc_seleccionado_filtro.split("(")[0].strip().lower()
                    if "centro_costo" in df_auditoria.columns:
                        df_auditoria = df_auditoria[df_auditoria["centro_costo"].str.lower() == nombre_cc_buscado]
                
                if not ignorar_huerto and huerto_seleccionado_filtro != "Todos":
                    nombre_huerto_buscado = huerto_seleccionado_filtro.split("(")[0].strip().lower()
                    if "origen_huerto" in df_auditoria.columns:
                        df_auditoria = df_auditoria[df_auditoria["origen_huerto"].str.lower() == nombre_huerto_buscado]

                if not ignorar_contratista and contratista_seleccionado_filtro != "Todos":
                    rut_cont_buscado = contratista_seleccionado_filtro.split("|")[0].strip().lower()
                    if "rut_contratista" in df_auditoria.columns:
                        df_auditoria = df_auditoria[df_auditoria["rut_contratista"].str.lower() == rut_cont_buscado]
                        
                if filtro_rut_cosechador.strip():
                    rut_buscado_limpio = filtro_rut_cosechador.strip().replace(".", "").replace("-", "").lower()
                    if "rut_cosechador" in df_auditoria.columns:
                        df_auditoria = df_auditoria[df_auditoria["rut_cosechador"].str.replace("-", "").str.lower() == rut_buscado_limpio]
                
                # Filtro ID Express
                if filtro_id_express.strip():
                    id_buscado = filtro_id_express.strip().lower()
                    if "id_documento_firebase" in df_auditoria.columns:
                        df_auditoria = df_auditoria[df_auditoria["id_documento_firebase"].str.lower().str.contains(id_buscado)]
                
                if filtro_tipo_registro == "Solo Merma":
                    if "es_merma" in df_auditoria.columns:
                        df_auditoria = df_auditoria[df_auditoria["es_merma"] == True]
                    else:
                        df_auditoria = df_auditoria.iloc[0:0]
                elif filtro_tipo_registro == "Solo Producción":
                    if "es_merma" in df_auditoria.columns:
                        df_auditoria = df_auditoria[(df_auditoria["es_merma"] == False) | (df_auditoria["es_merma"].isna())]

                if not df_auditoria.empty:
                    if "fecha_registro" in df_auditoria.columns:
                        try:
                            df_auditoria["fecha"] = pd.to_datetime(df_auditoria["fecha_registro"]).dt.strftime('%d/%m/%Y')
                        except:
                            df_auditoria["fecha"] = df_auditoria["fecha_registro"]
                    else:
                        df_auditoria["fecha"] = ""

                    # Formateo visual con nombres compactos
                    df_auditoria["rut op."] = df_auditoria.get("rut_cosechador", "n/a").str.upper()
                    df_auditoria["nombre op."] = df_auditoria.get("nombre_cosechador", "n/a")
                    df_auditoria["huerto"] = df_auditoria.get("origen_huerto", "n/a")
                    df_auditoria["sku huerto"] = df_auditoria.get("codigo_origen_huerto", "n/a")
                    df_auditoria["cont."] = df_auditoria.get("contratista_nombre", "n/a")
                    df_auditoria["rut cont."] = df_auditoria.get("rut_contratista", "0-0")
                    df_auditoria["sku c."] = df_auditoria.get("codigo_contratista", "n/a")
                    df_auditoria["U.N."] = df_auditoria.get("centro_costo", "n/a")
                    df_auditoria["sku U.N."] = df_auditoria.get("codigo_centro_costo", "n/a")
                    df_auditoria["familia flor"] = df_auditoria.get("familia_flor", "n/a")
                    df_auditoria["variedad"] = df_auditoria.get("variedad_flor", "n/a")
                    df_auditoria["sku flor"] = df_auditoria.get("codigo_flor", "n/a")
                    df_auditoria["v."] = df_auditoria.get("cantidad_varas", 0).astype(int)
                    df_auditoria["es_merma_bool"] = df_auditoria.get("es_merma", False)

                    # 💾 GUARDAMOS EL RESULTADO EN MEMORIA DE SESIÓN
                    st.session_state["df_auditoria_activo"] = df_auditoria
                else:
                    st.session_state["df_auditoria_activo"] = None
                    st.info("📝 No se encontraron registros con los filtros aplicados.")
            else:
                st.session_state["df_auditoria_activo"] = None
                st.info("📝 No hay registros históricos en la base de datos.")
                
        except Exception as e_error_auditoria:
            st.error(f"❌ Error en consulta Firebase: {e_error_auditoria}")

# 3. 🔄 RENDERIZADO DEL EDITOR INTERACTIVO DE DATOS
    if st.session_state.get("df_auditoria_activo") is not None:
        df_ver = st.session_state["df_auditoria_activo"]
        
        if "v." not in df_ver.columns and "cantidad_varas" in df_ver.columns:
            df_ver["v."] = df_ver["cantidad_varas"].astype(int)
        if "huerto" not in df_ver.columns and "origen_huerto" in df_ver.columns:
            df_ver["huerto"] = df_ver["origen_huerto"]
        if "sku huerto" not in df_ver.columns and "codigo_origen_huerto" in df_ver.columns:
            df_ver["sku huerto"] = df_ver["codigo_origen_huerto"]
        st.session_state["df_auditoria_activo"] = df_ver

        columnas_vista = [
            "fecha", "rut op.", "nombre op.", "huerto", "sku huerto", 
            "cont.", "rut cont.", "sku c.", "U.N.", "sku U.N.", 
            "familia flor", "variedad", "sku flor", "v."
        ]
        
        cols_presentes = [c for c in columnas_vista if c in df_ver.columns]
        
        st.markdown("---")
        st.info("✏️ **Modo Edición Activado:** Haz doble clic sobre cualquier celda de la tabla inferior para modificar sus valores. Al terminar, presiona el botón de guardar para actualizar la base de datos en la nube.")
        
        num_filas = len(df_ver)
        altura_calculada = min(max((num_filas + 1) * 38, 100), 400)
        
        df_editado_vista = st.data_editor(
            df_ver[cols_presentes], 
            use_container_width=True, 
            hide_index=True,
            disabled=["fecha"], 
            height=altura_calculada,
            key="editor_tabla_auditoria"
        )
        
        col_metrica, col_guardar_cambios = st.columns([2, 1])
        with col_metrica:
            col_vara_key = "v." if "v." in df_editado_vista.columns else df_editado_vista.columns[-1]
            total_v = df_editado_vista[col_vara_key].sum()
            st.metric(label="Suma Total de Varas (Editadas)", value=f"{total_v} varas")
            
        with col_guardar_cambios:
            st.write("") 
            if st.button("💾 Guardar Cambios en Firebase", type="primary", use_container_width=True, key="btn_guardar_cambios_firebase"):
                try:
                    barra_progreso = st.progress(0, text="Sincronizando cambios con la nube...")
                    total_filas = len(df_editado_vista)
                    
                    mapa_codigos_huerto = {}
                    try:
                        for doc in db.collection("config_origen_huerto").stream():
                            d_h = doc.to_dict()
                            if "nombre" in d_h and "codigo" in d_h:
                                mapa_codigos_huerto[str(d_h["nombre"]).strip().lower()] = str(d_h["codigo"]).strip()
                    except:
                        pass

                    for idx, row in df_editado_vista.iterrows():
                        doc_id = df_ver.iloc[idx].get("id_documento_firebase")
                        
                        familia_actualizada = str(row.get("familia flor", "")).strip()
                        es_merma_calculada = familia_actualizada.lower() == "merma"
                        
                        huerto_actualizado = str(row.get("huerto", "")).strip()
                        sku_huerto_actualizado = str(row.get("sku huerto", "")).strip()
                        if huerto_actualizado.lower() in mapa_codigos_huerto:
                            sku_huerto_actualizado = mapa_codigos_huerto[huerto_actualizado.lower()]
                        
                        if doc_id:
                            datos_actualizados = {
                                "rut_cosechador": str(row.get("rut op.", "")).strip().upper(),
                                "nombre_cosechador": str(row.get("nombre op.", "")).strip().upper(),
                                "origen_huerto": huerto_actualizado,
                                "codigo_origen_huerto": sku_huerto_actualizado,
                                "contratista_nombre": str(row.get("cont.", "")).strip(),
                                "rut_contratista": str(row.get("rut cont.", "")).strip(),
                                "codigo_contratista": str(row.get("sku c.", "")).strip(),
                                "centro_costo": str(row.get("U.N.", "")).strip(),
                                "codigo_centro_costo": str(row.get("sku U.N.", "")).strip(),
                                "familia_flor": familia_actualizada,
                                "variedad_flor": str(row.get("variedad", "")).strip(),
                                "codigo_flor": str(row.get("sku flor", "")).strip(),
                                "cantidad_varas": int(row.get(col_vara_key, 0)),
                                "es_merma": es_merma_calculada 
                            }
                            db.collection("cosecha_diaria").document(doc_id).update(datos_actualizados)
                        
                        progreso = int(((idx + 1) / total_filas) * 100)
                        barra_progreso.progress(progreso, text=f"Actualizando registro {idx + 1} de {total_filas}...")
                    
                    df_ver.update(df_editado_vista)
                    df_ver["es_merma_bool"] = df_ver["familia flor"].astype(str).str.strip().str.lower() == "merma"
                    st.session_state["df_auditoria_activo"] = df_ver
                    
                    st.success("✅ ¡Todos los cambios fueron guardados y sincronizados correctamente en Firebase!")
                    st.rerun()
                    
                except Exception as e_guardar:
                    st.error(f"❌ Error al guardar los cambios en la nube: {e_guardar}")

# ==================================================================
# E. EXPORTACIÓN ERP Y EMISIÓN DE VALES FORMALES EN TICKET CHILE
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
                if st.session_state.get("df_auditoria_activo") is not None and not st.session_state["df_auditoria_activo"].empty:
                    df_source = st.session_state["df_auditoria_activo"].copy()
                
                    # Crear un nuevo DataFrame con las 13 columnas exactas requeridas por KAME
                    df_kame = pd.DataFrame()
                    num_filas = len(df_source)
                
                    # 1. Columnas fijas
                    df_kame["Tipo Movimiento"] = ["ENTRADA"] * num_filas
                    df_kame["Motivo Movimiento"] = ["Apertura"] * num_filas
                    df_kame["FolioAuto"] = ["S"] * num_filas
                    df_kame["Folio"] = ["11111"] * num_filas
                    df_kame["Bodega Entrada"] = ["PACKING 1"] * num_filas
                    df_kame["Bodega Salida"] = [""] * num_filas
                    df_kame["Ficha"] = ["77.517.427-7"] * num_filas
                    df_kame["PrecioUnitario"] = [1] * num_filas
                
                    # 2. Columnas dinámicas mapeadas desde la tabla de búsqueda/firebase
                    # Fecha: se obtiene de fecha o FechaFiltro
                    if "fecha" in df_source.columns:
                        df_kame["Fecha"] = df_source["fecha"].values
                    elif "FechaFiltro" in df_source.columns:
                        df_kame["Fecha"] = df_source["FechaFiltro"].values
                    else:
                        df_kame["Fecha"] = [filtro_fecha.strftime('%d/%m/%Y')] * num_filas
                
                    # Glosa: se obtiene de variedad_flor
                    df_kame["Glosa"] = df_source.get("variedad_flor", df_source.get("variedad", "")).values
                
                    # SKU: se obtiene de codigo_flor
                    df_kame["SKU"] = df_source.get("codigo_flor", df_source.get("sku flor", "")).values
                
                    # Nombre Unidad de Negocio: se obtiene de centro_costo
                    df_kame["Nombre Unidad de Negocio"] = df_source.get("centro_costo", df_source.get("U.N.", "")).values
                
                    # Cantidad: se obtiene de cantidad_varas
                    col_vara_key = "cantidad_varas" if "cantidad_varas" in df_source.columns else ("v." if "v." in df_source.columns else df_source.columns[-1])
                    df_kame["Cantidad"] = df_source.get(col_vara_key, 0).astype(int).values

                    # Orden estricto de las 13 columnas
                    columnas_kame_13 = [
                        "Tipo Movimiento",
                        "Motivo Movimiento",
                        "FolioAuto",
                        "Folio",
                        "Bodega Entrada",
                        "Bodega Salida",
                        "Ficha",
                        "Fecha",
                        "Glosa",
                        "SKU",
                        "Nombre Unidad de Negocio",
                        "Cantidad",
                        "PrecioUnitario"
                    ]
                
                    df_kame = df_kame[columnas_kame_13]

                    csv_kame = df_kame.to_csv(index=False, sep=";", encoding="utf-8-sig")
            
                    st.success("Planilla generada con éxito.")
                    st.download_button(
                        label="📥 DESCARGAR PLANILLA KAME", 
                        data=csv_kame, 
                        file_name=f"KAME_Cosecha_{filtro_fecha}.csv", 
                        mime="text/csv", 
                        use_container_width=True
                    )
                else:
                    st.warning("⚠️ No hay registros en memoria. Ejecuta primero la 'Búsqueda en la Nube' arriba.")
            except Exception as e: 
                st.error(f"Error al procesar KAME: {e}")

    with col_admin_vale:
        st.markdown("### Opciones de Impresión")
        
        if "html_vale_actual" not in st.session_state: 
            st.session_state.html_vale_actual = ""
        
        if st.button("🔄 Cargar / Actualizar Datos del Vale", key="btn_vale_process", use_container_width=True):
            try:
                if st.session_state.get("df_auditoria_activo") is not None and not st.session_state["df_auditoria_activo"].empty:
                    df_fuente = st.session_state["df_auditoria_activo"]
                
                    df_fuente["es_merma_eval"] = df_fuente["familia flor"].astype(str).str.strip().str.lower() == "merma"
                    
                    df_flores_prod = df_fuente[df_fuente["es_merma_eval"] == False]
                    df_flores_mermas = df_fuente[df_fuente["es_merma_eval"] == True]

                    df_vale_prod = df_flores_prod.groupby(["rut op.", "nombre op.", "huerto", "sku huerto", "familia flor", "variedad"], as_index=False)["v."].sum() if not df_flores_prod.empty else pd.DataFrame(columns=["rut op.", "nombre op.", "huerto", "sku huerto", "familia flor", "variedad", "v."])
                    df_vale_merma = df_flores_mermas.groupby(["rut op.", "nombre op.", "huerto", "sku huerto", "familia flor", "variedad"], as_index=False)["v."].sum() if not df_flores_mermas.empty else pd.DataFrame(columns=["rut op.", "nombre op.", "huerto", "sku huerto", "familia flor", "variedad", "v."])
                
                    fechas_unicas = df_fuente["fecha"].unique() if "fecha" in df_fuente.columns else []
                    str_fecha = str(fechas_unicas[0]) if len(fechas_unicas) == 1 else "Todas las fechas"
                    
                    ccs_unicos = df_fuente["U.N."].unique() if "U.N." in df_fuente.columns else []
                    str_origen = ccs_unicos[0] if len(ccs_unicos) == 1 else "Todos los orígenes"

                    # Recuperar el Origen del Huerto para mostrarlo claramente en el voucher impreso
                    huertos_unicos = df_fuente["huerto"].unique() if "huerto" in df_fuente.columns else []
                    str_huerto = huertos_unicos[0] if len(huertos_unicos) == 1 else "Varios huertos"

                    b2b_unicos = df_fuente["cont."].unique() if "cont." in df_fuente.columns else []
                    str_empresa = b2b_unicos[0] if len(b2b_unicos) == 1 else "Todas las empresas"
                
                    ruts_unicos = df_fuente["rut op."].unique() if "rut op." in df_fuente.columns else []
                    str_cosechador = ruts_unicos[0] if len(ruts_unicos) == 1 else f"Varios operarios ({len(ruts_unicos)})"

                    nombre_unicos = df_fuente["nombre op."].unique() if "nombre op." in df_fuente.columns else []
                    str_cosecheros = nombre_unicos[0] if len(nombre_unicos) == 1 else f"Varios operarios ({len(nombre_unicos)})"
                
                    filas_html = ""
                    
                    if not df_vale_prod.empty:
                        filas_html += "<tr><td colspan='2' style='padding:6px 4px 2px 4px; font-weight:bold; background-color:#f3f4f6; color:#111827;'>🌿 PRODUCCIÓN DE FLORES</td></tr>"
                        for _, r in df_vale_prod.iterrows():
                            filas_html += f"<tr><td style='padding:4px;'>&nbsp;&nbsp;• {r['familia flor']} - {r['variedad']}</td><td style='text-align:right; font-weight:bold;'>{r['v.']}</td></tr>"

                    if not df_vale_merma.empty:
                        filas_html += "<tr><td colspan='2' style='padding:8px 4px 2px 4px; font-weight:bold; background-color:#fee2e2; color:#991b1b;'>🗑️ MERMAS</td></tr>"
                        for _, r in df_vale_merma.iterrows():
                            filas_html += f"<tr><td style='padding:4px;'>&nbsp;&nbsp;• {r['familia flor']} - {r['variedad']}</td><td style='text-align:right; font-weight:bold; color:#991b1b;'>{r['v.']}</td></tr>"

                    total_varas_prod = int(df_vale_prod["v."].sum()) if not df_vale_prod.empty else 0
                    total_varas_merma = int(df_vale_merma["v."].sum()) if not df_vale_merma.empty else 0
                
                    st.session_state.html_vale_actual = f"""
                    <style>
                        @media print {{
                            @page {{
                                size: portrait;
                                margin: 0;
                            }}
                            html, body {{
                                background-color: #ffffff !important;
                                background: #ffffff !important;
                                width: 100% !important;
                                height: 100% !important;
                                margin: 0 !important;
                                padding: 0 !important;
                                overflow: hidden !important;
                            }}
                            body * {{
                                visibility: hidden !important;
                            }}
                            #printable-wrapper, #printable-wrapper * {{
                                visibility: visible !important;
                            }}
                            #printable-wrapper {{
                                position: fixed !important;
                                left: 0px !important;
                                top: 0px !important;
                                width: 100% !important;
                                height: auto !important;
                                margin: 0 !important;
                                padding: 0 !important;
                                background-color: #ffffff !important;
                                z-index: 999999 !important;
                            }}
                            #printable-voucher {{
                                margin: 10px !important;
                                page-break-before: avoid !important;
                                page-break-after: avoid !important;
                                page-break-inside: avoid !important;
                                break-before: avoid !important;
                                break-after: avoid !important;
                                break-inside: avoid !important;
                            }}
                        }}
                    </style>
                    <div id='printable-wrapper'>
                        <div id='printable-voucher' style='background-color:white; color:black; padding:15px; font-family:monospace; border:1px solid #ccc; max-width: 380px;'>
                            <h3 style='text-align:center; margin:0; color:black;'>FLORES ANTIVERO</h3>
                            <p style='text-align:center; margin:5px 0; font-size:12px; color:black;'>COMPROBANTE DE COSECHA Y AUDITORÍA</p>
                            <hr style='border-top:1px dashed black;'>
                            <p style='margin:3px 0; color:black;'><b>Fecha:</b> {str_fecha}</p>
                            <p style='margin:3px 0; color:black;'><b>Centro Costo:</b> {str_origen}</p>
                            <p style='margin:3px 0; color:black;'><b>Origen Huerto:</b> {str_huerto}</p>
                            <p style='margin:3px 0; color:black;'><b>Empresa:</b> {str_empresa}</p>
                            <p style='margin:3px 0; color:black;'><b>Cosechador:</b> {str_cosechador}</p>
                            <p style='margin:3px 0; color:black;'><b>Nombre Cosechador:</b> {str_cosecheros}</p>
                            <hr style='border-top:1px dashed black;'>
                            <table style='width:100%; border-collapse:collapse; color:black;'>
                                <thead><tr><th style='text-align:left;'>Variedad</th><th style='text-align:right;'>Varas</th></tr></thead>
                                <tbody>{filas_html}</tbody>
                            </table>
                            <hr style='border-top:1px dashed black;'>
                            <p style='margin:3px 0; display:flex; justify-content:space-between; color:black;'><span>Total Flores:</span> <b>{total_varas_prod} Varas</b></p>
                            <p style='margin:3px 0; display:flex; justify-content:space-between; color:black;'><span>Total Mermas:</span> <b>{total_varas_merma} Varas</b></p>
                            <hr style='border-top:1px dashed black;'>
                            <h3 style='display:flex; justify-content:space-between; margin:0; color:black;'><span>TOTAL GENERAL:</span> <span>{total_varas_prod + total_varas_merma} Varas</span></h3>
                        </div>
                    </div>"""
                    st.success("✅ Datos cargados correctamente para imprimir.")
                else:
                    st.warning("⚠️ No existen registros en la tabla. Ejecuta la búsqueda primero.")
                    st.session_state.html_vale_actual = ""
            except Exception as e: 
                st.error(f"Error: {e}")

        if st.button("🚀 IMPRESIÓN DIRECTA (ZEBRA ZM400)", key="btn_impresion_directa_zebra", use_container_width=True, type="primary"):
            st.info("⚡ Enviando directamente a la impresora ZPL (Zebra)...")

        if st.session_state.html_vale_actual != "":
            components.html("""
            <div style="font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New', monospace; width: 100%; margin-top: 0px;">
                <button onclick="window.parent.print();" style="
                    background-color: rgb(14, 17, 23); 
                    color: rgb(250, 250, 250); 
                    border: 1px solid rgb(48, 54, 61); 
                    padding: 0.5rem 1rem; 
                    font-size: 14px; 
                    font-weight: 400; 
                    border-radius: 0.5rem; 
                    cursor: pointer; 
                    width: 100%;
                    text-align: center;
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    gap: 8px;
                    box-sizing: border-box;
                    font-family: inherit;
                " onmouseover="this.style.borderColor='rgb(125, 211, 252)'; this.style.color='rgb(125, 211, 252)';" onmouseout="this.style.borderColor='rgb(48, 54, 61)'; this.style.color='rgb(250, 250, 250)';"">
                    🖨️ Salida de Impresión Nativa (Windows)
                </button>
            </div>
            """, height=45)
        else:
            st.button("🖨️ Salida de Impresión Nativa (Windows)", key="btn_impresion_windows_disabled", use_container_width=True, disabled=True)

        if st.session_state.html_vale_actual: 
            st.markdown("---")
            st.markdown("##### Vista Previa del Comprobante:")
            st.html(st.session_state.html_vale_actual)

    # ==================================================================
    # F. PANEL DE CONFIGURACIÓN DEL CATÁLOGO DIRECTO EN LA NUBE
    # ==================================================================
    st.write("---")
    st.markdown("<h2 style='color:#38bdf8;'>⚙️ Panel de Configuración del Catálogo</h2>", unsafe_allow_html=True)
    
    # Se añade la pestaña "📍 Origen de Huerto" a la lista de solapas
    s_cc, s_b2b, s_flores, s_mermas, s_huerto = st.tabs([
        "🏬 Centros de Costo", 
        "🤝 Contratistas B2B", 
        "💐 Flores y Variedades", 
        "🗑️ Mermas",
        "📍 Origen de Huerto"
    ])
    
    with s_cc:
        with st.form("form_add_cc", clear_on_submit=True):
            nuevo_cc_nombre = st.text_input("Nombre del nuevo Centro de Costo:", placeholder="Ej: Fundo El Quillay", key="in_cc_nom").strip()
            nuevo_cc_codigo = st.text_input("Código del Centro de Costo:", placeholder="Ej: CC 03", key="in_cc_cod").strip()
                
            if st.form_submit_button("Registrar Centro de Costo", use_container_width=True):
                if nuevo_cc_nombre and nuevo_cc_codigo:
                    try:
                        db.collection("config_centros_costo").add({
                            "nombre": nuevo_cc_nombre, 
                            "codigo": nuevo_cc_codigo,
                            "fecha_creacion": datetime.datetime.now()
                        })
                        st.success(f"✅ Centro de Costo '{nuevo_cc_nombre} ({nuevo_cc_codigo})' inyectado.")
                        st.rerun()
                    except Exception as e: st.error(f"Error: {e}")
                else: st.warning("Ambos campos (Nombre y Código) son obligatorios.")
                    
    with s_b2b:
        with st.form("form_add_contratista", clear_on_submit=True):
            new_rut_b2b = st.text_input("RUT Contratista (Con puntos y guión):", placeholder="Ej: 76.888.999-K", key="in_b2b_rut").strip()
            new_nom_b2b = st.text_input("Razón Social / Nombre Contratista:", placeholder="Ej: Cosechas del Valle SpA", key="in_b2b_nom").strip()
            new_cod_b2b = st.text_input("Código Interno / Corto del Contratista:", placeholder="Ej: htr54", key="in_b2b_cod").strip()
                
            if st.form_submit_button("Registrar Contratista B2B", use_container_width=True):
                if new_rut_b2b and new_nom_b2b and new_cod_b2b:
                    try:
                        cadena_kame = f"{new_rut_b2b} | {new_nom_b2b}"
                        db.collection("config_contratistas").add({
                            "rut": new_rut_b2b,
                            "nombre": new_nom_b2b,
                            "codigo": new_cod_b2b,
                            "formato_kame": cadena_kame, 
                            "fecha_creacion": datetime.datetime.now()
                        })
                        st.success(f"✅ Contratista '{cadena_kame}' [Código: {new_cod_b2b}] configurado.")
                        st.rerun()
                    except Exception as e: st.error(f"Error: {e}")
                else: st.warning("Todos los campos (RUT, Nombre y Código) son obligatorios.")

    with s_flores:
        st.markdown("### ➕ Registrar Nueva Variedad de Flor")
        familias_existentes = sorted(list(diccionario_flores_dinamico.keys())) if 'diccionario_flores_dinamico' in globals() and diccionario_flores_dinamico else ["Delphinium", "Peonía", "Ranunculus Romance", "Ranunculus Standard"]
        opciones_familia = familias_existentes + ["➕ Crear Nueva Familia..."]
        familia_seleccionada = st.selectbox(
            "Seleccione Familia Agrícola:",
            opciones_familia,
            key="selectbox_auditoria_familia"
        )
        if familia_seleccionada == "➕ Crear Nueva Familia...":
            nueva_familia_input = st.text_input(
                "📝 Escriba el nombre de la nueva Familia:",
                placeholder="Ej: ANÉMONAS, TULIPANES...",
                key="input_nueva_familia_auditoria"
            ).strip()
            familia_final = nueva_familia_input
        else:
            familia_final = familia_seleccionada
        nuevo_codigo = st.text_input("Código de Artículo (Kame ERP):", placeholder="Ej: PB-ROSA-01", key="in_flor_cod").strip()
        nuevo_nombre = st.text_input("Nombre de la Variedad:", placeholder="Ej: PB ROSA HOT PARIS", key="in_flor_nom").strip()
        nuevo_color = st.color_picker("Color de Identificación Visual:", "#FA819F", key="picker_color_flor")
        if st.button("💾 Guardar Nueva Variedad", type="primary", use_container_width=True, key="btn_guardar_nueva_flor"):
            if not familia_final:
                st.error("❌ Error: Debes seleccionar o ingresar una Familia Agrícola.")
            elif not nuevo_codigo or not nuevo_nombre:
                st.error("❌ Error: El Código y Nombre de variedad son obligatorios.")
            else:
                try:
                    doc_data = {
                        "codigo": nuevo_codigo,
                        "color": nuevo_color,
                        "familia": familia_final,
                        "nombre": nuevo_nombre
                    }
                    db.collection("config_flores").add(doc_data)
                    st.success(f"✅ ¡Variedad '{nuevo_nombre}' guardada con éxito bajo la familia '{familia_final}'!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al guardar en Firestore: {e}")

    with s_mermas:
        with st.form("form_add_merma", clear_on_submit=True):
            st.markdown("### ➕ Registrar Nueva Merma")
            nueva_merma_codigo = st.text_input("Código de Merma:", placeholder="Ej: MH01", key="in_merma_cod").strip()
            nueva_merma_nombre = st.text_input("Descripción de KAME:", placeholder="Ej: MERMA HUERTO ROSA", key="in_merma_nom").strip()
            nueva_merma_familia = st.text_input("Familia:", placeholder="Ej: ROSA", key="in_merma_fam").strip()
            nueva_merma_variedad = st.text_input("Variedad:", placeholder="Ej: Red Globe / Royal Gala", key="in_merma_var").strip()
                
            if st.form_submit_button("Registrar Merma", use_container_width=True):
                if nueva_merma_codigo and nueva_merma_nombre:
                    try:
                        db.collection("merma").add({
                            "codigo": nueva_merma_codigo,
                            "descripcion_kame": nueva_merma_nombre,
                            "familia": nueva_merma_familia,
                            "variedad": nueva_merma_variedad,
                            "fecha_creacion": datetime.datetime.now()
                        })
                        st.success(f"✅ Merma '{nueva_merma_nombre}' (Variedad: {nueva_merma_variedad if nueva_merma_variedad else 'N/A'}) registrada correctamente en la colección 'merma'.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al guardar la merma en Firebase: {e}")
                else:
                    st.warning("⚠️ Los campos Código y Descripción son obligatorios.")

    with s_huerto:
        with st.form("form_add_origen_huerto", clear_on_submit=True):
            st.markdown("### ➕ Registrar Origen de Huerto")
            nombre_huerto = st.text_input("Nombre del Huerto / Sector:", placeholder="Ej: Nave o Cuartel", key="in_huerto_nom").strip()
            codigo_huerto = st.text_input("Código de Origen:", placeholder="Ej: N01", key="in_huerto_cod").strip()
                
            if st.form_submit_button("Registrar Origen de Huerto", use_container_width=True):
                if nombre_huerto and codigo_huerto:
                    try:
                        db.collection("config_origen_huerto").add({
                            "nombre": nombre_huerto,
                            "codigo": codigo_huerto.upper(),
                            "fecha_creacion": datetime.datetime.now()
                        })
                        st.success(f"✅ Origen de huerto '{nombre_huerto}' (Código: {codigo_huerto.upper()}) registrado correctamente.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al guardar el origen de huerto en Firebase: {e}")
                else:
                    st.warning("⚠️ Ambos campos (Nombre y Código) son obligatorios.")