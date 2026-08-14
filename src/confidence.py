"""Read the per-item confidences the models report, tolerating older answers.

The sentence-level prompts ask for a confidence alongside every prediction, which
widens the answer shapes by one value per element:

    extraction      ["a plane", ...]            -> [["a plane", 0.9], ...]
    classification  [["a plane", "Obj"], ...]   -> [["a plane", "Obj", 0.9], ...]

Every reader here accepts both shapes and reports a missing confidence as None,
so raw answers collected before this feature existed keep parsing exactly as they
did - no re-querying, and no distinction between "was not asked" and "answered
0.0". Callers that only want the prediction can ignore the confidence entirely.
"""

from typing import Optional, Tuple


def as_confidence(value) -> Optional[float]:
    """Coerce a reported confidence to a float in [0, 1], or None.

    Accepts the number itself, a numeric string, and percentages: models asked
    for "a number between 0 and 1" not infrequently answer `85`, and reading that
    as out-of-range - and so discarding it - would lose the measurement rather
    than record it. Anything else, including a bare `1`, is taken at face value.
    """
    if value is None or isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if 0.0 <= number <= 1.0:
        return number
    if 1.0 < number <= 100.0:
        return number / 100.0
    return None


def split_span_confidence(item) -> Tuple[str, Optional[float]]:
    """Read one extraction element as `(span, confidence)`.

    Args:
        item: Either a bare span (the pre-confidence shape) or a
            `[span, confidence]` pair.

    Returns:
        The stripped span - empty when the element is unusable - and its
        confidence, or None when none was reported.
    """
    if isinstance(item, str):
        return item.strip(), None
    if isinstance(item, (list, tuple)) and item:
        span = item[0]
        if not isinstance(span, str):
            return "", None
        confidence = as_confidence(item[1]) if len(item) > 1 else None
        return span.strip(), confidence
    return "", None


def split_pair_confidence(item) -> Tuple[str, str, Optional[float]]:
    """Read one classification element as `(span, class, confidence)`.

    Args:
        item: `[span, class]` (the pre-confidence shape) or
            `[span, class, confidence]`. A two-element item whose second value is
            a number is read as `[span, confidence]`, which is what a model that
            drops the class produces - keeping the confidence is better than
            recording the number as if it were a class name.

    Returns:
        The stripped span - empty when the element is unusable - the class as a
        string, and the confidence or None.
    """
    if not isinstance(item, (list, tuple)) or not item:
        return "", "", None
    span = item[0]
    if not isinstance(span, str) or not span.strip():
        return "", "", None

    if len(item) == 2 and not isinstance(item[1], str):
        confidence = as_confidence(item[1])
        if confidence is not None:
            return span.strip(), "", confidence

    class_ = item[1] if len(item) > 1 else None
    confidence = as_confidence(item[2]) if len(item) > 2 else None
    return span.strip(), "" if class_ is None else str(class_).strip(), confidence
