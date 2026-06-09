from playwright.sync_api import sync_playwright
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from pathlib import Path
import os

# Cargar .env que está junto a este script, sin depender del cwd
load_dotenv(Path(__file__).parent / ".env")

# Credenciales Portal COMPENSAR
USER = os.getenv("COMPENSAR_USERNAME")
PASSWORD = os.getenv("COMPENSAR_PASSWORD")

URL = "https://elyon.compensarsalud.com/login"


def consultar_autorizaciones(
    patient_doc: str,
    meses_atras: int = 2,
    headless: bool = True,
    slow_mo: int = 300,
) -> list[dict[str, str]]:
    """Consulta las autorizaciones de un paciente en el portal de COMPENSAR.

    Args:
        patient_doc: Número de identificación del paciente.
        meses_atras: Cuántos meses hacia atrás usar como fecha inicial de búsqueda.
        headless: Ejecutar Chromium sin interfaz (True en producción).

    Returns:
        Lista de autorizaciones; cada elemento es un dict con las claves
        "num_autorizacion" e "id_servicio".
    """
    if not USER or not PASSWORD:
        raise RuntimeError(
            "Faltan COMPENSAR_USERNAME / COMPENSAR_PASSWORD en el archivo .env"
        )

    # Fechas de búsqueda
    fecha_actual = datetime.now()
    fecha_inicial = fecha_actual - relativedelta(months=meses_atras)
    fecha_inicial_str = fecha_inicial.strftime("%Y/%m/%d")
    fecha_final_str = fecha_actual.strftime("%Y/%m/%d")

    """Locators de selección de tipo documento (en el formulario de búsqueda de autorizaciones):
    page.get_by_role("option", name="AS ADULTO SIN IDENTIFICAR").click()
    page.locator(".ui-icon.ui-icon-triangle-1-s").first.click()
    page.get_by_role("option", name="CC CEDULA CIUDADANIA").click()
    page.locator(".ui-icon.ui-icon-triangle-1-s").first.click()
    page.get_by_role("option", name="CD CARNÉ DIPLOMÁTICO").click()
    page.locator(".ui-icon.ui-icon-triangle-1-s").first.click()
    page.get_by_role("option", name="CE CEDULA EXTRANJERIA").click()
    page.locator(".ui-icon.ui-icon-triangle-1-s").first.click()
    page.get_by_role("option", name="CN CERTIFICADO DE NACIDO VIVO").click()
    page.locator(".ui-icon.ui-icon-triangle-1-s").first.click()
    page.get_by_role("option", name="MS MENOR SIN IDENTIFICAR").click()
    page.locator(".ui-icon.ui-icon-triangle-1-s").first.click()
    page.get_by_role("option", name="NI NIT").click()
    page.locator(".ui-icon.ui-icon-triangle-1-s").first.click()
    page.get_by_role("option", name="NU NUIP").click()
    page.locator(".ui-icon.ui-icon-triangle-1-s").first.click()
    page.get_by_role("option", name="PA PASAPORTE").click()
    page.locator(".ui-icon.ui-icon-triangle-1-s").first.click()
    page.get_by_role("option", name="PE PERMANENCIA ESPECIAL").click()
    page.locator(".ui-icon.ui-icon-triangle-1-s").first.click()
    page.get_by_role("option", name="PT PERMISO PROTECCION TEMPORAL").click()
    page.locator(".ui-icon.ui-icon-triangle-1-s").first.click()
    page.get_by_role("option", name="RC REGISTRO CIVIL").click()
    page.locator(".ui-icon.ui-icon-triangle-1-s").first.click()
    page.get_by_role("option", name="SC SALVOCONDUCTO").click()
    page.locator(".ui-selectonemenu-trigger").first.click()
    page.get_by_role("option", name="TI TARJETA IDENTIDAD").click()
    """

    

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, slow_mo=slow_mo)
        context = browser.new_context()
        page = context.new_page()
        try:
            page.goto(URL)
            #page.get_by_role("button", name="Close").click()
            #LOGIN
            #page.get_by_role("textbox", name="Usuario").click()
            page.get_by_role("textbox", name="Usuario").fill(USER)
            #page.get_by_role("textbox", name="Contraseña").click()
            page.get_by_role("textbox", name="Contraseña").fill(PASSWORD)
            page.get_by_role("button", name="Iniciar Sesión").click()
            #Navegacion modal autorizaciones
            #page.pause()
            page.get_by_role("link", name=" Autorizaciones").click()
            page.get_by_role("link", name=" Consultas").click()

            ##Llenar formulario de busqueda
            
            #Seleccion tipo documento
            page.locator(".ui-icon.ui-icon-triangle-1-s").first.click()
            page.get_by_role("option", name="CC CEDULA CIUDADANIA").click()
            
            #Llenar numero documento
            page.locator("[id=\"id_main:txtNumeroDocumento\"]").fill(patient_doc)
            
            #Llenar fechas
            page.locator("[id=\"id_main:fec_iniId_input\"]").fill(fecha_inicial_str)
            page.locator("[id=\"id_main:fec_finId_input\"]").fill(fecha_final_str)

            #Seleccion tipo autorizacion
            page.get_by_role("combobox", name="--Seleccione--").click()
            page.get_by_role("option", name="Hospitalizacion").click()
            page.get_by_role("button", name=" Enviar").click()
            page.pause()


        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    patient_doc = "1053776586"

    autorizaciones = consultar_autorizaciones(patient_doc=patient_doc, meses_atras=2, headless=False, slow_mo=500)
    print(autorizaciones)