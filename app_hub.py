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

# Estilo CSS responsivo conservando siempre accesible el controlador del panel lateral
# y asegurando contraste oscuro legible en cualquier modo del dispositivo
st.markdown("""
<style>
    /* Base oscura consistente para evitar texto claro sobre fondo blanco */
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    section.main {
        background-color: #0E1117 !important;
        color: #F1F5F9 !important;
    }

    /* Mantener siempre visible y accesible el botón para abrir/ocultar la barra lateral */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebarHeader"] button {
        visibility: visible !important;
        opacity: 1 !important;
        z-index: 1000002 !important;
        pointer-events: auto !important;
    }

    /* Ancho de barra lateral solo en pantallas amplias de escritorio */
    @media (min-width: 1025px) and (min-height: 551px) {
        [data-testid="stSidebar"] {
            min-width: 350px !important;
            max-width: 380px !important;
        }
    }

    /* Celulares y tablets (vertical y rotado en horizontal) */
    @media (max-width: 1024px), (max-height: 550px) and (orientation: landscape) {
        [data-testid="stSidebar"] {
            min-width: 0 !important;
            max-width: 78vw !important;
        }
        [data-testid="stSidebar"][aria-expanded="false"] {
            min-width: 0 !important;
            max-width: 0 !important;
        }
        .main .block-container,
        [data-testid="stMainBlockContainer"] {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 2.5rem !important;
            max-width: 100% !important;
        }
        h1 {
            font-size: 1.45rem !important;
            line-height: 1.25 !important;
            word-wrap: break-word !important;
        }
        h2 {
            font-size: 1.2rem !important;
        }
    }

    /* Botón destacado del Demo Gratuito: morado (#6D28D9) con letras amarillas (#fbbf24) */
    .demo-btn-morado button,
    .demo-btn-morado [data-testid="stBaseButton-secondary"],
    .demo-btn-morado [data-testid="stBaseButton-primary"],
    .demo-btn-morado div[data-testid="stButton"] > button {
        background: linear-gradient(135deg, #6D28D9 0%, #5B21B6 100%) !important;
        background-color: #6D28D9 !important;
        color: #fbbf24 !important;
        border: 2px solid #fbbf24 !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
        font-size: 0.98rem !important;
        box-shadow: 0 4px 16px rgba(109, 40, 217, 0.45) !important;
        transition: transform 0.15s ease, box-shadow 0.2s ease, background-color 0.2s ease !important;
    }
    .demo-btn-morado button:hover,
    .demo-btn-morado [data-testid="stBaseButton-secondary"]:hover,
    .demo-btn-morado [data-testid="stBaseButton-primary"]:hover,
    .demo-btn-morado div[data-testid="stButton"] > button:hover {
        background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%) !important;
        background-color: #7C3AED !important;
        color: #fde047 !important;
        border-color: #fde047 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(124, 58, 237, 0.6) !important;
    }
    .demo-btn-morado button *,
    .demo-btn-morado button p,
    .demo-btn-morado button span {
        color: #fbbf24 !important;
        font-weight: 800 !important;
    }

    /* Catálogo de 12 calculadoras y tipologías */
    .catalogo-box {
        background: #181824;
        border: 1px solid #2e2e42;
        border-radius: 14px;
        padding: 18px 20px;
        margin-top: 12px;
        margin-bottom: 16px;
        color: #F1F5F9;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.28);
    }
    .catalogo-header {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        align-items: center;
        gap: 8px;
        margin-bottom: 12px;
        padding-bottom: 10px;
        border-bottom: 1px solid #2e2e42;
    }
    .catalogo-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #F8FAFC;
        margin: 0;
    }
    .catalogo-resumen {
        font-size: 0.85rem;
        font-weight: 600;
        color: #fbbf24;
    }
    .catalogo-item {
        background: #12121c;
        border: 1px solid #262638;
        border-radius: 10px;
        padding: 9px 12px;
        margin-bottom: 8px;
        font-size: 0.86rem;
        line-height: 1.35;
        color: #E2E8F0;
    }
    .catalogo-tipologias {
        display: block;
        font-size: 0.8rem;
        color: #93c5fd;
        margin-top: 3px;
        font-weight: 600;
    }
    .catalogo-nota {
        font-size: 0.8rem;
        color: #CBD5E1;
        margin-top: 8px;
        line-height: 1.4;
    }

    /* Banner superior fijo en el panel de resultados del Demo */
    .demo-catalogo-top {
        background: #181824;
        border: 1px solid #334155;
        border-left: 4px solid #3b82f6;
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 14px;
        color: #F1F5F9;
    }
    .demo-catalogo-top-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #F8FAFC;
        margin: 0 0 6px 0;
    }
    .demo-catalogo-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-top: 6px;
    }
    .demo-pill {
        background: #11131f;
        border: 1px solid #2a3346;
        color: #E2E8F0;
        border-radius: 8px;
        padding: 4px 8px;
        font-size: 0.76rem;
        line-height: 1.25;
    }
    .demo-pill strong {
        color: #fbbf24;
    }

    .plan-card-wide {
        background: #181824;
        border: 1px solid #2e2e42;
        border-radius: 14px;
        padding: 20px 22px;
        margin-bottom: 14px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
    }
    .plan-badge {
        display: inline-block;
        background: rgba(59, 130, 246, 0.16);
        color: #93c5fd;
        border: 1px solid rgba(59, 130, 246, 0.35);
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.76rem;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .plan-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #f8fafc;
        margin: 0 0 4px 0;
    }
    .plan-price {
        font-size: 1.55rem;
        font-weight: 800;
        color: #fbbf24;
        margin: 0 0 10px 0;
    }
    .plan-price span {
        font-size: 0.9rem;
        font-weight: 500;
        color: #94a3b8;
    }
    .plan-lead {
        font-size: 0.88rem;
        line-height: 1.45;
        color: #cbd5e1;
        margin: 0;
        font-style: italic;
    }
    .plan-list {
        list-style: none;
        padding: 0;
        margin: 0;
        font-size: 0.88rem;
        line-height: 1.5;
        color: #e2e8f0;
    }
    .plan-list li {
        margin-bottom: 6px;
    }
    .demo-plan-list {
        list-style: none;
        padding: 0;
        margin: 6px 0 10px 0;
        font-size: 0.8rem;
        line-height: 1.42;
        color: #e2e8f0;
    }
    .demo-plan-list li {
        margin-bottom: 4px;
    }

    /* Botones de enlace (st.link_button) armonizados con el globo de bienvenida (#2D2B42) */
    div[data-testid="stLinkButton"] > a,
    div[data-testid="stLinkButton"] a,
    [data-testid="stExpander"] a[href*="buy.stripe.com"],
    [data-testid="stSidebar"] a[href*="buy.stripe.com"] {
        background-color: #2D2B42 !important;
        background: #2D2B42 !important;
        color: #FFFFFF !important;
        border: 1.5px solid #4A476B !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        text-decoration: none !important;
        transition: background-color 0.2s ease, border-color 0.2s ease !important;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.28) !important;
    }
    div[data-testid="stLinkButton"] > a:hover,
    div[data-testid="stLinkButton"] a:hover,
    [data-testid="stExpander"] a[href*="buy.stripe.com"]:hover,
    [data-testid="stSidebar"] a[href*="buy.stripe.com"]:hover {
        background-color: #393654 !important;
        background: #393654 !important;
        border-color: #6B6699 !important;
        color: #FFFFFF !important;
    }
    div[data-testid="stLinkButton"] > a *,
    div[data-testid="stLinkButton"] a * {
        color: #FFFFFF !important;
    }

    /* Elevar marca de agua fija en esquina inferior derecha para evitar encimarse con Manage app */
    [class*="watermark"],
    [class*="marca-agua"],
    [id*="watermark"],
    [id*="marca-agua"] {
        bottom: 62px !important;
        right: 24px !important;
        z-index: 40 !important;
    }
</style>
""", unsafe_allow_html=True)

# Directorio raíz absoluto del Hub
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Asegurar siempre el directorio raíz al iniciar el script
os.chdir(ROOT_DIR)

# Catálogo oficial de las 12 calculadoras y sus tipologías
CATALOGO_CALCULADORAS = [
    {"num": "01", "icono": "🏢", "nombre": "Departamentos", "tipologias": 7, "modalidad": "Individual", "detalle": "7 tipologías"},
    {"num": "02", "icono": "🏭", "nombre": "Bodegas y Naves", "tipologias": 6, "modalidad": "Individual", "detalle": "6 tipologías"},
    {"num": "03", "icono": "🛒", "nombre": "Comercios y Locales", "tipologias": 14, "modalidad": "Individual", "detalle": "14 tipologías"},
    {"num": "04", "icono": "🏛️", "nombre": "Culturales", "tipologias": 5, "modalidad": "Paquete Dúo", "detalle": "5 tipologías · exclusivo paq. Dúo"},
    {"num": "05", "icono": "⚽", "nombre": "Deportivos", "tipologias": 5, "modalidad": "Paquete Dúo", "detalle": "5 tipologías · exclusivo paq. Dúo"},
    {"num": "06", "icono": "🏫", "nombre": "Escuelas y Educación", "tipologias": 4, "modalidad": "Paquete Dúo", "detalle": "4 tipologías · exclusivo paq. Dúo"},
    {"num": "07", "icono": "🏥", "nombre": "Hospitales y Salud", "tipologias": 4, "modalidad": "Paquete Dúo", "detalle": "4 tipologías · exclusivo paq. Dúo"},
    {"num": "08", "icono": "🏨", "nombre": "Hoteles y Hospedaje", "tipologias": 7, "modalidad": "Individual", "detalle": "7 tipologías"},
    {"num": "09", "icono": "🛣️", "nombre": "Infraestructura Vial", "tipologias": 2, "modalidad": "Bono", "detalle": "2 tipologías · gratis con cualquier suscripción"},
    {"num": "10", "icono": "🏢", "nombre": "Oficinas y Corporativos", "tipologias": 10, "modalidad": "Individual", "detalle": "10 tipologías"},
    {"num": "11", "icono": "🏗️", "nombre": "Urbanización y Obras", "tipologias": 12, "modalidad": "Individual", "detalle": "12 tipologías"},
    {"num": "12", "icono": "🏠", "nombre": "Vivienda Habitacional", "tipologias": 7, "modalidad": "Individual", "detalle": "7 tipologías"},
]

TOTAL_CALCULADORAS = len(CATALOGO_CALCULADORAS)
TOTAL_TIPOLOGIAS = sum(item["tipologias"] for item in CATALOGO_CALCULADORAS)

# Catálogo comercial con Payment Links oficiales de Stripe
PLANES_ECOSISTEMA = [
    {
        "id": "estandar",
        "tag": "Plan Individual",
        "nombre": "Estándar",
        "precio": "$105.00 USD",
        "periodo": "/año",
        "enfoque": "Tu punto de partida ideal para presupuestar con criterio paramétrico en tu práctica diaria, con el respaldo de una comunidad activa y soporte continuo.",
        "url": "https://buy.stripe.com/8x2aEXbJz3Aqad41tggfu02",
        "cta": "Unirme a la experiencia Estándar",
        "beneficios": [
            "1 calculadora paramétrica a elegir (de las 7 disponibles) con vigencia anual",
            "Bono incluido: Infraestructura Vial (2 tipologías)",
            "Hasta 2 usuarios simultáneos (ideal para oficina y casa, o calculista y auxiliar)",
            "LCI Regionales fijo en Ciudad de México (Factor 1.00)",
            "Soporte técnico durante 365 días",
        ],
    },
    {
        "id": "premium",
        "tag": "Plan Dúo",
        "nombre": "Premium",
        "precio": "$185.00 USD",
        "periodo": "/año",
        "enfoque": "Pensado para despachos pequeños o medianos que desean iniciar su experiencia con dos calculadoras nuevas o adicionales a su experiencia Estándar previamente contratada.",
        "url": "https://buy.stripe.com/dRm8wP00Rdb070S6NAgfu03",
        "cta": "Unirme a la experiencia Premium",
        "beneficios": [
            "2 calculadoras paramétricas a elegir con vigencia anual",
            "Bono incluido: Infraestructura Vial (2 tipologías)",
            "Hasta 2 usuarios simultáneos para trabajo individual o despacho pequeño",
            "LCI Regionales fijo en Ciudad de México (Factor 1.00)",
            "Soporte técnico durante 365 días",
        ],
    },
    {
        "id": "vip",
        "tag": "Add-on LCI México",
        "nombre": "VIP",
        "precio": "$75.00 USD",
        "periodo": "/año",
        "enfoque": "Lleva tus estimaciones al contexto real de cualquier plaza del país, ajustando tus modelos a las condiciones regionales de México.",
        "url": "https://buy.stripe.com/4gM7sL6pfgnc70Sgoagfu04",
        "cta": "Sumar la experiencia VIP",
        "beneficios": [
            "Habilita el Índice de Contexto Local (LCI) en tus calculadoras activas",
            "Factores LCI regionales activos para estados y ciudades de la República Mexicana",
            "Requiere contar con al menos 1 calculadora activa (Plan Estándar o Premium)",
            "Soporte técnico por 365 días",
        ],
    },
    {
        "id": "acceso_total",
        "tag": "Suscripción Individual",
        "nombre": "Acceso Total + LCI",
        "precio": "$475.00 USD",
        "periodo": "/año",
        "enfoque": "La experiencia integral individual para trabajar sin límites de tipologías ni plazas, con todo el catálogo paramétrico y el contexto regional de México habilitado.",
        "url": "https://buy.stripe.com/7sY7sLeVL9YO5WO9ZMgfu00",
        "cta": "Unirme a la experiencia Acceso Total",
        "beneficios": [
            "Acceso a todas las calculadoras con vigencia anual",
            "Índice de Contexto Local (LCI) habilitado para estados y ciudades de México",
            "Hasta 2 usuarios simultáneos (suscripción individual)",
            "Soporte técnico durante 365 días",
        ],
    },
    {
        "id": "corporativo",
        "tag": "Licencia Multiusuario",
        "nombre": "Corporativo",
        "precio": "$940.00 USD",
        "periodo": "/año",
        "enfoque": "Diseñado para empresas constructoras, desarrolladoras o firmas de consultoría que buscan estandarizar presupuestos y operar en equipo con respaldo anual.",
        "url": "https://buy.stripe.com/5kQ5kD7tj3Aqdpg2xkgfu01",
        "cta": "Unirme a la experiencia Corporativa",
        "beneficios": [
            "Licencia multiusuario anual para equipos y proyectos múltiples",
            "Cobertura corporativa para operación empresarial y consultoría",
            "Acompañamiento y soporte técnico durante 365 días",
        ],
    },
]

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

# Inicialización centralizada y temprana del estado de sesión
if "session_token" not in st.session_state:
    st.session_state.session_token = str(uuid.uuid4())

if "usuario_autenticado" not in st.session_state:
    st.session_state.usuario_autenticado = None

if "modo_demo" not in st.session_state:
    st.session_state.modo_demo = False

if "calculadora_activa" not in st.session_state:
    st.session_state.calculadora_activa = "📊 Selecciona una calculadora..."

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

def limpiar_estado_demo():
    for k in ["demo_calcular", "demo_resultado"]:
        if k in st.session_state:
            del st.session_state[k]

def limpiar_estado_calculadora():
    """Limpia las variables de sesión para evitar conflictos de datos entre diferentes módulos."""
    keys_to_remove = ["calcular", "resultado_activo"]
    for k in keys_to_remove:
        if k in st.session_state:
            del st.session_state[k]

def _formatear_csi_label(opcion):
    if str(opcion).strip().upper() == "NULA (0%)":
        return "ESTÁNDAR (0%)"
    return str(opcion)

def aplicar_formato_csi_seguro():
    """Muestra 'ESTÁNDAR (0%)' en el selector de CSI mediante format_func sin alterar valores ni estados."""
    sb_orig = st.selectbox
    sb_side_orig = st.sidebar.selectbox

    def envolver(fn):
        def wrapper(label, options, *args, **kwargs):
            try:
                lbl_low = str(label).lower()
                opts_list = list(options) if options is not None else []
                es_csi = any(str(o).strip().upper() == "NULA (0%)" for o in opts_list) or (
                    "singularidad" in lbl_low or "csi" in lbl_low
                )
                if es_csi and opts_list and "format_func" not in kwargs:
                    kwargs["format_func"] = _formatear_csi_label
            except Exception:
                pass
            return fn(label, options, *args, **kwargs)
        return wrapper

    st.selectbox = envolver(sb_orig)
    st.sidebar.selectbox = envolver(sb_side_orig)
    return sb_orig, sb_side_orig

def render_listado_calculadoras_login():
    """Muestra las 12 calculadoras y el número de tipologías de cada una en el Hub principal (Login)."""
    items_html = []
    for item in CATALOGO_CALCULADORAS:
        items_html.append(
            f"<div class='catalogo-item'>"
            f"<strong>{item['icono']} {item['num']}. {item['nombre']}</strong>"
            f"<span class='catalogo-tipologias'>({item['detalle']})</span>"
            f"</div>"
        )

    col_a, col_b, col_c = st.columns(3)
    for idx, html_card in enumerate(items_html):
        target_col = [col_a, col_b, col_c][idx % 3]
        with target_col:
            st.markdown(html_card, unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="catalogo-box" style="margin-top: 8px; margin-bottom: 14px;">
            <div class="catalogo-header">
                <p class="catalogo-title">🧮 Catálogo Completo del Ecosistema</p>
                <span class="catalogo-resumen">{TOTAL_CALCULADORAS} Calculadoras · {TOTAL_TIPOLOGIAS} Tipologías en total</span>
            </div>
            <p class="catalogo-nota" style="margin: 0;">
- <strong>7 calculadoras individuales</strong> a elegir en planes Estándar y Premium.<br>
- <strong>4 calculadoras en Paquetes Dúo</strong> (Culturales, Deportivos, Escuelas y Educación, Hospitales y Salud) disponibles mediante paquete Dúo o Acceso Total / Corporativo.<br>
- <strong>1 calculadora bono</strong> (<em>Infraestructura Vial</em>, 2 tipologías) incluida gratis con cualquier suscripción.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_banner_catalogo_demo():
    """Muestra un resumen visible en la parte superior del panel principal del Demo."""
    pills_html = "".join([
        f"<div class='demo-pill'><strong>{c['icono']} {c['num']}. {c['nombre']}:</strong> {c['detalle']}</div>"
        for c in CATALOGO_CALCULADORAS
    ])
    st.markdown(
        f"""
        <div class="demo-catalogo-top">
            <div class="demo-catalogo-top-title">
                🧮 Catálogo Completo Disponible ({TOTAL_CALCULADORAS} Calculadoras · {TOTAL_TIPOLOGIAS} Tipologías)
            </div>
            <div class="demo-catalogo-pills">
                {pills_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_tarjeta_plan_apilada(plan):
    """Renderiza un paquete en formato ancho y apilado verticalmente."""
    items_html = "".join([f"<li>✅ {b}</li>" for b in plan["beneficios"]])
    with st.container(border=True):
        col_info, col_detalles = st.columns([1.15, 1.85], gap="large")
        with col_info:
            st.markdown(
                f"""
                <div class="plan-badge">{plan["tag"]}</div>
                <div class="plan-title">{plan["nombre"]}</div>
                <div class="plan-price">{plan["precio"]}<span>{plan["periodo"]}</span></div>
                <p class="plan-lead">{plan["enfoque"]}</p>
                """,
                unsafe_allow_html=True,
            )
        with col_detalles:
            st.markdown(f"<ul class='plan-list'>{items_html}</ul>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.link_button(plan["cta"], plan["url"], use_container_width=True)

def render_pasarela_desplegable_login():
    """Muestra los 5 planes apilados verticalmente dentro de un expander a ancho completo."""
    with st.expander("💎 Conoce los planes y experiencias de suscripción (Stripe)", expanded=False):
        st.caption(
            "Elige la modalidad que mejor se adapte a tu forma de presupuestar y crecer. "
            "Al seleccionar una opción irás directamente a su checkout seguro en Stripe."
        )
        for plan in PLANES_ECOSISTEMA:
            render_tarjeta_plan_apilada(plan)

def render_planes_en_sidebar_demo():
    """Descripción completa y beneficios de cada plan dentro del desplegable en la barra lateral del Demo."""
    st.sidebar.divider()
    with st.sidebar.expander("💎 Ver planes y unirme en Stripe", expanded=False):
        for plan in PLANES_ECOSISTEMA:
            precio_txt = f"{plan['precio']}{plan['periodo']}" if plan["periodo"] else plan["precio"]
            items_html = "".join([f"<li>✅ {b}</li>" for b in plan["beneficios"]])
            st.markdown(f"**{plan['nombre']}** — `{precio_txt}`")
            st.caption(plan["enfoque"])
            st.markdown(f"<ul class='demo-plan-list'>{items_html}</ul>", unsafe_allow_html=True)
            st.link_button(plan["cta"], plan["url"], use_container_width=True)
            st.markdown("---")

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
        return False, f"Tu suscripción anual venció el {fecha_venc.strftime('%Y-%m-%d')}. Renuévala para reactivar el acceso.", None

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
# VISTA DEMO GRATUITA (SIN REGISTRO PREVIO)
# -------------------------------------------------------------
if st.session_state.usuario_autenticado is None and st.session_state.modo_demo:
    ruta_demo_dir = os.path.join(ROOT_DIR, "modulos", "00Demo")
    ruta_demo_script = os.path.join(ruta_demo_dir, "app_demo.py")

    if os.path.exists(ruta_demo_script):
        render_banner_catalogo_demo()

        os.chdir(ruta_demo_dir)
        with open(ruta_demo_script, "r", encoding="utf-8") as f:
            codigo_demo = f.read()

        sb_orig, sb_side_orig = aplicar_formato_csi_seguro()
        try:
            exec(codigo_demo, {"__name__": "__main__", "__file__": ruta_demo_script})
        finally:
            st.selectbox = sb_orig
            st.sidebar.selectbox = sb_side_orig
            os.chdir(ROOT_DIR)

        render_planes_en_sidebar_demo()

        st.sidebar.markdown("<br>", unsafe_allow_html=True)
        if st.sidebar.button("⬅️ Regresar al Hub Principal (Login)", use_container_width=True, type="primary"):
            limpiar_estado_demo()
            st.session_state.modo_demo = False
            os.chdir(ROOT_DIR)
            st.rerun()
    else:
        os.chdir(ROOT_DIR)
        st.error(f"⚠️ No se encontró el archivo del Demo en: `{ruta_demo_script}`.")
        if st.button("⬅️ Regresar al Hub Principal (Login)"):
            st.session_state.modo_demo = False
            st.rerun()

    st.stop()

# -------------------------------------------------------------
# CONTROL DE INICIO DE SESIÓN OBLIGATORIO (PANTALLA DE CAPTURA)
# -------------------------------------------------------------
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
                        st.session_state.modo_demo = False
                        st.session_state.usuario_autenticado = datos_usr
                        st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='demo-btn-morado'>", unsafe_allow_html=True)
        if st.button("🧪 Explorar Demo Gratuito (Sin Registro)", use_container_width=True):
            limpiar_estado_demo()
            st.session_state.modo_demo = True
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        if avatar_b64:
            st.markdown(f"""
            <div style="display: flex; justify-content: center; margin-top: 15px;">
                <img src="data:image/png;base64,{avatar_b64}" width="130">
            </div>
            """, unsafe_allow_html=True)

        st.info("💡 ¿Aún no tienes licencia activa? Prueba el **Demo** o despliega aquí abajo las opciones de suscripción.")

    # Listado completo de las 12 calculadoras y tipologías justo antes del desplegable de suscripciones
    _, col_catalogo, _ = st.columns([0.4, 9.2, 0.4])
    with col_catalogo:
        render_listado_calculadoras_login()

    # Desplegable a ancho completo fuera de la columna central angosta
    _, col_planes, _ = st.columns([0.4, 9.2, 0.4])
    with col_planes:
        render_pasarela_desplegable_login()

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
