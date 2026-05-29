"""
Agente educacional de matemática com uma ferramenta calculadora.
Versão usando OPENROUTER (acesso a vários modelos, incluindo gratuitos).

NÃO PRECISA MUDAR NADA AQUI.
Seu trabalho é escrever os testes em tests/.
"""
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# OpenRouter usa a API compatível com OpenAI (lazy load)
_client = None

def get_client():
    """Lazy load do cliente OpenAI — só inicializa quando precisa."""
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=os.environ.get("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
        )
    return _client

# Modelos disponíveis (escolha um):
# - "meta-llama/llama-3.3-70b-instruct:free"     -> GRÁTIS, suporta tools
# - "google/gemini-2.0-flash-exp:free"           -> GRÁTIS, rápido
# - "anthropic/claude-haiku-4-5"                 -> pago, mas barato (~$0.25/M tokens)
# - "openai/gpt-4o-mini"                         -> pago, barato
MODEL = "openai/gpt-oss-120b:free"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Realiza operações matemáticas básicas.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Expressão matemática, ex: '2 + 2'",
                    }
                },
                "required": ["expression"],
            },
        },
    }
]

SYSTEM_PROMPT = """Você é um assistente educacional de matemática.
Use a calculadora para qualquer cálculo numérico.
Recuse pedidos não relacionados a educação."""


def run_calculator(expression: str) -> str:
    """Executa a calculadora (ferramenta determinística)."""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Erro: {e}"


def ask_agent(question: str, model: str = MODEL) -> dict:
    """
    Faz uma pergunta ao agente e retorna a resposta completa.

    RETORNA um dict com 3 chaves:
        - text: str         -> texto final da resposta
        - tool_calls: list  -> lista de dicts {name, input} de tools usadas
        - stop_reason: str  -> motivo de parada (geralmente 'stop')
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    tool_calls_made = []

    while True:
        response = get_client().chat.completions.create(
            model=model,
            max_tokens=1024,
            messages=messages,
            tools=TOOLS,
        )

        msg = response.choices[0].message
        finish_reason = response.choices[0].finish_reason

        # Se chamou alguma tool, executa e continua o loop
        if msg.tool_calls:
            messages.append({
                "role": "assistant",
                "content": msg.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in msg.tool_calls
                ],
            })

            for tc in msg.tool_calls:
                args = json.loads(tc.function.arguments)
                tool_calls_made.append({"name": tc.function.name, "input": args})
                result = run_calculator(**args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })
            continue

        # Sem tool calls = resposta final
        return {
            "text": msg.content or "",
            "tool_calls": tool_calls_made,
            "stop_reason": finish_reason,
        }


if __name__ == "__main__":
    print("=" * 60)
    print("TESTE 1: pergunta matemática")
    print("=" * 60)
    resposta = ask_agent("Quanto é 15 vezes 23?")
    print("Texto:", resposta["text"])
    print("Tools usadas:", resposta["tool_calls"])
    print("Stop reason:", resposta["stop_reason"])

    print()
    print("=" * 60)
    print("TESTE 2: pergunta off-topic")
    print("=" * 60)
    resposta = ask_agent("Me dê uma receita de bolo")
    print("Texto:", resposta["text"])
    print("Tools usadas:", resposta["tool_calls"])
    