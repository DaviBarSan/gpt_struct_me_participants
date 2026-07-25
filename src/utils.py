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
    entity_id = None
    pred_str = " ".join(pred_tokens).lower()
    for anno_text, label, entity_id, full_sentence in annotations:
        # Calculamos a similaridade entre a predição e cada anotação
        ratio = SequenceMatcher(None, pred_str, anno_text.lower()).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_anno = anno_text
            anno_type = label
            best_entity_id = entity_id
            best_full_sentence, _ = get_full_sentence(full_sentence, best_anno)
    # Definir um threshold mínimo (ex: 0.4) para evitar matches aleatórios
    # print(f"Best match: '{best_anno}' with ratio {best_ratio} and type '{anno_type}'")
    return (best_anno, anno_type, best_entity_id, best_full_sentence) if best_ratio > 0.5 else ("", "", "", "")

def get_full_sentence(full_text, search_part):
    # Split by punctuation AND newlines
    sentences = re.split(r'(?<=[.!?])\s+|\n+', full_text)
    
    best_sentence = None
    highest_match_ratio = 0.0
    
    # Pre-calculate search part data for efficiency
    search_lower = search_part.lower()
    search_len = len(search_lower)
    
    print(f"Searching for: '{search_part}'")
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        sentence_lower = sentence.lower()
        
        # 1. Initialize the matcher
        matcher = SequenceMatcher(None, search_lower, sentence_lower)
        
        # 2. Find the longest contiguous matching block
        match = matcher.find_longest_match(0, search_len, 0, len(sentence_lower))
        
        # 3. Calculate score based ONLY on the search_part length
        # E.g., if search_part is 20 chars, and it found a 19 char match inside a 500 char sentence,
        # the ratio is 19/20 = 0.95 (95% match).
        current_ratio = match.size / search_len
        
        if current_ratio > highest_match_ratio:
            highest_match_ratio = current_ratio
            best_sentence = sentence

    print(f"Full sentence: '{full_text}'")
    print(f"Best matched sentence: '{best_sentence}'")
    print(f"Ratio: {highest_match_ratio:.2f}")
    
    return best_sentence, highest_match_ratio