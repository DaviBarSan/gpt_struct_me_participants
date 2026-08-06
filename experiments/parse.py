"""Parse models predictions."""

import sys

# Must run before `import fire`: on Windows, fire wraps whatever sys.stdout
# is at import time with colorama, which writes through the console's cp1252
# codepage. Model outputs routinely contain characters outside cp1252 (e.g.
# '√'), which would otherwise crash print() mid-run and abort parsing.
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

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

    Prediction files are always written as UTF-8 by the generation pipeline
    (see `answer_path.write_text(..., encoding='utf-8')` in
    experiments/prompt_selection.py), so UTF-8 is tried first. Being strict,
    it fails loudly on genuinely non-UTF-8 bytes instead of risking chardet
    guessing a wrong 8-bit codec (e.g. it once called a UTF-8 file "MacRoman"
    at 0.69 confidence), which silently turns valid UTF-8 bytes into mojibake
    rather than raising. `detect_encoding` is only consulted as a fallback,
    and finally latin1, which maps every byte 0-255 and therefore never
    raises.
    """
    try:
        return filepath.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        pass

    hint = detect_encoding(filepath)
    for encoding in dict.fromkeys([hint, "latin1"]):
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
    """Return the substring from the first '[' or '{' to its balanced
    closing bracket, for models that skip the <Output> tag and/or emit
    trailing garbage (stray extra brackets, end-of-turn tokens, prose)
    after the JSON value. Tracks bracket depth (ignoring brackets inside
    quoted strings) rather than jumping to the last bracket in the text,
    so trailing garbage after a complete value doesn't get pulled in."""
    starts = [i for i in (content.find("["), content.find("{")) if i != -1]
    if not starts:
        return content
    start = min(starts)
    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(content)):
        ch = content[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
            if depth == 0:
                return content[start:i + 1]
    return content[start:]


def insert_missing_commas(content: str) -> str:
    """Best-effort repair for a missing comma between adjacent JSON values
    (e.g. `["a", "b"] ["c", "d"]`), a formatting slip some models make when
    an array grows long. Walks the string tracking whether we're inside a
    quoted value, and inserts a comma whenever a closed value (`]`, `}`, or
    a closing quote) is immediately followed - modulo whitespace - by the
    start of the next one (`[`, `{`, or an opening quote), since valid JSON
    never places two sibling values directly next to each other.
    """
    out = []
    in_string = False
    escape = False
    just_closed_value = False
    for ch in content:
        if in_string:
            out.append(ch)
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
                just_closed_value = True
            continue
        if ch.isspace():
            out.append(ch)
            continue
        if just_closed_value and ch in '[{"':
            out.append(",")
        just_closed_value = ch in "]}"
        if ch == '"':
            in_string = True
        out.append(ch)
    return "".join(out)


def close_truncated_json(content: str) -> str:
    """Best-effort repair for JSON truncated mid-generation (e.g. the model
    hit its output token cap before finishing the array). Walks the value
    tracking bracket depth and drops back to the last point where a sibling
    element had just completed (right after a closing `]`/`}`, or right
    before a `,`); if the string is still inside an open array/object at
    that point, drops the incomplete trailing element and appends the
    closing brackets needed to balance what's left. Returns `content`
    unchanged if it's already balanced or has no recoverable safe cut point.
    """
    stack = []
    in_string = False
    escape = False
    start = None
    last_cut = None
    for i, ch in enumerate(content):
        if start is None:
            if ch in "[{":
                start = i
                stack.append(ch)
            continue
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
            continue
        if ch in "[{":
            stack.append(ch)
            continue
        if ch in "]}":
            if stack:
                stack.pop()
            if not stack:
                return content
            last_cut = (i + 1, list(stack))
            continue
        if ch == "," and stack:
            last_cut = (i, list(stack))

    if start is None or not stack or last_cut is None:
        return content

    cut_index, stack_snapshot = last_cut
    truncated = content[start:cut_index]
    closing = "".join("]" if opener == "[" else "}" for opener in reversed(stack_snapshot))
    return truncated + closing


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

    # 3. Normalizar aspas tipograficas (smart quotes) para aspas retas: alguns
    # modelos (ex. llama32_3b) emitem \u201C/\u201D em vez de ", o que o
    # json.loads() nao reconhece como delimitador de string.
    for smart_quote in ('\u201C', '\u201D'):
        cleaned_text = cleaned_text.replace(smart_quote, '"')
    for smart_quote in ('\u2018', '\u2019'):
        cleaned_text = cleaned_text.replace(smart_quote, "'")

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

    # Try the content as-is, then wrapped in an outer "[...]" (for models
    # that emit comma-separated top-level arrays, e.g. ["a","b"],["c","d"],
    # without the enclosing list brackets), then the balanced bracket span
    # (for models that add leading/trailing garbage around a complete JSON
    # value) and that span wrapped too. The wrapped-content check must come
    # before the span, since the span only recovers the first balanced
    # value and would otherwise wrongly short-circuit on the missing-wrapper
    # case.
    span = extract_json_span(content)
    candidates = dict.fromkeys([content, f"[{content}]", span, f"[{span}]"])
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

    # Last resort: repair two common model formatting slips - a missing
    # comma between adjacent array elements, and JSON truncated mid-array
    # because the model hit its output token cap - and retry. Applied only
    # after the strategies above fail, since both repairs are lossy
    # (the comma repair guesses at the model's intent; the truncation
    # repair discards the incomplete trailing element).
    repaired_candidates = dict.fromkeys(
        close_truncated_json(insert_missing_commas(candidate))
        for candidate in candidates
    )
    for candidate in repaired_candidates:
        try:
            answer = json.loads(candidate)
            print(f"ERROR: but loaded JSON answer after repair: {answer}")
            return answer, True
        except json.decoder.JSONDecodeError:
            continue

    print("Failed to parse JSON content after sanitization. Invalid response from model. Returning empty dict.")
    return {}, False


def read_predictions(path: Path) -> list:
    """Parse the prediction files."""
    predictions = []
    failed_filepaths = []
    filepaths = path.glob("**/*.txt")

    for filepath in filepaths:
        if filepath.name == "parse_failures.txt":
            continue
        # A prompt-variation run nests one extra directory between the
        # template and the prediction file, named "<template>_<suffix>"
        # (e.g. cls_exp/cls_exp_temp0.3_nodelim_norole_nocot/doc.txt).
        # Detect it per file from the folder names themselves - rather than
        # a caller-supplied template name - since a single run's results
        # mix models that have variation subfolders with ones that don't.
        *_, model, entity, template, variation, _ = filepath.parts
        if variation.startswith(f"{template}_"):
            template = variation
        else:
            *_, model, entity, template, _ = filepath.parts
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


def main(
    mode: str = "prompt_selection",
    language: str = "portuguese",
    model: str = None,
) -> None:
    """Run the script.

    If `model` is given, only that model's subtree is walked (instead of
    every model under `results/<mode>/<language>`), which is what makes
    re-parsing a single model fast. The result is then merged into the
    existing `predictions.json`/`parse_failures.txt` - replacing only that
    model's entries - since `evaluate.py` expects a single aggregate file
    covering all models.
    """
    path = RESULTS_PATH / mode / language
    parse_path = path / model if model else path

    print(parse_path)

    predictions, failed_filepaths = read_predictions(parse_path)

    predictions_path = path / "predictions.json"
    failures_path = path / "parse_failures.txt"

    if model:
        existing_predictions = []
        if predictions_path.exists():
            existing_predictions = json.loads(predictions_path.read_text(encoding="utf-8"))
            existing_predictions = [p for p in existing_predictions if p["model"] != model]
        predictions = existing_predictions + predictions

        existing_failed_filepaths = []
        if failures_path.exists():
            model_prefix = str(parse_path)
            existing_failed_filepaths = [
                Path(line) for line in failures_path.read_text(encoding="utf-8").splitlines()
                if line and not line.startswith(model_prefix)
            ]
        failed_filepaths = existing_failed_filepaths + failed_filepaths

    json.dump(predictions, predictions_path.open("w"), indent=4)

    total = len(predictions)
    n_failed = len(failed_filepaths)
    print(f"\nParse summary: {total - n_failed}/{total} files parsed successfully, {n_failed} failed.")
    if failed_filepaths:
        print("Failed files:")
        for failed_path in failed_filepaths:
            print(f"  - {failed_path}")

        failures_path.write_text(
            "\n".join(str(failed_path) for failed_path in failed_filepaths), encoding="utf-8"
        )
        print(f"List of failed files written to {failures_path}")
    elif failures_path.exists():
        failures_path.unlink()


if __name__ == "__main__":
    fire.Fire(main)
