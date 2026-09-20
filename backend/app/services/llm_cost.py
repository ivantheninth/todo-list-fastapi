INPUT_PRICE_PER_MILLION = 0.05
OUTPUT_PRICE_PER_MILLION = 0.40


def calculate_llm_cost(
    input_tokens: int,
    output_tokens: int,
) -> float:
    input_cost = (
        input_tokens / 1_000_000
        * INPUT_PRICE_PER_MILLION
    )

    output_cost = (
        output_tokens / 1_000_000
        * OUTPUT_PRICE_PER_MILLION
    )

    return input_cost + output_cost