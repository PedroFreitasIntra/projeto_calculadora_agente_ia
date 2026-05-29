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
import os
from pathlib import Path
import pytest
from agent import ask_agent


CACHE_DIR = Path(".llm_cache")
CACHE_DIR.mkdir(exist_ok=True)


def has_api_key() -> bool:
    """Verifica se há credenciais disponíveis para API."""
    return bool(os.environ.get("OPENROUTER_API_KEY"))


def get_cache_key(question: str) -> str:
    """Gera a chave de cache para uma pergunta."""
    return hashlib.md5(question.encode()).hexdigest()


@pytest.fixture(scope="session")
def agent():
    """Wrapper do agente com cache em disco. Skipa testes se sem cache e sem API key."""

    def _ask(question: str, use_cache: bool = True) -> dict:
        key = get_cache_key(question)
        cache_file = CACHE_DIR / f"{key}.json"

        if use_cache and cache_file.exists():
            return json.loads(cache_file.read_text(encoding='utf-8'))

        # Sem cache: precisa de API key para continuar
        if not has_api_key():
            pytest.skip(f"Sem cache para '{question}' e sem OPENROUTER_API_KEY")

        result = ask_agent(question)

        if use_cache:
            cache_file.write_text(json.dumps(result, ensure_ascii=False), encoding='utf-8')
        return result

    return _ask


@pytest.fixture
def golden_dataset():
    """Casos de teste curados manualmente — carregados do JSON."""
    path = Path(__file__).parent / "golden_dataset.json"
    return json.loads(path.read_text(encoding='utf-8'))
