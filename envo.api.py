
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ENVO_API_KEY")
if not API_KEY:
    raise RuntimeError("Falta ENVO_API_KEY en el archivo .env")

URL = "https://api.envoapi.com/v1/jobs/search"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json",
}

# Ubicaciones obtenidas con la API de EnvoAPI
UBICACIONES = {
    "Cantabria": "geo_4S0NCZ",
    "Bilbao": "geo_5Cuj7n",
}

# Puedes añadir más palabras clave a esta lista
PALABRAS_CLAVE = [
    "software developer",
    "Python developer",
    "Java developer",
    "industrial software",
]

todas_las_ofertas = []
urls_vistas = set()

for zona, location_id in UBICACIONES.items():
    for keyword in PALABRAS_CLAVE:
        print(f"\nBuscando: {keyword} | {zona}")

        params = {
            "keywords": keyword,
            "location": location_id,
            "start": 0,
            "sort": "recent",
            "timePosted": "week",
            "easyApply": "true",
        }

        try:
            response = requests.get(
                URL,
                params=params,
                headers=HEADERS,
                timeout=30,
            )

            print("HTTP:", response.status_code)
            response.raise_for_status()
            resultado = response.json()

            ofertas = resultado.get("data", {}).get("jobs", [])
            print("Ofertas recibidas:", len(ofertas))

            for oferta in ofertas:
                enlace = oferta.get("url")

                if not enlace or enlace in urls_vistas:
                    continue

                urls_vistas.add(enlace)
                oferta["zona_busqueda"] = zona
                oferta["palabra_clave"] = keyword
                todas_las_ofertas.append(oferta)

        except requests.exceptions.RequestException as error:
            print("Error en la petición:", error)
            if response is not None:
                print(response.text)

        # Guardar progresivamente por si falla otra consulta
        with open("ofertas.json", "w", encoding="utf-8") as archivo:
            json.dump(
                todas_las_ofertas,
                archivo,
                ensure_ascii=False,
                indent=2,
            )

print(f"\nTotal de ofertas únicas: {len(todas_las_ofertas)}")
print("Archivo guardado: ofertas.json")

for oferta in todas_las_ofertas:
    print(
        oferta.get("title"),
        "|", oferta.get("companyName"),
        "|", oferta.get("location"),
        "|", oferta.get("url"),
    )
