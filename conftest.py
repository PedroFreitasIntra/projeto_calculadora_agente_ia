"""
Fixtures compartilhadas — JÁ ESTÁ PRONTO, não precisa mudar.

A fixture `agent` faz cache em disco, então rodar os mesmos testes
várias vezes não gasta dinheiro da API.

COMO USAR nos seus testes:
    def test_alguma_coisa(agent):
        resultado = agent("sua pergunta aqui")
        assert ...

    def test_com_dataset(agent, golden_dataset):
        for caso in golden_dataset:
            ...
"""
import json
import hashlib
from pathlib import Path
import pytest
import sys
from pathlib import Path
from agent import ask_agent


CACHE_DIR = Path(".llm_cache")
CACHE_DIR.mkdir(exist_ok=True)


@pytest.fixture(scope="session")
def agent():
    """Wrapper do agente com cache em disco."""

    def _ask(question: str, use_cache: bool = True) -> dict:
        if use_cache:
            key = hashlib.md5(question.encode()).hexdigest()
            cache_file = CACHE_DIR / f"{key}.json"
            if cache_file.exists():
                return json.loads(cache_file.read_text())

        result = ask_agent(question)

        if use_cache:
            cache_file.write_text(json.dumps(result))
        return result

    return _ask


@pytest.fixture
def golden_dataset():
    """Casos de teste curados manualmente — carregados do JSON."""
    path = Path(__file__).parent / "golden_dataset.json"
    return json.loads(path.read_text())
