"""Parse models predictions."""

import json
import logging
from pathlib import Path
import re
import chardet
import fire
from src.utils import is_json

from experiments.constants import ROOT

logging.basicConfig(level=logging.INFO)

RESULTS_PATH = ROOT / "results"



def detect_encoding(file_path: str, buffer_size: int = 4096) -> str:
    """
    Detects the encoding of a file and reads its content using that encoding.

    Since encoding detection is probabilistic, it only reads a sample of the 
    file (buffer_size) for speed, but the whole file is read using the 
    detected encoding.

    Args:
        file_path: The path to the text file.
        buffer_size: The number of bytes to read for encoding detection.

    Returns:
        A tuple (detected_encoding, file_content) or (None, None) if an error occurs.
    """
    p = Path(file_path)

    if not p.is_file():
        print(f"Error: File not found at '{file_path}'")
        return None
        
    try:
        # Step 1: Read a sample of the file in binary mode for detection
        with open(p, 'rb') as f:
            sample_bytes = f.read(buffer_size)

        # Step 2: Use chardet to detect the encoding
        detection_result = chardet.detect(sample_bytes)
        
        detected_encoding = detection_result.get('encoding')
        confidence = detection_result.get('confidence')

        if detected_encoding and confidence > 0.5:
            # Normalize common names (e.g., 'ISO-8859-1' is often called 'latin1' in Python)
            if detected_encoding.lower() == 'iso-8859-1':
                python_encoding = 'latin1'
            else:
                # Use the detected encoding for the final read
                python_encoding = detected_encoding
            print(f"Detected Encoding: {python_encoding} (Confidence: {confidence:.2f})")
            return python_encoding
            
        else:
            print(f"Could not confidently detect encoding for '{file_path}'. Falling back to UTF-8.")
            # Fallback to UTF-8, which covers most modern files
            try:
                return 'utf-8'
            except UnicodeDecodeError:
                print("Error: UTF-8 fallback also failed. The file is likely highly corrupted or using a rare encoding.")
                return None
    except Exception as e:
        print(f"An error occurred during file processing: {e}")
        return None

def read_text_safe(filepath: Path) -> str:
    """Read a text file's content, never raising on a bad/misdetected encoding.

    `detect_encoding` is probabilistic and occasionally picks a codec (e.g.
    cp1252) that can't actually decode the file, which used to crash the
    whole parse run on a single bad prediction file. Falls through utf-8 and
    finally latin1, which maps every byte 0-255 and therefore never raises.
    """
    hint = detect_encoding(filepath)
    for encoding in dict.fromkeys([hint, "utf-8", "latin1"]):
        if not encoding:
            continue
        try:
            return filepath.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return filepath.read_text(encoding="latin1")


def strip_thinking(content: str) -> str:
    """Drop a leading reasoning block from `<think>` models, keeping only
    what follows the last `</think>` tag.

    Reasoning text routinely quotes or discusses JSON-shaped examples (e.g.
    example arrays copied from the prompt), which throws off bracket-span
    extraction if left in. The real answer always comes after the block.
    """
    matches = list(re.finditer(r"</think>", content, re.IGNORECASE))
    if matches:
        return content[matches[-1].end():]
    return content


def extract_json_span(content: str) -> str:
    """Return the substring from the first '[' or '{' to the last matching
    closing bracket, for models that skip the <Output> tag and emit the
    JSON array/object directly, sometimes with prose before/after it."""
    starts = [i for i in (content.find("["), content.find("{")) if i != -1]
    if not starts:
        return content
    start = min(starts)
    closer = "]" if content[start] == "[" else "}"
    end = content.rfind(closer)
    if end == -1 or end < start:
        return content
    return content[start:end + 1]


def sanitize_json_string(raw_text: str) -> str:
    """
    Limpa uma string que se espera ser um array ou objeto JSON:
    1. Remove as delimitações de código Markdown (```json, ```) do início/fim.
    2. Substitui espaços não-padrão (\u00A0) por espaços normais (\u0020).
    
    Args:
        raw_text: O conteúdo da string que pode conter delimitações ou espaços problemáticos.
        
    Returns:
        A string limpa, pronta para json.loads().
    """
    # 1. Remover Delimitações Markdown (```json, ```)
    # Primeiro, removemos espaços em branco externos para facilitar a correspondência
    cleaned_text = raw_text.strip()
    
    # Verifica e remove a tag de abertura (```json)
    if cleaned_text.lower().startswith('```json'):
        # Pula '```json' (7 caracteres)
        cleaned_text = cleaned_text[7:]
    
    # Verifica e remove a tag de fecho (```)
    if cleaned_text.endswith('```'):
        # Remove '```' (3 caracteres)
        cleaned_text = cleaned_text[:-3]

    # Remove qualquer espaço em branco adicional que possa ter sido criado
    cleaned_text = cleaned_text.strip()
    # 2. Substituir Espaços Não-Padrão (\u00A0)
    # Este é o caractere de "Non-Breaking Space" que costuma quebrar o json.loads()
    cleaned_text = cleaned_text.replace('\u00A0', ' ')
    
    return cleaned_text



def json_loads_section(content: str) -> dict:
    """Parse a section of a JSON file.

    Grows the candidate string line by line until it becomes valid JSON,
    which recovers cases where the model appended trailing prose after a
    complete JSON value. Lines are joined with a space (not concatenated
    raw) so a literal newline inside a string value doesn't glue two
    tokens together.
    """
    content = content.strip()
    lines = content.split("\n")
    running_content = ""
    while lines:
        running_content += lines.pop(0) + " "
        if is_json(running_content):
            return json.loads(running_content)
    raise ValueError("Invalid JSON")


def read_json(filepath: Path) -> tuple:
    """Read and parse a model's raw text output into JSON.

    Returns (answer, ok). `ok` is False (and answer is {}) when every
    parsing strategy below fails, so callers can report which files
    couldn't be parsed instead of silently treating them like a
    legitimate empty prediction.
    """
    content = read_text_safe(filepath)
    print(f"{filepath}")
    content = strip_thinking(content)
    match = re.search(r"<Output>(.*?)</Output>", content, re.DOTALL)
    if match:
        content = match.group(1)
        print("Extracted String:")
        print(content)
    else:
        print("Output tag not found.")

    content = sanitize_json_string(content)
    content = content.replace('\u00A0', ' ')

    # Try the content as-is first, then fall back to just the outermost
    # bracket span, for models that skip the <Output> tag and/or add
    # leading/trailing prose around the JSON. Also try both wrapped in an
    # outer "[...]", for models that emit comma-separated top-level arrays
    # (e.g. ["a","b"],["c","d"]) without the enclosing list brackets.
    span = extract_json_span(content)
    candidates = dict.fromkeys([content, span, f"[{content}]", f"[{span}]"])
    for candidate in candidates:
        try:
            return json.loads(candidate), True
        except json.decoder.JSONDecodeError:
            pass

        try:
            answer = json_loads_section(candidate)
            print(f"ERROR: but loaded JSON answer: {answer}")
            return answer, True
        except ValueError:
            continue

    print("Failed to parse JSON content after sanitization. Invalid response from model. Returning empty dict.")
    return {}, False


def read_predictions(path: Path, prompt_name_variations: str = "False") -> list:
    """Parse the prediction files."""
    predictions = []
    failed_filepaths = []
    filepaths = path.glob("**/*.txt")

    for filepath in filepaths:
        *_, model, entity, template, _ = filepath.parts
        # if it is a prompt variation, the filepath is different. Set as template the prompt variation abreviations.
        if prompt_name_variations in entity:
            *_, model, entity, _, template, _ = filepath.parts
        doc = filepath.stem

        answer, ok = read_json(filepath)
        if not ok:
            failed_filepaths.append(filepath)

        # print(f"Read answer from {filepath}: {answer}")

        if "ext" in template:
            is_valid = len(answer) and isinstance(answer, list) and isinstance(answer[0], str)
            # print(f"ext task! is valid: {is_valid} -> answer: {answer}")
            
            if not is_valid:
                answer = []

            
            predictions.append({
                "model": model,
                "entity": entity,
                "doc": doc,
                "template": template,
                "answer": answer,
                "entities": answer
            })

        else:
            is_valid = isinstance(answer, list) and \
                all(isinstance(a, list) for a in answer) and \
                all(len(a) == 2 for a in answer) and \
                all(isinstance(a[0], str) for a in answer)
            # print(f"cls task! is valid: {is_valid} -> answer: {answer}")
                
            if not is_valid:
                answer = []

            entities, classes = list(zip(*answer)) if answer else ([], [])
            predictions.append({
                "model": model,
                "entity": entity,
                "doc": doc,
                "template": template,
                "answer": answer,
                "entities": entities,
                "classes": classes
            })

    return predictions, failed_filepaths


def main(mode: str = "prompt_selection", language: str = "portuguese", prompt_name_variations: str = None) -> None:
    """Run the script."""
    path = RESULTS_PATH / mode / language

    print(path)

    predictions, failed_filepaths = read_predictions(path, prompt_name_variations)

    predictions_path = path / "predictions.json"
    json.dump(predictions, predictions_path.open("w"), indent=4)

    total = len(predictions)
    n_failed = len(failed_filepaths)
    print(f"\nParse summary: {total - n_failed}/{total} files parsed successfully, {n_failed} failed.")
    if failed_filepaths:
        print("Failed files:")
        for failed_path in failed_filepaths:
            print(f"  - {failed_path}")

        failures_path = path / "parse_failures.txt"
        failures_path.write_text(
            "\n".join(str(failed_path) for failed_path in failed_filepaths), encoding="utf-8"
        )
        print(f"List of failed files written to {failures_path}")


if __name__ == "__main__":
    fire.Fire(main)
