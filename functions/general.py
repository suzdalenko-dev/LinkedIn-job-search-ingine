import time

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
    """Extrae las ofertas visibles del listado de LinkedIn."""

    tarjetas = page.locator(".job-card-container")
    ofertas = []

    for i in range(tarjetas.count()):
        tarjeta = tarjetas.nth(i)

        try:
            titulo = tarjeta.locator(
                ".job-card-list__title"
            ).inner_text(timeout=2000).strip()

            empresa = tarjeta.locator(
                ".artdeco-entity-lockup__subtitle"
            ).inner_text(timeout=2000).strip()

            ubicacion = tarjeta.locator(
                ".job-card-container__metadata-item"
            ).first.inner_text(timeout=2000).strip()

            ofertas.append({
                "indice": i,
                "titulo": titulo,
                "empresa": empresa,
                "ubicacion": ubicacion,
            })

        except Exception:
            # Ignorar tarjetas incompletas o con estructura distinta.
            continue

    print(f"Ofertas extraídas: {len(ofertas)}", flush=True)
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