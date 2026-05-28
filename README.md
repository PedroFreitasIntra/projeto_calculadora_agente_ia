# Projeto Exercício: Testando Agentes de IA

Este projeto é pra você **praticar escrevendo testes**. O agente está pronto,
você precisa implementar os testes em `tests/`.

## 📖 LEIA O GUIA PRIMEIRO

Abra `GUIA.md` antes de qualquer coisa. Ele explica todo o raciocínio
necessário pra escrever os testes.

## Setup rápido

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sua-chave"

# Explore o agente primeiro
python agent.py

# Quando começar a implementar, rode os testes
pytest tests/test_agent.py
```

## Estrutura

```
projeto-exercicio/
├── GUIA.md                 ← LEIA PRIMEIRO
├── agent.py                ← PRONTO (não mexa)
├── tests/
│   ├── conftest.py         ← PRONTO (fixtures)
│   ├── golden_dataset.json ← PRONTO (casos de teste)
│   ├── test_agent.py       ← VOCÊ IMPLEMENTA (determinísticos)
│   ├── test_safety.py      ← VOCÊ IMPLEMENTA (segurança)
│   └── test_semantic.py    ← VOCÊ IMPLEMENTA (LLM-judge)
└── pytest.ini
```

## Ordem sugerida

1. Leia `GUIA.md` inteiro
2. Rode `python agent.py` e explore o formato da resposta
3. Implemente `tests/test_agent.py` (do mais simples ao mais complexo)
4. `pytest tests/test_agent.py` — veja passar
5. Implemente `test_safety.py`
6. Implemente `test_semantic.py`

Bom estudo!
