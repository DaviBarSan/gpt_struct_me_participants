from src.models import (
    gemini,
    amalia,
    gemma3_12b,
    qwen3_4b,
    qwen3_14b,
    qwen3_30b,
    qwen25_14b,
    qwen35_9b,
    mistral_7b,
    phi_4_6b,
    gemma3_1b,
    llama32_3b,
    qwen3_8b
)


def mid2model(mid: str):
    if mid == "gemini":
        return gemini
    elif mid == "amalia":
        return amalia
    elif mid == "qwen3_4b":
        return qwen3_4b
    elif mid == "qwen3_14b":
        return qwen3_14b
    elif mid == "qwen35_9b":
        return qwen35_9b
    elif mid == "mistral_7b":
        return mistral_7b
    elif mid == "phi_4_6b":
        return phi_4_6b
    elif mid == "gemma3_1b":
	    return gemma3_1b
    elif mid == "qwen3_30b":
        return qwen3_30b
    elif mid == "llama32_3b":
        return llama32_3b
    elif mid == "qwen25_14b":
        return qwen25_14b
    elif mid == "qwen3_8b":
        return qwen3_8b
    elif mid == "gemma3_12b":
        return gemma3_12b