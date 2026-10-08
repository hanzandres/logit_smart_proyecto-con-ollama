# CLASIFICADOR HÍBRIDO (LLM + PYDANTIC + MOTOR DE REGLAS)

import json
import time
import ollama
from pydantic import BaseModel, Field
from typing import List, Optional
from logica import evaluar_camion

MODELO = "llama3.2"

# 1. Esquema estricto Pydantic
class EstructuraIncidente(BaseModel):
    categoria: str = Field(..., description="Categoría del incidente (ej. Acceso, Exceso Peso, Derrame, Certificación)")
    prioridad: str = Field(..., description="Nivel de prioridad: CRITICA, ALTA, MEDIA, BAJA")
    entidades: List[str] = Field(default=[], description="Menciones de camiones, placas o personal (ej. CAM-102, 456-DEF)")
    resumen: str = Field(..., description="Resumen conciso del correo en una oración")

def clasificar_con_llm(texto_correo: str):
    """
    Intenta clasificar el correo con Ollama garantizando respuesta en formato JSON.
    """
    prompt = f"""
    Analiza el siguiente correo recibido en el centro de control y extrae un JSON exacto con la siguiente estructura:
    {{
        "categoria": "Categoría lógica",
        "prioridad": "CRITICA" | "ALTA" | "MEDIA" | "BAJA",
        "entidades": ["lista", "de", "placas_o_ids"],
        "resumen": "Resumen claro de lo sucedido"
    }}

    Correo a clasificar:
    "{texto_correo}"

    Responde ÚNICAMENTE con el objeto JSON, sin texto explicativo adicional.
    """

    inicio = time.time()
    try:
        respuesta = ollama.chat(
            model=MODELO,
            messages=[{"role": "user", "content": prompt}],
            format="json"
        )
        latencia = time.time() - inicio
        contenido = respuesta["message"]["content"]
        
        # Validación Pydantic
        datos_dict = json.loads(contenido)
        valida = EstructuraIncidente(**datos_dict)
        return valida.model_dump(), latencia, True
    except Exception as e:
        latencia = time.time() - inicio
        print(f"⚠️ Fallo en clasificación LLM/Pydantic: {e}")
        return None, latencia, False

def clasificar_por_reglas(texto_correo: str):
    """
    Respaldo basado en reglas por palabras clave.
    """
    texto = texto_correo.lower()
    prioridad = "BAJA"
    categoria = "Consulta General"

    if "urgente" in texto or "fuga" in texto or "derrame" in texto or "accidente" in texto:
        prioridad = "CRITICA"
        categoria = "Seguridad / Emergencia"
    elif "exceso" in texto or "peso" in texto or "báscula" in texto:
        prioridad = "ALTA"
        categoria = "Exceso de Peso"
    elif "vencid" in texto or "certificado" in texto or "licencia" in texto:
        prioridad = "MEDIA"
        categoria = "Documentación"

    return {
        "categoria": categoria,
        "prioridad": prioridad,
        "entidades": [],
        "resumen": f"Clasificación automática por reglas: {categoria}"
    }

def clasificador_hibrido(texto_correo: str):
    """
    Fusión Híbrida: Ejecuta LLM y Reglas. Si discrepan, asigna mayor prioridad y marca revisión humana.
    """
    mapa_prioridad = {"CRITICA": 4, "ALTA": 3, "MEDIA": 2, "BAJA": 1}

    # 1. Ejecutar Reglas
    res_reglas = clasificar_por_reglas(texto_correo)

    # 2. Ejecutar LLM
    res_llm, latencia, exito_llm = clasificar_con_llm(texto_correo)

    if not exito_llm or res_llm is None:
        # Fallback a reglas
        res_reglas["modo"] = "Fallback - Solo Reglas"
        res_reglas["requiere_revision_humana"] = True
        return res_reglas, latencia

    # 3. Comparar y Fusionar
    prio_reglas = mapa_prioridad.get(res_reglas["prioridad"], 1)
    prio_llm = mapa_prioridad.get(res_llm["prioridad"], 1)

    requiere_revision = False
    prioridad_final = res_llm["prioridad"]

    if prio_reglas != prio_llm:
        requiere_revision = True
        # Asignar la mayor prioridad ante discrepancia por seguridad
        if prio_reglas > prio_llm:
            prioridad_final = res_reglas["prioridad"]

    resultado_final = {
        "categoria": res_llm["categoria"],
        "prioridad": prioridad_final,
        "entidades": res_llm["entidades"],
        "resumen": res_llm["resumen"],
        "requiere_revision_humana": requiere_revision,
        "modo": "Híbrido (LLM + Reglas)"
    }

    return resultado_final, latencia

if __name__ == "__main__":
    correo_prueba = "URGENTE: El camión CAM-102 con placa 456-DEF intentó ingresar pero trae la certificación vencida y se detectó sobrepeso."
    resultado, t = clasificador_hibrido(correo_prueba)
    print("\n========== RESULTADO CLASIFICADOR HÍBRIDO ==========")
    print(json.dumps(resultado, indent=4, ensure_ascii=False))
    print(f"Latencia: {t:.2f} segundos")