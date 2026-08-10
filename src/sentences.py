"""Sentence segmentation for the sentence-level experiments."""

import re
from typing import List, Tuple


# Same pattern `get_full_sentence` (src/utils.py) uses to locate the sentence a
# gold annotation lives in: a sentence-final punctuation mark followed by
# whitespace, or one or more newlines. The newline branch matters for the Lusa
# articles, whose paragraphs - and a few of whose headline-style sentences -
# are separated by bare newlines without final punctuation.
SENTENCE_DELIMITER = re.compile(r"(?<=[.!?])\s+|\n+")


def split_sentences(text: str) -> List[Tuple[int, str]]:
    """Split `text` into `(sentence_id, sentence)` pairs.

    Ids are 0-based positions in the sequence of non-empty sentences, which
    makes them stable for a given document text and safe to use as filename
    stems. Empty and whitespace-only segments are dropped, so an id is never
    handed out for something the model could not be asked about.

    Args:
        text: The document body to segment.

    Returns:
        A list of `(sentence_id, sentence)` pairs, sentences stripped.
    """
    segments = SENTENCE_DELIMITER.split(text)
    return list(enumerate(
        segment.strip() for segment in segments if segment and segment.strip()
    ))
