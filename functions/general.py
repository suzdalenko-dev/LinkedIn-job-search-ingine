def click_text_button(page, text):
    if page is None:
        raise ValueError("La página de Playwright es None.")

    try:
        boton = page.get_by_role("button", name=text, exact=True).first
        boton.wait_for(state="visible", timeout=10000)
        boton.click(timeout=10000)

        print(f"Botón pulsado: {text}", flush=True)
        return True

    except Exception:
        print(f"No se encontró un botón visible: {text}", flush=True)
        return False