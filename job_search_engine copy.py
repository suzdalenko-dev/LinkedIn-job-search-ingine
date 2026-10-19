
import os
import json
import time
import traceback
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from google import genai
from google.genai import types
from playwright.sync_api import sync_playwright
from plyer import notification


# ============================================================
# CONFIGURACIÓN
# ============================================================

MODEL = "gemini-3.8-flash"
MAX_OFFERS = 3
VIEWPORT_WIDTH = 1111
VIEWPORT_HEIGHT = 900

EXPERIENCE = """
Ingeniero de Software Industrial | OT + IT | Industria 4.0.
Desarrollo de aplicaciones industriales, OEE, KPIs y producción.
Integración PLC, OPC UA, MQTT, sockets TCP, backend y visualización.
Python, Django, PHP, Laravel, C#/.NET, Java y JavaScript/Vue.
PostgreSQL, MySQL, SQL Server, SQLite, Power BI y DAX.
Automatización de informes PDF/Excel y ERP para el sector pesquero.

IA, LLMs, OCR, NLP y procesamiento documental.
"""

# Evita repetir títulos durante esta ejecución.
ofertas_vistas = []


# ============================================================
# LOGS Y NOTIFICACIONES
# ============================================================

def log(mensaje):
    hora = datetime.now().strftime("%H:%M:%S")
    print(f"[{hora}] {mensaje}", flush=True)


def notificar(titulo, mensaje):
    log(f"NOTIFICACIÓN: {titulo} | {mensaje}")

    try:
        notification.notify(title=titulo,message=mensaje,app_name="Buscador de empleo",timeout=8,)
    except Exception as error:
        log(f"No se pudo mostrar la notificación: {error}")


def mostrar_estado(page):
    log(f"URL actual: {page.url}")

    try:
        log(f"Título de la página: {page.title()}")
    except Exception:
        pass


# ============================================================
# CAPTURAS
# ============================================================

def capturar(page, nombre):
    ruta = Path(__file__).with_name(nombre)

    log(f"Capturando pantalla: {nombre}")

    imagen = page.screenshot(
        path=str(ruta),
        full_page=False,
    )

    log(f"Captura guardada: {ruta}")
    log(f"Tamaño: {len(imagen)} bytes")

    return imagen


# ============================================================
# GEMINI: ANALIZAR LA PANTALLA
# ============================================================

def analizar_pantalla(client, imagen, tarea):
    log("Enviando captura a Gemini...")
    log(f"Modelo: {MODEL}")
    log(f"Tarea: {tarea}")
    log(f"Ofertas vistas: {ofertas_vistas}")

    prompt = f"""
Eres un asistente visual para buscar ofertas de empleo.

Experiencia del candidato:
{EXPERIENCE}

Ofertas ya abiertas:
{json.dumps(ofertas_vistas, ensure_ascii=False)}

Tarea actual:
{tarea}

La captura corresponde al viewport de {VIEWPORT_WIDTH}x{VIEWPORT_HEIGHT}.

Devuelve exclusivamente un objeto JSON con esta estructura:
{{
  "action": "click" o "done",
  "title": "texto visible del objetivo",
  "reason": "motivo breve",
  "x": 0,
  "y": 0
}}

Reglas:
- Elige ofertas relacionadas con software industrial, OT/IT,
  backend, integración, datos, programación o IA.
- No selecciones un título incluido en las ofertas ya abiertas.
- En los resultados, selecciona el título de una oferta concreta.
- En el detalle, busca Solicitud sencilla, Easy Apply o Solicitar.
- Las coordenadas deben corresponder al centro del objetivo visible.
- Usa x entre 0 y {VIEWPORT_WIDTH - 1}.
- Usa y entre 0 y {VIEWPORT_HEIGHT - 1}.
- No inventes objetivos.
- Si no hay un objetivo claro, devuelve action="done".
- No selecciones ni confirmes el botón final de envío.
"""

    inicio = time.time()

    respuesta = client.models.generate_content(
        model=MODEL,
        contents=[
            types.Part.from_bytes(
                data=imagen,
                mime_type="image/png",
            ),
            prompt,
        ],
    )

    log(f"Gemini respondió en {time.time() - inicio:.2f} segundos.")

    texto = (respuesta.text or "").strip()

    log("Respuesta original de Gemini:")
    print(texto or "(Respuesta vacía)", flush=True)

    if not texto:
        raise ValueError("Gemini devolvió una respuesta vacía.")

    if texto.startswith("```"):
        texto = "\n".join(
            linea
            for linea in texto.splitlines()
            if not linea.strip().startswith("```")
        )

    decision = json.loads(texto)

    log("Decisión interpretada:")
    print(
        json.dumps(decision, indent=2, ensure_ascii=False),
        flush=True,
    )

    return decision


# ============================================================
# CLIC VISUAL AUTOMÁTICO
# ============================================================

def clic_visual(page, decision):
    if decision.get("action") != "click":
        log("Gemini no ha identificado un objetivo.")
        return False

    x = decision.get("x")
    y = decision.get("y")
    titulo = decision.get("title", "Objetivo sin título")

    if (
        not isinstance(x, (int, float))
        or isinstance(x, bool)
        or not isinstance(y, (int, float))
        or isinstance(y, bool)
        or not (0 <= x < VIEWPORT_WIDTH)
        or not (0 <= y < VIEWPORT_HEIGHT)
    ):
        log(f"Coordenadas inválidas: x={x}, y={y}")
        return False

    log(f"Objetivo: {titulo}")
    log(f"Motivo: {decision.get('reason', '')}")
    log(f"Clic automático en ({x}, {y})")

    page.mouse.click(x, y)
    page.wait_for_timeout(1800)

    mostrar_estado(page)
    return True


# ============================================================
# ENCONTRAR BOTONES POR TEXTO
# ============================================================

def pulsar_boton_solicitud(page):
    """
    Busca primero los botones reales de LinkedIn.
    No utiliza coordenadas visuales para esta acción.
    """

    candidatos = [
        "Solicitud sencilla",
        "Easy Apply",
        "Solicitar",
        "Apply",
    ]

    for texto in candidatos:
        log(f"Buscando botón: {texto}")

        try:
            # Limitar la búsqueda a botones y enlaces.
            selectores = [
                page.get_by_role(
                    "button", name=texto, exact=False
                ),
                page.get_by_role(
                    "link", name=texto, exact=False
                ),
            ]

            for grupo in selectores:
                cantidad = grupo.count()
                log(f"Coincidencias para '{texto}': {cantidad}")

                for indice in range(cantidad):
                    elemento = grupo.nth(indice)

                    if not elemento.is_visible():
                        continue

                    if not elemento.is_enabled():
                        continue

                    # Evitar pulsar enlaces de publicidad u otros
                    # elementos si el texto no coincide claramente.
                    texto_visible = elemento.inner_text().strip()
                    log(f"Elemento visible: {texto_visible!r}")

                    log(f"Pulsando: {texto_visible}")
                    elemento.click(timeout=5000)
                    page.wait_for_timeout(1800)

                    mostrar_estado(page)
                    return True

        except Exception as error:
            log(f"No se pudo utilizar '{texto}': {error}")

    log("No se encontró un botón de solicitud compatible.")
    return False


# ============================================================
# FORMULARIO DE CANDIDATURA
# ============================================================

def buscar_dialogo(page):
    dialogo = page.get_by_role("dialog")

    if dialogo.count() > 0:
        for indice in range(dialogo.count() - 1, -1, -1):
            candidato = dialogo.nth(indice)
            try:
                if candidato.is_visible():
                    return candidato
            except Exception:
                pass

    return None


def revisar_campos(page, contenedor):
    """
    Imprime los campos que hay que completar.
    No inventa datos personales ni respuestas.
    """

    log("Analizando campos del formulario...")

    campos = contenedor.locator(
        "input:not([type='hidden']), textarea, select"
    )

    try:
        cantidad = campos.count()
        log(f"Campos encontrados: {cantidad}")
    except Exception as error:
        log(f"No se pudieron contar los campos: {error}")
        return

    for indice in range(cantidad):
        campo = campos.nth(indice)

        try:
            if not campo.is_visible():
                continue

            tipo = campo.get_attribute("type") or "text"
            nombre = (
                campo.get_attribute("name")
                or campo.get_attribute("id")
                or campo.get_attribute("aria-label")
                or "sin nombre"
            )

            valor = campo.input_value() if tipo not in (
                "file", "checkbox", "radio"
            ) else ""

            requerido = campo.get_attribute("required") is not None

            log(
                f"Campo {indice + 1}: "
                f"nombre={nombre!r}, tipo={tipo}, "
                f"requerido={requerido}, valor_actual={valor!r}"
            )

        except Exception as error:
            log(f"No se pudo inspeccionar el campo {indice}: {error}")


def desplazar_formulario(page):
    """
    Desplaza el modal de candidatura si existe.
    Si no hay modal, desplaza la página.
    """

    dialogo = buscar_dialogo(page)

    if dialogo is not None:
        log("Formulario dentro de un diálogo: desplazando el modal.")

        for paso in range(8):
            try:
                dialogo.evaluate(
                    "(el) => { el.scrollTop += 500; }"
                )
                page.wait_for_timeout(250)
                log(f"Scroll del modal {paso + 1}/8")
            except Exception as error:
                log(f"Error al desplazar el modal: {error}")
                break
    else:
        log("No se detecta un modal. Desplazando la página.")

        for paso in range(8):
            page.mouse.wheel(0, 500)
            page.wait_for_timeout(250)
            log(f"Scroll de página {paso + 1}/8")


def localizar_envio(page):
    dialogo = buscar_dialogo(page)
    contenedor = dialogo if dialogo is not None else page

    nombres = [
        "Enviar solicitud",
        "Submit application",
        "Enviar",
    ]

    for texto in nombres:
        try:
            botones = contenedor.get_by_role(
                "button",
                name=texto,
                exact=False,
            )

            for indice in range(botones.count()):
                boton = botones.nth(indice)

                if boton.is_visible() and boton.is_enabled():
                    log(f"Botón final detectado: {texto}")
                    return boton

        except Exception as error:
            log(f"Error buscando botón final '{texto}': {error}")

    log("No se ha encontrado el botón final de envío.")
    return None


def revisar_formulario(page):
    log("Esperando al formulario de candidatura...")
    page.wait_for_timeout(1500)

    dialogo = buscar_dialogo(page)
    contenedor = dialogo if dialogo is not None else page

    if dialogo is not None:
        log("Se ha detectado un formulario modal.")
    else:
        log("No se detecta un modal; revisando la página.")

    revisar_campos(page, contenedor)

    log("Desplazándose hacia la parte inferior del formulario...")
    desplazar_formulario(page)

    # Inspeccionar de nuevo después del desplazamiento.
    dialogo = buscar_dialogo(page)
    contenedor = dialogo if dialogo is not None else page

    revisar_campos(page, contenedor)

    boton = localizar_envio(page)

    if boton is not None:
        notificar(
            "Candidatura preparada",
            "Se ha encontrado el botón final. Revisa los datos.",
        )

        log(
            "IMPORTANTE: el programa NO pulsa el botón de envío. "
            "Revisa los campos y confirma la candidatura manualmente."
        )

        print(
            "\nFormulario localizado. Comprueba el CV seleccionado, "
            "las respuestas y todos los campos obligatorios. "
            "Cuando esté correcto, pulsa manualmente «Enviar solicitud» "
            "en el navegador.",
            flush=True,
        )

        input(
            "Pulsa ENTER aquí cuando hayas terminado de revisar "
            "esta candidatura..."
        )
    else:
        notificar(
            "Revisión necesaria",
            "No se ha encontrado el botón final de la candidatura.",
        )

        log(
            "Puede haber pasos adicionales, campos pendientes "
            "o un formulario externo."
        )

        input(
            "Completa o revisa el formulario en el navegador. "
            "Pulsa ENTER para continuar..."
        )


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():
    log("=" * 65)
    log("INICIO DEL BUSCADOR AUTOMÁTICO DE EMPLEO")
    log("=" * 65)

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "No se encuentra GEMINI_API_KEY en el archivo .env."
        )

    log("Clave de API cargada desde el entorno.")

    log(f"Inicializando Gemini con {MODEL}...")
    client = genai.Client(api_key=api_key)

    # Comprobar el modelo antes de abrir LinkedIn.
    log("Comprobando que Gemini puede responder...")

    prueba = client.models.generate_content(
        model=MODEL,
        contents="Responde únicamente: OK",
    )

    log(f"Respuesta de prueba: {prueba.text}")

    perfil = Path(__file__).with_name("perfil_linkedin")

    with sync_playwright() as p:
        context = None

        try:
            log(f"Abriendo Chromium con perfil: {perfil}")

            context = p.chromium.launch_persistent_context(
                user_data_dir=str(perfil),
                headless=False,
                viewport={
                    "width": VIEWPORT_WIDTH,
                    "height": VIEWPORT_HEIGHT,
                },
            )

            page = (
                context.pages[0]
                if context.pages
                else context.new_page()
            )

            log("Abriendo LinkedIn Jobs...")

            page.goto(
                "https://www.linkedin.com/jobs/",
                wait_until="domcontentloaded",
                timeout=60000,
            )

            page.wait_for_timeout(2000)
            mostrar_estado(page)

            input(
                "\nInicia sesión si hace falta y prepara los resultados "
                "de búsqueda. Pulsa ENTER para empezar..."
            )

            for numero in range(1, MAX_OFFERS + 1):
                log("")
                log("=" * 65)
                log(f"OFERTA {numero}/{MAX_OFFERS}")
                log("=" * 65)

                # 1. Capturar resultados.
                imagen = capturar(
                    page,
                    f"captura_{numero}.png",
                )

                # 2. Gemini elige una oferta.
                decision = analizar_pantalla(
                    client,
                    imagen,
                    tarea=(
                        "Estás en la lista de resultados de empleo. "
                        "Selecciona el título de una oferta relevante "
                        "que no se haya abierto anteriormente."
                    ),
                )

                if decision.get("action") != "click":
                    log("No se ha identificado una oferta adecuada.")
                    break

                titulo = decision.get(
                    "title",
                    "Oferta sin título",
                )

                # 3. Abrir la oferta automáticamente.
                if not clic_visual(page, decision):
                    log("No se ha podido abrir la oferta.")
                    break

                ofertas_vistas.append(titulo)

                notificar(
                    "Oferta seleccionada",
                    f"Oferta abierta: {titulo}",
                )

                log(f"Oferta abierta: {titulo}")

                # Esperar a que se actualice el panel de detalle.
                page.wait_for_timeout(1500)

                # 4. Buscar Solicitud sencilla / Solicitar.
                log("Buscando la opción de solicitud...")
                abierta = pulsar_boton_solicitud(page)

                if abierta:
                    # 5. Revisar campos y bajar al final.
                    revisar_formulario(page)
                else:
                    # Segundo intento: Gemini inspecciona el detalle.
                    log(
                        "No se encontró el botón por texto. "
                        "Solicitando ayuda visual a Gemini..."
                    )

                    imagen_detalle = capturar(
                        page,
                        f"detalle_{numero}.png",
                    )

                    decision_detalle = analizar_pantalla(
                        client,
                        imagen_detalle,
                        tarea=(
                            "Estás en el detalle de una oferta. "
                            "Localiza el botón Solicitud sencilla, "
                            "Easy Apply o Solicitar. No selecciones "
                            "Enviar solicitud ni otro botón final."
                        ),
                    )

                    if decision_detalle.get("action") == "click":
                        if clic_visual(page, decision_detalle):
                            revisar_formulario(page)
                    else:
                        log(
                            "No se ha identificado el botón de solicitud."
                        )

                # 6. Preparar la siguiente búsqueda.
                if numero < MAX_OFFERS:
                    log("Volviendo a los resultados de LinkedIn...")

                    page.goto(
                        "https://www.linkedin.com/jobs/",
                        wait_until="domcontentloaded",
                        timeout=60000,
                    )

                    page.wait_for_timeout(1500)

                    input(
                        "Comprueba que los resultados están visibles. "
                        "Pulsa ENTER para buscar la siguiente oferta..."
                    )

            log("")
            log("=" * 65)
            log("RESUMEN")
            log("=" * 65)

            log(f"Ofertas abiertas: {len(ofertas_vistas)}")

            for indice, titulo in enumerate(ofertas_vistas, start=1):
                log(f"{indice}. {titulo}")

            log("Proceso terminado.")

        except KeyboardInterrupt:
            log("Proceso interrumpido con Ctrl+C.")

        except Exception as error:
            log(f"ERROR GENERAL: {error}")
            traceback.print_exc()

        finally:
            if context is not None:
                log("Cerrando Chromium...")
                try:
                    context.close()
                except Exception as error:
                    log(f"Error al cerrar Chromium: {error}")

    log("Fin del programa.")


if __name__ == "__main__":
    main()
