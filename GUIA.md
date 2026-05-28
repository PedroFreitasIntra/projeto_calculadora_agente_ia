# GUIA: Como pensar pra testar agentes de IA

Este guia te dá o **raciocínio** que você precisa pra escrever os testes sozinho.
Leia ANTES de tentar escrever qualquer teste.

---

## 1. Setup (faça isso primeiro)

```bash
python -m venv venv
source venv/bin/activate            # Linux/Mac
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sua-chave"
```

**Antes de escrever testes, EXPLORE o agente:**

```bash
python agent.py
```

Veja o formato real da resposta. Adicione `print()` com outras perguntas e veja o que vem. Isso te dá intuição.

---

## 2. As 3 mentalidades fundamentais

### Mentalidade 1: "Eu testo PROPRIEDADES, não strings exatas"

LLMs são probabilísticos. A mesma pergunta pode gerar:
- "O resultado é 345"
- "345 é a resposta!"
- "Calculando 15 × 23 = 345"

**ERRADO:**
```python
assert result["text"] == "O resultado é 345"   # vai falhar quase sempre
```

**CERTO:**
```python
assert "345" in result["text"]   # qualquer formato passa, desde que tenha 345
```

### Mentalidade 2: "O que eu REALMENTE quero garantir?"

Antes de escrever um teste, pergunte: **qual a propriedade essencial?**

Exemplo — testando "Quanto é 15 × 23?":
- ❌ "Resposta tem exatamente 50 caracteres" — irrelevante
- ❌ "Resposta começa com 'O'" — arbitrário
- ✅ "Resposta contém '345'" — propriedade essencial
- ✅ "Calculator foi chamada" — propriedade comportamental

### Mentalidade 3: "Mensagens de erro são pra mim, não pro computador"

Quando um teste falha, você precisa saber **por quê**. Sempre coloque uma mensagem de erro útil:

```python
# Ruim
assert "calculator" in tools

# Bom
assert "calculator" in tools, f"Tools chamadas: {tools}"
```

---

## 3. Anatomia da fixture `agent`

Em todos os testes você vai usar:

```python
def test_alguma_coisa(agent):    # ← `agent` é injetado pelo pytest
    result = agent("sua pergunta")
```

**`agent` é uma FUNÇÃO**. Ela retorna um dict:

```python
{
    "text": "O resultado é 345",        # string com a resposta final
    "tool_calls": [                      # lista de tools chamadas
        {"name": "calculator", "input": {"expression": "15 * 23"}}
    ],
    "stop_reason": "end_turn"            # geralmente "end_turn"
}
```

**Operações comuns:**

```python
# Pegar texto da resposta
texto = result["text"]

# Pegar texto em lowercase (útil pra testes de segurança)
texto = result["text"].lower()

# Pegar lista de nomes de tools chamadas
nomes = [tc["name"] for tc in result["tool_calls"]]

# Checar se uma tool foi chamada
assert "calculator" in nomes

# Checar quantas tools foram chamadas
assert len(result["tool_calls"]) == 0  # nenhuma
```

---

## 4. Os 3 níveis de teste (e quando usar cada um)

### Nível 1: DETERMINÍSTICO (`test_agent.py`)

**Pergunta:** "Posso verificar isso com `in`, `==`, `len()`?"

Se sim → é determinístico → rápido e barato → rode sempre.

Exemplos:
- "Resposta contém '345'?"
- "Calculator foi chamada?"
- "stop_reason é 'end_turn'?"

### Nível 2: SEGURANÇA (`test_safety.py`)

**Pergunta:** "O agente respeita os limites que defini pra ele?"

Foca em comportamentos que **não deveriam acontecer**:
- Não responder fora do escopo
- Não obedecer prompt injection
- Não usar tools desnecessariamente

Padrão recomendado — **lista de indicadores**:

```python
texto = result["text"].lower()
indicadores = ["não posso", "desculpe", "matemática"]
assert any(ind in texto for ind in indicadores)
```

### Nível 3: SEMÂNTICO / LLM-JUDGE (`test_semantic.py`)

**Pergunta:** "Posso verificar isso só com código, ou precisa de JULGAMENTO?"

Se precisa de julgamento → use LLM-judge → mais caro → rode menos.

Exemplos:
- "A explicação é educacional?"
- "O tom é empático?"
- "A resposta está em português?"

A função `llm_judge` já está pronta, é só usar:

```python
veredito = llm_judge(
    question="Quanto é 8 × 7?",
    answer=result["text"],
    criterion="Deve explicar o cálculo passo a passo."
)
assert veredito["pass"], veredito["reason"]
```

---

## 5. Padrão `parametrize`: o seu melhor amigo

Em vez de escrever 4 funções de teste quase iguais, escreva 1 e parametrize:

```python
@pytest.mark.parametrize(
    "pergunta,esperado",      # nomes das variáveis
    [
        ("Quanto é 10 + 5?", "15"),
        ("Quanto é 7 * 8?", "56"),
        ("Quanto é 100 / 4?", "25"),
    ],
)
def test_calculos(self, agent, pergunta, esperado):
    result = agent(pergunta)
    assert esperado in result["text"]
```

Isso vira **3 testes separados** no relatório. Se um falhar, os outros continuam.

---

## 6. Fluxo de raciocínio pra escrever UM teste

Sempre que for escrever um teste, siga estes 5 passos:

**1. O que estou tentando garantir?**
   Escreva em 1 frase. "Quero garantir que o agente usa a calculadora pra perguntas matemáticas."

**2. Que pergunta vai disparar o comportamento?**
   "Quanto é 50 vezes 7?"

**3. O que vou medir na resposta?**
   - tool_calls inclui "calculator"
   - text contém "350"

**4. Escrevo o assert mais simples possível**
   ```python
   assert "calculator" in [tc["name"] for tc in result["tool_calls"]]
   ```

**5. Adiciono mensagem de erro útil**
   ```python
   tools = [tc["name"] for tc in result["tool_calls"]]
   assert "calculator" in tools, f"Tools chamadas: {tools}"
   ```

---

## 7. Erros comuns que iniciantes cometem

### Erro 1: Comparar strings exatas
```python
# RUIM — vai falhar com qualquer variação de fraseado
assert result["text"] == "O resultado é 345"

# BOM
assert "345" in result["text"]
```

### Erro 2: Esquecer `.lower()` em comparações de texto
```python
# RUIM — falha se o agente escrever "Desculpe" com D maiúsculo
assert "desculpe" in result["text"]

# BOM
assert "desculpe" in result["text"].lower()
```

### Erro 3: Testar várias coisas no mesmo `assert`
```python
# RUIM — se falhar, qual condição falhou?
assert "345" in texto and "calculator" in tools

# BOM — dois asserts separados, mensagens claras
assert "345" in texto, "Número correto não apareceu"
assert "calculator" in tools, f"Tools: {tools}"
```

### Erro 4: Não usar mensagens de erro nos asserts
Você vai agradecer ao "você do passado" quando um teste falhar em CI e
você só tiver a mensagem pra debugar.

### Erro 5: Critérios vagos no LLM-judge
```python
# RUIM — o juiz vai variar muito
criterion="A resposta é boa"

# BOM
criterion="A resposta explica o passo a passo do cálculo em português."
```

---

## 8. Como rodar e depurar

```bash
# Rodar tudo
pytest

# Só um arquivo
pytest tests/test_agent.py

# Um teste específico
pytest tests/test_agent.py::TestEstrutura::test_resposta_nao_vazia

# Parar no primeiro erro
pytest -x

# Mostrar print()s
pytest -s

# Só testes com marker safety
pytest -m safety
```

**Quando um teste falhar:**

1. Leia a mensagem de erro até o final
2. Veja o que o agente REALMENTE respondeu (use `print(result)`)
3. Decida: o teste está errado? Ou o agente está errado?

---

## 9. Ordem sugerida pra fazer os exercícios

1. **Comece simples**: `test_resposta_nao_vazia` em `test_agent.py`
2. **Próximo**: `test_usa_calculadora_para_matematica`
3. **Próximo**: `test_resposta_contem_resultado_correto`
4. Rode `pytest tests/test_agent.py` e veja se passa
5. **Depois**: implemente o `parametrize`
6. **Depois**: `test_todos_os_casos` (mais complexo, junta tudo)
7. **Depois**: segurança (`test_safety.py`)
8. **Por último**: semânticos (`test_semantic.py`)

---

## 10. Quando estiver travado

Lembre: **rode `python agent.py`** com a pergunta que você quer testar.
Veja a resposta. Aí o teste fica óbvio.

Se ainda estiver travado, abra o arquivo `GABARITO.md` (mas tente sozinho
primeiro!).

Boa sorte. 🚀
