# ============================================================
# LOGISMART PYTHON SUITE
# PROYECTO INTEGRADOR (CLI + DASHBOARD STREAMLIT)
# ============================================================

import sys
import streamlit as st
import pandas as pd
from datetime import datetime
import itertools

# ------------------------------------------------------------
# IMPORTACIONES ORIGINALES DEL PROFESOR
# ------------------------------------------------------------
from peas import AgenteLogiSmart
from logica import evaluar_camion
from incidentes import (
    clasificar_incidente,
    enviar_correo_soporte
)
from riesgos import EvaluadorRiesgosIA

# ------------------------------------------------------------
# IMPORTACIONES DE NUESTROS MÓDULOS (LLM, RAG, MONGODB)
# ------------------------------------------------------------
from conexion import obtener_conexion_db
from clasificador import clasificador_hibrido
from rag import consultar_rag

# ============================================================
# 1. DASHBOARD GRÁFICO CON STREAMLIT (LO QUE HICIMOS)
# ============================================================
def render_dashboard():
    # CONFIGURACIÓN DE PÁGINA
    st.set_page_config(page_title="LogiSmart Pro", page_icon="🏭", layout="wide")

    # --------------------------------------------------------
    # INYECCIÓN DE CSS PARA CAMBIAR COLORES
    # --------------------------------------------------------
    st.markdown("""
        <style>
        /* Cambiar el color de fondo de toda la aplicación a un tono oscuro profesional */
        .stApp {
            background-color: #0E1117; 
        }
        
        /* Cambiar el color del texto principal a blanco */
        html, body, [class*="css"] {
            color: #FAFAFA; 
        }

        /* Cambiar el color de los botones primarios a naranja LogiSmart */
        .stButton>button[data-baseweb="button"] {
            background-color: #F39C12 !important; 
            color: white !important;
            border-radius: 6px !important; 
            border: none !important;
        }

        /* Cambiar el fondo del panel de pestañas */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #262730;
            border-radius: 8px;
            padding: 5px;
        }
        </style>
        """, unsafe_allow_html=True)
    # --------------------------------------------------------

    st.title("🏭 Plataforma Integral LogiSmart")
    st.caption("Sistema Híbrido de Seguridad y Control Logístico (LLM + Reglas)")

    # CONEXIÓN A BD
    db = obtener_conexion_db()
    if db is None:
        st.error("❌ No se pudo conectar a MongoDB Atlas. Revisa tu archivo conexion.py")
        return

    # CREAR PESTAÑAS (TABS)
    tab_chat, tab_clasificador, tab_simulador, tab_motor, tab_datos = st.tabs([
        "💬 Asistente RAG", 
        "📧 Clasificador de Correos", 
        "🧮 Simulador Lógico",
        "🚛 Motor de Accesos", 
        "📊 Base de Datos y Riesgos"
    ])

    # PESTAÑA 1: ASISTENTE RAG
    with tab_chat:
        st.header("💬 Asistente de Normatividad (RAG)")
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if "contexto" in msg and msg["contexto"]:
                    with st.expander("Ver documentos consultados"):
                        for c in msg["contexto"]:
                            st.write(f"- {c}")
        pregunta = st.chat_input("Ej: ¿A qué hora entran los materiales peligrosos?")
        if pregunta:
            with st.chat_message("user"):
                st.markdown(pregunta)
            st.session_state.chat_history.append({"role": "user", "content": pregunta})
            with st.chat_message("assistant"):
                with st.spinner("Consultando manual normativo..."):
                    resultado_rag = consultar_rag(pregunta)
                    st.markdown(resultado_rag["respuesta"])
                    with st.expander("Ver documentos consultados"):
                        for c in resultado_rag["contexto_usado"]:
                            st.write(f"- {c}")
            st.session_state.chat_history.append({
                "role": "assistant", "content": resultado_rag["respuesta"], "contexto": resultado_rag["contexto_usado"]
            })

    # PESTAÑA 2: CLASIFICADOR DE CORREOS
    with tab_clasificador:
        st.header("📧 Clasificador de Reportes de Seguridad")
        texto_correo = st.text_area("Pega el contenido del correo aquí:", height=150)
        if st.button("Analizar y Clasificar", type="primary"):
            if texto_correo:
                with st.spinner("Ejecutando Clasificador Híbrido..."):
                    resultado, latencia = clasificador_hibrido(texto_correo)
                    st.subheader("Resultado del Análisis")
                    st.json(resultado)
                    st.caption(f"⏱️ Tiempo de procesamiento: {latencia:.2f} segundos")
                    if resultado["requiere_revision_humana"]:
                        st.warning("⚠️ Se requiere revisión humana.")
                    else:
                        st.success("✅ Análisis confiable. Proceso continuado.")
                    db.incidentes.insert_one({"correo": texto_correo, "resultado": resultado, "fecha": datetime.now().isoformat()})
                    st.toast("Incidente guardado en MongoDB")

    # ----------------------------------------------------
    # PESTAÑA 3: Simulador Lógico
    # ----------------------------------------------------
    with tab_simulador:
        st.header("Tabla de Verdad de Reglas Operativas")
        st.caption(
            "Simulación determinista de lógica proposicional $O(1)$ para la toma de"
            " decisiones en el patio."
        )

        # Leyenda opcional explicativa
        with st.expander("📌 Ver Leyenda de Proposiciones y Reglas", expanded=False):
            st.markdown("""
            - **P**: Licencia Vigente (True/False)
            - **Q**: Sobrecarga de Peso (True/False)
            - **R**: Material Peligroso / Hazmat (True/False)
            - **S**: Ingreso en Horario Habilitado (True/False)
            
            **Reglas:**
            - **Acceso (A)** = $P \land \neg Q \land S$
            - **Especial (E)** = $P \land (Q \lor R)$
            - **Hazmat Crítico (R3)** = $R \land \neg S$
            - **Bloqueo (R4)** = $Q \land R$
            """)

        # Generación automática de las 16 combinaciones de la Tabla de Verdad
        filas = []
        # Recorremos todas las combinaciones posibles de True/False para (P, Q, R, S)
        for P, Q, R, S in itertools.product([True, False], repeat=4):
            acceso = P and (not Q) and S
            especial = P and (Q or R)
            hazmat_critico = R and (not S)
            bloqueo = Q and R

            filas.append({
                "P": str(P).lower(),
                "Q": str(Q).lower(),
                "R": str(R).lower(),
                "S": str(S).lower(),
                "Acceso (A)": str(acceso).lower(),
                "Especial (E)": str(especial).lower(),
                "Hazmat Crítico (R3)": str(hazmat_critico).lower(),
                "Bloqueo (R4)": str(bloqueo).lower(),
            })

        # Convertir a DataFrame de Pandas
        df_tabla_verdad = pd.DataFrame(filas)

        # Mostrar la tabla interactiva en Streamlit
        st.dataframe(
            df_tabla_verdad,
            use_container_width=True,
            height=550,
            hide_index=True,  # Oculta el índice numérico para verse más limpio
        )


    # PESTAÑA 4: MOTOR DE REGLAS
    with tab_motor:
        st.header("🚛 Evaluación de Acceso a Patio")
        col1, col2 = st.columns(2)
        with col1:
            P = st.checkbox("P - Autorización previa", value=True)
            S = st.checkbox("S - Certificación vigente", value=True)
            V = st.checkbox("V - Licencia del operador vigente", value=True)
        with col2:
            Q = st.checkbox("Q - Excede el peso permitido", value=False)
            R = st.checkbox("R - Materiales peligrosos", value=False)
            H = st.checkbox("H - Horario permitido", value=True)
            
        if st.button("Evaluar Camión", type="primary"):
            res_logica = evaluar_camion(P, Q, R, S, V, H)
            if res_logica.get("acceso_estandar", False):
                st.success("✅ ACCESO ESTÁNDAR AUTORIZADO")
            elif res_logica.get("inspeccion_especial", False):
                st.warning("⚠️ REQUIERE INSPECCIÓN ESPECIAL")
            else:
                st.error("⛔ ACCESO DENEGADO o CONDICIONADO")
            st.json(res_logica)

    # PESTAÑA 5: BASE DE DATOS
    with tab_datos:
        st.header("📊 Tablero de Datos (MongoDB)")
        st.subheader("Historial de Riesgos Éticos")
        riesgos = list(db.riesgos_eticos.find({}, {"_id": 0}))
        if riesgos:
            st.dataframe(pd.DataFrame(riesgos), use_container_width=True)
        else:
            st.info("No hay riesgos registrados.")


# ============================================================
# 2. CÓDIGO ORIGINAL DEL PROFESOR (INTACTO)
# ============================================================
def main():
    print("\n")
    print("=" * 60)
    print("            LOGISMART PYTHON SUITE")
    print("=" * 60)

    # ========================================================
    # 1. PEAS
    # ========================================================
    agente = AgenteLogiSmart()
    agente.mostrar_peas()

    # ========================================================
    # 2. MOTOR DE REGLAS
    # ========================================================
    print("\n\n========== MOTOR DE REGLAS ==========")
    resultado = evaluar_camion(
        P=True,
        Q=False,
        R=False,
        S=True
    )
    for clave, valor in resultado.items():
        print(f"{clave}: {valor}")

    # ========================================================
    # 3. INCIDENTE
    # ========================================================
    print("\n\n========== CLASIFICACIÓN DE INCIDENTE ==========")
    incidente = clasificar_incidente(
        tipo="Control de acceso",
        descripcion="Vehículo detectado con peso excedido",
        nivel=8
    )
    print(incidente)
    enviar_correo_soporte(
        destinatario="soporte@logismart.com",
        asunto="Incidente LogiSmart",
        mensaje=incidente
    )

    # ========================================================
    # 4. EVALUACIÓN DE RIESGOS
    # ========================================================
    print("\n\n========== EVALUACIÓN DE RIESGOS ==========")
    evaluador = EvaluadorRiesgosIA()
    evaluador.registrar_riesgo(
        modulo="Cámara de detección",
        riesgo="Sesgo en condiciones nocturnas",
        categoria="Sesgo",
        impacto="Alto",
        probabilidad="Media",
        mitigacion="Realizar pruebas con diferentes condiciones de iluminación"
    )
    evaluador.registrar_riesgo(
        modulo="Sistema de vigilancia",
        riesgo="Uso inadecuado de información personal",
        categoria="Privacidad",
        impacto="Alto",
        probabilidad="Media",
        mitigacion="Aplicar controles de acceso y políticas de retención"
    )
    evaluador.mostrar_riesgos()
    evaluador.exportar_reporte("reportes/reporte_riesgos.json")

    print("\n")
    print("=" * 60)
    print("            SISTEMA FINALIZADO")
    print("=" * 60)

# ============================================================
# PUNTO DE ENTRADA
# ============================================================
if __name__ == "__main__":
    # Si se corre con el comando de Streamlit, levanta el Dashboard
    if "streamlit" in sys.modules:
        render_dashboard()
    # Si se corre en consola normal con 'python main.py', ejecuta el código del maestro
    else:
        main()