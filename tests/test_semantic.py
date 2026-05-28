"""
EXERCÍCIO 3 — TESTES SEMÂNTICOS (LLM-AS-JUDGE)
================================================

Como testar qualidades SUBJETIVAS como tom, clareza, ou se a explicação
é boa? Usamos OUTRO LLM como JUIZ.

FLUXO:
1. Agente responde uma pergunta
2. Mandamos pergunta + resposta + critério pro juiz
3. Juiz devolve {"pass": true/false, "reason": "..."}
4. Assert que pass é True

ATENÇÃO:
- Estes testes são MAIS CAROS (2 chamadas de API)
- Use o marker @pytest.mark.semantic pra rodar separado
- A função `llm_judge` JÁ ESTÁ PRONTA — só precisa usar ela
"""
import os
import json
import pytest
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Usamos OpenRouter também como juiz
client = OpenAI(
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

JUDGE_MODEL = "openai/gpt-oss-120b:free"

JUDGE_PROMPT = """Você é um avaliador rigoroso de respostas de IA.

Pergunta do usuário: {question}
Resposta do agente: {answer}
Critério: {criterion}

Avalie se a resposta atende ao critério. Responda APENAS em JSON válido,
sem markdown, sem cercas de código:
{{"pass": true, "reason": "explicação breve"}}"""


def llm_judge(question: str, answer: str, criterion: str) -> dict:
    """
    JÁ ESTÁ PRONTO — use esta função nos seus testes.

    Retorna: {"pass": bool, "reason": str}
    """
    response = client.chat.completions.create(
        model=JUDGE_MODEL,
        max_tokens=256,
        messages=[
            {
                "role": "user",
                "content": JUDGE_PROMPT.format(
                    question=question, answer=answer, criterion=criterion
                ),
            }
        ],
    )
    text = response.choices[0].message.content.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)


@pytest.mark.semantic
class TestSemantica:
    """Avaliações qualitativas — mais caras, rode com moderação."""

    def test_resposta_educacional(self, agent):
        """
        OBJETIVO: a resposta deve EXPLICAR o cálculo, não só dar o número.

        PASSOS:
        1. Chame o agent com "Quanto é 8 vezes 7?"
        2. Chame llm_judge com:
           - question: a pergunta original
           - answer: result["text"]
           - criterion: "A resposta deve explicar o cálculo de forma
                         educacional, não apenas dar o número."
        3. assert veredito["pass"], veredito["reason"]
           -> a `reason` aparece se falhar, ajudando a debugar

        DICA SOBRE CRITÉRIOS:
        Seja ESPECÍFICO. "Boa resposta" é vago demais.
        "Explica o cálculo passo a passo em português" é melhor.
        """
        # TODO: escreva seu teste aqui
        pass

    def test_tom_amigavel(self, agent):
        """
        OBJETIVO: quando o usuário expressa frustração, o agente deve ser
        empático.

        PERGUNTA SUGERIDA: "Não entendo matemática, me ajude"

        PASSOS:
        1. Chame o agent
        2. Use llm_judge com critério tipo:
           "A resposta deve ser empática e encorajadora, sem ser
            condescendente."
        3. assert no veredito
        """
        # TODO: escreva seu teste aqui
        pass

    def test_resposta_em_portugues(self, agent):
        """
        OBJETIVO: a resposta deve estar em PT-BR.

        Esse é um caso onde o juiz LLM funciona MUITO bem porque
        detectar idioma é fácil e objetivo pra ele.

        PASSOS:
        1. Chame o agent com qualquer pergunta de matemática
        2. llm_judge com critério "A resposta deve estar em português
           brasileiro."
        3. assert no veredito
        """
        # TODO: escreva seu teste aqui
        pass
