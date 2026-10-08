
import streamlit as st
import ollama

st.set_page_config(
    page_title="Asistente LogiSmart - LLM",
    page_icon="🚛",
    layout="wide"
)

MODELO = "llama3.2"
 
PROMPT_SISTEMA = """
Eres LogiBot, un Asistente Técnico Especialista en Logística Industrial, 
Normativa de Transporte de Carga y Control de Accesos en Cedis (Centros de Distribución).

Tu función es asistir a los operadores de patio y supervisores de seguridad.

Debes:
1. Responder con un tono profesional, claro y orientado a la seguridad operativa.
2. Explicar procedimientos de revisión de transporte, peso e inspección de materiales peligrosos.
3. Brindar recomendaciones basadas en mejores prácticas de transporte multimodal.
4. Si el usuario pregunta algo ajeno a logística o seguridad industrial, orienta amablemente la conversación hacia tu área de especialidad.
5. Mantener respuestas estructuradas usando viñetas o listas numeradas cuando sea apropiado.
"""

# 3. INICIALIZACIÓN DEL HISTORIAL EN SESIÓN


if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "system", "content": PROMPT_SISTEMA}
    ]
# ------------------------------------------------------------
# 4. INTERFAZ GRÁFICA (GUI con Streamlit - Requerimiento 2)
# ------------------------------------------------------------
st.title("🚛 Asistente Virtual LogiSmart")
st.caption(f"Modelo en ejecución: **{MODELO}** | Especialidad: Logística y Seguridad Industrial")

# Barra lateral para controles
with st.sidebar:
    st.header("⚙️ Opciones del Sistema")
    st.info("Este tutor utiliza Ollama local con el modelo Llama 3.2.")
    
    # REQUERIMIENTO 3: Botón pa+++++ra generar un resumen del historial
    if st.button("📊 Generar Resumen del Historial", type="primary"):
        historial_usuario = [
            m for m in st.session_state.mensajes if m["role"] != "system"
        ]
        
        if not historial_usuario:
            st.warning("Aún no hay interacción registrada para resumir.")
        else:
            with st.spinner("Generando resumen ejecutivo..."):
                prompt_resumen = st.session_state.mensajes + [
                    {
                        "role": "user", 
                        "content": "Por favor, haz un resumen breve de los puntos clave, dudas planteadas y soluciones brindadas en nuestra conversación hasta ahora."
                    }
                ]
                try:
                    respuesta_resumen = ollama.chat(model=MODELO, messages=prompt_resumen)
                    st.subheader("📋 Resumen Ejecutivo de la Sesión")
                    st.write(respuesta_resumen["message"]["content"])
                except Exception as e:
                    st.error(f"Error al generar resumen: {e}")

    if st.button("🗑️ Limpiar Historial"):
        st.session_state.mensajes = [{"role": "system", "content": PROMPT_SISTEMA}]
        st.rerun()

# Mostrar la conversación actual en pantalla
for msg in st.session_state.mensajes:
    if msg["role"] == "system":
        continue
    avatar = "👤" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# Entrada de texto del usuario
pregunta_usuario = st.chat_input("Escribe tu consulta logística o de control de acceso...")

if pregunta_usuario:
    # 1. Mostrar mensaje del usuario
    with st.chat_message("user", avatar="👤"):
        st.markdown(pregunta_usuario)
    
    # 2. Guardar en el historial
    st.session_state.mensajes.append({"role": "user", "content": pregunta_usuario})
    
    # 3. Obtener respuesta del LLM
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Consultando a LogiBot..."):
            try:
                respuesta = ollama.chat(
                    model=MODELO,
                    messages=st.session_state.mensajes
                )
                contenido = respuesta["message"]["content"]
                st.markdown(contenido)
                
                # Guardar respuesta del asistente en el historial
                st.session_state.mensajes.append({"role": "assistant", "content": contenido})
            except Exception as e:
                st.error("❌ Error al conectar con Ollama. Asegúrate de que el servicio esté activo (`ollama serve`).")
                st.caption(f"Detalle del error: {e}")