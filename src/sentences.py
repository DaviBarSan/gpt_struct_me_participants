"""Sentence segmentation for the sentence-level experiments."""

import re
from typing import List, Tuple


# Same pattern `get_full_sentence` (src/utils.py) uses to locate the sentence a
# gold annotation lives in: a sentence-final punctuation mark followed by
# whitespace, or one or more newlines. The newline branch matters for the Lusa
# articles, whose paragraphs - and a few of whose headline-style sentences -
# are separated by bare newlines without final punctuation.
SENTENCE_DELIMITER = re.compile(r"(?<=[.!?])\s+|\n+")


def split_sentences_with_offsets(
    text: str, skip_headline: bool = True
) -> List[Tuple[int, str, int, int]]:
    """Split `text` into `(sentence_id, sentence, start, end)` tuples.

    Same segmentation and same ids as `split_sentences`, plus the character span
    the stripped sentence occupies in `text`. The span is what lets a gold
    annotation - which carries an offset into the document, not a sentence id -
    be attributed to the sentence it was annotated in.

    Args:
        text: The document body to segment.
        skip_headline: Drop the headline, i.e. everything before the first
            newline. `LusaDocument` already strips the two boilerplate lines
            preceding it (the dateline and the "APM // MSP" initials marker),
            leaving the headline as the first line of the text - and it carries
            no annotation in 92 of the 116 English documents, so asking a model
            about it would score its answer against gold that was never
            recorded. Ids are still assigned over *all* segments before the
            headline is dropped, so the id of a body sentence does not depend on
            this flag and stays valid for raw answers already on disk.

    Returns:
        A list of `(sentence_id, sentence, start, end)` tuples, where
        `text[start:end] == sentence`.
    """
    # Mirrors `re.split` on a pattern without capture groups: the segments are
    # the gaps between consecutive delimiter matches, plus the tail.
    spans = []
    cursor = 0
    for match in SENTENCE_DELIMITER.finditer(text):
        spans.append((cursor, match.start()))
        cursor = match.end()
    spans.append((cursor, len(text)))

    sentences = []
    for start, end in spans:
        segment = text[start:end]
        stripped = segment.strip()
        if not stripped:
            continue
        offset = start + (len(segment) - len(segment.lstrip()))
        sentences.append((len(sentences), stripped, offset, offset + len(stripped)))

    if skip_headline:
        headline_end = text.find("\n")
        # A document with no newline at all is a single line: there is no body to
        # keep, so nothing is dropped.
        if headline_end != -1:
            sentences = [s for s in sentences if s[2] >= headline_end]
    return sentences


def split_sentences(text: str, skip_headline: bool = True) -> List[Tuple[int, str]]:
    """Split `text` into `(sentence_id, sentence)` pairs.

    Ids are 0-based positions in the sequence of non-empty sentences, which
    makes them stable for a given document text and safe to use as filename
    stems. Empty and whitespace-only segments are dropped, so an id is never
    handed out for something the model could not be asked about.

    Args:
        text: The document body to segment.
        skip_headline: Drop the headline; see `split_sentences_with_offsets`.

    Returns:
        A list of `(sentence_id, sentence)` pairs, sentences stripped. With the
        headline skipped the first id is the headline's successor, not 0.
    """
    # Delegates so the ids here and the ids used to align annotations can never
    # drift apart - raw answer filenames are keyed by them.
    return [
        (sid, sentence)
        for sid, sentence, _, _ in split_sentences_with_offsets(text, skip_headline)
    ]
