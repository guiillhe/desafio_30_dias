# ============================================================
# EXERCÍCIO: Custo de contexto em LLM
# GPT-5.6 Sol
#
# Estratégias:
# 1. Full Context
# 2. RAG
# 3. Sumarização
# 4. RAG + Cache
# ============================================================

# Preços do GPT-5.6 Sol
INPUT_PRICE = 4.00       # US$ / 1M tokens
CACHE_PRICE = 0.40       # US$ / 1M tokens
OUTPUT_PRICE = 20.00     # US$ / 1M tokens


def calculate_cost(
    input_tokens,
    output_tokens,
    cached_tokens=0,
    long_context=False
):
    """
    Calcula o custo de uma chamada à API.

    input_tokens:
        Total de tokens de entrada.

    output_tokens:
        Tokens gerados pelo modelo.

    cached_tokens:
        Parte do input que está em cache.

    long_context:
        True quando o contexto ultrapassa 272K tokens.
    """

    # Tokens que não estão em cache
    uncached_tokens = input_tokens - cached_tokens

    # Multiplicadores para contexto longo
    if long_context:
        input_rate = INPUT_PRICE * 2
        cache_rate = CACHE_PRICE * 2
        output_rate = OUTPUT_PRICE * 1.5
    else:
        input_rate = INPUT_PRICE
        cache_rate = CACHE_PRICE
        output_rate = OUTPUT_PRICE

    # Custo do input normal
    input_cost = (
        uncached_tokens / 1_000_000
    ) * input_rate

    # Custo do input em cache
    cache_cost = (
        cached_tokens / 1_000_000
    ) * cache_rate

    # Custo da resposta
    output_cost = (
        output_tokens / 1_000_000
    ) * output_rate

    return input_cost + cache_cost + output_cost


# ============================================================
# 1. FULL CONTEXT
# ============================================================
#
# Enviamos 1 milhão de tokens em TODA chamada.
#
# Como 1M > 272K:
#   input = 2x
#   output = 1.5x
#
# Input:
#   1.000.000 tokens
#
# Output:
#   10.000 tokens
# ============================================================

full_context_cost = calculate_cost(
    input_tokens=1_000_000,
    output_tokens=10_000,
    long_context=True
)


# ============================================================
# 2. RAG
# ============================================================
#
# Temos uma base enorme, mas recuperamos apenas
# 10K tokens relevantes para cada pergunta.
#
# Input:
#   10.000 tokens
#
# Output:
#   1.000 tokens
# ============================================================

rag_cost = calculate_cost(
    input_tokens=10_000,
    output_tokens=1_000
)


# ============================================================
# 3. SUMARIZAÇÃO
# ============================================================
#
# Primeiro fazemos:
#
# 1M tokens
#      ↓
# resumo de 50K tokens
#
# Esse resumo é gerado uma vez.
#
# Depois cada pergunta utiliza os 50K tokens.
# ============================================================

summary_generation_cost = calculate_cost(
    input_tokens=1_000_000,
    output_tokens=50_000,
    long_context=True
)

summary_query_cost = calculate_cost(
    input_tokens=50_000,
    output_tokens=1_000
)


# ============================================================
# 4. RAG + CACHE
# ============================================================
#
# Cada chamada possui 10K tokens:
#
# 6K = contexto repetido → CACHE
# 4K = contexto novo
#
# Output:
# 1K tokens
# ============================================================

rag_cache_cost = calculate_cost(
    input_tokens=10_000,
    output_tokens=1_000,
    cached_tokens=6_000
)


# ============================================================
# ORGANIZAR AS ESTRATÉGIAS
# ============================================================

strategies = {
    "Full Context": full_context_cost,

    "RAG": rag_cost,

    "Sumarização": summary_query_cost,

    "RAG + Cache": rag_cache_cost,
}


# ============================================================
# NÚMERO DE CHAMADAS
# ============================================================

monthly_calls = [
    100,
    1_000,
    100_000
]


# ============================================================
# MOSTRAR CUSTO POR CHAMADA
# ============================================================

print("=" * 60)
print("CUSTO POR CHAMADA")
print("=" * 60)

for strategy, cost in strategies.items():

    print(
        f"{strategy:<20} "
        f"US$ {cost:.4f}"
    )


# ============================================================
# MOSTRAR CUSTO MENSAL
# ============================================================

print()
print("=" * 60)
print("CUSTO MENSAL")
print("=" * 60)

for strategy, cost_per_call in strategies.items():

    for calls in monthly_calls:

        # A sumarização precisa pagar o custo inicial
        # para criar o resumo de 50K tokens.
        initial_cost = 0

        if strategy == "Sumarização":
            initial_cost = summary_generation_cost

        monthly_cost = (
            cost_per_call * calls
            + initial_cost
        )

        print(
            f"{strategy:<20} "
            f"{calls:>8,} chamadas → "
            f"US$ {monthly_cost:,.2f}"
        )


# ============================================================
# ECONOMIA DO RAG
# ============================================================

print()
print("=" * 60)
print("COMPARAÇÃO: FULL CONTEXT x RAG")
print("=" * 60)

for calls in monthly_calls:

    full_cost = (
        full_context_cost * calls
    )

    rag_total = (
        rag_cost * calls
    )

    savings = full_cost - rag_total

    savings_percent = (
        savings / full_cost
    ) * 100

    print()
    print(f"Chamadas: {calls:,}")
    print(f"Full Context: US$ {full_cost:,.2f}")
    print(f"RAG:          US$ {rag_total:,.2f}")
    print(f"Economia:     US$ {savings:,.2f}")
    print(f"Redução:      {savings_percent:.2f}%")


# ============================================================
# RESUMO
# ============================================================

print()
print("=" * 60)
print("RESUMO")
print("=" * 60)

print(
    f"Custo Full Context: "
    f"US$ {full_context_cost:.4f} / chamada"
)

print(
    f"Custo RAG:          "
    f"US$ {rag_cost:.4f} / chamada"
)

print(
    f"Custo Sumarização:  "
    f"US$ {summary_query_cost:.4f} / chamada"
)

print(
    f"Custo RAG + Cache:  "
    f"US$ {rag_cache_cost:.4f} / chamada"
)

print()
print(
    f"Custo inicial da sumarização: "
    f"US$ {summary_generation_cost:.2f}"
)