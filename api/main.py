from fastapi import FastAPI, HTTPException, Query

from WebScrappers_Eps.CapitalSalud_WebS import validar_autorizacion

app = FastAPI(title="Auth Web Appointment API", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/capital-salud/validar-autorizacion")
def validar_autorizacion_capital_salud(
    patient_doc: str = Query(..., min_length=4, description="Número de documento del paciente"),
    id_servicio: str = Query(..., description="ID de servicio / número CUPS a validar"),
    num_autorizacion: str = Query(..., description="Número de autorización a validar"),
    meses_atras: int = Query(2, ge=1, le=12, description="Meses hacia atrás para la búsqueda"),
    headless: bool = Query(True, description="Ejecutar el navegador en modo headless"),
):
    """Valida que exista una autorización del paciente en Capital Salud cuyo
    `num_autorizacion` e `id_servicio` coincidan exactamente con los enviados.
    """
    try:
        resultado = validar_autorizacion(
            patient_doc=patient_doc,
            id_servicio=id_servicio,
            num_autorizacion=num_autorizacion,
            meses_atras=meses_atras,
            headless=headless,
        )
    except RuntimeError as e:
        # Errores de configuración (credenciales faltantes, etc.)
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        # Cualquier error del portal o del scraping
        raise HTTPException(status_code=502, detail=f"Error consultando el portal: {e}")

    return {
        "patient_doc": patient_doc,
        "num_autorizacion": num_autorizacion.strip(),
        "id_servicio": id_servicio.strip(),
        **resultado,
    }
