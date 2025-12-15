from src.models import (
    gemini,
    qwen3_4b,
    mistral_7b,
    phi_4_6b
)


def mid2model(mid: str):
    if mid == "gemini":
        return gemini
    elif mid == "qwen3_4b":
        return qwen3_4b
    elif mid == "mistral_7b":
        return mistral_7b
    elif mid == "phi_4_6b":
        return phi_4_6b