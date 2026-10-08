# ============================================================
# ASISTENTE RAG (Recuperación Aumentada por Generación)
# ============================================================

import ollama
import numpy as np

MODELO_CHAT = "llama3.2"
MODELO_EMBED = "nomic-embed-text"

# 1. Base de Conocimiento Simulada (Manual de Normatividad)
MANUAL_LOGISTICA = [
    "NORMA 01: Todo camión que transporte materiales peligrosos debe ingresar exclusivamente entre las 22:00 y las 05:00 horas.",
    "NORMA 02: El límite máximo de peso para camiones de doble remolque en patios internos es de 75.5 toneladas.",
    "NORMA 03: Los operadores con certificación vencida no podrán operar montacargas ni acceder a zonas de carga crítica.",
    "NORMA 04: En caso de derrame de materiales peligrosos, se debe aislar el área 50 metros a la redonda y notificar a la brigada de emergencias (Prioridad CRITICA).",
    "NORMA 05: Los camiones sin autorización previa (P=False) serán retenidos en la aduana de acceso principal hasta validación del supervisor."
]

# 2. Generar Embeddings en Memoria
# Nota: En producción esto se guarda en MongoDB o ChromaDB. Aquí lo hacemos al vuelo para la práctica.
embeddings_db = []

def inicializar_conocimiento():
    """Convierte las reglas del manual en vectores matemáticos usando Ollama."""
    print(" Vectorizando manual de normatividad...")
    for texto in MANUAL_LOGISTICA:
        respuesta = ollama.embeddings(model=MODELO_EMBED, prompt=texto)
        vector = respuesta["embedding"]
        embeddings_db.append({"texto": texto, "vector": vector})
    print(" Conocimiento cargado y vectorizado.")

def calcular_similitud(vec1, vec2):
    """Calcula la Similitud del Coseno entre dos vectores."""
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def buscar_contexto(pregunta, top_k=2):
    """Busca los fragmentos del manual más relevantes para la pregunta del usuario."""
    if not embeddings_db:
        inicializar_conocimiento()
        
    respuesta_pregunta = ollama.embeddings(model=MODELO_EMBED, prompt=pregunta)
    vector_pregunta = respuesta_pregunta["embedding"]
    
    # Puntuar cada documento en la base de datos
    resultados = []
    for doc in embeddings_db:
        score = calcular_similitud(vector_pregunta, doc["vector"])
        resultados.append((score, doc["texto"]))
    
    # Ordenar de mayor a menor similitud y tomar los mejores (top_k)
    resultados.sort(key=lambda x: x[0], reverse=True)
    mejores_contextos = [res[1] for res in resultados[:top_k]]
    
    return mejores_contextos

def consultar_rag(pregunta):
    """Responde a la pregunta usando contexto recuperado (RAG)."""
    # 1. Recuperar contexto relevante
    contexto_recuperado = buscar_contexto(pregunta)
    texto_contexto = "\n".join(f"- {c}" for c in contexto_recuperado)
    
    # 2. Armar el Prompt Aumentado
    prompt_rag = f"""
    Eres LogiBot, un experto en normatividad logística.
    Responde a la pregunta del usuario basándote ÚNICAMENTE en el siguiente contexto normativo.
    Si la respuesta no está en el contexto, indica que no tienes esa información. No inventes.

    CONTEXTO NORMATIVO ENCONTRADO:
    {texto_contexto}

    PREGUNTA DEL USUARIO:
    {pregunta}
    """
    
    # 3. Generar la respuesta final con el LLM
    respuesta = ollama.chat(
        model=MODELO_CHAT,
        messages=[{"role": "user", "content": prompt_rag}]
    )
    
    return {
        "respuesta": respuesta["message"]["content"],
        "contexto_usado": contexto_recuperado
    }

if __name__ == "__main__":
    # Prueba del sistema RAG
    print("=====================================================")
    pregunta_prueba = "¿Qué pasa si un camión con materiales peligrosos llega a las 10 de la mañana?"
    print(f"👤 Pregunta: {pregunta_prueba}\n")
    
    resultado = consultar_rag(pregunta_prueba)
    
    print("🤖 Respuesta de LogiBot (RAG):")
    print(resultado["respuesta"])
    print("\n📄 Contextos extraídos de la BD:")
    for c in resultado["contexto_usado"]:
        print(f"   * {c}")
    print("=====================================================")