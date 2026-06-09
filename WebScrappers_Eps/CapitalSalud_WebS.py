from playwright.sync_api import sync_playwright
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from pathlib import Path
import os

# Cargar .env que está junto a este script, sin depender del cwd
load_dotenv(Path(__file__).parent / ".env")

# Credenciales Portal CAPITAL SALUD
DOCUMENT_NUMBER = os.getenv("CAPITAL_SALUD_USERNAME")
PASSWORD = os.getenv("CAPITAL_SALUD_PASSWORD")

URL = "https://portal.capitalsalud.gov.co/AutorizacionWebWS/Access/Index"


def consultar_autorizaciones(
    patient_doc: str,
    meses_atras: int = 2,
    headless: bool = True,
    slow_mo: int = 300,
) -> list[dict[str, str]]:
    """Consulta las autorizaciones de un paciente en el portal de Capital Salud.

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
            "Faltan CAPITAL_SALUD_USERNAME / CAPITAL_SALUD_PASSWORD en el archivo .env"
        )

    # Fechas de búsqueda
    fecha_actual = datetime.now()
    fecha_inicial = fecha_actual - relativedelta(months=meses_atras)
    fecha_inicial_str = fecha_inicial.strftime("%Y-%m-%d")
    fecha_final_str = fecha_actual.strftime("%Y-%m-%d")

    

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, slow_mo=slow_mo)
        context = browser.new_context()
        page = context.new_page()
        try:
            page.goto(URL)

            # Login
            page.locator("#cboTiposUsuario").select_option(value="IPS")
            page.locator("#txtIdentificacion").fill(DOCUMENT_NUMBER)
            page.locator("#txtContrasena").fill(PASSWORD)
            page.get_by_role("button", name="Ingresar").click()

            page.get_by_role("link", name="Aceptar").click()
            page.get_by_title("Continuar").click()

            # Búsqueda del paciente
            # Nota: el portal deja "CC" seleccionado por defecto en el combo de
            # Tipo de Identificación, así que no es necesario forzarlo aquí.
            page.get_by_role("textbox", name="* Número de Identificación:").fill(patient_doc)
            page.get_by_title("Buscar", exact=True).click()

            # Validación: esperamos a que aparezca el botón "Ver Servicios Autorizados".
            # Si no aparece en tiempo razonable, el paciente no fue encontrado.
            btn_ver_servicios = page.get_by_role("button", name="Ver Servicios Autorizados")
            try:
                btn_ver_servicios.wait_for(timeout=10000)
            except Exception:
                raise ValueError(
                    f"Usuario no encontrado para el documento '{patient_doc}'"
                )

            btn_ver_servicios.click()

            # Rango de fechas y búsqueda
            page.get_by_role("textbox", name="Fecha Inicial:").fill(fecha_inicial_str)
            page.get_by_role("textbox", name="Fecha Final:").fill(fecha_final_str)
            page.get_by_title("Buscar Autorizaciones").click()

            # Esperar a que la grilla cargue. Si no aparece ninguna celda,
            # no se encontraron autorizaciones en el rango de fechas.
            page.wait_for_load_state("networkidle")
            celda_grilla = page.locator(
                'td[aria-describedby="gridAutorizaciones_NumAutorizacion"]'
            ).first
            try:
                celda_grilla.wait_for(timeout=15000)
            except Exception:
                return []  # sin autorizaciones en el rango de fechas

            nums_autorizacion = page.locator(
                'td[aria-describedby="gridAutorizaciones_NumAutorizacion"]'
            ).all_inner_texts()
            ids_servicio = page.locator(
                'td[aria-describedby="gridAutorizaciones_IdServicio"]'
            ).all_inner_texts()

            autorizaciones = [
                {"num_autorizacion": num.strip(), "id_servicio": sid.strip()}
                for num, sid in zip(nums_autorizacion, ids_servicio)
                if num.strip() or sid.strip()
            ]

            return autorizaciones
        finally:
            ##if not headless:
            ##    page.pause()  # inspección visual solo en modo no-headless
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
    # Prueba manual (no-headless para inspección visual)
    Patient_Doc = "3098587"
    Id_Servicio = "890226"           # <- reemplazar por un CUPS real para probar
    Num_Autorizacion = "261031560358939"      # <- reemplazar por un número real para probar

    resultado = validar_autorizacion(
        patient_doc=Patient_Doc,
        id_servicio=Id_Servicio,
        num_autorizacion=Num_Autorizacion,
        headless=False,
    )

    print(f"valid: {resultado['valid']}")
    print(f"match: {resultado['match']}")
    print(f"total consultadas: {resultado['total_consultadas']}")
