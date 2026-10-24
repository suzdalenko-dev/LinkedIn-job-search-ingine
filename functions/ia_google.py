import json
import os
from google import genai
from google.genai import types
from mistralai.client import Mistral


def arrancar_ia():
    """Inicializa el cliente de Mistral."""

    api_key = (os.getenv("MISTRAL_KEY"))

    if not api_key:
        raise ValueError(
            "Configura MISTRAL_API_KEY o MISTRAL_KEY en .env"
        )

    client = Mistral(api_key=api_key)

    print("IA de Mistral inicializada.", flush=True)
    return client




def analizar_pagina(client, page, perfil):
    """Envía a Gemini la captura y el contenido de LinkedIn."""

    captura = page.screenshot(type="png")

    texto_pagina = page.locator("body").inner_text(timeout=10000)
    texto_pagina = texto_pagina[:15000]

    instrucciones = f"""
        Eres un asistente que analiza ofertas de empleo en LinkedIn.
        
        PERFIL DEL CANDIDATO:
        {perfil}
        
        TEXTO VISIBLE DE LA PÁGINA:
        {texto_pagina}
        
        Analiza también la captura de pantalla.
        
        Tu trabajo:
        1. Identificar las ofertas de empleo del listado izquierdo.
        2. Compararlas con el perfil del candidato.
        3. Elegir la oferta más adecuada que todavía no se haya analizado.
        4. Indicar si hay que seleccionar una oferta, pulsar Solicitar,
           rellenar un formulario con los datos de usuario o muy similares que podrian ser
        
        
        Devuelve exclusivamente un JSON con esta estructura:
        {{
          "accion": "seleccionar_oferta | solicitar | rellenar_formulario | revisar_oferta | pedir_confirmacion",
          "titulo_oferta": "Título visible o cadena vacía",
          "empresa": "Empresa visible o cadena vacía",
          "motivo": "Explicación breve",
          "datos_necesarios": [],
          "confirmacion_usuario": false
        }}
    """

    respuesta = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
        contents=[
            instrucciones,
            types.Part.from_bytes(
                data=captura,
                mime_type="image/png"
            )
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )

    resultado = json.loads(respuesta.text)

    print("Decisión de Gemini:", resultado, flush=True)
    return resultado








def elegir_oferta(client, ofertas, perfil):
    """Selecciona la oferta que mejor encaja con el perfil."""

    if not ofertas:
        return None

    instrucciones = f"""
Eres un asistente especializado en búsqueda de empleo.

PERFIL DEL CANDIDATO:
{perfil}

OFERTAS DISPONIBLES:
{json.dumps(ofertas, ensure_ascii=False)}

Compara las ofertas con el perfil y selecciona la que mejor encaje.

Prioriza:
- Software industrial e integración OT/IT.
- Desarrollo backend y aplicaciones empresariales.
- Python, PHP, C#/.NET y Java.
- Bases de datos, APIs y automatización de procesos.
- Datos, Power BI e IA aplicada.

No inventes requisitos ni información que no aparezca en
las ofertas. Solo conoces título, empresa y ubicación.

Devuelve únicamente un objeto JSON con esta estructura:
{{
  "indice": 0,
  "titulo": "Título exacto de la oferta",
  "motivo": "Por qué encaja con el perfil"
}}

El índice debe corresponder al campo "indice" de una oferta.
Si ninguna encaja razonablemente, devuelve:
{{
  "indice": -1,
  "titulo": "",
  "motivo": "Por qué ninguna oferta encaja"
}}

Responde en español.
"""

    respuesta = client.chat.complete(
        model=os.getenv("MISTRAL_MODEL", "mistral-small-2603"),
        messages=[
        {
            "role": "user",
            "content": instrucciones
        }
    ],
    response_format={"type": "json_object"},
    temperature=0.2
)

    contenido = respuesta.choices[0].message.content

    if not isinstance(contenido, str) or not contenido.strip():
        raise ValueError("Mistral ha devuelto una respuesta vacía.")

    decision = json.loads(contenido)

    if not isinstance(decision, dict):
        raise ValueError("La respuesta no es un objeto JSON.")

    indice = decision.get("indice")
    indices_validos = {
        oferta["indice"] for oferta in ofertas
    }

    if (
        not isinstance(indice, int)
        or isinstance(indice, bool)
        or (indice != -1 and indice not in indices_validos)
    ):
        raise ValueError(
            f"Índice de oferta no válido: {indice!r}"
        )

    print("Oferta elegida por Mistral:", decision, flush=True)
    return decision
