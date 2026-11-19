import streamlit as st
import pandas as pd
import os
import plotly.express as px

EXCEL_PATH = "calculadora_costos_demo_LCI.xlsx"
LOGO_PATH = "00. Logo Georgeley.png"
AVATAR_PATH = "Georgeley AV09.png"


@st.cache_data
def cargar_datos(path):
    if not os.path.exists(path):
        return None, None, None
    df_calc = pd.read_excel(path, sheet_name="Calculadora")
    df_datos = pd.read_excel(path, sheet_name="Datos")
    df_lci = pd.read_excel(path, sheet_name="LCI")
    return df_calc, df_datos, df_lci


def render_marca_agua():
    st.markdown(
        """
        <div style="
            background-color: rgba(245, 158, 11, 0.14);
            border: 1px dashed #f59e0b;
            color: #fbbf24;
            padding: 8px 14px;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 600;
            text-align: center;
            margin-bottom: 12px;
        ">
            ⚠️ VERSIÓN DEMO — DATOS REPRESENTATIVOS DE EVALUACIÓN (NO VÁLIDO PARA PRESUPUESTOS REALES) • GEORGELEY
        </div>
        """,
        unsafe_allow_html=True,
    )


def run():
    st.set_page_config(
        page_title="Demo Calculadora Paramétrica - Vivienda",
        page_icon="🏠",
        layout="wide",
    )

    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {
                min-width: 350px !important;
                max-width: 380px !important;
            }
            .watermark-overlay {
                position: fixed;
                bottom: 14px;
                right: 18px;
                background: rgba(17, 24, 39, 0.78);
                color: rgba(251, 191, 36, 0.85);
                border: 1px solid rgba(251, 191, 36, 0.45);
                padding: 5px 10px;
                border-radius: 6px;
                font-size: 0.75rem;
                font-weight: 600;
                z-index: 999;
                pointer-events: none;
            }
        </style>
        <div class="watermark-overlay">DEMO GEORGELEY • SOLO EVALUACIÓN</div>
        """,
        unsafe_allow_html=True,
    )

    render_marca_agua()

    col_title, col_ver = st.columns([4, 1])
    with col_title:
        st.title("🏠 Demo: Calculadora Paramétrica de Costos — Vivienda")
    with col_ver:
        st.markdown(
            """
            <div style="text-align: right; padding-top: 15px;">
                <span style="background-color: #92400e; color: #ffffff; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.95rem; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                    DEMO v2.1
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.warning(
        "📌 **Aviso importante sobre el Demo:** Esta versión incluye un subconjunto limitado de tipologías y "
        "**valores representativos ajustados para fines de demostración y exploración** (no aptos para presupuestos "
        "formales ni toma de decisiones financieras). Para acceder a los datos completos, más tipologías, LCI regional "
        "y soporte, realiza tu suscripción en el Hub / comunidad."
    )

    _, df_datos, df_lci = cargar_datos(EXCEL_PATH)

    if df_datos is None or df_lci is None:
        st.error(
            f"⚠️ No se encontró el archivo '{EXCEL_PATH}' en '{os.getcwd()}'. "
            "Verifica que esté ubicado dentro de 'modulos/00Demo'."
        )
        st.stop()

    # Barra lateral
    if os.path.exists(LOGO_PATH):
        col_l1, col_l2, col_l3 = st.sidebar.columns([1, 4, 1])
        with col_l2:
            st.image(LOGO_PATH, width=190)
    else:
        st.sidebar.markdown("### 🏢 **GEORGELEY**")

    st.sidebar.markdown(
        """
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
            <p style="margin: 0 0 6px 0; font-size: 0.95rem; font-weight: 700; color: #FFFFFF;">👋 ¡Hola, bienvenido al Demo!</p>
            <p style="margin: 0; font-size: 0.85rem; line-height: 1.4; color: #F1F5F9;">
                Soy <b>Georgeley</b>. Explora cómo funciona el cálculo paramétrico con estas tipologías de muestra.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if os.path.exists(AVATAR_PATH):
        col_av1, col_av2, col_av3 = st.sidebar.columns([1, 2, 1])
        with col_av2:
            st.image(AVATAR_PATH, use_container_width=True)

    st.sidebar.divider()
    st.sidebar.header("⚙️ Parámetros del Proyecto (Demo)")

    if "demo_calcular" not in st.session_state:
        st.session_state.demo_calcular = False
    if "demo_resultado" not in st.session_state:
        st.session_state.demo_resultado = None

    lista_tipologias = ["-- Selecciona una tipología --"] + df_datos["Tipología / Modelo Comercial"].dropna().tolist()
    tipologia_sel = st.sidebar.selectbox("1. Selecciona la Tipología / Modelo:", lista_tipologias, index=0)

    if tipologia_sel != "-- Selecciona una tipología --":
        row_modelo = df_datos[df_datos["Tipología / Modelo Comercial"] == tipologia_sel].iloc[0]
        unidad_base = str(row_modelo["Unidad"])
        descripcion_base = str(row_modelo["Descripción General Orientativa"])
        area_sugerida = float(row_modelo["Area_Base_M2"])
        st.sidebar.info(f"💡 **Descripción:** {descripcion_base}")
    else:
        row_modelo = None
        unidad_base = "M2"
        descripcion_base = ""
        area_sugerida = 0.0

    HELP_SUPERFICIE = (
        "Ingresa una superficie de prueba para explorar el comportamiento del modelo paramétrico demo."
    )
    superficie = st.sidebar.number_input(
        "2. Superficie del proyecto:",
        min_value=0.0,
        value=area_sugerida,
        step=10.0,
        help=HELP_SUPERFICIE,
    )

    st.sidebar.markdown("**3. Unidad de Medida:**")
    st.sidebar.text_input("Unidad de Medida", value=unidad_base, disabled=True, label_visibility="collapsed")

    # LCI bloqueado en Ciudad de México (1.00)
    ciudad_demo = "Ciudad de México"
    factor_lci_demo = 1.0
    if "Ciudad_Estado" in df_lci.columns and not df_lci.empty:
        ciudad_demo = str(df_lci.iloc[0]["Ciudad_Estado"])
        if "LCI_Factor" in df_lci.columns:
            factor_lci_demo = float(df_lci.iloc[0]["LCI_Factor"])

    st.sidebar.markdown("**4. Índice LCI (Ubicación / Región):**")
    st.sidebar.text_input(
        "Índice LCI",
        value=f"{ciudad_demo} (Factor base: {factor_lci_demo:.2f} — Regionalización bloqueada en Demo)",
        disabled=True,
        label_visibility="collapsed",
    )

    # CSI bloqueado en NULA (0%)
    variable_demo = "NULA (0%)"
    factor_csi_demo = 1.0

    st.sidebar.markdown("**5. Índice de Singularidad Constructiva (CSI):**")
    st.sidebar.text_input(
        "Índice CSI",
        value="NULA (0%) — Opciones BAJA/ALTA disponibles en versión completa",
        disabled=True,
        label_visibility="collapsed",
    )

    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    col_btn1, col_btn2 = st.sidebar.columns([2, 1])

    with col_btn1:
        if st.button("🚀 Generar Cálculo Demo", type="primary", use_container_width=True):
            if tipologia_sel == "-- Selecciona una tipología --" or row_modelo is None:
                st.sidebar.error("⚠️ Por favor selecciona una tipología válida.")
            else:
                costo_unit_base = float(row_modelo["Costo_Unitario_Promedio"])
                costo_m2 = costo_unit_base * factor_lci_demo * factor_csi_demo
                costo_total = costo_m2 * superficie

                st.session_state.demo_calcular = True
                st.session_state.demo_resultado = {
                    "tipologia": tipologia_sel,
                    "descripcion": descripcion_base,
                    "unidad": unidad_base,
                    "superficie": superficie,
                    "ciudad": ciudad_demo,
                    "variable": variable_demo,
                    "costo_m2": costo_m2,
                    "costo_total": costo_total,
                    "row_modelo": row_modelo.copy(),
                }

    with col_btn2:
        if st.button("🔄 Limpiar", use_container_width=True):
            st.session_state.demo_calcular = False
            st.session_state.demo_resultado = None
            st.rerun()

    if st.session_state.demo_calcular and st.session_state.demo_resultado is not None:
        res = st.session_state.demo_resultado
        render_marca_agua()

        st.markdown(f"### 📌 Simulación Demo Activa: **{res['tipologia']}**")
        st.markdown(f"> *{res['descripcion']}*")
        st.caption("Valores calculados con fines demostrativos a partir de la base ajustada del Demo.")
        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            st.metric(label=f"💵 Paramétrico por {res['unidad']} (Demo)", value=f"${res['costo_m2']:,.2f} MXN")
        with col2:
            st.metric(label="💰 Estimado Total Referencial (Demo)", value=f"${res['costo_total']:,.2f} MXN")

        st.divider()
        st.subheader("📊 Desglose Referencial por Especialidades (Partidas)")

        partidas_cols = df_datos.columns[8:]
        desglose = []
        for col_pct in partidas_cols:
            pct = float(res["row_modelo"][col_pct])
            if pct > 0:
                nombre_limpio = (
                    str(col_pct).replace("Pct_", "").replace("Pct ", "").replace("_", " ").title()
                )
                monto = res["costo_total"] * pct
                pct_formato = f"{pct * 100:.2f}%"
                desglose.append(
                    {
                        "Especialidad": nombre_limpio,
                        "Porcentaje_Num": pct * 100,
                        "Porcentaje_Str": pct_formato,
                        "Monto (MXN)": monto,
                    }
                )

        if desglose:
            df_desglose = pd.DataFrame(desglose)
            colors = px.colors.qualitative.Plotly
            color_map = {row["Especialidad"]: colors[i % len(colors)] for i, row in df_desglose.iterrows()}

            col_dona, col_leyenda = st.columns([1.1, 1])
            with col_dona:
                fig = px.pie(
                    df_desglose,
                    values="Monto (MXN)",
                    names="Especialidad",
                    title="Distribución Referencial (%)",
                    hole=0.4,
                    color="Especialidad",
                    color_discrete_map=color_map,
                    custom_data=["Porcentaje_Str"],
                )
                fig.update_traces(
                    sort=False,
                    direction="clockwise",
                    textposition="inside",
                    text=df_desglose["Porcentaje_Str"],
                    textinfo="text",
                    textfont_size=15,
                    insidetextorientation="auto",
                    hovertemplate=(
                        "<b>%{label}</b><br>Monto: $%{value:,.2f} MXN<br>"
                        "Porcentaje: %{customdata[0]}<extra></extra>"
                    ),
                )
                fig.update_layout(
                    height=380,
                    margin=dict(t=40, b=10, l=10, r=10),
                    showlegend=False,
                )
                st.plotly_chart(fig, use_container_width=True)

            with col_leyenda:
                st.markdown("##### 🎨 Simbología de Especialidades")
                st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
                for _, row in df_desglose.iterrows():
                    esp = row["Especialidad"]
                    color_hex = color_map[esp]
                    st.markdown(
                        f"""
                        <div style="display: flex; align-items: center; margin-bottom: 10px;">
                            <div style="width: 14px; height: 14px; background-color: {color_hex}; border-radius: 3px; margin-right: 12px; flex-shrink: 0;"></div>
                            <span style="font-size: 0.95rem; font-weight: 500; color: #F8FAFC;">{esp}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("##### 📑 Tabla Referencial por Especialidad (Demo)")
            df_tabla_view = df_desglose[["Especialidad", "Porcentaje_Str", "Monto (MXN)"]].copy()
            df_tabla_view.columns = ["Especialidad", "Porcentaje", "Monto (MXN)"]
            df_tabla_view["Monto (MXN)"] = df_tabla_view["Monto (MXN)"].map("${:,.2f}".format)
            st.dataframe(df_tabla_view, hide_index=True, use_container_width=True)

        st.divider()
        st.warning(
            "⚠️ **Descargo de Responsabilidad (Versión Demo):** Los montos y porcentajes mostrados son "
            "exclusivamente ilustrativos/representativos para evaluar el flujo de la calculadora. No deben "
            "emplearse para presupuestos formales, concursos ni licitaciones. Adquiere una suscripción para "
            "acceder a los parámetros y análisis completos."
        )
        st.markdown(
            """
            ---
            *Información recopilada, estructurada y programada por el **M.G.P. Arq. Jorge A. López Kúk (Georgeley)**.*  
            > *"No es teoría, es lo que funciona en campo."*
            """
        )
    else:
        st.info(
            "👈 **Selecciona una tipología en la barra lateral, ajusta la superficie y presiona "
            "'🚀 Generar Cálculo Demo' para explorar la herramienta.**"
        )


if __name__ == "__main__":
    run()