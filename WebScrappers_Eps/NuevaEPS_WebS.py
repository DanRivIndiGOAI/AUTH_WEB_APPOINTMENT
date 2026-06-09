from playwright.sync_api import sync_playwright
from dateutil.relativedelta import relativedelta
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# Credenciales Portal Nueva eps
DOCUMENT_TYPE = os.getenv("NUEVA_EPS_DOCUMENT_TYPE")
DOCUMENT_NUMBER = os.getenv("NUEVA_EPS_USERNAME")
PASSWORD = os.getenv("NUEVA_EPS_PASSWORD")

URL = "https://portal.nuevaeps.com.co/Portal/home.jspx"

def consultar_autorizaciones(
    patient_doc: str,
    meses_atras: int = 2,
    headless: bool = True,
    slow_mo: int = 300,
) -> list[dict[str, str]]:
    """Consulta las autorizaciones de un paciente en el portal de Nueva EPS.

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
            "Faltan NUEVA_EPS_USERNAME / NUEVA_EPS_PASSWORD en el archivo .env"
        )

    # Fechas de búsqueda
    fecha_actual = datetime.now()
    fecha_inicial = fecha_actual - relativedelta(months=meses_atras)
    fecha_inicial_str = fecha_inicial.strftime("%Y-%m-%d")
    fecha_final_str = fecha_actual.strftime("%Y-%m-%d")

    

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled"
            ]
        )

        context = browser.new_context()

        page = context.new_page()

        #page.add_init_script("""
        #Object.defineProperty(navigator, 'webdriver', {
        #    get: () => undefined
        #});
        #""")
    
        page.goto(URL)
    
        page.locator("#loginForm\\:tipoId").select_option(DOCUMENT_TYPE)
    
        page.locator("input.iceInpTxt.fondoCampo").fill(DOCUMENT_NUMBER)
    
        page.locator("input.iceInpSecrt.fondoCampo").fill(PASSWORD)


        #Encontrar boton login y hacer click usando JavaScript para evitar posibles bloqueos por detección de automatización
        page.evaluate("""
        () => {
            const btn = document.getElementById('loginForm:loginButton');
            if(btn) btn.click();
        }
        """)
        
        login_btn = page.locator('[id="loginForm:loginButton"]')

        login_btn.highlight()
        login_btn.evaluate("el => el.outerHTML")

        #Modal servicios
        page.locator("#tabServicios").click()
        #Modal Ips
        page.locator("a[href*='selectMenu.jspx']").filter(has_text="IPS").click()

        page.pause()
        ##Toca arreglar desde aca abajo porque la pag usa un tipo especifico de estados que bloquea automatizaciones
        #Refactorizar segun boton de ingreso por estados de pagina

        page.locator("#j_id121\\:ips").select_option("4;899999123;212")

        page.locator("#j_id121\\:sucIps").select_option("4;899999123;212;899999123;1")

        page.locator("#j_id121\\:acceptButton").click()

        page.locator("div.handPointer").filter(has_text="Autorizaciones").click()

        page.locator("div.handPointer").filter(has_text="Reportes").click()
        
        page.locator("a[href*='selectOption.jspx']").filter(has_text="- Autorizaciones por Afiliado").click()
        
        page.wait_for_load_state("networkidle")

        page.locator("#ifAuto").content_frame.get_by_role("textbox", name="Seleccione un dato").click()

        page.locator("#ifAuto").content_frame.get_by_text("CC", exact=True).click()

        page.locator("#ifAuto").content_frame.get_by_role("textbox", name="Identificación").fill("51712875")

        page.locator("#ifAuto").content_frame.locator("#fechaInicial").click()

        today = datetime.now().day

        if today < 10:
            page.locator("#ifAuto").content_frame.get_by_role("button", name="Mes anterior").click()

            page.locator("#ifAuto").content_frame.get_by_role("button", name="1", exact=True).click()

            page.locator("#ifAuto").content_frame.locator("#fechaFinal").click()

            page.locator("#ifAuto").content_frame.get_by_role("button", name=str(today), exact=True).click()

        else:
            page.locator("#ifAuto").content_frame.get_by_role("button", name="1", exact=True).click()

            page.locator("#ifAuto").content_frame.locator("#fechaFinal").click()

            page.locator("#ifAuto").content_frame.get_by_role("button", name=str(today), exact=True).click()

        page.locator("#ifAuto").content_frame.get_by_role("button", name="Aceptar").click()

        page.pause()


if __name__ == "__main__":
    autorizaciones = consultar_autorizaciones(patient_doc="51712875", meses_atras=2, headless=False, slow_mo=300)
    print(autorizaciones)