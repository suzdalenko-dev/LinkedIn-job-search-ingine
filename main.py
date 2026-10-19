import time
from playwright.sync_api import sync_playwright
from functions.a_open_brouser import open_brouser
from functions.general import click_text_button, log



from winotify import Notification

def notificar(titulo, mensaje):
    aviso = Notification(
        app_id="Job Search Engine",
        title=titulo,
        msg=mensaje,
        duration="short"
    )
    aviso.show()

notificar(1, 2)

def main():
    with sync_playwright() as p:
        context, page = open_brouser(p)

        try:
            time.sleep(1)
            text = click_text_button(page, "Mostrar todo")
            text = click_text_button(page, "Fecha de publicación") 
            text = click_text_button(page, "Última semana")
            text = click_text_button(page, "Mostrar resultados")
            text = click_text_button(page, "Solicitud sencilla")




            while True:
                page.wait_for_timeout(1000)

        except KeyboardInterrupt:
            print("Programa interrumpido.", flush=True)

        finally:
            context.close()


if __name__ == "__main__":
    main()
