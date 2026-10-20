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
    """Extrae las ofertas de LinkedIn usando el DOM actual
    y mantiene compatibilidad con las tarjetas antiguas.
    """

    selector_nuevo = (
        '[role="button"]'
        '[componentkey^="job-card-component-ref-"]'
    )

    # Esperar a que LinkedIn muestre alguna tarjeta.
    try:
        page.locator(selector_nuevo).first.wait_for(
            state="attached",
            timeout=10000
        )
    except Exception:
        pass

    # Primero buscamos las tarjetas de la estructura nueva.
    tarjetas = page.locator(
        f'[data-testid="lazy-column"] {selector_nuevo}'
    )

    if tarjetas.count() == 0:
        tarjetas = page.locator(selector_nuevo)

    estructura_nueva = tarjetas.count() > 0

    # Compatibilidad con la estructura antigua.
    if not estructura_nueva:
        tarjetas = page.locator(".job-card-container")

    cantidad = tarjetas.count()
    ofertas = []
    errores = 0

    for i in range(cantidad):
        tarjeta = tarjetas.nth(i)

        try:
            if estructura_nueva:
                parrafos = tarjeta.locator("p")

                # En el HTML observado:
                # p[0] = título
                # p[1] = empresa
                # p[2] = ubicación
                if parrafos.count() < 3:
                    print(
                        f"Tarjeta {i}: solo tiene "
                        f"{parrafos.count()} párrafos",
                        flush=True
                    )
                    errores += 1
                    continue

                # El título aparece duplicado en el HTML.
                # Tomamos solo el primer span para evitarlo.
                spans = parrafos.nth(0).locator("span")

                if spans.count() > 0:
                    titulo = spans.first.inner_text(
                        timeout=3000
                    ).strip()
                else:
                    titulo = parrafos.nth(0).inner_text(
                        timeout=3000
                    ).strip()

                empresa = parrafos.nth(1).inner_text(
                    timeout=3000
                ).strip()

                ubicacion = parrafos.nth(2).inner_text(
                    timeout=3000
                ).strip()

            else:
                # Selectores de la estructura antigua.
                titulo = tarjeta.locator(
                    ".job-card-list__title"
                ).inner_text(timeout=3000).strip()

                empresa = tarjeta.locator(
                    ".artdeco-entity-lockup__subtitle"
                ).inner_text(timeout=3000).strip()

                ubicacion = tarjeta.locator(
                    ".job-card-container__metadata-item"
                ).first.inner_text(timeout=3000).strip()

            if not titulo:
                errores += 1
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
                f"Error al extraer la tarjeta {i}: {error}",
                flush=True
            )

    print(
        f"Tarjetas detectadas: {cantidad}",
        flush=True
    )
    print(
        f"Ofertas extraídas: {len(ofertas)}",
        flush=True
    )
    print(
        f"Tarjetas omitidas: {errores}",
        flush=True
    )

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