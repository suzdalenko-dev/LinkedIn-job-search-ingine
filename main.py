
from playwright.sync_api import sync_playwright

from functions.a_open_brouser import open_brouser
from functions.general import click_text_button


def main():
    with sync_playwright() as p:
        context, page = open_brouser(p)

        try:
            resultado = click_text_button(page, "Mostrar todo")

            print(f"Resultado del clic: {resultado}", flush=True)
            print(f"URL final: {page.url}", flush=True)

            while True:
                page.wait_for_timeout(1000)

        except KeyboardInterrupt:
            print("Programa interrumpido.", flush=True)

        finally:
            context.close()


if __name__ == "__main__":
    main()
