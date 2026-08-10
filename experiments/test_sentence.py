"""Run the best prompt for each model on the test set, one sentence at a time.

The document-level counterpart is `experiments/test.py`, which sends a whole
article per request. Here every article is segmented into sentences and each
sentence goes through three requests:

    1. detection      - does this sentence mention any <entity>? (yes/no)
    2. extraction     - if yes, extract the <entity> spans (`ext` prompt)
    3. classification - classify the spans extraction returned (`cls` prompt,
                        conditioned on those candidates)

Both prompts keep the modifiers (`def`, `exp`) of the model's document-level
winner in `BEST_TEMPLATES`, so a sentence-level run stays comparable to the
document-level one it is contrasted against.

Only raw answers are written here - one file per sentence per step - so an
interrupted run resumes at the sentence it stopped on and re-deriving the
per-document artefacts never costs another request. Turning them into the files
`experiments.parse`/`experiments.evaluate` consume is
`experiments/compile_sentence.py`'s job.
"""

import json
import re
import sys
import time
import logging
from pathlib import Path
from typing import List, Tuple

# Windows consoles default to the cp1252 codepage, which can't represent every
# Unicode character a model may generate (smart quotes, non-breaking hyphens,
# etc.), crashing the whole run on a plain print()/log call. Force UTF-8 on the
# output streams themselves; this doesn't touch the actual prompt/answer strings.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

import fire
import dotenv
import yaml

from experiments.constants import (
    BEST_TEMPLATES,
    ENTITIES,
    EXAMPLERS,
    RESOURCE_PATH,
    ROOT,
    SAMPLE_DOCS_IDS
)
from experiments.parse import read_json, read_text_safe, strip_thinking

from src.prompts import Prompter
from src.sentences import split_sentences

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dotenv.load_dotenv(ROOT / ".env")

SENTENCE_PATH = ROOT / "results" / "sentence_level"
RAW_PATH = SENTENCE_PATH / "raw"

# "yes"/"no" in both corpus languages. Models answer the detection request with
# a bare word most of the time, but also with "No, there are no participants
# in this sentence." - hence a word-boundary search rather than an equality test.
DETECTION_TOKENS = re.compile(r"\b(yes|no|sim|n[aã]o)\b", re.IGNORECASE)
POSITIVE_TOKENS = {"yes", "sim"}


def run_dir_name(definition: bool, example: bool) -> str:
    """Name of the raw-run directory, encoding the prompt modifiers in play.

    A single raw run holds all three steps, so it is named after the modifier
    set (`sent_def_exp`) rather than after either step's template id.
    """
    return "sent" + ("_def" if definition else "") + ("_exp" if example else "")


def modifiers_from_run_name(run_name: str) -> Tuple[bool, bool]:
    """Recover `(definition, example)` from a raw-run directory name."""
    parts = run_name.split("_")
    return "def" in parts, "exp" in parts


def templates_for(definition: bool, example: bool) -> Tuple[str, str]:
    """The `(extraction, classification)` template ids for a modifier set.

    Careful with the naming: `experiments.parse` and `src.evaluate` both branch
    on `"ext" in template`, so a classification template id must never contain
    the substring "ext".
    """
    suffix = ("_def" if definition else "") + ("_exp" if example else "")
    return f"ext{suffix}", f"cls{suffix}"


def read_detection(answer: str) -> str:
    """Read a detection answer as "yes", "no" or "unparseable"."""
    match = DETECTION_TOKENS.search(strip_thinking(answer or ""))
    if not match:
        return "unparseable"
    return "yes" if match.group(1).lower() in POSITIVE_TOKENS else "no"


def read_candidates(path: Path, template: str) -> List[str]:
    """Read the extraction answer at `path` as a list of candidate spans.

    Goes through `experiments.parse.read_json`, so the whole repair ladder the
    document-level pipeline relies on (truncated arrays, smart quotes, Python
    literals, `<think>` blocks) applies at sentence granularity too. Duplicates
    are dropped keeping first occurrence, since the same span repeated in one
    answer is one candidate to classify.
    """
    answer, _ = read_json(path, template)
    if not isinstance(answer, list):
        return []
    candidates = [
        span.strip() for span in answer
        if isinstance(span, str) and span.strip()
    ]
    return list(dict.fromkeys(candidates))


def load_dataset(language: str) -> list:
    """Read the corpus for `language`.

    Imported lazily: `src.reader` pulls in `tieval` at module load, which is
    only needed for the TimeBank reader and is not installed everywhere the
    sentence-level driver is exercised.
    """
    from src.reader import read_lusa, read_lusa_en

    if language == "portuguese":
        return read_lusa(RESOURCE_PATH / "lusa_news")
    elif language == "english":
        return read_lusa_en(RESOURCE_PATH / "lusa_en")
    raise ValueError(f"Language {language} not supported.")


def ask(model, path: Path, prompt: str, temp: float, mid: str, sleep: float) -> Tuple[str, bool]:
    """Return the answer at `path`, querying `model` only if it isn't there yet.

    Returns `(answer, queried)`, where `queried` is False when the answer was
    already on disk - which is what makes a run resumable and what the batch
    runner counts to tell a completed phase from a fresh one.
    """
    if path.exists():
        return read_text_safe(path), False

    answer = model(prompt, temp=temp) or ""
    path.write_text(answer, encoding="utf-8")
    logger.info(f"{mid} answer for {path.name}:\n{answer}")
    if sleep > 0:
        time.sleep(sleep)
    return answer, True


def run(
    model,
    mid: str,
    language: str,
    shot_language: str,
    config: dict,
    temp: float = 0.3,
    sleep: float = 20.0,
    docs: str = None,
    ext_template: str = None,
    cls_template: str = None,
) -> None:
    """Query `model` sentence by sentence over the test set.

    `model` is passed in rather than resolved here so the loop can be exercised
    with a stub, without loading a multi-billion parameter checkpoint.
    """
    entities = ENTITIES[language]
    sample_docs = SAMPLE_DOCS_IDS[language]
    examples = EXAMPLERS[shot_language]
    best_templates = BEST_TEMPLATES[language]

    dataset = load_dataset(language)
    shot_dataset = dataset if shot_language == language else load_dataset(shot_language)

    docs2drop = sample_docs + list(examples.values())
    test_docs = [doc for doc in dataset if doc.id not in docs2drop]
    if docs:
        wanted = {d.strip() for d in docs.split(",")} if isinstance(docs, str) else set(docs)
        test_docs = [doc for doc in test_docs if doc.id in wanted]
        logger.info(f"Restricted to {len(test_docs)} document(s): {[d.id for d in test_docs]}")

    doc_sentences = {doc.id: split_sentences(doc.text) for doc in test_docs}
    n_sentences = sum(len(sentences) for sentences in doc_sentences.values())
    n_iter = len(entities) * len(config["prompt_configs"]) * n_sentences
    logger.info(f"{len(test_docs)} documents, {n_sentences} sentences, {n_iter} iterations")

    iter = 0
    n_queries = 0
    for entity in entities:
        logger.info(f"Entity: {entity}")

        tid = best_templates[(mid, entity)]
        # The document-level winner only fixes the modifiers; the sentence-level
        # run always needs both an extraction and a classification prompt.
        definition = "def" in tid
        use_example = "exp" in tid
        if use_example:
            try:
                print(f"Looking for example doc id: {examples[entity]}")
                example_doc_id = examples[entity]
                example = [doc for doc in shot_dataset if doc.id == example_doc_id][0]
            except IndexError:
                print(f"Missing doc_id {example_doc_id} in annotations.")
                continue
        else:
            example = None

        ext_tid, cls_tid = templates_for(definition, use_example)
        ext_tid = ext_template or ext_tid
        cls_tid = cls_template or cls_tid
        logger.info(f"Document-level winner {tid} -> extraction {ext_tid}, classification {cls_tid}")

        for experiment_config in config["prompt_configs"]:
            prompt_config = experiment_config["experiment"]
            prompter_kwargs = dict(
                entity=entity,
                definition=definition,
                delimiter=prompt_config["delimiters"],
                role=prompt_config["role"],
                language=language,
                constraints=prompt_config["constraints"],
                chain_of_thought=prompt_config["chain_of_thought"],
            )
            det_prompter = Prompter(task="detection", example=None, **prompter_kwargs)
            ext_prompter = Prompter(task="extraction", example=example, **prompter_kwargs)
            cls_prompter = Prompter(task="classification", example=example, candidates=True, **prompter_kwargs)

            exp_suffix = (
                f"temp{temp}"
                f"_{'delim' if prompt_config['delimiters'] else 'nodelim'}"
                f"_{'role' if prompt_config['role'] else 'norole'}"
                f"_{'cot' if prompt_config['chain_of_thought'] else 'nocot'}"
            )
            run_path = (
                RAW_PATH / language / mid / entity
                / run_dir_name(definition, use_example) / exp_suffix
            )

            for doc in test_docs:
                sentences = doc_sentences[doc.id]
                doc_path = run_path / doc.id
                doc_path.mkdir(parents=True, exist_ok=True)
                # Persist the segmentation next to the answers so the compile
                # step never has to re-split the text or re-read the corpus.
                (doc_path / "sentences.json").write_text(
                    json.dumps(
                        [{"sentence_id": sid, "full_sentence": text} for sid, text in sentences],
                        ensure_ascii=False, indent=2,
                    ),
                    encoding="utf-8",
                )

                for sid, sentence in sentences:
                    logger.info(f"Iteration {iter}/{n_iter}")
                    iter += 1
                    queried = False

                    det_path = doc_path / f"{sid:03d}_det.txt"
                    print(f"Detection prompt: {det_prompter.generate(sentence)}")
                    det_answer, det_queried = ask(model, det_path, det_prompter.generate(sentence), temp, mid, sleep)
                    queried = queried or det_queried
                    detection = read_detection(det_answer)

                    # An unreadable detection answer opens the gate rather than
                    # closing it: a parser miss must not cost the sentence's
                    # participants, which would be indistinguishable from the
                    # model judging the sentence empty.
                    if detection == "no":
                        logger.info(f"Sentence {sid}: no {entity} detected, skipping extraction.")
                    else:
                        if detection == "unparseable":
                            logger.info(f"Sentence {sid}: detection answer unreadable, extracting anyway.")

                        ext_path = doc_path / f"{sid:03d}_ext.txt"
                        print(f"Extraction prompt: {ext_prompter.generate(sentence)}")
                        _, ext_queried = ask(model, ext_path, ext_prompter.generate(sentence), temp, mid, sleep)
                        queried = queried or ext_queried

                        candidates = read_candidates(ext_path, ext_tid)
                        if candidates:
                            cls_path = doc_path / f"{sid:03d}_cls.txt"
                            print(f"Classification prompt: {cls_prompter.generate(sentence, candidates=candidates)}")
                            _, cls_queried = ask(
                                model, cls_path,
                                cls_prompter.generate(sentence, candidates=candidates),
                                temp, mid, sleep,
                            )
                            queried = queried or cls_queried
                        else:
                            logger.info(f"Sentence {sid}: nothing extracted, skipping classification.")

                    if queried:
                        n_queries += 1
                    else:
                        logger.info(f"{mid} answer already exists.")

    logger.info(f"Finished: {iter} iterations, {n_queries} sentences queried.")


def main(
    mid: str = "gemini",
    language: str = "english",
    shot_language: str = "english",
    config_path: str = "experiments/exp_config.yaml",
    temp: float = 0.3,
    sleep: float = 20.0,
    docs: str = None,
    ext_template: str = None,
    cls_template: str = None,
) -> None:
    """Main script.

    Args:
        mid: Model id, as accepted by `experiments.utils.mid2model`.
        language: Corpus language to run on.
        shot_language: Language the few-shot example document is taken from.
        config_path: YAML with the prompt-variation configs to run.
        temp: Sampling temperature.
        sleep: Seconds to wait after each request. Rate limiting only matters
            for the hosted APIs; set 0 for the local vLLM models, where the
            document-level pipeline's hardcoded 20s would add days to a run
            that now issues up to three requests per sentence.
        docs: Optional comma-separated document ids, for a smoke test.
        ext_template: Override the extraction template id.
        cls_template: Override the classification template id.
    """
    # Imported here because `src.models` pulls in torch/transformers at module
    # load, which the compile and inspection paths have no need for.
    from experiments.utils import mid2model

    model = mid2model(mid)
    logger.info(f"Using temperature: {temp}, sleep: {sleep}s")
    config = yaml.safe_load(open(config_path))
    print(f"Config: {config}")

    run(
        model=model,
        mid=mid,
        language=language,
        shot_language=shot_language,
        config=config,
        temp=temp,
        sleep=sleep,
        docs=docs,
        ext_template=ext_template,
        cls_template=cls_template,
    )


if __name__ == "__main__":
    fire.Fire(main)
