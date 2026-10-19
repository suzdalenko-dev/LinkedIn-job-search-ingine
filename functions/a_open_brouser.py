
from pathlib import Path
from playwright.sync_api import sync_playwright


def open_brouser():
    print("Iniciando Playwright...", flush=True)

    perfil = Path(__file__).with_name("perfil_linkedin")

    with sync_playwright() as p:
        print("Abriendo Chromium...", flush=True)

        context = p.chromium.launch_persistent_context(
            user_data_dir=str(perfil),
            headless=False,
            viewport={"width": 1111, "height": 900},
        )

        try:
            page = (
                context.pages[0]
                if context.pages
                else context.new_page()
            )

            print("Navegador abierto.", flush=True)
            print("Entrando en LinkedIn Jobs...", flush=True)

            page.goto(
                "https://www.linkedin.com/jobs/",
                wait_until="domcontentloaded",
                timeout=60000,
            )

            

            print("Página cargada.", flush=True)
            print(f"URL: {page.url}", flush=True)
            print(f"Título: {page.title()}", flush=True)

            return page


        finally:
            print("Cerrando navegador...", flush=True)
            # context.close()

