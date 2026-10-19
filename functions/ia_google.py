import json
import os
from google import genai
from google.genai import types


def arrancar_ia():
    """Inicializa el cliente de Google Gemini."""
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("No se ha configurado GEMINI_API_KEY.")

    client = genai.Client(api_key=api_key)

    print("IA de Google inicializada.", flush=True)
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
    if not ofertas:
        return None

    instrucciones = f"""
        Eres un asistente de búsqueda de empleo.

        PERFIL:
        {perfil}

        OFERTAS DISPONIBLES:
        {json.dumps(ofertas, ensure_ascii=False)}

        Selecciona la oferta más adecuada según el perfil.
        No inventes información que no aparezca en los datos.

        Devuelve JSON con esta estructura:
        {{
          "indice": 0,
          "titulo": "Título exacto de la oferta",
          "motivo": "Por qué encaja con el perfil"
        }}

        El índice debe corresponder al campo indice de una oferta.
        Si ninguna encaja razonablemente, devuelve indice -1.
    """

    respuesta = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
        contents=instrucciones,
        config={
            "response_mime_type": "application/json"
        },
    )

    decision = json.loads(respuesta.text)
    print("Oferta elegida por Gemini:", decision, flush=True)
    return decision
