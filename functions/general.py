import time

from winotify import Notification

def click_text_button(page, text):
    elemento = page.get_by_text(text, exact=True).first

    try:
        elemento.wait_for(state="visible", timeout=11000)
        elemento.click(timeout=11000)
        print(f"Texto pulsado: {text}", flush=True)
        time.sleep(1)
        return True

    except Exception as error:
        print(f"No se pudo pulsar '{text}': {error}", flush=True)
        return False



def log(text, page):
    print(f"Resultado del clic: {text}", flush=True)
    print(f"URL final: {page.url}", flush=True)






def extraer_ofertas(page):
    """Extrae ofertas de LinkedIn con dos métodos:
    1. Leer los párrafos de la tarjeta.
    2. Como alternativa, leer el texto completo visible.
    """

    selector_nuevo = (
        '[role="button"]'
        '[componentkey^="job-card-component-ref-"]'
    )

    # Esperar a que aparezcan las tarjetas.
    try:
        page.locator(selector_nuevo).first.wait_for(
            state="attached",
            timeout=10000
        )
    except Exception:
        pass

    # Intentar primero la estructura actual.
    tarjetas = page.locator(
        f'[data-testid="lazy-column"] {selector_nuevo}'
    )

    if tarjetas.count() == 0:
        tarjetas = page.locator(selector_nuevo)

    estructura_nueva = tarjetas.count() > 0

    # Si no encontramos tarjetas con la estructura nueva,
    # probar la estructura antigua.
    if not estructura_nueva:
        tarjetas = page.locator(".job-card-container")

    cantidad = tarjetas.count()
    ofertas = []
    errores = 0

    for i in range(cantidad):
        tarjeta = tarjetas.nth(i)

        try:
            titulo = ""
            empresa = ""
            ubicacion = ""
            textos_p = []

            # Leer el texto completo para poder diagnosticar
            # tarjetas con estructuras HTML diferentes.
            texto_tarjeta = tarjeta.inner_text(timeout=5000)

            lineas = [
                linea.strip()
                for linea in texto_tarjeta.splitlines()
                if linea.strip()
            ]

            if estructura_nueva:
                parrafos = tarjeta.locator("p")
                textos_p = [
                    texto.strip()
                    for texto in parrafos.all_inner_texts()
                    if texto.strip()
                ]

                # Método principal: usar los párrafos.
                if len(textos_p) >= 3:
                    spans = parrafos.nth(0).locator("span")

                    if spans.count() > 0:
                        titulo = spans.first.inner_text(
                            timeout=3000
                        ).strip()

                    if not titulo:
                        titulo = textos_p[0]

                    empresa = textos_p[1]
                    ubicacion = textos_p[2]

            else:
                # Método para la estructura antigua.
                try:
                    titulo = tarjeta.locator(
                        ".job-card-list__title"
                    ).inner_text(timeout=3000).strip()
                except Exception:
                    pass

                try:
                    empresa = tarjeta.locator(
                        ".artdeco-entity-lockup__subtitle"
                    ).inner_text(timeout=3000).strip()
                except Exception:
                    pass

                try:
                    ubicacion = tarjeta.locator(
                        ".job-card-container__metadata-item"
                    ).first.inner_text(timeout=3000).strip()
                except Exception:
                    pass

            # Método alternativo si falta algún dato.
            if not titulo or not empresa or not ubicacion:
                print(
                    f"[DIAGNÓSTICO {i}] "
                    f"P encontrados: {len(textos_p)}",
                    flush=True
                )

                if len(lineas) >= 3:
                    titulo = titulo or lineas[0]
                    empresa = empresa or lineas[1]
                    ubicacion = ubicacion or lineas[2]

                    print(
                        f"[ALTERNATIVA {i}] "
                        f"Se intenta recuperar la tarjeta usando "
                        f"el texto visible: {lineas[:6]!r}",
                        flush=True
                    )

            # Una tarjeta solo se acepta si tiene título.
            if not titulo:
                errores += 1
                print(
                    f"[OMITIDA {i}] No se pudo extraer el título. "
                    f"P={len(textos_p)}, "
                    f"líneas={lineas[:8]!r}",
                    flush=True
                )
                continue

            ofertas.append({
                "indice": i,
                "titulo": titulo,
                "empresa": empresa,
                "ubicacion": ubicacion,
            })

        except Exception as error:
            errores += 1

            print(
                f"[ERROR TARJETA {i}] {type(error).__name__}: "
                f"{error}",
                flush=True
            )

    print(f"Tarjetas detectadas: {cantidad}", flush=True)
    print(f"Ofertas extraídas: {len(ofertas)}", flush=True)
    print(f"Tarjetas omitidas: {errores}", flush=True)

    return ofertas




def seleccionar_oferta(page, titulo):
    tarjeta = page.locator(".job-card-container").filter(
        has=page.locator(".job-card-list__title").get_by_text(
            titulo, exact=True
        )
    ).first

    try:
        tarjeta.wait_for(state="visible", timeout=10000)
        tarjeta.click(timeout=10000)
        page.wait_for_timeout(1500)

        print(f"Oferta seleccionada: {titulo}", flush=True)
        return True

    except Exception as error:
        print(f"No se pudo seleccionar la oferta: {error}", flush=True)
        return False



def notificar(titulo, mensaje):
    aviso = Notification(
        app_id="Job Search Engine",
        title=titulo,
        msg=mensaje,
        duration="short"
    )
    aviso.show()