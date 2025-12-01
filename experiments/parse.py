"""Parse models predictions."""

import json
import logging
from pathlib import Path
<<<<<<< HEAD
import chardet
=======

>>>>>>> origin/main
import fire
from src.utils import is_json

from constants import ROOT

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
    """Parse a section of a JSON file."""
    content = content.strip()
    lines = content.split("\n")
    running_content = ""
    while lines:
        running_content += lines.pop(0)
        if is_json(running_content):
            return json.loads(running_content)
    raise ValueError("Invalid JSON")


def read_json(filepath: Path) -> dict:
    """Read a JSON file."""
<<<<<<< HEAD
    encoding = detect_encoding(filepath)
    content = filepath.read_text(encoding=encoding)
    content = sanitize_json_string(content)
    content = content.replace('\u00A0', ' ')
    print(filepath.absolute)
    try:
        answer = json.loads(content)
        print(f"Loaded JSON answer: {answer}")
=======
    content = filepath.read_text()
    try:
        answer = json.loads(content)
>>>>>>> origin/main
        return answer

    except json.decoder.JSONDecodeError:
        try:
            answer = json_loads_section(content)
<<<<<<< HEAD
            print(f"ERROR: but loaded JSON answer: {answer}")

            return answer
        
        except ValueError:
            raise
=======
            return answer
        
        except ValueError:
            print(filepath)
            return []
>>>>>>> origin/main


def read_predictions(path: Path):
    """Parse the prediction files."""
    predictions = []
    filepaths = path.glob("**/*.txt")
<<<<<<< HEAD
    
=======
>>>>>>> origin/main
    for filepath in filepaths:
        *_, model, entity, template, _ = filepath.parts
        doc = filepath.stem

        answer = read_json(filepath)
<<<<<<< HEAD
        # print(f"Read answer from {filepath}: {answer}")

        if "ext" in template:
            is_valid = len(answer) and isinstance(answer, list) and isinstance(answer[0], str)
            # print(f"ext task! is valid: {is_valid} -> answer: {answer}")
            
            if not is_valid:
                answer = []

            
=======

        if "ext" in template:
            is_valid = len(answer) and isinstance(answer, list) and isinstance(answer[0], str)
            if not is_valid:
                answer = []

>>>>>>> origin/main
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
<<<<<<< HEAD
            # print(f"cls task! is valid: {is_valid} -> answer: {answer}")
=======
>>>>>>> origin/main
                
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

    return predictions


def main(mode: str = "prompt_selection", language: str = "portuguese") -> None:
    """Run the script."""
    path = RESULTS_PATH / mode / language

<<<<<<< HEAD
    print(path)

=======
>>>>>>> origin/main
    predictions = read_predictions(path)

    predictions_path = path / "predictions.json"
    json.dump(predictions, predictions_path.open("w"), indent=4)


if __name__ == "__main__":
    fire.Fire(main)
