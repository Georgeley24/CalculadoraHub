import streamlit as st
import os
import base64
import time
import uuid
import datetime
import pandas as pd

# 1. Configuración de la página principal del Hub Central
st.set_page_config(
    page_title="Hub Central - Ecosistema de Calculadoras Paramétricas Georgeley",
    page_icon="🏢",
    layout="wide"
)

# Estilo CSS para fijar el ancho óptimo de la barra lateral
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        min-width: 350px !important;
        max-width: 380px !important;
    }
</style>
""", unsafe_allow_html=True)

# Directorio raíz absoluto del Hub
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Asegurar siempre el directorio raíz al iniciar el script
os.chdir(ROOT_DIR)

# Función auxiliar para convertir imágenes a Base64 usando rutas absolutas
def get_image_base64(filename):
    path = os.path.join(ROOT_DIR, filename)
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

# -------------------------------------------------------------
# GESTOR GLOBAL DE SESIONES CONCURRENTES (2 INDIV / 5 CORP)
# -------------------------------------------------------------
@st.cache_resource
def obtener_registro_sesiones():
    """Almacena en memoria global del servidor las sesiones activas por correo."""
    return {}

SESIONES_ACTIVAS = obtener_registro_sesiones()
TIMEOUT_SESION_SEG = 1800  # 30 minutos de inactividad liberan el asiento automáticamente

if "session_token" not in st.session_state:
    st.session_state.session_token = str(uuid.uuid4())

def limpiar_sesiones_expiradas(correo):
    ahora = time.time()
    if correo in SESIONES_ACTIVAS:
        SESIONES_ACTIVAS[correo] = {
            tok: ts for tok, ts in SESIONES_ACTIVAS[correo].items()
            if (ahora - ts) < TIMEOUT_SESION_SEG
        }

def registrar_o_validar_sesion(correo, max_usuarios):
    limpiar_sesiones_expiradas(correo)
    token = st.session_state.session_token
    sesiones_usuario = SESIONES_ACTIVAS.setdefault(correo, {})
    if token in sesiones_usuario:
        sesiones_usuario[token] = time.time()
        return True, len(sesiones_usuario)
    if len(sesiones_usuario) < max_usuarios:
        sesiones_usuario[token] = time.time()
        return True, len(sesiones_usuario)
    return False, len(sesiones_usuario)

def liberar_sesion_actual():
    usuario = st.session_state.get("usuario_autenticado")
    token = st.session_state.get("session_token")
    if usuario and usuario["correo"] in SESIONES_ACTIVAS:
        SESIONES_ACTIVAS[usuario["correo"]].pop(token, None)

# -------------------------------------------------------------
# LECTURA Y VALIDACIÓN CONTRA EXCEL MAESTRO (usuarios_hub.xlsx)
# -------------------------------------------------------------
ARCHIVO_USUARIOS = os.path.join(ROOT_DIR, "usuarios_hub.xlsx")

def validar_credenciales_excel(correo_ingresado, contrasena_ingresada):
    if not os.path.exists(ARCHIVO_USUARIOS):
        return False, "No se encontró el archivo maestro 'usuarios_hub.xlsx' en la carpeta raíz del Hub.", None

    try:
        # Fila 3 (índice 2) contiene las llaves técnicas exactas; datos inician en fila 5 (índice 4)
        df = pd.read_excel(ARCHIVO_USUARIOS, sheet_name="Control_Usuarios", header=2)
        df = df.iloc[1:].copy()  # Omitir fila 4 de encabezados visuales
    except Exception as e:
        return False, f"Error al leer la base de datos de usuarios: {e}", None

    correo_clean = str(correo_ingresado).strip().lower()
    pass_clean = str(contrasena_ingresada).strip()

    df["correo_norm"] = df["correo"].astype(str).str.strip().str.lower()
    fila = df[df["correo_norm"] == correo_clean]

    if fila.empty:
        return False, "Correo electrónico no registrado en el ecosistema Georgeley.", None

    registro = fila.iloc[0]
    if str(registro["contrasena"]).strip() != pass_clean:
        return False, "Contraseña incorrecta. Verifica tus credenciales de acceso.", None

    # Validar vigencia anual (365 días)
    try:
        fecha_susc = pd.to_datetime(registro["fecha_suscripcion"]).date()
        fecha_venc = fecha_susc + datetime.timedelta(days=365)
        dias_restantes = (fecha_venc - datetime.date.today()).days
    except Exception:
        return False, "Fecha de suscripción inválida en el registro. Contacta al administrador.", None

    if dias_restantes < 0:
        return False, f"Tu suscripción anual venció el {fecha_venc.strftime('%Y-%m-%d')}. Renuévala en Skool para reactivar el acceso.", None

    tipo_plan = str(registro.get("tipo_plan", "Individual")).strip()
    max_usuarios = 5 if tipo_plan.lower() == "corporativo" else 2

    def flag_activo(col):
        val = registro.get(col, 0)
        return str(val).strip() in ("1", "1.0", "True", "TRUE", "VERDADERO")

    vip = flag_activo("vip_total")

    permisos = {
        "vip_total": vip,
        "lci": vip or flag_activo("lci"),
        "depas": vip or flag_activo("depas"),
        "bodegas": vip or flag_activo("bodegas"),
        "comercios": vip or flag_activo("comercios"),
        "hoteles": vip or flag_activo("hoteles"),
        "oficinas": vip or flag_activo("oficinas"),
        "urbanizacion": vip or flag_activo("urbanizacion"),
        "vivienda": vip or flag_activo("vivienda"),
        "paq_educ_cult": vip or flag_activo("paq_educ_cult"),
        "paq_bien_salud": vip or flag_activo("paq_bien_salud"),
        "infraestructura": vip or flag_activo("infraestructura"),
    }

    datos_usuario = {
        "correo": correo_clean,
        "tipo_plan": tipo_plan,
        "max_usuarios": max_usuarios,
        "fecha_vencimiento": fecha_venc.strftime("%Y-%m-%d"),
        "dias_restantes": dias_restantes,
        "permisos": permisos,
    }
    return True, "Acceso concedido", datos_usuario

# -------------------------------------------------------------
# CONTROL DE INICIO DE SESIÓN OBLIGATORIO
# -------------------------------------------------------------
if "usuario_autenticado" not in st.session_state:
    st.session_state.usuario_autenticado = None

if st.session_state.usuario_autenticado is None:
    logo_b64 = get_image_base64("00. Logo Georgeley.png")
    avatar_b64 = get_image_base64("Georgeley AV01.png")

    col_izq, col_centro, col_der = st.columns([1.2, 1.6, 1.2])
    with col_centro:
        if logo_b64:
            st.markdown(f"""
            <div style="display: flex; justify-content: center; margin-top: 10px; margin-bottom: 10px;">
                <img src="data:image/png;base64,{logo_b64}" width="180">
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<h2 style='text-align: center; margin-bottom: 4px;'>🔐 Acceso al Hub Central</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #94A3B8; font-size: 0.92rem;'>Ecosistema de Calculadoras Paramétricas Georgeley</p>", unsafe_allow_html=True)

        with st.form("form_login_hub"):
            correo_input = st.text_input("Correo Electrónico Registrado:", placeholder="tu.correo@ejemplo.com")
            pass_input = st.text_input("Contraseña Única:", type="password", placeholder="••••••••••••")
            btn_login = st.form_submit_button("🚀 Ingresar al Ecosistema", use_container_width=True, type="primary")

            if btn_login:
                ok, mensaje, datos_usr = validar_credenciales_excel(correo_input, pass_input)
                if not ok:
                    st.error(f"❌ {mensaje}")
                else:
                    permitido, activos = registrar_o_validar_sesion(datos_usr["correo"], datos_usr["max_usuarios"])
                    if not permitido:
                        st.error(
                            f"🚫 **Límite de dispositivos simultáneos alcanzado ({activos}/{datos_usr['max_usuarios']}).**\n\n"
                            f"Tu plan **{datos_usr['tipo_plan']}** permite máximo **{datos_usr['max_usuarios']}** sesión(es) activa(s) al mismo tiempo. "
                            "Cierra sesión en otro equipo o espera unos minutos."
                        )
                    else:
                        st.session_state.usuario_autenticado = datos_usr
                        st.rerun()

        if avatar_b64:
            st.markdown(f"""
            <div style="display: flex; justify-content: center; margin-top: 15px;">
                <img src="data:image/png;base64,{avatar_b64}" width="130">
            </div>
            """, unsafe_allow_html=True)
        st.info("💡 ¿Aún no tienes licencia activa? Adquiere tu suscripción anual en nuestra comunidad oficial de **Skool**.")
    st.stop()

# Renovar marca de tiempo de sesión activa en cada interacción
usuario_actual = st.session_state.usuario_autenticado
permitido_continuar, sesiones_en_uso = registrar_o_validar_sesion(
    usuario_actual["correo"], usuario_actual["max_usuarios"]
)
if not permitido_continuar:
    st.session_state.usuario_autenticado = None
    st.rerun()

permisos_usuario = usuario_actual["permisos"]

# -------------------------------------------------------------
# CONTROL DE ESTADO DE NAVEGACIÓN Y LIMPIEZA (INTACTO)
# -------------------------------------------------------------
if "calculadora_activa" not in st.session_state:
    st.session_state.calculadora_activa = "📊 Selecciona una calculadora..."

# Mapa completo de calculadoras + llave de permiso asociada
catalogo_completo = {
    "📊 Selecciona una calculadora...": (None, None, True),
    "🏢 01. Departamentos": ("01departamentos", "app_departamentos.py", permisos_usuario["depas"]),
    "🏭 02. Bodegas y Naves": ("02bodegas", "app_bodegas.py", permisos_usuario["bodegas"]),
    "🛒 03. Comercios y Locales": ("03comercios", "app_comercios.py", permisos_usuario["comercios"]),
    "🏛️ 04. Culturales": ("04culturales", "app_culturales.py", permisos_usuario["paq_educ_cult"]),
    "⚽ 05. Deportivos": ("05deportivos", "app_deportivos.py", permisos_usuario["paq_bien_salud"]),
    "🏫 06. Escuelas y Educación": ("06escuelas", "app_escuelas.py", permisos_usuario["paq_educ_cult"]),
    "🏥 07. Hospitales y Salud": ("07hospitales", "app_hospitales.py", permisos_usuario["paq_bien_salud"]),
    "🏨 08. Hoteles y Hospedaje": ("08hoteles", "app_hoteles.py", permisos_usuario["hoteles"]),
    "🛣️ 09. Infraestructura Vial": ("09infraestructura", "app_infraestructura.py", permisos_usuario["infraestructura"]),
    "🏢 10. Oficinas y Corporativos": ("10oficinas", "app_oficinas.py", permisos_usuario["oficinas"]),
    "🏗️ 11. Urbanización y Obras": ("11urbanizacion", "app_urbanizacion.py", permisos_usuario["urbanizacion"]),
    "🏠 12. Vivienda Habitacional": ("12vivienda", "app_vivienda.py", permisos_usuario["vivienda"]),
}

# Filtrar únicamente los módulos autorizados para el usuario
calculadoras_disponibles = {
    nombre: (carpeta, archivo)
    for nombre, (carpeta, archivo, autorizado) in catalogo_completo.items()
    if autorizado
}

if st.session_state.calculadora_activa not in calculadoras_disponibles:
    st.session_state.calculadora_activa = "📊 Selecciona una calculadora..."

def limpiar_estado_calculadora():
    """Limpia las variables de sesión para evitar conflictos de datos entre diferentes módulos."""
    keys_to_remove = ["calcular", "resultado_activo"]
    for k in keys_to_remove:
        if k in st.session_state:
            del st.session_state[k]

# -------------------------------------------------------------
# BARRA LATERAL DINÁMICA SEGÚN EL ESTADO (ORDEN VERIFICADO)
# -------------------------------------------------------------
if st.session_state.calculadora_activa == "📊 Selecciona una calculadora...":
    # --- VISTA DEL HUB PRINCIPAL (ORDEN: Logo -> Texto -> Avatar AV01 -> Navegación) ---
    
    # 01. Logo Georgeley centrado (Ruta absoluta blindada)
    logo_b64 = get_image_base64("00. Logo Georgeley.png")
    if logo_b64:
        st.sidebar.markdown(f"""
        <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 10px;">
            <img src="data:image/png;base64,{logo_b64}" width="190" style="display: block; margin: 0 auto;">
        </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown("<h3 style='text-align: center;'>🏢 <b>GEORGELEY</b></h3>", unsafe_allow_html=True)

    # 02. Globo de diálogo (Texto de bienvenida)
    st.sidebar.markdown("""
    <div style="
        position: relative;
        background: #2D2B42;
        border: 3px solid #111118;
        border-radius: 18px;
        padding: 14px 16px;
        margin-top: 10px;
        margin-bottom: 15px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.3);
        color: #FFFFFF;
    ">
        <p style="margin: 0 0 6px 0; font-size: 0.95rem; font-weight: 700; color: #FFFFFF;">👋 ¡Hola, bienvenido!</p>
        <p style="margin: 0; font-size: 0.85rem; line-height: 1.4; color: #F1F5F9;">
            Soy <b>Georgeley</b>. Selecciona cualquier módulo en el menú inferior para desplegarlo.
        </p>
        <div style="
            position: absolute;
            bottom: -14px;
            left: 50%;
            transform: translateX(-50%);
            width: 0;
            height: 0;
            border-left: 10px solid transparent;
            border-right: 10px solid transparent;
            border-top: 14px solid #2D2B42;
        "></div>
    </div>
    """, unsafe_allow_html=True)

    # 03. Avatar exclusivo del Hub (Georgeley AV01.png) centrado y blindado
    avatar_b64 = get_image_base64("Georgeley AV01.png")
    if avatar_b64:
        st.sidebar.markdown(f"""
        <div style="display: flex; justify-content: center; align-items: center; margin-top: 10px; margin-bottom: 15px;">
            <img src="data:image/png;base64,{avatar_b64}" width="190" style="display: block; margin: 0 auto;">
        </div>
        """, unsafe_allow_html=True)

    st.sidebar.divider()
    
    # 04. Apartado de Navegación del Hub (Selector)
    st.sidebar.markdown("### 🎛️ Navegación del Hub")

    seleccion_menu = st.sidebar.selectbox(
        "Selecciona un módulo:", 
        list(calculadoras_disponibles.keys()),
        index=list(calculadoras_disponibles.keys()).index(st.session_state.calculadora_activa)
    )

    if seleccion_menu != st.session_state.calculadora_activa:
        limpiar_estado_calculadora()
        st.session_state.calculadora_activa = seleccion_menu
        st.rerun()

    # Tarjeta compacta de estado de licencia y botón cerrar sesión
    st.sidebar.divider()
    etiqueta_lci = "✅ LCI Regionales Activo" if permisos_usuario["lci"] else "🔒 LCI: Solo CDMX (1.00)"
    st.sidebar.caption(
        f"👤 **{usuario_actual['correo']}**\n\n"
        f"📋 Plan: **{usuario_actual['tipo_plan']}** ({sesiones_en_uso}/{usuario_actual['max_usuarios']} sesiones)\n\n"
        f"📅 Vence: **{usuario_actual['fecha_vencimiento']}** ({usuario_actual['dias_restantes']} días)\n\n"
        f"{etiqueta_lci}"
    )
    if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
        liberar_sesion_actual()
        st.session_state.usuario_autenticado = None
        st.session_state.calculadora_activa = "📊 Selecciona una calculadora..."
        st.rerun()

# -------------------------------------------------------------
# RENDERIZADO PRINCIPAL (HUB O MÓDULO ACTIVO)
# -------------------------------------------------------------
if st.session_state.calculadora_activa == "📊 Selecciona una calculadora...":
    # Pantalla Principal del Hub
    col_title, col_ver = st.columns([4, 1])
    with col_title:
        st.title("🚀 Hub Central: Ecosistema de Ingeniería de Costos")
    with col_ver:
        st.markdown("""
        <div style="text-align: right; padding-top: 15px;">
            <span style="background-color: #1e3a8a; color: #ffffff; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.95rem; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                Hub v3.0
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("Bienvenido al centro de control maestro de tus modelos paramétricos. Selecciona una opción en el menú de la barra lateral para desplegar la herramienta deseada.")
    st.divider()

    st.markdown("### 🌟 Módulos Activos en tu Suscripción")

    def marca_estado(nombre_menu):
        return "✅" if nombre_menu in calculadoras_disponibles else "🔒"

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        #### 🏢 Edificación Vertical
        * {marca_estado("🏢 01. Departamentos")} Departamentos
        * {marca_estado("🏢 10. Oficinas y Corporativos")} Oficinas y Corporativos
        * {marca_estado("🏨 08. Hoteles y Hospedaje")} Hoteles y Hospedaje
        * {marca_estado("🏥 07. Hospitales y Salud")} Hospitales y Salud
        """)
    with col2:
        st.markdown(f"""
        #### 🏛️ Espacios Públicos y Sociales
        * {marca_estado("🛒 03. Comercios y Locales")} Comercios y Locales
        * {marca_estado("🏫 06. Escuelas y Educación")} Escuelas y Educación
        * {marca_estado("🏛️ 04. Culturales")} Culturales y Recreativos
        * {marca_estado("⚽ 05. Deportivos")} Deportivos
        * {marca_estado("🏭 02. Bodegas y Naves")} Bodegas y Naves Industriales
        """)
    with col3:
        st.markdown(f"""
        #### 🛣️ Infraestructura y Vivienda
        * {marca_estado("🏠 12. Vivienda Habitacional")} Vivienda Habitacional
        * {marca_estado("🏗️ 11. Urbanización y Obras")} Urbanización y Loteos
        * {marca_estado("🛣️ 09. Infraestructura Vial")} Infraestructura Vial
        """)

    if not permisos_usuario["lci"]:
        st.warning("🔒 **Modo LCI Base Activo:** Tu suscripción actual opera únicamente con el factor de **Ciudad de México (1.00)**. Actualiza a LCI Regionales o VIP en Skool para desbloquear todas las ciudades.")

    st.info("👈 **Para comenzar, elige un módulo habilitado (✅) en la barra lateral izquierda.**")

else:
    # --- EJECUCIÓN DEL MÓDULO ACTIVO ---
    carpeta, archivo = calculadoras_disponibles[st.session_state.calculadora_activa]
    ruta_modulo_dir = os.path.join(ROOT_DIR, "modulos", carpeta)
    ruta_script = os.path.join(ruta_modulo_dir, archivo)
    
    if os.path.exists(ruta_script):
        os.chdir(ruta_modulo_dir)
        with open(archivo, "r", encoding="utf-8") as f:
            codigo_modulo = f.read()

        # Si el usuario NO tiene LCI activo, restringimos selectbox de ciudades/LCI a Ciudad de México (1.0)
        selectbox_original = st.selectbox
        sidebar_selectbox_original = st.sidebar.selectbox

        def crear_selectbox_restringido(orig_fn):
            def wrapper(label, options, *args, **kwargs):
                lbl_low = str(label).lower()
                opts_list = list(options) if options is not None else []
                es_selector_lci = any(
                    pal in lbl_low for pal in ("ciudad", "estado", "localidad", "ubicación", "ubicacion", "contexto", "lci", "región", "region", "plaza", "zona")
                )
                if es_selector_lci and opts_list:
                    cdmx_opts = [
                        o for o in opts_list
                        if any(k in str(o).lower() for k in ("ciudad de méxico", "ciudad de mexico", "cdmx", "distrito federal"))
                    ]
                    opciones_filtradas = cdmx_opts if cdmx_opts else [opts_list[0]]
                    kwargs["index"] = 0
                    kwargs["help"] = "🔒 Suscripción sin LCI Regionales: bloqueado a Ciudad de México (Factor 1.00)."
                    return orig_fn(label, opciones_filtradas, *args, **kwargs)
                return orig_fn(label, options, *args, **kwargs)
            return wrapper

        if not permisos_usuario["lci"]:
            st.selectbox = crear_selectbox_restringido(selectbox_original)
            st.sidebar.selectbox = crear_selectbox_restringido(sidebar_selectbox_original)

        try:
            exec(codigo_modulo, {'__name__': '__main__', '__file__': ruta_script})
        finally:
            st.selectbox = selectbox_original
            st.sidebar.selectbox = sidebar_selectbox_original
        
        # --- CONTROL DE NAVEGACIÓN UBICADO AL FINAL DE LA BARRA LATERAL ---
        st.sidebar.divider()
        st.sidebar.markdown("### 🎛️ Control de Navegación")

        seleccion_menu = st.sidebar.selectbox(
            "Cambiar de módulo:", 
            list(calculadoras_disponibles.keys()),
            index=list(calculadoras_disponibles.keys()).index(st.session_state.calculadora_activa)
        )

        if seleccion_menu != st.session_state.calculadora_activa:
            limpiar_estado_calculadora()
            st.session_state.calculadora_activa = seleccion_menu
            os.chdir(ROOT_DIR)
            st.rerun()

        if st.sidebar.button("🏠 Ir al Inicio del Hub", use_container_width=True, type="primary"):
            limpiar_estado_calculadora()
            st.session_state.calculadora_activa = "📊 Selecciona una calculadora..."
            os.chdir(ROOT_DIR)
            st.toast("⚠️ Se han reiniciado los parámetros y regresaste al Hub.", icon="🔄")
            st.rerun()

        if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
            liberar_sesion_actual()
            limpiar_estado_calculadora()
            st.session_state.usuario_autenticado = None
            st.session_state.calculadora_activa = "📊 Selecciona una calculadora..."
            os.chdir(ROOT_DIR)
            st.rerun()

        os.chdir(ROOT_DIR)
    else:
        os.chdir(ROOT_DIR)
        st.error(f"⚠️ No se encontró el archivo del módulo en la ruta exacta: `{ruta_script}`.")