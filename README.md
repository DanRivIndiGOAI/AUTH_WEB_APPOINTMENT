# Auth Web Appointment

API para la validación automática de autorizaciones médicas en portales de EPS colombianas. Combina extracción de datos desde PDFs (OCR) con scraping de portales web, y expone todo como un servicio HTTP accesible públicamente vía ngrok.

---

## Cómo funciona el flujo completo

```
PDF de autorización (papel escaneado)
          ↓
  pdf_Auth_extraction.py   ←  OCR con EasyOCR + PyMuPDF
  extrae: num_autorizacion, CUPS
          ↓
  GET /capital-salud/validar-autorizacion?...   ←  FastAPI local
          ↓
  CapitalSalud_WebS.py   ←  Playwright abre Chromium headless
  navega el portal de la EPS y consulta las autorizaciones del paciente
          ↓
  Respuesta JSON: { valid, match, total_consultadas }
```

El API corre localmente y se expone al exterior mediante un túnel ngrok, lo que permite que sistemas externos (HIS, agendador de citas, etc.) lo consuman sin necesidad de un servidor en la nube.

---

## OCR — `pdf_Auth_extraction.py`

Script independiente que procesa el PDF físico de una autorización médica.

**Librerías usadas:**
- `PyMuPDF (fitz)` — abre el PDF y renderiza cada página como imagen a 200 DPI
- `EasyOCR` — lee el texto de la imagen (modelos en español e inglés)
- `re` — expresiones regulares para extraer campos específicos

**Qué extrae de la página 1:**

| Campo | Patrón buscado |
|---|---|
| `N° Autorización` | `N° Autorización: XXXXXXXXX` |
| `CUPS` | Código entre corchetes `[XXXXXX]` |

**Para las páginas siguientes** imprime el texto completo extraído, útil para revisar el contenido de cada hoja de la autorización.

**Uso:**
```bash
# Colocar el PDF como Autorizaciones.pdf en la raíz del proyecto
uv run pdf_Auth_extraction.py
```

> Los datos extraídos (num_autorizacion y CUPS) son los que se pasan como parámetros al endpoint del API.

---

## Web Scrapers — `WebScrappers_Eps/`

Cada scraper usa **Playwright con Chromium** para automatizar la navegación en el portal web de la EPS, como si fuera un operario ingresando manualmente.

### Estado por EPS

| EPS | Archivo | Estado | Integrado al API |
|---|---|---|---|
| Capital Salud | `CapitalSalud_WebS.py` | ✅ Funcional y completo | ✅ Sí |
| Nueva EPS | `NuevaEPS_WebS.py` | 🔧 En desarrollo | ❌ No |
| Colsanitas | `Colsanitas_WebS.py` | 🔧 En desarrollo | ❌ No |
| Salud Total | `SaludTotal_WebS.py` | 🔧 En desarrollo | ❌ No |

### Capital Salud — flujo del scraper

1. Login en el portal con credenciales de la IPS
2. Busca al paciente por número de documento (CC)
3. Abre "Ver Servicios Autorizados"
4. Filtra por rango de fechas (configurable, por defecto 2 meses atrás)
5. Extrae la tabla de autorizaciones: `num_autorizacion` + `id_servicio` (CUPS)
6. Compara contra los valores recibidos y retorna si hay coincidencia

Las credenciales se cargan desde `WebScrappers_Eps/.env` y nunca se hardcodean en el código.

---

## API — `api/main.py`

Servicio FastAPI que expone la validación de Capital Salud como endpoint HTTP.

### Endpoints

#### `GET /health`
Verifica que el servicio esté corriendo.

```json
{ "status": "ok" }
```

#### `GET /capital-salud/validar-autorizacion`

Valida que exista una autorización activa para el paciente con el número de autorización y CUPS indicados.

**Parámetros (query string):**

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| `patient_doc` | string | ✅ | Número de documento del paciente |
| `id_servicio` | string | ✅ | Código CUPS del servicio |
| `num_autorizacion` | string | ✅ | Número de autorización a validar |
| `meses_atras` | int | No (default: 2) | Rango de búsqueda hacia atrás |
| `headless` | bool | No (default: true) | Modo sin interfaz del navegador |

**Respuesta exitosa:**
```json
{
  "patient_doc": "3098587",
  "num_autorizacion": "261031560358938",
  "id_servicio": "890226",
  "valid": true,
  "match": {
    "num_autorizacion": "261031560358938",
    "id_servicio": "890226"
  },
  "total_consultadas": 5
}
```

**Códigos de error:**
- `500` — Credenciales faltantes en `.env`
- `502` — Error al consultar el portal de la EPS

---

## Disponibilidad pública — ngrok

El API corre localmente con uvicorn. Para exponerlo a sistemas externos se usa **ngrok**, que crea un túnel HTTPS hacia el puerto local.

```
Sistema externo  →  https://xxxx.ngrok-free.app  →  localhost:8000  →  FastAPI
```

### Levantar el servicio

**1. Iniciar el API:**
```bash
uv run uvicorn api.main:app --reload --port 8000
```

**2. En otra terminal, abrir el túnel ngrok:**
```bash
ngrok http 8000
```

ngrok mostrará una URL pública tipo `https://xxxx.ngrok-free.app`. Esa es la URL que se comparte con los sistemas que necesiten consumir el API.

**Ejemplo de llamada desde la URL pública:**
```
GET https://xxxx.ngrok-free.app/capital-salud/validar-autorizacion?patient_doc=3098587&id_servicio=890226&num_autorizacion=261031560358938
```

> **Nota:** La URL de ngrok cambia cada vez que se reinicia el túnel (en el plan gratuito). Para una URL fija se puede usar un dominio estático de ngrok o desplegar el API en un servidor.

---

## Configuración

### Variables de entorno — `WebScrappers_Eps/.env`

```env
CAPITAL_SALUD_USERNAME=<nit_o_usuario_ips>
CAPITAL_SALUD_PASSWORD=<contraseña>

NUEVA_EPS_DOCUMENT_TYPE=<tipo_doc>
NUEVA_EPS_USERNAME=<usuario>
NUEVA_EPS_PASSWORD=<contraseña>

COLSANITAS_USERNAME=<usuario>
COLSANITAS_PASSWORD=<contraseña>

SALUD_TOTAL_USERNAME=<usuario>
SALUD_TOTAL_PASSWORD=<contraseña>
```

### Instalación de dependencias

```bash
# Instalar dependencias con uv
uv sync

# Instalar navegador Chromium para Playwright
uv run playwright install chromium
```

---

## Estructura del proyecto

```
Auth_web_appointment/
├── api/
│   └── main.py                  # FastAPI — endpoints HTTP
├── WebScrappers_Eps/
│   ├── CapitalSalud_WebS.py     # Scraper Capital Salud (funcional)
│   ├── NuevaEPS_WebS.py         # Scraper Nueva EPS (en desarrollo)
│   ├── Colsanitas_WebS.py       # Scraper Colsanitas (en desarrollo)
│   ├── SaludTotal_WebS.py       # Scraper Salud Total (en desarrollo)
│   └── .env                     # Credenciales (no versionar)
├── pdf_Auth_extraction.py       # OCR standalone para PDFs de autorizaciones
├── Autorizaciones.pdf           # PDF de prueba (no versionar)
├── pyproject.toml
└── Dockerfile
```
