# ============================================================
# MOTOR DE REGLAS LÓGICAS AMPLIADO - LOGISMART
# ============================================================

def evaluar_camion(P, Q, R, S, V=True, H=True):
    """
    Evalúa un camión utilizando lógica proposicional ampliada.

    Variables base:
    P = autorización previa
    Q = peso excedido
    R = materiales peligrosos
    S = certificación vigente
    
    Nuevas variables añadidas (Requerimiento 2.2):
    V = vigencia de licencia/documentación del conductor (True = Vigente, False = Vencida)
    H = horario permitido para circular (True = Permitido, False = Restringido/Nocturno)

    Reglas:
    A = P ∧ S ∧ ¬Q ∧ V             (Acceso estándar condicionado a vigencia)
    E = P ∧ (R ∨ Q ∨ ¬H)           (Inspección especial por peligroso, peso o mal horario)
    """

    # --------------------------------------------------------
    # REGLA 1 (Modificada con vigencia V)
    # A = P AND S AND NOT Q AND V
    # --------------------------------------------------------
    acceso_estandar = P and S and not Q and V

    # --------------------------------------------------------
    # REGLA 2 (Modificada con restricción de horario H si trae R)
    # E = P AND (R OR Q OR NOT H)
    # --------------------------------------------------------
    inspeccion_especial = P and (R or Q or not H)

    # --------------------------------------------------------
    # Generamos la respuesta detallada con explicación paso a paso
    # --------------------------------------------------------
    explicacion = []
    if not P:
        explicacion.append("Denegado: Falta autorización previa (P).")
    if Q:
        explicacion.append("Alerta: El vehículo excede el límite de peso permitido (Q).")
    if R:
        explicacion.append("Aviso: Transporta materiales peligrosos (R), requiere inspección.")
    if not S:
        explicacion.append("Alerta: La certificación del camión no está vigente (S).")
    if not V:
        explicacion.append("Alerta: La documentación del operador se encuentra vencida (V).")
    if not H:
        explicacion.append("Alerta: Circula fuera del horario autorizado para su tipo de carga (H).")

    if not explicacion:
        explicacion.append("Vehículo cumple con todos los parámetros normativos estándar.")

    resultado = {
        "autorizacion": P,
        "peso_excedido": Q,
        "carga_peligrosa": R,
        "certificacion": S,
        "vigencia_conductor": V,
        "horario_permitido": H,
        "acceso_estandar": acceso_estandar,
        "inspeccion_especial": inspeccion_especial,
        "explicacion_paso_a_paso": explicacion
    }

    return resultado

if __name__ == "__main__":
    resultado = evaluar_camion(
        P=True,
        Q=False,
        R=True,
        S=True,
        V=True,
        H=False
    )

    print("\n========== RESULTADO DE EVALUACIÓN DE CAMIÓN ==========")
    for clave, valor in resultado.items():
        print(f"{clave}: {valor}")