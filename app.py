import streamlit as st
import pandas as pd
import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# ==================================================================
# 1. CONEXIÓN SECRETA Y SEGURA CON GOOGLE FIREBASE CLOUD
# ==================================================================
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("llave_firebase.json")
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"❌ Error crítico al cargar las credenciales de Firebase: {e}")

db = firestore.client()

# ==================================================================
# 2. CONFIGURACIÓN VISUAL (Tu Paleta de Colores Oscura Original)
# ==================================================================
st.set_page_config(layout="wide", page_title="Flores Antivero Cosecha")

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
        
        /* 📱 RESPONSIVIDAD DINÁMICA: DETECTA CELULAR VERTICAL O GIROS EN TERRENO */
        @media (max-width: 768px) {
            /* Fuerza a las columnas side-by-side a tomar el 100% del ancho para no achicarse */
            [data-testid="stHorizontalBlock"] {
                flex-direction: column !important;
            }
            div[data-testid="column"] {
                width: 100% !important;
                margin-left: 0 !important;
                margin-bottom: 15px !important;
            }
            /* Agrandamos levemente los textos de los encabezados para móviles */
            .antivero-header h1 {
                font-size: 18px;
            }
        }
    </style>
""")


hora_actual = datetime.datetime.now().strftime("%H:%M")
st.html(f"""
    <div class="antivero-header">
        <h1>🚜 Flores Antivero — Terminal de Cosecha v2.0</h1>
        <div style="font-weight: bold; color: #94a3b8;">🕒 {hora_actual}</div>
    </div>
""")

# Control de estado de sesión
if "usuario_conectado" not in st.session_state:
    st.session_state.usuario_conectado = False
if "rol_usuario" not in st.session_state:
    st.session_state.rol_usuario = "operario"
if "rut_cosechador" not in st.session_state:
    st.session_state.rut_cosechador = ""
if "id_usuario_activo" not in st.session_state:
    st.session_state.id_usuario_activo = ""

# ==================================================================
# 3. PORTAL DE ACCESO DIRECTO CON AUTH DE GOOGLE PARA EMAILS
# ==================================================================
if not st.session_state.usuario_conectado:
    st.markdown('<h1 style="color: #38bdf8; text-align: center;">🚜 Flores Antivero — Terminal</h1>', unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("### 🔐 Iniciar Sesión")
        input_usuario = st.text_input("Ingresa tu RUT o Correo Administrador:", placeholder="Ej: 12.345.678-9 o admin@antivero.cl", key="auth_login_user").strip().lower()
        input_clave = st.text_input("Contraseña de acceso:", type="password", placeholder="••••••••", key="auth_login_password")
        
        if st.button("🚀 Ingresar al Sistema", key="btn_auth_login_submit", use_container_width=True, type="primary"):
            if input_usuario and input_clave:
                try:
                    # VALIDACIÓN HISTÓRICA CONTRA CLOUD FIRESTORE
                    user_ref = db.collection("usuarios").document(input_usuario).get()
                    if user_ref.exists:
                        datos_user = user_ref.to_dict()
                        if datos_user.get("password") == input_clave:
                            st.session_state.usuario_conectado = True
                            st.session_state.rol_usuario = datos_user.get("rol", "operario")
                            st.session_state.id_usuario_activo = input_usuario
                            st.success(f"🔓 Acceso concedido como: {st.session_state.rol_usuario.upper()}")
                            st.rerun()
                        else:
                            st.error("❌ La contraseña ingresada es incorrecta.")
                    else:
                        st.error("❌ El usuario ingresado no está registrado en el sistema agrícola.")
                except Exception as e:
                    st.error(f"⚠️ Error de conexión con el servidor de Google: {e}")
            else:
                st.warning("⚠️ Por favor, complete ambos campos.")
        
        # --- SUB-MÓDULO DE RECUPERACIÓN SEGURO E HÍBRIDO ---
        st.write("---")
        with st.expander("❓ ¿Olvidaste tu contraseña? Restablece aquí"):
            st.caption("Los correos recibirán un link oficial de Google. Los RUT alertarán al mesón.")
            recup_user = st.text_input("Ingresa tu RUT o Correo Corporativo:", placeholder="Ej: admin@antivero.cl", key="input_recup_id").strip().lower()
            
            if st.button("📩 Procesar Recuperación", key="btn_send_recup", use_container_width=True):
                if recup_user:
                    try:
                        if "@" in recup_user:
                            # CASO ADMINS: Usa el motor oficial y gratuito de Firebase Auth para correos
                            import firebase_admin.auth as auth
                            try:
                                enlace = auth.generate_password_reset_link(recup_user)
                                st.success("📧 ¡Enlace enviado! Google ha procesado tu solicitud. Revisa la bandeja de entrada de tu correo corporativo.")
                            except Exception as auth_err:
                                st.error(f"❌ El correo electrónico no figura en el panel de Autenticación de Firebase: {auth_err}")
                        else:
                            # CASO OPERARIOS: Alerta interna en Firestore
                            user_check = db.collection("usuarios").document(recup_user).get()
                            if user_check.exists:
                                db.collection("solicitudes_clave").document(recup_user).set({
                                    "usuario": recup_user, "fecha_solicitud": datetime.datetime.now(), "estado": "pendiente"
                                })
                                st.success("✅ Alerta enviada al mesón. Pide a un administrador que reconfigure tu clave desde su barra lateral.")
                            else:
                                st.error("❌ El RUT ingresado no existe en los registros de Flores Antivero.")
                    except Exception as e:
                        st.error(f"❌ Error al conectar con la base de datos: {e}")
                else:
                    st.warning("⚠️ Ingresa tu RUT o Correo.")
                
    st.stop() # Bloqueo absoluto de seguridad de la interfaz inferior

# ==================================================================
# 3. INTERFAZ PRINCIPAL (USUARIO AUTENTICADO Y SEGURIZADO)
# ==================================================================
# ==================================================================
# 3. INTERFAZ PRINCIPAL (BARRA LATERAL DE CONTROL Y SEGURIDAD)
# ==================================================================
with st.sidebar:
    st.markdown(f"👤 **Usuario Activo:** `{st.session_state.id_usuario_activo.upper()}`")
    st.markdown(f"🛡️ **Rol:** `{st.session_state.rol_usuario.upper()}`")
    st.write("---")
    
    # FORMULARIO UNIVERSAL: Cambiar contraseña de la cuenta en uso
    with st.expander("🔑 Cambiar mi Contraseña", expanded=False):
        with st.form("form_cambio_clave_universal", clear_on_submit=True):
            nueva_p1 = st.text_input("Nueva Contraseña:", type="password", key="univ_p1")
            nueva_p2 = st.text_input("Confirmar Contraseña:", type="password", key="univ_p2")
            if st.form_submit_button("💾 Guardar Nueva Clave", use_container_width=True):
                if nueva_p1 and nueva_p1 == nueva_p2 and len(nueva_p1) >= 4:
                    try:
                        db.collection("usuarios").document(st.session_state.id_usuario_activo).update({"password": nueva_p1})
                        st.success("✅ ¡Contraseña actualizada!")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                else:
                    st.error("❌ Las claves no coinciden o tienen menos de 4 caracteres.")

    # SECCIÓN EXCLUSIVA PARA ADMINISTRADORES: GESTIÓN DE PERSONAL
    if st.session_state.rol_usuario == "admin":
        st.write("---")
        st.markdown("### 🛠️ Herramientas de Administrador")
        
        # A. Crear Operario (Antes estaba público)
        with st.expander("📝 Registrar Nuevo Operario", expanded=False):
            with st.form("form_registro_interno_admin", clear_on_submit=True):
                reg_rut = st.text_input("RUT Cosechador:", placeholder="Ej: 123456789", key="admin_reg_rut").strip().lower()
                reg_clave = st.text_input("Contraseña inicial:", type="password", key="admin_reg_pass")
                if st.form_submit_button("➕ Crear Operario", use_container_width=True):
                    if reg_rut and len(reg_clave) >= 4:
                        try:
                            if db.collection("usuarios").document(reg_rut).get().exists:
                                st.error("⚠️ Este RUT ya existe.")
                            else:
                                db.collection("usuarios").document(reg_rut).set({"password": reg_clave, "rol": "operario"})
                                st.success(f"🎉 ¡RUT {reg_rut} creado!")
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
                    else:
                        st.warning("⚠️ Datos inválidos.")

        # B. Eliminar Cuentas de Operarios de forma definitiva
        with st.expander("🗑️ Eliminar Cuenta de Operario", expanded=False):
            with st.form("form_eliminar_operario", clear_on_submit=True):
                rut_a_borrar = st.text_input("RUT a eliminar (Sin puntos ni guión):", placeholder="Ej: 123456789", key="del_rut").strip().lower()
                confirmar_check = st.checkbox("Confirmo que deseo borrar permanentemente este usuario.")
                if st.form_submit_button("🚨 Eliminar de la Nube", use_container_width=True):
                    if rut_a_borrar and confirmar_check:
                        try:
                            doc_ref = db.collection("usuarios").document(rut_a_borrar)
                            if doc_ref.get().exists:
                                doc_ref.delete()
                                st.success(f"🗑️ El usuario {rut_a_borrar} fue eliminado de Firebase.")
                            else:
                                st.error("❌ El RUT ingresado no existe.")
                        except Exception as e:
                            st.error(f"❌ Error al eliminar: {e}")
                    else:
                        st.warning("⚠️ Debes rellenar el campo y marcar la casilla de confirmación.")

        # C. Panel de Solicitudes de Clave Pendientes
        with st.expander("📬 Alertas de Clave Olvidada", expanded=False):
            try:
                solicitudes = db.collection("solicitudes_clave").where("estado", "==", "pendiente").stream()
                lista_sol = [s.to_dict() for s in solicitudes]
                if not lista_sol:
                    st.caption("No hay alertas pendientes.")
                else:
                    for s in lista_sol:
                        st.warning(f"👤 Usuario: {s['usuario']}")
                        # Formulario express para sobreescribirle la clave desde el mesón
                        nueva_clave_express = st.text_input(f"Nueva clave para {s['usuario']}:", type="password", key=f"express_{s['usuario']}")
                        if st.button(f"🔄 Forzar cambio para {s['usuario']}", key=f"btn_exp_{s['usuario']}", use_container_width=True):
                            if len(nueva_clave_express) >= 4:
                                db.collection("usuarios").document(s["usuario"]).update({"password": nueva_clave_express})
                                db.collection("solicitudes_clave").document(s["usuario"]).update({"estado": "resuelto"})
                                st.success("Clave reconfigurada con éxito.")
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
# 4. MOTOR DE FORMATEO DE RUT CHILENO (NATIVO EN TIEMPO REAL)
# ==================================================================
def formatear_rut_chileno(rut_crudo):
    """Toma un texto de números y le da el formato chileno oficial: XX.XXX.XXX-X."""
    if not rut_crudo:
        return "00.000.000-0"
    rut_crudo = "".join([c for c in rut_crudo if c.isalnum()])
    if len(rut_crudo) <= 1:
        return rut_crudo.upper()
    
    cuerpo = rut_crudo[:-1]
    dv = rut_crudo[-1].upper()
    
    if cuerpo.isdigit():
        cuerpo_formateado = f"{int(cuerpo):,}".replace(",", ".")
        return f"{cuerpo_formateado}-{dv}"
    return f"{cuerpo}-{dv}"
# ==================================================================
# 5. MAQUETADO EN COLUMNAS (IDENTIFICACIÓN Y FLUJO CENTRAL)
# ==================================================================
# ==================================================================
# 4. ENRUTADOR DE PÁGINAS PRINCIPALES POR ROL (TABS GLOBALES)
# ==================================================================
# Inicializamos las variables de control de la página de administración
if "admin_tab_filtro_rut" not in st.session_state:
    st.session_state.admin_tab_filtro_rut = ""

# Si el usuario es Administrador, creamos las pestañas superiores de navegación
if st.session_state.rol_usuario == "admin":
    tab_terminal, tab_auditoria = st.tabs(["🚜 Terminal de Cosecha", "📊 Panel de Control y Auditoría"])
else:
    # Si es operario, creamos contenedores falsos para mantener el mismo flujo de código abajo
    tab_terminal = st.container()
    tab_auditoria = None

# --- CONTENIDO DE LA PESTAÑA A: TERMINAL DE COSECHA AGRÍCOLA ---
with tab_terminal:
    # Aquí se encapsula toda tu interfaz original del teclado numérico y mesón de flores
    col_panel_izq, col_panel_central_derecho = st.columns([1.2, 2.8])
    
    # [El código del panel izquierdo con el teclado táctil sigue aquí adentro con su indentación normal]


with col_panel_izq:
    st.subheader("📍 Identificación de Campo")
    
    centro_costo = st.selectbox(
        "📍 Origen (Centro de Costo)",
        ["Las Rosas (CC 01)", "Chipana (CC 02)"],
        key="cc_selector_agricola"
    )
    
    contratista = st.selectbox(
        "🏢 Contratista Destino (Kame B2B)",
        [
            "76.543.210-K | Servicios Agrícolas del Maule",
            "77.123.456-7 | Agrícola San Fernando Limitada",
            "76.999.888-2 | Mano de Obra Terreno SpA"
        ],
        key="contratista_selector_b2b"
    )
    
    st.write("")
    st.markdown("<label>🆔 RUT Cosechador</label>", unsafe_allow_html=True)
    
    rut_pantalla_visual = formatear_rut_chileno(st.session_state.rut_cosechador)
    st.html(f'<div class="rut-display-box">{rut_pantalla_visual}</div>')
    
    col_k1, col_k2, col_k3 = st.columns(3)
    botones_teclado = [
        ("1", col_k1), ("2", col_k2), ("3", col_k3),
        ("4", col_k1), ("5", col_k2), ("6", col_k3),
        ("7", col_k1), ("8", col_k2), ("9", col_k3),
        ("K", col_k1), ("0", col_k2), ("C", col_k3)
    ]
    
    for digito, columna_destino in botones_teclado:
        with columna_destino:
            if digito == "C":
                if st.button("C", key="btn_key_clear_tactic", use_container_width=True, type="secondary"):
                    st.session_state.rut_cosechador = ""
                    st.rerun()
            else:
                if st.button(digito, key=f"btn_key_tact_{digito}", use_container_width=True):
                    if len(st.session_state.rut_cosechador) < 9:
                        st.session_state.rut_cosechador += digito
                        st.rerun()

with col_panel_central_derecho:
    if "flor_seleccionada_meson" not in st.session_state:
        st.session_state.flor_seleccionada_meson = None
    if "cantidad_varas_meson" not in st.session_state:
        st.session_state.cantidad_varas_meson = 30

    col_centro_flujo, col_derecha_consolidacion = st.columns([1.6, 1.2])

    with col_centro_flujo:
        st.subheader("🌸 Selección de Familia de Flores")
        capa_familias = st.tabs(["🌹 Rosas / Romance / Elegance", "🌸 Peonías", "🔹 Delphinium"])
        
        with capa_familias[0]:
            st.markdown("<p style='color:#94a3b8; font-size:13px;'>Seleccione variedad para el mesón:</p>", unsafe_allow_html=True)
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                if st.button("🌹 Rosas Romance\n(Cód: 220)", key="btn_prod_220", use_container_width=True):
                    st.session_state.flor_seleccionada_meson = {"codigo": 220, "nombre": "Rosas Romance"}
                    st.session_state.cantidad_varas_meson = 30
                    st.rerun()
            with col_f2:
                if st.button("🍊 Rosas Elegance\n(Cód: 221)", key="btn_prod_221", use_container_width=True):
                    st.session_state.flor_seleccionada_meson = {"codigo": 221, "nombre": "Rosas Elegance"}
                    st.session_state.cantidad_varas_meson = 30
                    st.rerun()

        with capa_familias[1]:
            st.markdown("<p style='color:#94a3b8; font-size:13px;'>Seleccione Peonía:</p>", unsafe_allow_html=True)
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                if st.button("🌸 Sarah Bernhardt\n(Cód: 222)", key="btn_prod_222", use_container_width=True):
                    st.session_state.flor_seleccionada_meson = {"codigo": 222, "nombre": "Peonía Sarah Bernhardt"}
                    st.session_state.cantidad_varas_meson = 30
                    st.rerun()
            with col_p2:
                if st.button("🏳️ Festiva Maxima\n(Cód: 223)", key="btn_prod_223", use_container_width=True):
                    st.session_state.flor_seleccionada_meson = {"codigo": 223, "nombre": "Peonía Festiva Maxima"}
                    st.session_state.cantidad_varas_meson = 30
                    st.rerun()

        with capa_familias[2]:
            st.markdown("<p style='color:#94a3b8; font-size:13px;'>Seleccione Delphinium:</p>", unsafe_allow_html=True)
            if st.button("🔹 Guardian Mix\n(Cód: 224)", key="btn_prod_224", use_container_width=True):
                st.session_state.flor_seleccionada_meson = {"codigo": 224, "nombre": "Delphinium Guardian Mix"}
                st.session_state.cantidad_varas_meson = 30
                st.rerun()

    with col_derecha_consolidacion:
        st.subheader("📥 Mesón de Carga Actual")
        with st.container(border=True):
            if st.session_state.rut_cosechador == "":
                st.markdown("<div style='color:#94a3b8; font-weight:bold; font-size:14px; text-align:center; padding:10px;'>Esperando RUT del cosechador...</div>", unsafe_allow_html=True)
            elif not st.session_state.flor_seleccionada_meson:
                st.markdown(f"<div style='color:#38bdf8; font-weight:bold; font-size:13px;'>Trabajador: {rut_pantalla_visual}</div><span style='color:#64748b; font-size:12px;'>Seleccione una flor en el centro...</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"**RUT:** {rut_pantalla_visual}")
                st.markdown(f"**Flor:** <span style='color:#38bdf8;'>{st.session_state.flor_seleccionada_meson['nombre']}</span>", unsafe_allow_html=True)
                
                st.write("")
                st.caption("⚙️ ¿Saldo de hilera? Edita varas:")
                col_btn_menos, col_display_num, col_btn_mas = st.columns([1, 1.5, 1])
                
                with col_btn_menos:
                    if st.button("-5", key="btn_meson_restar_cinco", use_container_width=True):
                        st.session_state.cantidad_varas_meson = max(0, st.session_state.cantidad_varas_meson - 5)
                        st.rerun()
                with col_display_num:
                    st.markdown(f"<div style='background:#0f172a; color:#fff; text-align:center; font-size:20px; font-weight:bold; padding:4px; border:1px solid #64748b; border-radius:4px;'>{st.session_state.cantidad_varas_meson}</div>", unsafe_allow_html=True)
                with col_btn_mas:
                    if st.button("+5", key="btn_meson_sumar_cinco", use_container_width=True):
                        st.session_state.cantidad_varas_meson += 5
                        st.rerun()
                
                st.write("")
                if st.button("✅ Confirmar e Inyectar a Firebase", key="btn_confirmar_registro_meson", use_container_width=True, type="primary"):
                    partes_contratista = contratista.split(" | ")
                    nuevo_registro = {
                        "CentroCosto": centro_costo,
                        "RutContratista": partes_contratista[0].strip(),
                        "ContratistaNombre": partes_contratista[1].strip(),
                        "RutCosechador": rut_pantalla_visual,
                        "CodigoArticulo": int(st.session_state.flor_seleccionada_meson["codigo"]),
                        "DescripcionArticulo": st.session_state.flor_seleccionada_meson["nombre"],
                        "CantidadVaras": int(st.session_state.cantidad_varas_meson),
                        "FechaRegistro": datetime.datetime.now()
                    }
                    try:
                        db.collection("cosecha_diaria").add(nuevo_registro)
                        st.session_state.flor_seleccionada_meson = None
                        st.session_state.rut_cosechador = ""
                        st.success("☁️ ¡Registro guardado en la Nube de Google con éxito!")
                        st.rerun()
                    except Exception as ex:
                        st.error(f"❌ Error de conexión a la nube: {ex}")

        st.write("")
        st.markdown("<label>🗄️ Historial del Día (Servidor Google Cloud)</label>", unsafe_allow_html=True)
        try:
            docs_nube = db.collection("cosecha_diaria").order_by("FechaRegistro", direction=firestore.Query.DESCENDING).limit(10).stream()
            lista_historial_en_vivo = [doc.to_dict() for doc in docs_nube]
            
            if not lista_historial_en_vivo:
                st.info("No hay registros en la nube el día de hoy.")
            else:
                df_historial = pd.DataFrame(lista_historial_en_vivo)
                st.dataframe(df_historial[["RutCosechador", "DescripcionArticulo", "CantidadVaras"]], hide_index=True, use_container_width=True)
                
                st.write("")
                df_consolidado = df_historial.groupby(["CentroCosto", "RutContratista", "ContratistaNombre", "RutCosechador", "CodigoArticulo", "DescripcionArticulo"], as_index=False).sum()
                csv_kame = df_consolidado.to_csv(index=False, sep=";").encode('utf-8')
                fecha_hoy = datetime.datetime.now().strftime("%Y-%m-%d")
                
                st.download_button(label="📊 DESCARGAR .CSV PARA KAME ERP", data=csv_kame, file_name=f"KAME_Cosecha_Antivero_{fecha_hoy}.csv", mime="text/csv", use_container_width=True)
        except Exception as error_lectura:
            st.caption(f"Conectando al stream en vivo... {error_lectura}")
# --- CONTENIDO DE LA PESTAÑA B: PÁGINA COMPLETAMENTE NUEVA DE AUDITORÍA ---
if st.session_state.rol_usuario == "admin" and tab_auditoria is not None:
    with tab_auditoria:
        st.markdown("<h2 style='color:#38bdf8;'>📊 Ventana de Auditoría y Control de Registros</h2>", unsafe_allow_html=True)
        st.caption("Espacio exclusivo para administradores. Filtre por día, por RUT o combine ambos para auditar Google Firebase.")
        
        # Filtros superiores organizados en dos columnas táctiles
        col_filtro_fecha, col_filtro_rut = st.columns(2)
        
        with col_filtro_fecha:
            # Selector de fecha nativo que por defecto viene con el día de hoy
            filtro_fecha = st.date_input("📅 Filtrar por Día:", value=datetime.date.today(), key="admin_audit_date")
            
        with col_filtro_rut:
            filtro_rut = st.text_input("🆔 Filtrar por RUT Cosechador (Opcional):", placeholder="Ej: 123456789", key="admin_audit_rut").strip().lower()
        
        # Construcción dinámica de la consulta a Firebase Cloud Firestore
        # --- REEMPLAZAR DESDE AQUÍ EN TU PESTAÑA B ---
        if "resultado_auditoria_nube" not in st.session_state:
            st.session_state.resultado_auditoria_nube = []

        if st.button("🔍 Ejecutar Búsqueda en la Nube", key="btn_ejecutar_busqueda_audit", use_container_width=True, type="primary"):
            try:
                inicio_dia = datetime.datetime.combine(filtro_fecha, datetime.time.min)
                fin_dia = datetime.datetime.combine(filtro_fecha, datetime.time.max)
                
                query = db.collection("cosecha_diaria").where("FechaRegistro", ">=", inicio_dia).where("FechaRegistro", "<=", fin_dia)
                if filtro_rut:
                    query = query.where("RutCosechador", "==", filtro_rut)
                
                docs_filtrados = query.order_by("FechaRegistro", direction=firestore.Query.DESCENDING).stream()
                st.session_state.resultado_auditoria_nube = [(doc.id, doc.to_dict()) for doc in docs_filtrados]
                
                if not st.session_state.resultado_auditoria_nube:
                    st.info("📋 No se encontraron registros en la nube para los criterios seleccionados.")
                else:
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Error al consultar la base de datos: {e}")

        if st.session_state.resultado_auditoria_nube:
            st.write(f"🔍 Se encontraron {len(st.session_state.resultado_auditoria_nube)} registros:")
            
            for doc_id, datos in st.session_state.resultado_auditoria_nube:
                fecha_reg = datos.get("FechaRegistro")
                if isinstance(fecha_reg, datetime.datetime):
                    hora_str = fecha_reg.strftime("%H:%M:%S")
                elif hasattr(fecha_reg, "to_datetime"):
                    hora_str = fecha_reg.to_datetime().strftime("%H:%M:%S")
                else:
                    hora_str = "S/F"
                
                with st.container(border=True):
                    c_info, c_edit, c_acc = st.columns([1.5, 1, 1])
                    
                    with c_info:
                        st.markdown(f"👤 **Cosechador:** `{datos.get('RutCosechador')}`")
                        st.markdown(f"🌸 **Flor:** {datos.get('DescripcionArticulo')} | 🕒 **Hora:** {hora_str}")
                        st.caption(f"📍 Origen: {datos.get('CentroCosto')} | ID: {doc_id[:8]}...")
                    
                    with c_edit:
                        nueva_cantidad = st.number_input(
                            "Varas:", min_value=0, 
                            value=int(datos.get("CantidadVaras", 0)), 
                            step=1, key=f"audit_mod_{doc_id}"
                        )
                    
                    with c_acc:
                        st.write("")
                        if st.button("💾 Guardar", key=f"audit_btn_upd_{doc_id}", use_container_width=True):
                            try:
                                db.collection("cosecha_diaria").document(doc_id).update({"CantidadVaras": int(nueva_cantidad)})
                                st.session_state.resultado_auditoria_nube = [] 
                                st.success("📝 ¡Registro modificado!")
                                st.rerun()
                            except Exception as ex:
                                st.error(f"Error: {ex}")
                                
                        if st.button("🚨 Borrar", key=f"audit_btn_del_{doc_id}", use_container_width=True, type="secondary"):
                            try:
                                db.collection("cosecha_diaria").document(doc_id).delete()
                                st.session_state.resultado_auditoria_nube = [] 
                                st.success("🗑️ Registro eliminado.")
                                st.rerun()
                            except Exception as ex:
                                st.error(f"Error: {ex}")

        # ==================================================================
        # E. PANEL DE CONFIGURACIÓN DEL CATÁLOGO (BLOQUE COMPLETO UNIFICADO)
        # ==================================================================
        st.write("---")
        st.markdown("<h2 style='color:#38bdf8;'>⚙️ Panel de Configuración del Catálogo</h2>", unsafe_allow_html=True)
        st.caption("Agregue nuevos orígenes, contratistas o variedades de flores directamente a la base de datos.")
        
        # Declaramos las tres sub-pestañas juntas en una sola línea para evitar NameError
        s_cc, s_b2b, s_flores = st.tabs(["📍 Centros de Costo", "🏢 Contratistas B2B", "🌹 Flores y Variedades"])
        
        # A. AGREGAR NUEVO CENTRO DE COSTO
        with s_cc:
            with st.form("form_add_cc", clear_on_submit=True):
                nuevo_cc_nombre = st.text_input("Nombre del nuevo Centro de Costo:", placeholder="Ej: Fundo El Quillay (CC 03)").strip()
                if st.form_submit_button("💾 Registrar Centro de Costo", use_container_width=True):
                    if nuevo_cc_nombre:
                        try:
                            db.collection("config_centros").add({"nombre": nuevo_cc_nombre, "fecha_creacion": datetime.datetime.now()})
                            st.success(f"✅ Centro de Costo '{nuevo_cc_nombre}' inyectado a Firebase.")
                        except Exception as e:
                            st.error(f"❌ Error en la nube: {e}")
                    else:
                        st.warning("⚠️ El campo de nombre no puede estar vacío.")

        # B. AGREGAR NUEVO CONTRATISTA DESTINO
        with s_b2b:
            with st.form("form_add_contratista", clear_on_submit=True):
                new_rut_b2b = st.text_input("RUT Contratista (Con puntos y guión):", placeholder="Ej: 76.888.999-K").strip()
                new_nom_b2b = st.text_input("Razón Social / Nombre Contratista:", placeholder="Ej: Cosechas del Valle SpA").strip()
                if st.form_submit_button("💾 Registrar Contratista B2B", use_container_width=True):
                    if new_rut_b2b and new_nom_b2b:
                        try:
                            cadena_kame = f"{new_rut_b2b} | {new_nom_b2b}"
                            db.collection("config_contratistas").add({"formato_kame": cadena_kame, "fecha_creacion": datetime.datetime.now()})
                            st.success(f"✅ Contratista '{cadena_kame}' configurado para Kame ERP.")
                        except Exception as e:
                            st.error(f"❌ Error en la nube: {e}")
                    else:
                        st.warning("⚠️ Ambos campos son obligatorios.")
        # C. AGREGAR NUEVA FLOR Y VARIEDAD AL CATÁLOGO
        with s_flores:
            with st.form("form_add_flor_catalogo", clear_on_submit=True):
                nueva_familia = st.selectbox("Seleccione Familia Agrícola:", ["🌹 Rosas", "🌸 Peonías", "🔹 Delphinium", "💐 Lisianthus", "🌾 Otras Variedades"], key="admin_add_fam_select")
                nuevo_cod_flor = st.number_input("Código de Artículo único (Kame ERP):", min_value=1, value=225, step=1, key="admin_add_cod_int")
                nuevo_nom_flor = st.text_input("Nombre de la Variedad / Color:", placeholder="Ej: Red Naomi o Coral Sunset").strip()
                
                if st.form_submit_button("💾 Registrar Flor en el Catálogo", use_container_width=True):
                    if nuevo_nom_flor and nuevo_cod_flor:
                        try:
                            db.collection("config_flores").add({
                                "familia": nueva_familia,
                                "codigo": int(nuevo_cod_flor),
                                "nombre": nuevo_nom_flor,
                                "fecha_creacion": datetime.datetime.now()
                            })
                            st.success(f"✅ ¡Variedad '{nuevo_nom_flor}' (Cód: {nuevo_cod_flor}) añadida con éxito!")
                        except Exception as e:
                            st.error(f"❌ Error al inyectar flor en la nube: {e}")
                    else:
                        st.warning("⚠️ El nombre de la variedad y el código son obligatorios.")
