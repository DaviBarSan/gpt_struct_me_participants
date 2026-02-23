"""Utility functions for the project."""

import json
import re
from difflib import SequenceMatcher



def is_sublist(list1: list, list2: list) -> bool:
    """Check if list1 is a subset of list2."""
    if len(list1) > len(list2):
        return False

    for i in range(len(list2) - len(list1) + 1):
        if list2[i:i + len(list1)] == list1:
            return True
    return False


def string_overlap(source: str, target: str) -> bool:
    """Check if two strings overlap at the word level."""
    if source == "" or target == "":
        return False

    tkns_src = tokenize(source)
    tkns_tgt = tokenize(target)
    # print(f"Tokenized source: {tkns_src}")
    # print(f"Tokenized target: {tkns_tgt}")
    src_in_tgt = is_sublist(tkns_src, tkns_tgt)
    tgt_in_src = is_sublist(tkns_tgt, tkns_src)
    if src_in_tgt or tgt_in_src:
        return True

    for idx in range(len(tkns_src)):
        starts = " ".join(tkns_src[idx:])
        if starts and target.startswith(starts):
            return True

        ends = " ".join(tkns_src[:-idx])
        if ends and target.endswith(ends):
            return True

    return False


def tokenize(text):
    """Simple tokenizer."""
    try:
        text = re.sub(r'[^\w\s]', ' ', text)
    except TypeError:
        print(f"Error tokenizing text: {text}")        
    tokens = text.lower().split()
    print(f"Tokens after tokenization: {tokens}")
    return tokens


def is_json(text: str) -> bool:
    """Check if the text is a valid JSON."""
    try:
        json.loads(text)
        return True
    except json.decoder.JSONDecodeError:
        return False

def get_best_match(pred_tokens, annotations):
    best_ratio = 0
    best_anno = None
    anno_type = None
    pred_str = " ".join(pred_tokens).lower()
    for anno_text, label in annotations:
        # Calculamos a similaridade entre a predição e cada anotação
        ratio = SequenceMatcher(None, pred_str, anno_text.lower()).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_anno = anno_text
            anno_type = label
    # Definir um threshold mínimo (ex: 0.4) para evitar matches aleatórios
    # print(f"Best match: '{best_anno}' with ratio {best_ratio} and type '{anno_type}'")
    return (best_anno, anno_type) if best_ratio > 0.5 else ("", "")