"""Compile the raw sentence-level answers into per-document artefacts.

`experiments/test_sentence.py` writes one raw answer file per sentence per step.
This script folds them back up to the document level, which is the unit the gold
annotations and the whole evaluation stack are keyed by, producing three things
per document:

    overview/.../<doc_id>.json  - per-sentence summary: the sentence, whether
                                  the model said it mentions participants, what
                                  was extracted and how it was classified.
    ext/.../<doc_id>.txt        - every extracted span in the document, as the
                                  JSON list an `ext` prompt would have answered.
    cls/.../<doc_id>.txt        - every classified span, as the JSON list of
                                  [entity, class] pairs a `cls` prompt would
                                  have answered.

The last two are written into a directory layout `experiments.parse` already
understands, so the existing pipeline evaluates a sentence-level run unchanged:

    python -m experiments.parse    --mode sentence_level/ext --language english
    python -m experiments.evaluate --mode sentence_level/ext --language english

Being a pure function of the raw answers, this can be re-run at will (e.g. after
changing the de-duplication policy) without issuing a single request.
"""

import csv
import json
import sys
import logging
from pathlib import Path
from typing import List, Tuple

# Must run before `import fire`: on Windows, fire wraps whatever sys.stdout is
# at import time with colorama, which writes through the console's cp1252
# codepage. Model outputs routinely contain characters outside cp1252, which
# would otherwise crash print() mid-run and abort the compilation.
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import fire

from experiments.parse import read_json, read_text_safe
from experiments.test_sentence import (
    RAW_PATH,
    SENTENCE_PATH,
    modifiers_from_run_name,
    read_detection,
    templates_for,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUMMARY_HEADER = (
    "doc_id", "n_sentences", "n_detected", "n_not_detected", "n_detection_unparseable",
    "n_extracted_spans", "n_classified_spans", "n_unlisted_spans", "n_parse_failures",
)


def read_pairs(path: Path, template: str) -> Tuple[List[Tuple[str, str]], str]:
    """Read a classification answer as `[(entity, class), ...]`.

    A missing class is kept as an empty string rather than dropped, so
    `src.evaluate.normalize_type` can report it as "N/A" instead of the span
    vanishing from the predictions.
    """
    answer, status = read_json(path, template)
    if not isinstance(answer, list):
        return [], status

    pairs = []
    for item in answer:
        if not isinstance(item, list) or len(item) != 2:
            continue
        entity, class_ = item
        if not isinstance(entity, str) or not entity.strip():
            continue
        pairs.append((entity.strip(), "" if class_ is None else str(class_).strip()))
    return pairs, status


def read_spans(path: Path, template: str) -> Tuple[List[str], str]:
    """Read an extraction answer as a list of spans."""
    answer, status = read_json(path, template)
    if not isinstance(answer, list):
        return [], status

    spans = [span.strip() for span in answer if isinstance(span, str) and span.strip()]
    return spans, status


def compile_doc(doc_path: Path, ext_tid: str, cls_tid: str) -> dict:
    """Fold one document's raw sentence answers into its three artefacts."""
    sentences = json.loads((doc_path / "sentences.json").read_text(encoding="utf-8"))

    records = []
    ext_spans, cls_pairs, failures, unlisted = [], [], [], []
    n_detected = n_not_detected = n_unparseable = 0

    for entry in sentences:
        sid = entry["sentence_id"]
        det_path = doc_path / f"{sid:03d}_det.txt"
        if not det_path.exists():
            # The run stopped before reaching this sentence. Recorded rather
            # than skipped, so a partially compiled document is visible as such
            # instead of looking like a document with fewer sentences.
            records.append({
                "sentence_id": sid,
                "full_sentence": entry["full_sentence"],
                "detection": "missing",
                "extracted": [],
                "participants": {},
            })
            continue

        detection = read_detection(read_text_safe(det_path))
        if detection == "yes":
            n_detected += 1
        elif detection == "no":
            n_not_detected += 1
        else:
            n_unparseable += 1

        extracted: List[str] = []
        ext_path = doc_path / f"{sid:03d}_ext.txt"
        if ext_path.exists():
            extracted, status = read_spans(ext_path, ext_tid)
            if status != "ok":
                failures.append((ext_path, status))
            ext_spans.extend(extracted)

        participants = {}
        cls_path = doc_path / f"{sid:03d}_cls.txt"
        if cls_path.exists():
            pairs, status = read_pairs(cls_path, cls_tid)
            if status != "ok":
                failures.append((cls_path, status))
            cls_pairs.extend(pairs)
            # Last one wins within a sentence, matching how `src.evaluate`
            # builds its prediction lookup.
            participants = {entity: class_ for entity, class_ in pairs}
            unlisted.extend(
                entity for entity, _ in pairs if entity not in set(extracted)
            )

        records.append({
            "sentence_id": sid,
            "full_sentence": entry["full_sentence"],
            "detection": detection,
            "extracted": extracted,
            "participants": participants,
        })

    # De-duplicate document-wide, keeping first occurrence: a span mentioned in
    # three sentences is one prediction for the document, and `src.evaluate`
    # set-ifies the predictions anyway - but doing it here keeps the artefacts
    # honest about what is being scored.
    ext_unique = list(dict.fromkeys(ext_spans))
    cls_unique = [list(pair) for pair in dict.fromkeys(cls_pairs)]

    overview = {
        "doc_id": doc_path.name,
        "n_sentences": len(sentences),
        "n_detected": n_detected,
        "n_extracted_spans": len(ext_unique),
        "n_classified_spans": len(cls_unique),
        "sentences": records,
    }
    summary = (
        doc_path.name, len(sentences), n_detected, n_not_detected, n_unparseable,
        len(ext_unique), len(cls_unique), len(set(unlisted)), len(failures),
    )
    return {
        "overview": overview,
        "ext": ext_unique,
        "cls": cls_unique,
        "failures": failures,
        "summary": summary,
    }


def compile_run(exp_path: Path, language: str) -> Tuple[int, int]:
    """Compile every document of one raw run.

    Args:
        exp_path: `raw/<language>/<mid>/<entity>/<run>/<exp_suffix>`.
        language: Corpus language, used to place the outputs.

    Returns:
        `(n_documents, n_parse_failures)`.
    """
    mid, entity, run_name, exp_suffix = exp_path.parts[-4:]
    definition, example = modifiers_from_run_name(run_name)
    ext_tid, cls_tid = templates_for(definition, example)
    logger.info(f"Compiling {mid}/{entity}/{run_name}/{exp_suffix} -> {ext_tid}, {cls_tid}")

    overview_path = SENTENCE_PATH / "overview" / language / mid / entity / run_name / exp_suffix
    ext_path = SENTENCE_PATH / "ext" / language / mid / entity / ext_tid / f"{ext_tid}_{exp_suffix}"
    cls_path = SENTENCE_PATH / "cls" / language / mid / entity / cls_tid / f"{cls_tid}_{exp_suffix}"
    for path in (overview_path, ext_path, cls_path):
        path.mkdir(parents=True, exist_ok=True)

    summaries, failures = [], []
    doc_paths = sorted(p for p in exp_path.iterdir() if p.is_dir())
    for doc_path in doc_paths:
        if not (doc_path / "sentences.json").exists():
            logger.warning(f"Skipping {doc_path}: no sentences.json.")
            continue

        compiled = compile_doc(doc_path, ext_tid, cls_tid)
        doc_id = doc_path.name

        (overview_path / f"{doc_id}.json").write_text(
            json.dumps(compiled["overview"], ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (ext_path / f"{doc_id}.txt").write_text(
            json.dumps(compiled["ext"], ensure_ascii=False), encoding="utf-8"
        )
        (cls_path / f"{doc_id}.txt").write_text(
            json.dumps(compiled["cls"], ensure_ascii=False), encoding="utf-8"
        )

        summaries.append(compiled["summary"])
        failures.extend(compiled["failures"])

    with (overview_path / "detection_summary.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(SUMMARY_HEADER)
        writer.writerows(summaries)

    failures_path = overview_path / "sentence_parse_failures.txt"
    if failures:
        failures_path.write_text(
            "\n".join(f"{status}\t{path}" for path, status in failures), encoding="utf-8"
        )
    elif failures_path.exists():
        failures_path.unlink()

    n_sentences = sum(row[1] for row in summaries)
    n_detected = sum(row[2] for row in summaries)
    logger.info(
        f"  {len(summaries)} documents, {n_sentences} sentences, "
        f"{n_detected} with participants detected, {len(failures)} unparseable answers"
    )
    return len(summaries), len(failures)


def main(language: str = "english", mid: str = None) -> None:
    """Run the script.

    Args:
        language: Corpus language to compile.
        mid: Optional model id, to compile only that model's raw answers.
    """
    root = RAW_PATH / language
    if not root.exists():
        raise SystemExit(f"No raw sentence-level answers at {root}")

    # raw/<language>/<mid>/<entity>/<run>/<exp_suffix>
    exp_paths = sorted(p for p in root.glob("*/*/*/*") if p.is_dir())
    if mid:
        exp_paths = [p for p in exp_paths if p.parts[-4] == mid]
    if not exp_paths:
        raise SystemExit(f"No raw runs found under {root}" + (f" for model {mid}" if mid else ""))

    n_docs = n_failures = 0
    for exp_path in exp_paths:
        docs, failures = compile_run(exp_path, language)
        n_docs += docs
        n_failures += failures

    print(f"\nCompiled {n_docs} documents across {len(exp_paths)} run(s), "
          f"{n_failures} unparseable sentence answers.")
    print("\nNext, to score the two phases with the existing pipeline:")
    for phase in ("ext", "cls"):
        print(f"  python -m experiments.parse    --mode sentence_level/{phase} --language {language}")
        print(f"  python -m experiments.evaluate --mode sentence_level/{phase} --language {language}")


if __name__ == "__main__":
    fire.Fire(main)
