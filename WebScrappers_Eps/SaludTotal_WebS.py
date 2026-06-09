from playwright.sync_api import sync_playwright
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv(Path(__file__).parent / ".env")

# Credenciales Portal SALUD TOTAL
DOCUMENT_NUMBER = os.getenv("SALUD_TOTAL_USERNAME")
PASSWORD = os.getenv("SALUD_TOTAL_PASSWORD")

URL = "https://www.saludtotal.com.co"  # reemplazar por URL del portal de autorizaciones


def consultar_autorizaciones(
    patient_doc: str,
    meses_atras: int = 2,
    headless: bool = True,
    slow_mo: int = 300,
) -> list[dict[str, str]]:
    """Consulta las autorizaciones de un paciente en el portal de Salud Total.

    Args:
        patient_doc: Número de identificación del paciente.
        meses_atras: Cuántos meses hacia atrás usar como fecha inicial de búsqueda.
        headless: Ejecutar Chromium sin interfaz (True en producción).

    Returns:
        Lista de autorizaciones; cada elemento es un dict con las claves
        "num_autorizacion" e "id_servicio".
    """
    if not DOCUMENT_NUMBER or not PASSWORD:
        raise RuntimeError(
            "Faltan SALUD_TOTAL_USERNAME / SALUD_TOTAL_PASSWORD en el archivo .env"
        )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, slow_mo=slow_mo)
        context = browser.new_context()
        page = context.new_page()
        try:
            page.goto(URL)
            page.locator("#username").fill(DOCUMENT_NUMBER)
            page.locator("#password").fill(PASSWORD)
            page.get_by_role("button", name="Ingresar").click()
            page.pause()
            return []

        finally:
            context.close()
            browser.close()


def validar_autorizacion(
    patient_doc: str,
    id_servicio: str,
    num_autorizacion: str,
    meses_atras: int = 2,
    headless: bool = True,
) -> dict:
    """Valida que exista una autorización del paciente con `num_autorizacion` e
    `id_servicio` coincidentes en la misma fila.

    Returns:
        dict con:
          - valid (bool): True si se encontró coincidencia en ambos campos.
          - match (dict | None): la fila coincidente, o None si no hubo match.
          - total_consultadas (int): cuántas autorizaciones se revisaron.
    """
    autorizaciones = consultar_autorizaciones(
        patient_doc=patient_doc,
        meses_atras=meses_atras,
        headless=headless,
    )

    num_autorizacion_norm = num_autorizacion.strip()
    id_servicio_norm = id_servicio.strip()

    match = next(
        (
            a
            for a in autorizaciones
            if a["num_autorizacion"] == num_autorizacion_norm
            and a["id_servicio"] == id_servicio_norm
        ),
        None,
    )

    return {
        "valid": match is not None,
        "match": match,
        "total_consultadas": len(autorizaciones),
    }


if __name__ == "__main__":
    autorizaciones = consultar_autorizaciones(patient_doc="", meses_atras=2, headless=False, slow_mo=300)
    print(autorizaciones)
