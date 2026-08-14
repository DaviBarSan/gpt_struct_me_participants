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

and, per run, `overview/.../confidence.csv`: one raw row per prediction that
carries a reported confidence, tagged with the run's identity. The confidences
deliberately do not enter the `ext`/`cls` artefacts - those keep the exact shapes
`experiments.parse` and `src.evaluate` already consume, so scoring is untouched
and the confidences are analysed separately.

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
from typing import List, Optional, Tuple

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
    read_detection_confidence,
    templates_for,
)
from src.confidence import split_pair_confidence, split_span_confidence

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUMMARY_HEADER = (
    "doc_id", "n_sentences", "n_detected", "n_not_detected", "n_detection_unparseable",
    "n_extracted_spans", "n_classified_spans", "n_unlisted_spans", "n_parse_failures",
)

# One row per reported prediction, raw - no averaging - so any downstream
# analysis (calibration curves, confidence against correctness, per-stage
# distributions) can aggregate however it needs to. `label` is the verdict for
# detection and the class for classification; `item` is empty for detection,
# whose confidence is about the sentence as a whole. Every row carries the run's
# identity, so the CSVs of different models, languages and prompt variations can
# be concatenated without losing what produced each number. `template` is the
# stage's own template id, which differs between extraction and classification.
CONFIDENCE_HEADER = (
    "model", "language", "entity", "template", "variation",
    "doc_id", "sentence_id", "stage", "item", "label", "confidence",
)


def read_pairs(path: Path, template: str) -> Tuple[List[Tuple[str, str, Optional[float]]], str]:
    """Read a classification answer as `[(entity, class, confidence), ...]`.

    A missing class is kept as an empty string rather than dropped, so
    `src.evaluate.normalize_type` can report it as "N/A" instead of the span
    vanishing from the predictions. `confidence` is None for answers collected
    before confidences were asked for.
    """
    answer, status = read_json(path, template)
    if not isinstance(answer, list):
        return [], status

    pairs = []
    for item in answer:
        entity, class_, confidence = split_pair_confidence(item)
        if not entity:
            continue
        pairs.append((entity, class_, confidence))
    return pairs, status


def read_spans(path: Path, template: str) -> Tuple[List[Tuple[str, Optional[float]]], str]:
    """Read an extraction answer as `[(span, confidence), ...]`.

    `confidence` is None for answers collected before confidences were asked for.
    """
    answer, status = read_json(path, template)
    if not isinstance(answer, list):
        return [], status

    spans = []
    for item in answer:
        span, confidence = split_span_confidence(item)
        if span:
            spans.append((span, confidence))
    return spans, status


def compile_doc(doc_path: Path, templates: dict, identity: tuple) -> dict:
    """Fold one document's raw sentence answers into its artefacts.

    Args:
        doc_path: The document's directory of raw per-sentence answers.
        templates: Template id per stage - "detection", "extraction",
            "classification" - used both to pick the parse repair ladder and to
            label the confidence rows. Detection has no template of its own, so
            it is labelled with the raw run's name.
        identity: `(model, language, entity, variation)`, prefixed to every
            confidence row so runs can be concatenated downstream.
    """
    sentences = json.loads((doc_path / "sentences.json").read_text(encoding="utf-8"))
    ext_tid, cls_tid = templates["extraction"], templates["classification"]
    model, language, entity_name, variation = identity

    def confidence_row(sid, stage, item, label, confidence):
        """One CONFIDENCE_HEADER row."""
        return (model, language, entity_name, templates[stage], variation,
                doc_path.name, sid, stage, item, label, confidence)

    records = []
    ext_spans, cls_pairs, failures, unlisted = [], [], [], []
    confidences = []
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

        det_answer = read_text_safe(det_path)
        detection = read_detection(det_answer)
        detection_confidence = read_detection_confidence(det_answer)
        confidences.append(
            confidence_row(sid, "detection", "", detection, detection_confidence)
        )
        if detection == "yes":
            n_detected += 1
        elif detection == "no":
            n_not_detected += 1
        else:
            n_unparseable += 1

        extracted: List[str] = []
        extraction_confidence = {}
        ext_path = doc_path / f"{sid:03d}_ext.txt"
        if ext_path.exists():
            spans, status = read_spans(ext_path, ext_tid)
            if status != "ok":
                failures.append((ext_path, status))
            extracted = [span for span, _ in spans]
            ext_spans.extend(extracted)
            for span, span_confidence in spans:
                if span_confidence is not None:
                    extraction_confidence[span] = span_confidence
                confidences.append(
                    confidence_row(sid, "extraction", span, "", span_confidence)
                )

        participants = {}
        classification_confidence = {}
        cls_path = doc_path / f"{sid:03d}_cls.txt"
        if cls_path.exists():
            pairs, status = read_pairs(cls_path, cls_tid)
            if status != "ok":
                failures.append((cls_path, status))
            # The aggregate keeps the (entity, class) shape the document-level
            # `parse`/`evaluate` stack consumes: the confidence travels in
            # confidence.csv instead, so nothing downstream has to change.
            cls_pairs.extend((entity, class_) for entity, class_, _ in pairs)
            # Last one wins within a sentence, matching how `src.evaluate`
            # builds its prediction lookup.
            participants = {entity: class_ for entity, class_, _ in pairs}
            unlisted.extend(
                entity for entity, _, _ in pairs if entity not in set(extracted)
            )
            for entity, class_, pair_confidence in pairs:
                if pair_confidence is not None:
                    classification_confidence[entity] = pair_confidence
                confidences.append(
                    confidence_row(sid, "classification", entity, class_, pair_confidence)
                )

        records.append({
            "sentence_id": sid,
            "full_sentence": entry["full_sentence"],
            "detection": detection,
            "detection_confidence": detection_confidence,
            "extracted": extracted,
            "extraction_confidence": extraction_confidence,
            "participants": participants,
            "classification_confidence": classification_confidence,
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
        "confidences": confidences,
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

    templates = {
        "detection": run_name,
        "extraction": ext_tid,
        "classification": cls_tid,
    }
    identity = (mid, language, entity, exp_suffix)

    summaries, failures, confidences = [], [], []
    doc_paths = sorted(p for p in exp_path.iterdir() if p.is_dir())
    for doc_path in doc_paths:
        if not (doc_path / "sentences.json").exists():
            logger.warning(f"Skipping {doc_path}: no sentences.json.")
            continue

        compiled = compile_doc(doc_path, templates, identity)
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
        confidences.extend(compiled["confidences"])

    with (overview_path / "detection_summary.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(SUMMARY_HEADER)
        writer.writerows(summaries)

    # Only written when the run actually reported confidences: a run collected
    # before the feature existed would otherwise get a file of empty values,
    # which reads as "the model was unsure" rather than "was never asked".
    confidence_path = overview_path / "confidence.csv"
    n_reported = sum(1 for row in confidences if row[-1] is not None)
    if n_reported:
        with confidence_path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(CONFIDENCE_HEADER)
            writer.writerows(confidences)
        logger.info(f"  {n_reported} of {len(confidences)} predictions carry a confidence "
                    f"-> {confidence_path}")
    elif confidence_path.exists():
        confidence_path.unlink()

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
