from playwright.sync_api import sync_playwright
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# Credenciales Portal COLSANITAS
DOCUMENT_NUMBER = os.getenv("COLSANITAS_USERNAME")
PASSWORD = os.getenv("COLSANITAS_PASSWORD")
 
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=300)
    page = browser.new_page()
   
    URL = "https://portal.colsanitas.com/sso/login"
 
    page.goto(URL)

    page.locator("#username").fill(DOCUMENT_NUMBER)

    page.locator("#password").fill(PASSWORD)

    page.get_by_role("button", name="Ingresar").click()



    page.pause()
 