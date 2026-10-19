def click_text_button(page, text):
    elemento = page.get_by_text(text, exact=True).first

    try:
        elemento.wait_for(state="visible", timeout=11000)
        elemento.click(timeout=11000)
        print(f"Texto pulsado: {text}", flush=True)
        return True

    except Exception as error:
        print(f"No se pudo pulsar '{text}': {error}", flush=True)
        return False