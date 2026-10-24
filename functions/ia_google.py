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
    """Selecciona y ordena las tres ofertas que mejor encajan."""

    if not ofertas:
        return {
            "total_ofertas_analizadas": 0,
            "seleccionadas": []
        }

    instrucciones = f"""
Eres un especialista en selección de ofertas de empleo para un candidato.

PERFIL DEL CANDIDATO:
{perfil}

OFERTAS DISPONIBLES:
{json.dumps(ofertas, ensure_ascii=False)}

OBJETIVO:
Selecciona las 3 ofertas que mejor encajan con el perfil.
Si hay menos de 3 ofertas disponibles, selecciona todas las disponibles.

CRITERIOS DE VALORACIÓN:
1. Software industrial, automatización e integración OT/IT.
2. Desarrollo backend y aplicaciones empresariales.
3. Python, PHP, C#/.NET, Java y desarrollo de APIs.
4. Bases de datos, integraciones y automatización de procesos.
5. Power BI, análisis de datos e IA aplicada.
6. Compatibilidad general con la experiencia profesional del candidato.

INSTRUCCIONES:
- Ordena las ofertas de mayor a menor coincidencia.
- Asigna a cada una una puntuación de 0 a 100.
- Explica brevemente por qué encaja con el perfil.
- Utiliza únicamente información disponible en las ofertas.
- No inventes requisitos, salarios ni responsabilidades.
- Cada índice debe corresponder al campo "indice" de una oferta.
- No repitas ninguna oferta.
- Devuelve exactamente 3 ofertas distintas si hay 3 o más disponibles.
- La primera debe ser la mejor coincidencia.

Devuelve exclusivamente JSON válido con esta estructura:

{{
  "seleccionadas": [
    {{
      "indice": 0,
      "puntuacion": 95,
      "titulo": "Título exacto",
      "empresa": "Empresa exacta",
      "ubicacion": "Ubicación exacta",
      "motivo": "Explicación de la coincidencia"
    }}
  ]
}}

Responde en español.
"""

    respuesta = client.chat.complete(
        model=os.getenv("MISTRAL_MODEL", "ministral-14b-2512"),
        messages=[
            {
                "role": "user",
                "content": instrucciones
            }
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
        max_tokens=1500
    )

    contenido = respuesta.choices[0].message.content

    if not isinstance(contenido, str) or not contenido.strip():
        raise ValueError("Mistral ha devuelto una respuesta vacía.")

    resultado = json.loads(contenido)

    if not isinstance(resultado, dict):
        raise ValueError("La respuesta no es un objeto JSON.")

    seleccionadas_ia = resultado.get("seleccionadas")

    if not isinstance(seleccionadas_ia, list):
        raise ValueError("La respuesta no contiene la lista seleccionadas.")

    # Usar los datos originales para validar los índices y los títulos.
    ofertas_por_indice = {
        oferta["indice"]: oferta
        for oferta in ofertas
    }

    seleccionadas = []
    indices_usados = set()

    for candidata in seleccionadas_ia:
        if not isinstance(candidata, dict):
            continue

        indice = candidata.get("indice")

        if (
            not isinstance(indice, int)
            or isinstance(indice, bool)
            or indice not in ofertas_por_indice
            or indice in indices_usados
        ):
            continue

        oferta_original = ofertas_por_indice[indice]

        try:
            puntuacion = float(candidata.get("puntuacion", 0))
        except (TypeError, ValueError):
            puntuacion = 0

        puntuacion = max(0, min(100, puntuacion))

        seleccionadas.append({
            "indice": indice,
            "puntuacion": puntuacion,
            "titulo": oferta_original["titulo"],
            "empresa": oferta_original["empresa"],
            "ubicacion": oferta_original["ubicacion"],
            "motivo": str(candidata.get("motivo", ""))
        })

        indices_usados.add(indice)

        if len(seleccionadas) == 3:
            break

    if len(seleccionadas) != min(3, len(ofertas)):
        raise ValueError(
            f"Mistral ha seleccionado {len(seleccionadas)} ofertas válidas; "
            f"se esperaban {min(3, len(ofertas))}. "
            "Revisa la respuesta de la IA."
        )

    decision = {
        "total_ofertas_analizadas": len(ofertas),
        "seleccionadas": seleccionadas
    }

    print("Tres mejores ofertas:", json.dumps(
        decision, ensure_ascii=False, indent=2
    ), flush=True)

    return decision
