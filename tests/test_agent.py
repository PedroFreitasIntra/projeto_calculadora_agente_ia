"""
EXERCÍCIO 1 — TESTES DETERMINÍSTICOS (CORRIGIDO)
=================================================
"""
import pytest


class TestEstrutura:
    """Testes determinísticos sobre formato da resposta."""

    def test_resposta_nao_vazia(self, agent):
        """OBJETIVO: garantir que o agente retornou ALGUMA resposta."""
        # Act
        result = agent("Quanto é 2 + 2?")

        # Assert
        assert result["text"], "Agente retornou texto vazio"
        # OpenRouter retorna "stop" (não "end_turn" como era na Anthropic)
        assert result["stop_reason"] in ["stop", "end_turn"]

    def test_usa_calculadora_para_matematica(self, agent):
        """OBJETIVO: verificar que o agente USOU a ferramenta calculator."""
        result = agent("Quanto é 12 vezes 9 multiplicado por 3?")
        tool_names = [tc["name"] for tc in result["tool_calls"]]
        assert "calculator" in tool_names, f"Tools chamadas: {tool_names}"

    def test_resposta_contem_resultado_correto(self, agent):
        """OBJETIVO: o número da resposta correta deve aparecer no texto."""
        result = agent("Quanto é 15 vezes 23?")
        assert "345" in result["text"], f"Resposta: {result['text']}"


class TestParametrizado:
    """
    PADRÃO ESSENCIAL: rode o MESMO teste com vários inputs.
    O @parametrize fica DENTRO da classe e COLADO na função.
    """

    @pytest.mark.parametrize(
        "pergunta,resultado_esperado",
        [
            ("Quanto é 10 + 5?","15"),
            ("Quanto é 5 vezes 6?", "30"),
            ("Quanto é 6 vezes 6?", "36"),
            ("Quanto é 9 vezes 9?", "81"),
            ("Quanto é 7 x 7?", "49"),
            ("Qual a raiz de 445", "22"),
        ],
    )
    def test_calculos_basicos(self, agent, pergunta, resultado_esperado):
        """Testa vários cálculos usando o mesmo padrão de verificação."""
        result = agent(pergunta)
        assert resultado_esperado in result["text"], (
            f"Esperava '{resultado_esperado}' em: {result['text']}"
        )


class TestGoldenDataset:
    """Roda todos os casos do dataset curado em golden_dataset.json."""

    def test_todos_os_casos(self, agent, golden_dataset):
        falhas = []

        for caso in golden_dataset:
            # Pula casos de segurança (testados em test_safety.py)
            if caso.get("should_refuse"):
                continue

            result = agent(caso["question"])

            # Verifica que a ferramenta esperada foi chamada
            if caso.get("expected_tool"):
                tool_names = [tc["name"] for tc in result["tool_calls"]]
                if caso["expected_tool"] not in tool_names:
                    falhas.append(
                        f"[{caso['id']}] Ferramenta '{caso['expected_tool']}' "
                        f"não foi chamada. Tools: {tool_names}"
                    )

            # Verifica que cada string esperada aparece na resposta
            for expected_str in caso.get("expected_in_answer", []):
                if expected_str not in result["text"]:
                    falhas.append(
                        f"[{caso['id']}] String '{expected_str}' não encontrada. "
                        f"Resposta: {result['text'][:100]}..."
                    )

        assert not falhas, "Falhas encontradas:\n" + "\n".join(falhas)