
import os
from dotenv import load_dotenv
from mistralai.client import Mistral

load_dotenv()

api_key = os.getenv("MISTRAL_API_KEY") or os.getenv("MISTRAL_KEY")
model = os.getenv("MISTRAL_MODEL", "ministral-14b-2512")

if not api_key:
    raise ValueError("No se encuentra la clave API en .env")

client = Mistral(api_key=api_key)

try:
    response = client.chat.complete(
        model=model,
        messages=[
            {
                "role": "user",
                "content": "busca en internet quien es Alexey Suzdalenko de España"
            }
        ],
        max_tokens=2222,
    )

    print("Respuesta:", response.choices[0].message.content)

except Exception as error:
    print("Tipo de error:", type(error).__name__)
    print("Detalle:", error)
