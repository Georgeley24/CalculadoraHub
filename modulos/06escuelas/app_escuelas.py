import streamlit as st
import pandas as pd
import os
import plotly.express as px

# 1. Configuración de la página web
st.set_page_config(
    page_title="Calculadora Paramétrica - Escuelas e Infraestructura Educativa",
    page_icon="🏫",
    layout="wide"
)

# Inyección de CSS personalizado para fijar el ancho óptimo de la barra lateral y diseño de versión
st.markdown("""
<style>
    /* Fijar un ancho profesional para la barra lateral */
    [data-testid="stSidebar"] {
        min-width: 350px !important;
        max-width: 380px !important;
    }
</style>
""", unsafe_allow_html=True)

# Cabecera principal con versión alineada a la derecha
col_title, col_ver = st.columns([4, 1])

with col_title:
    st.title("🏫 Calculadora Paramétrica de Costos: Escuelas e Infraestructura Educativa")

with col_ver:
    st.markdown("""
    <div style="text-align: right; padding-top: 15px;">
        <span style="background-color: #1e3a8a; color: #ffffff; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.95rem; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
            v2.1
        </span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("Herramienta interactiva para la estimación de costos basada en modelos paramétricos oficiales para edificación escolar e instalaciones educativas.")

# 2. Cargar datos del Excel oficial de Escuelas
EXCEL_PATH = "calculadora_costos_escuelas_LCI.xlsx"

@st.cache_data
def cargar_datos(path):
    if not os.path.exists(path):
        return None, None, None
    df_calc = pd.read_excel(path, sheet_name='Calculadora')
    df_datos = pd.read_excel(path, sheet_name='Datos')
    df_lci = pd.read_excel(path, sheet_name='LCI')
    return df_calc, df_datos, df_lci

df_calc, df_datos, df_lci = cargar_datos(EXCEL_PATH)

if df_datos is None:
    st.error(f"⚠️ No se encontró el archivo '{EXCEL_PATH}' en la ruta actual: {os.getcwd()}. Asegúrate de que esté en la carpeta '06escuelas'.")
    st.stop()

# -------------------------------------------------------------
# 3. BARRA LATERAL (Panel de Control e Inputs)
# -------------------------------------------------------------

# 01. Logo Georgeley elegante, centrado y con tamaño discreto (ancho reducido)
if os.path.exists("00. Logo Georgeley.png"):
    col_l1, col_l2, col_l3 = st.sidebar.columns([1, 4, 1])
    with col_l2:
        st.image("00. Logo Georgeley.png", width=190)
else:
    st.sidebar.markdown("### 🏢 **GEORGELEY**")

# 02. Globo de diálogo estilo cómic adaptable (Responsive CSS puro)
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
        Soy <b>Georgeley</b>, tu asistente de costos personal. Platícame sobre el proyecto escolar o educativo que deseas parametrizar.
    </p>
    <!-- Punta del bocadillo de diálogo -->
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
    <div style="
        position: absolute;
        bottom: -18px;
        left: 50%;
        transform: translateX(-50%);
        width: 0;
        height: 0;
        border-left: 12px solid transparent;
        border-right: 12px solid transparent;
        border-top: 15px solid #111118;
        z-index: -1;
    "></div>
</div>
""", unsafe_allow_html=True)

# Avatar debajo del globo de texto
if os.path.exists("Georgeley AV09.png"):
    col_av1, col_av2, col_av3 = st.sidebar.columns([1, 2, 1])
    with col_av2:
        st.image("Georgeley AV09.png", use_container_width=True)

st.sidebar.divider()

st.sidebar.header("⚙️ Parámetros del Proyecto")

# Control de estado de sesión para el cálculo y los resultados congelados
if "calcular" not in st.session_state:
    st.session_state.calcular = False

if "resultado_activo" not in st.session_state:
    st.session_state.resultado_activo = None

# Input 1: Tipología de escuelas
lista_tipologias = ["-- Selecciona una tipología --"] + df_datos['Tipología / Modelo Comercial'].tolist()
tipologia_sel = st.sidebar.selectbox("1. Selecciona la Tipología / Modelo:", lista_tipologias, index=0)

# Manejo de valores si hay o no tipología seleccionada
if tipologia_sel != "-- Selecciona una tipología --":
    row_modelo = df_datos[df_datos['Tipología / Modelo Comercial'] == tipologia_sel].iloc[0]
    unidad_base = str(row_modelo['Unidad'])
    descripcion_base = str(row_modelo['Descripción General Orientativa'])
    area_sugerida = float(row_modelo['Area_Base_M2'])
    st.sidebar.info(f"💡 **Descripción:** {descripcion_base}")
else:
    unidad_base = "M2"
    descripcion_base = ""
    area_sugerida = 0.00

# Textos de ayuda (Tooltips) exactos con las opciones reales de CSI
HELP_SUPERFICIE = "Coloca el tamaño aproximado de la superficie principal de tu proyecto educativo según la unidad de medida indicada (m², etc.). Este valor multiplicará el costo paramétrico unitario ajustado para obtener el presupuesto global estimado."

HELP_LCI = "El Índice de Contexto Local (LCI) es un factor regional que ajusta el costo base de edificación de acuerdo con las condiciones económicas, logísticas, de mano de obra y de costos de materiales específicos de cada ciudad o región de la República Mexicana, garantizando la congruencia del presupuesto frente a las realidades del mercado local."

HELP_CSI = """El Índice de Singularidad Constructiva (CSI) pondera las variaciones de complejidad técnica y de diseño del proyecto sobre el estándar paramétrico:
- BAJA (-5%): Para proyectos escolares con simplificaciones constructivas o especificaciones económicas.
- NULA (0%): Para planteles o módulos escolares convencionales con especificaciones estándar.
- ALTA (+10%): Para instituciones con particularidades complejas (laboratorios avanzados de alta tecnología, auditorios especializados, sistemas de climatización central o instalaciones estructurales singulares)."""

# Input 2: Superficie del proyecto (con Tooltip)
superficie = st.sidebar.number_input(
    "2. Superficie del proyecto:", 
    min_value=0.0, 
    value=area_sugerida, 
    step=50.0, 
    help=HELP_SUPERFICIE
)

# Input 3: Unidad de Medida
st.sidebar.markdown("**3. Unidad de Medida:**")
st.sidebar.text_input("Unidad de Medida", value=unidad_base, disabled=True, label_visibility="collapsed")

# Input 4: Índice LCI (Ubicación / Región) - Predeterminado en CDMX (con Tooltip)
lista_ciudades = df_lci['Ciudad_Estado'].tolist()
idx_cdmx = 0
for idx, ciudad in enumerate(lista_ciudades):
    if "Ciudad de México" in str(ciudad) or "CDMX" in str(ciudad):
        idx_cdmx = idx
        break

ciudad_sel = st.sidebar.selectbox(
    "4. Índice LCI (Ubicación / Región):", 
    lista_ciudades, 
    index=idx_cdmx, 
    help=HELP_LCI
)

# Input 5: Índice de Singularidad Constructiva (CSI) corregido estrictamente a BAJA, NULA y ALTA
variable_sel = st.sidebar.selectbox(
    "5. Índice de Singularidad Constructiva (CSI):", 
    ["BAJA (-5%)", "NULA (0%)", "ALTA (+10%)"], 
    index=1, # Predeterminado en NULA (0%)
    help=HELP_CSI
)

factores_var = {
    "BAJA (-5%)": 0.95,
    "NULA (0%)": 1.0,
    "ALTA (+10%)": 1.10
}

st.sidebar.markdown("<br>", unsafe_allow_html=True)

# Botones de Acción en la barra lateral
col_btn1, col_btn2 = st.sidebar.columns([2, 1])

with col_btn1:
    if st.button("🚀 Generar Cálculo", type="primary", use_container_width=True):
        if tipologia_sel == "-- Selecciona una tipología --":
            st.sidebar.error("⚠️ Por favor selecciona una tipología válida.")
        else:
            st.session_state.calcular = True
            st.session_state.resultado_activo = {
                "tipologia": tipologia_sel,
                "descripcion": descripcion_base,
                "unidad": unidad_base,
                "superficie": superficie,
                "ciudad": ciudad_sel,
                "variable": variable_sel,
                "costo_m2": float(row_modelo['Costo_Unitario_Promedio']) * float(df_lci[df_lci['Ciudad_Estado'] == ciudad_sel].iloc[0]['LCI_Factor']) * factores_var[variable_sel],
                "costo_total": (float(row_modelo['Costo_Unitario_Promedio']) * float(df_lci[df_lci['Ciudad_Estado'] == ciudad_sel].iloc[0]['LCI_Factor']) * factores_var[variable_sel]) * superficie,
                "row_modelo": row_modelo.copy()
            }

with col_btn2:
    if st.button("🔄 Limpiar", use_container_width=True):
        st.session_state.calcular = False
        st.session_state.resultado_activo = None
        st.rerun()

# -------------------------------------------------------------
# 4. MOTOR DE CÁLCULO Y DESPLIEGUE DE RESULTADOS CONGELADOS
# -------------------------------------------------------------
if st.session_state.calcular and st.session_state.resultado_activo is not None:
    res = st.session_state.resultado_activo

    # Referencia de análisis para capturas de pantalla
    st.markdown(f"### 📌 Análisis Activo: **{res['tipologia']}**")
    st.markdown(f"> *{res['descripcion']}*")
    st.markdown("---")

    # 5. MOSTRAR RESULTADOS EN PANTALLA PRINCIPAL
    col1, col2 = st.columns(2)

    with col1:
        st.metric(label=f"💵 Paramétrico por {res['unidad']} (Ajustado)", value=f"${res['costo_m2']:,.2f} MXN")

    with col2:
        st.metric(label="💰 Presupuesto Total Estimado", value=f"${res['costo_total']:,.2f} MXN")

    st.divider()

    # 6. DESGLOSE POR ESPECIALIDADES (Partidas)
    st.subheader("📊 Desglose Estimado por Especialidades (Partidas)")

    partidas_cols = df_datos.columns[8:]

    desglose = []
    for col_pct in partidas_cols:
        pct = float(res['row_modelo'][col_pct])
        if pct > 0:
            # Limpieza del nombre eliminando prefijos "Pct_" o "Pct "
            nombre_limpio = str(col_pct).replace("Pct_", "").replace("Pct ", "").replace("_", " ").title()
            monto = res['costo_total'] * pct
            pct_formato = f"{pct * 100:.2f}%"
            desglose.append({
                'Especialidad': nombre_limpio, 
                'Porcentaje_Num': pct * 100, 
                'Porcentaje_Str': pct_formato,
                'Monto (MXN)': monto
            })

    df_desglose = pd.DataFrame(desglose)

    # Mapeo de colores estricto manteniendo el orden exacto del DataFrame
    colors = px.colors.qualitative.Plotly
    color_map = {row['Especialidad']: colors[i % len(colors)] for i, row in df_desglose.iterrows()}

    # Dona y Simbología sincronizadas y ordenadas en sentido horario
    col_dona, col_leyenda = st.columns([1.1, 1])

    with col_dona:
        fig = px.pie(
            df_desglose, 
            values='Monto (MXN)', 
            names='Especialidad', 
            title='Distribución Presupuestal (%)',
            hole=0.4,
            color='Especialidad',
            color_discrete_map=color_map,
            custom_data=['Porcentaje_Str']
        )
        fig.update_traces(
            sort=False,
            direction='clockwise',
            textposition='inside', 
            text=df_desglose['Porcentaje_Str'],
            textinfo='text', 
            textfont_size=15,
            insidetextorientation='auto',
            hovertemplate='<b>%{label}</b><br>Monto: $%{value:,.2f} MXN<br>Porcentaje: %{customdata[0]}<extra></extra>'
        )
        fig.update_layout(
            height=380, 
            margin=dict(t=40, b=10, l=10, r=10),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_leyenda:
        st.markdown("##### 🎨 Simbología de Especialidades")
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        
        for idx, row in df_desglose.iterrows():
            esp = row['Especialidad']
            color_hex = color_map[esp]
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <div style="width: 14px; height: 14px; background-color: {color_hex}; border-radius: 3px; margin-right: 12px; flex-shrink: 0;"></div>
                    <span style="font-size: 0.95rem; font-weight: 500; color: #F8FAFC;">{esp}</span>
                </div>
                """, 
                unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # Tabla detallada completa
    st.markdown("##### 📑 Tabla Detallada de Costos por Especialidad")
    df_tabla_view = df_desglose[['Especialidad', 'Porcentaje_Str', 'Monto (MXN)']].copy()
    df_tabla_view.columns = ['Especialidad', 'Porcentaje', 'Monto (MXN)']
    df_tabla_view['Monto (MXN)'] = df_tabla_view['Monto (MXN)'].map("${:,.2f}".format)
    st.dataframe(df_tabla_view, hide_index=True, use_container_width=True)

    st.divider()

    # 7. CRÉDITOS, MENSAJE DE MENTORÍA, REFERENCIAS Y DISCLAIMER
    st.warning("""
    ⚠️ **Descargo de Responsabilidad:**  
    Esta herramienta fue desarrollada con fines de parametrización en proyectos escolares y educativos. Los valores e índices presentados no deben utilizarse como única fuente para la integración de presupuestos ejecutivos, propuestas económicas o licitaciones reales. Se recomienda realizar siempre un Análisis de Precios Unitarios (APU) detallado y ajustado a las especificaciones particulares de cada proyecto.
    """)

    st.info("""
    🚀 **Un mensaje de colega a colega**  
    **¡Muchas felicidades por dar el salto hacia la parametrización de costos educativos!** Estar aquí significa que buscas ir más allá de los métodos tradicionales y entender cómo la tecnología y los datos transforman nuestra labor en la construcción. No te detengas aquí: dominar los números, las bases de datos y la ingeniería de costos es lo que diferencia a los profesionales que lideran proyectos exitosos. Sigue capacitándote, analizando el mercado y perfeccionando tus APUs. ¡El siguiente nivel de la industria lo construimos quienes nos atrevemos a innovar!
    """)

    st.subheader("📚 Referencias Bibliográficas (APA 7)")
    st.markdown("""
    * BIMSA Reports, S.A. de C.V. (2022). *Análisis de costos de materiales para construcción (Valuador)* (Ed. 52, 3era. actualización 2022). BIMSA Reports, S.A. de C.V.
    * Cámara Mexicana de la Industria de la Construcción. (2022). *Catálogo de costos directos de vivienda 2023* (Actualización 2022). Centro Nacional de Ingeniería de Costos (CEICO).
    * Suárez Salazar, C. (2002). *Costo y tiempo en edificación* (3.ª ed.). Editorial Limusa.
    """)

    st.markdown("""
    ---
    *Información recopilada, estructurada y programada por el **M.G.P. Arq. Jorge A. López Kúk (Georgeley)**.*  
    > *"No es teoría, es lo que funciona en campo."*
    """)
else:
    st.info("👈 **Selecciona una tipología escolar, revisa tus parámetros en la barra lateral y presiona '🚀 Generar Cálculo' para desplegar los resultados.**")