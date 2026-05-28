import os
from dotenv import load_dotenv
import requests

load_dotenv()

response = requests.get(
    "https://openrouter.ai/api/v1/models",
    headers={"Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}"}
)

modelos = response.json()["data"]

# Filtra modelos gratuitos com suporte a tools
print("=" * 70)
print("MODELOS GRATUITOS DISPONÍVEIS:")
print("=" * 70)
for m in modelos:
    if ":free" in m["id"]:
        suporta_tools = "tools" in m.get("supported_parameters", [])
        print(f"  {m['id']}")
        print(f"    Suporta tools: {suporta_tools}")
        print()