from fastapi import FastAPI, HTTPException, Query

from WebScrappers_Eps.CapitalSalud_WebS import validar_autorizacion as validar_capital_salud
from WebScrappers_Eps.Compensar_WebS import validar_autorizacion as validar_compensar
from WebScrappers_Eps.NuevaEPS_WebS import validar_autorizacion as validar_nueva_eps
from WebScrappers_Eps.Colsanitas_WebS import validar_autorizacion as validar_colsanitas
from WebScrappers_Eps.SaludTotal_WebS import validar_autorizacion as validar_salud_total

app = FastAPI(title="Auth Web Appointment API", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok"}


def _run_validacion(fn, patient_doc, id_servicio, num_autorizacion, meses_atras, headless):
    """Ejecuta la función de validación y normaliza errores para la API."""
    try:
        resultado = fn(
            patient_doc=patient_doc,
            id_servicio=id_servicio,
            num_autorizacion=num_autorizacion,
            meses_atras=meses_atras,
            headless=headless,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error consultando el portal: {e}")

    return {
        "patient_doc": patient_doc,
        "num_autorizacion": num_autorizacion.strip(),
        "id_servicio": id_servicio.strip(),
        **resultado,
    }


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
    return _run_validacion(validar_capital_salud, patient_doc, id_servicio, num_autorizacion, meses_atras, headless)


@app.get("/compensar/validar-autorizacion")
def validar_autorizacion_compensar(
    patient_doc: str = Query(..., min_length=4, description="Número de documento del paciente"),
    id_servicio: str = Query(..., description="ID de servicio / número CUPS a validar"),
    num_autorizacion: str = Query(..., description="Número de autorización a validar"),
    meses_atras: int = Query(2, ge=1, le=12, description="Meses hacia atrás para la búsqueda"),
    headless: bool = Query(True, description="Ejecutar el navegador en modo headless"),
):
    """Valida que exista una autorización del paciente en Compensar cuyo
    `num_autorizacion` e `id_servicio` coincidan exactamente con los enviados.
    """
    return _run_validacion(validar_compensar, patient_doc, id_servicio, num_autorizacion, meses_atras, headless)


@app.get("/nueva-eps/validar-autorizacion")
def validar_autorizacion_nueva_eps(
    patient_doc: str = Query(..., min_length=4, description="Número de documento del paciente"),
    id_servicio: str = Query(..., description="ID de servicio / número CUPS a validar"),
    num_autorizacion: str = Query(..., description="Número de autorización a validar"),
    meses_atras: int = Query(2, ge=1, le=12, description="Meses hacia atrás para la búsqueda"),
    headless: bool = Query(True, description="Ejecutar el navegador en modo headless"),
):
    """Valida que exista una autorización del paciente en Nueva EPS cuyo
    `num_autorizacion` e `id_servicio` coincidan exactamente con los enviados.
    """
    return _run_validacion(validar_nueva_eps, patient_doc, id_servicio, num_autorizacion, meses_atras, headless)


@app.get("/colsanitas/validar-autorizacion")
def validar_autorizacion_colsanitas(
    patient_doc: str = Query(..., min_length=4, description="Número de documento del paciente"),
    id_servicio: str = Query(..., description="ID de servicio / número CUPS a validar"),
    num_autorizacion: str = Query(..., description="Número de autorización a validar"),
    meses_atras: int = Query(2, ge=1, le=12, description="Meses hacia atrás para la búsqueda"),
    headless: bool = Query(True, description="Ejecutar el navegador en modo headless"),
):
    """Valida que exista una autorización del paciente en Colsanitas cuyo
    `num_autorizacion` e `id_servicio` coincidan exactamente con los enviados.
    """
    return _run_validacion(validar_colsanitas, patient_doc, id_servicio, num_autorizacion, meses_atras, headless)


@app.get("/salud-total/validar-autorizacion")
def validar_autorizacion_salud_total(
    patient_doc: str = Query(..., min_length=4, description="Número de documento del paciente"),
    id_servicio: str = Query(..., description="ID de servicio / número CUPS a validar"),
    num_autorizacion: str = Query(..., description="Número de autorización a validar"),
    meses_atras: int = Query(2, ge=1, le=12, description="Meses hacia atrás para la búsqueda"),
    headless: bool = Query(True, description="Ejecutar el navegador en modo headless"),
):
    """Valida que exista una autorización del paciente en Salud Total cuyo
    `num_autorizacion` e `id_servicio` coincidan exactamente con los enviados.
    """
    return _run_validacion(validar_salud_total, patient_doc, id_servicio, num_autorizacion, meses_atras, headless)
