
from pathlib import Path


def open_brouser(p):
    print("Abriendo Chromium...", flush=True)
    context = p.chromium.launch_persistent_context(
        user_data_dir=str("functions/perfil_linkedin"),
        headless=False,
        viewport={"width": 1111, "height": 900},
    )

    page = context.pages[0] if context.pages else context.new_page()

    print("Abriendo LinkedIn Jobs...", flush=True)

    page.goto(
        "https://www.linkedin.com/jobs/",
        wait_until="domcontentloaded",
        timeout=60000,
    )

    page.wait_for_timeout(4000)

    print(f"URL: {page.url}", flush=True)
    print(f"Título: {page.title()}", flush=True)

    return context, page
