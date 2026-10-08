

from conexion import obtener_conexion_db
from datetime import datetime

def sembrar_datos_demo():
    db = obtener_conexion_db()
    if db is None:
        print("❌ No se pudo establecer conexión con MongoDB.")
        return

    # 1. Colección: camiones
    camiones = [
        {"camion_id": "CAM-101", "placa": "789-ABC", "empresa": "Transportes Toluca", "autorizacion": True, "certificacion_conductor": True},
        {"camion_id": "CAM-102", "placa": "456-DEF", "empresa": "Logística del Valle", "autorizacion": True, "certificacion_conductor": False},
        {"camion_id": "CAM-103", "placa": "123-GHI", "empresa": "Fletes Exprés", "autorizacion": False, "certificacion_conductor": True},
        {"camion_id": "CAM-104", "placa": "999-XYZ", "empresa": "Químicos Totoltepec", "autorizacion": True, "certificacion_conductor": True}
    ]
    db.camiones.delete_many({})
    db.camiones.insert_many(camiones)
    print("✅ Colección 'camiones' poblada.")

    # 2. Colección: accesos
    accesos = [
        {
            "camion_id": "CAM-101",
            "placa": "789-ABC",
            "P": True, "Q": False, "R": False, "S": True, "V": True, "H": True,
            "resultado_A": True, "resultado_E": False,
            "explicacion": "Cumple con todos los parámetros normativos estándar.",
            "timestamp": datetime.now().isoformat(),
            "operador": "Hans González"
        },
        {
            "camion_id": "CAM-102",
            "placa": "456-DEF",
            "P": True, "Q": True, "R": True, "S": False, "V": True, "H": True,
            "resultado_A": False, "resultado_E": True,
            "explicacion": "Inspección especial requerida: Exceso de peso (Q) y Carga Peligrosa (R). Certificación vencida (S).",
            "timestamp": datetime.now().isoformat(),
            "operador": "Héctor"
        }
    ]
    db.accesos.delete_many({})
    db.accesos.insert_many(accesos)
    print("✅ Colección 'accesos' poblada.")

    # 3. Colección: incidentes
    incidentes = [
        {
            "correo_original": "URGENTE: El camión CAM-102 llegó con fugas menores en los tanques secundarios. Placa 456-DEF.",
            "clasificacion": {"categoria": "Seguridad/Derrame", "prioridad": "ALTA"},
            "datos_extraidos": {"camion_id": "CAM-102", "placa": "456-DEF", "reportado_por": "Guardia Puerta 2"},
            "estado": "en_atencion",
            "requiere_revision_humana": True,
            "fecha": datetime.now().isoformat()
        }
    ]
    db.incidentes.delete_many({})
    db.incidentes.insert_many(incidentes)
    print("✅ Colección 'incidentes' poblada.")

    # 4. Colección: riesgos_eticos
    riesgos = [
        {
            "modulo": "Clasificador Híbrido LLM",
            "descripcion": "Alucinación en la extracción de placas o severidad del reporte en correos mal redactados.",
            "categoria": "Alucinación / Confiabilidad",
            "probabilidad": 3,
            "impacto": 4,
            "puntaje_inicial": 12,
            "mitigacion": "Validación con Pydantic y reintento estricto con respaldo en motor de reglas.",
            "probabilidad_residual": 1,
            "impacto_residual": 2,
            "puntaje_residual": 2,
            "historico": [{"fecha": datetime.now().isoformat(), "cambio": "Creación inicial de riesgo"}]
        },
        {
            "modulo": "Asistente LLM (RAG)",
            "descripcion": "Uso abusivo de automatización u omisión de la verificación del operador humano.",
            "categoria": "Dependencia Tecnológica",
            "probabilidad": 4,
            "impacto": 4,
            "puntaje_inicial": 16,
            "mitigacion": "Marcado obligatorio de 'requiere_revision_humana' en discrepancias.",
            "probabilidad_residual": 2,
            "impacto_residual": 2,
            "puntaje_residual": 4,
            "historico": [{"fecha": datetime.now().isoformat(), "cambio": "Creación inicial de riesgo"}]
        }
    ]
    db.riesgos_eticos.delete_many({})
    db.riesgos_eticos.insert_many(riesgos)
    print("✅ Colección 'riesgos_eticos' poblada.")

    print("\n🎉 ¡Base de datos poblada exitosamente con datos de demostración!")

if __name__ == "__main__":
    sembrar_datos_demo()