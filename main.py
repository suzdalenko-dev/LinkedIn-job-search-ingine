import time
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from functions.a_open_brouser import open_brouser
from functions.general import click_text_button, extraer_ofertas, log, notificar
from winotify import Notification
from functions.ia_google import analizar_pagina, arrancar_ia, elegir_oferta

load_dotenv()

PERFIL = """Ingeniero de Software Industrial | OT + IT | Industria 4.0
            Desarrolle aplicaciones industriales end-to-end para cálculo de OEE, ritmos de producción y KPIs en tiempo real.
            De planta a dato:
            OPC UA, MQTT, Sockets, PLCs → Backend → Visualización
            Experiencia implantando DECA y desarrollo completo de KPIs para PERTE Agroalimentario.
            Stack:
                Backend: Python (Django), PHP (Laravel/Symfony), C# .NET, Java Spring Boot, JS (Vue.js)
                Datos: PostgreSQL, Oracle, SQL Server, SQLite | Power BI (DAX)
                Automatización: Integración sistemas, scripts, informes PDF/Excel auto
                Mobile: Android (Kotlin + Firebase)
                ERP: Evolución ERP a medida sector pesca (PHP Laravel)
            IA: Aplicando IA y LLMs a industria
               OCR + NLP para procesamiento documental 
               Extracción y normalización automática de datos"""






def main():
    # Inicializar Gemini una sola vez
    ia = arrancar_ia()
    
    with sync_playwright() as p:
        context, page = open_brouser(p)

        try:
            time.sleep(1)
            text = click_text_button(page, "Mostrar todo")
            text = click_text_button(page, "Fecha de publicación") 
            text = click_text_button(page, "Última semana")
            text = click_text_button(page, "Mostrar resultados")
            text = click_text_button(page, "Solicitud sencilla")
            time.sleep(11)

            # decision = analizar_pagina(ia, page, PERFIL)

            ofertas = extraer_ofertas(page)
            print(ofertas)
            time.sleep(11)
 
            
            notificar("", str(ofertas))

            # decision = elegir_oferta(ia, ofertas, PERFIL)
            # print(print(decision))

            while True:
                page.wait_for_timeout(1000)

        except KeyboardInterrupt:
            print("Programa interrumpido.", flush=True)

        finally:
            context.close()


if __name__ == "__main__":
    main()

'''
ahora entonces la idea que la ia tiene que tener herrramientas como consular el contenido de la pagina, 
quizas a la vez hacer la foto y la idea es primero clicar ene el listado la ofertas en una de ellas que tiene sentido para mi uso, 
despues la pagina cambia y hay que clicar en solicitud sencilla y despues y rellenar los datos que hagan falta y despues puede ser que hace falta hacer el 
scroll para descubrir el boton de enviar solicitud y pasar a elegir la otra oferta de trabajo del listado general a la derecha
'''