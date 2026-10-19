def click_text_button(page, text):
    boton = page.get_by_text(text, exact=True).first
    boton.wait_for(state="visible", timeout=15000)
    boton.click()
    print("Pulsado «Mostrar todo». Esperando a que carguen las ofertas...", flush=True)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(2000)
    print(f"URL actual: {page.url}", flush=True)