"""Select the highest-F1 prompt template per (model, entity) from
prompt_selection results and persist it into BEST_TEMPLATES in constants.py.

Requires `experiments.parse` and `experiments.evaluate` to have already been
run in `prompt_selection` mode for the target language, since it reads
results/prompt_selection/{language}/results.csv.
"""

import re
from pathlib import Path

import fire
import pandas as pd

from experiments.constants import RESULTS_PATH

CONSTANTS_PATH = Path(__file__).parent / "constants.py"


def best_templates_from_results(mid: str, language: str) -> dict:
    """Return {entity: template} with the highest strict F1 for `mid`."""
    results_path = RESULTS_PATH / "prompt_selection" / language / "results.csv"
    if not results_path.exists():
        raise FileNotFoundError(
            f"{results_path} not found. Run `experiments.parse` and "
            f"`experiments.evaluate` in prompt_selection mode for '{language}' first."
        )

    df = pd.read_csv(results_path)
    df = df[df["model"] == mid]
    if df.empty:
        raise ValueError(f"No prompt_selection results for model '{mid}' in {results_path}")

    best = df.loc[df.groupby("entity")["f1"].idxmax()]
    return dict(zip(best["entity"], best["template"]))


def update_constants(
    language: str,
    mid: str,
    best_templates: dict,
    constants_path: Path = CONSTANTS_PATH,
) -> None:
    """Update (or add) the BEST_TEMPLATES[language][(mid, entity)] entries."""
    lines = constants_path.read_text(encoding="utf-8").splitlines(keepends=True)

    dict_start = next(i for i, line in enumerate(lines) if line.strip() == "BEST_TEMPLATES = {")
    block_start = next(
        i for i in range(dict_start + 1, len(lines))
        if lines[i].strip() == f'"{language}": {{'
    )
    block_indent = len(lines[block_start]) - len(lines[block_start].lstrip(" "))
    block_end = next(
        i for i in range(block_start + 1, len(lines))
        if lines[i].strip() in ("},", "}")
        and (len(lines[i]) - len(lines[i].lstrip(" "))) == block_indent
    )

    entry_indent = " " * (block_indent + 4)
    for entity, template in best_templates.items():
        key_pattern = re.compile(
            r'^\(\s*["\']' + re.escape(mid) + r'["\']\s*,\s*["\']' + re.escape(entity) + r'["\']\s*\)\s*:'
        )
        new_line = f'{entry_indent}("{mid}", "{entity}"): "{template}",\n'

        for i in range(block_start + 1, block_end):
            stripped = lines[i].lstrip()
            if not stripped.startswith("#") and key_pattern.match(stripped):
                lines[i] = new_line
                break
        else:
            lines.insert(block_end, new_line)
            block_end += 1

    constants_path.write_text("".join(lines), encoding="utf-8")


def main(mid: str, language: str = "portuguese") -> None:
    best_templates = best_templates_from_results(mid, language)
    print(f"Best templates for {mid} / {language}: {best_templates}")
    update_constants(language, mid, best_templates)
    print(f"Updated BEST_TEMPLATES in {CONSTANTS_PATH}")


if __name__ == "__main__":
    fire.Fire(main)
