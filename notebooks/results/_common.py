"""Shared loading, scoring and plotting helpers for notebooks/results/*.ipynb.

Kept deliberately small: each notebook still owns its own analysis logic,
this module only removes duplication of I/O, the derived type-aware
class-level metric, and the fixed color/style conventions used across all
four notebooks so a given model/language always renders in the same color.
"""
from pathlib import Path

import json
import re

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"
FIGURES_DIR = PROJECT_ROOT / "report" / "Figures" / "results"
BEST_TEMPLATES_PATH = HERE / "best_templates.json"
BEST_CONFIGS_PATH = HERE / "best_configs.json"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)

STAGES = ("prompt_selection", "test")
LANGUAGES = ("portuguese", "english")

# Test-stage runs with no `_temp<T>` suffix in their name predate the
# temperature sweep and used the pipeline default (experiments/test.py).
TEST_DEFAULT_TEMPERATURE = 0.3

# Fixed, colorblind-safe (Okabe-Ito) categorical palettes. Order and colors
# are fixed so a given model/language has the same color in every notebook.
MODEL_ORDER = ["gemini", "gemma3_4b", "gemma3_12b", "qwen3_4b", "qwen3_8b", "qwen3_14b", "amalia", "euro_llm_9b", "gervasio_8b_ptpt"]
MODEL_COLORS = {
    "gemini": "#E69F00",
    "gemma3_4b": "#56B4E9",
    "gemma3_12b": "#CC79A7",
    "qwen3_4b": "#D55E00",
    "qwen3_8b": "#009E73",
    "qwen3_14b": "#F0E442",
    "amalia": "#0072B2",
    "euro_llm_9b": "#000000",
    "gervasio_8b_ptpt": "#999999",
}
LANGUAGE_ORDER = ["portuguese", "english"]
LANGUAGE_COLORS = {
    "portuguese": "#0072B2",
    "english": "#000000",
}
HEATMAP_CMAP = "Blues"

# Canonical display order of the eight prompt variations. Ordered by the two
# prompt-engineering levers under study rather than alphabetically: the
# ext/cls framing alternates fastest, then the class *definition* block, then
# the worked *example*, so each successive pair adds one component
# (bare -> +def -> +exp -> +def+exp). Reading a heatmap row left to right
# therefore reads as an ablation ladder.
PROMPT_VAR_ORDER = [
    "ext", "cls",
    "ext_def", "cls_def",
    "ext_exp", "cls_exp",
    "ext_def_exp", "cls_def_exp",
]

# PROMPT_VAR_ORDER restricted to the classification-framed variations, for
# figures that only concern the `cls_*` family (the `ext_*` templates never
# predict an entity type, so any type-aware view is `cls_*`-only).
CLS_ONLY_PROMPT_VAR_ORDER = ["cls", "cls_def", "cls_exp", "cls_def_exp"]

# llama32_3b's results are invalid (near-zero precision/recall across every
# template/language -- see notebook 01's combined boxplot, where it stood
# out as flat near zero while every other model showed the expected
# *_exp-prompt improvement) and are excluded from all four notebooks via the
# loaders below, rather than filtered ad hoc in each notebook.
EXCLUDED_MODELS = ["llama32_3b", "gemma3_1b", "qwen25_12b"] 

# Type-label normalization, mirroring src/evaluate.py::normalize_type.
#
# The stored CSVs were written by whichever version of that function was
# current when the run happened, so labels the table has only just learned to
# fold ("Nature" -> "Nat") are still spelled the old way on disk. Re-applying
# the mapping at load time makes the notebooks agree with the pipeline without
# re-running evaluation over every result tree. Kept as an independent copy
# rather than an import because this package is run from the notebook
# directory and does not put the project root on sys.path.
TYPE_ABBREVIATIONS = {
    "Object": "Obj",
    "Facility": "Fac",
    "Location": "Loc",
    "Person": "Per",
    "Event": "Eve",
    "Organization": "Org",
    "Nature": "Nat",
    "Other": "Other",
}

_TYPE_LOOKUP = {full.lower(): abbr for full, abbr in TYPE_ABBREVIATIONS.items()}
_TYPE_LOOKUP.update({abbr.lower(): abbr for abbr in TYPE_ABBREVIATIONS.values()})

# Gold annotations use fine-grained location subtypes (Pl_capital, Pl_civil,
# Pl_country, Pl_region, Pl_state, Pl_water) that model outputs never
# reproduce -- predictions only ever use the generic "Loc", or invent subtypes
# of their own that the corpus does not define (Pl_city, Pl_district, ...).
# Left as-is this shows up as a wall of false negatives on every Pl_* class
# that is really a label-granularity mismatch, not an extraction failure:
# Pl_civil predicted as Loc alone accounts for roughly a third of all
# type mismatches on matched spans.
#
# `coarsen_types` therefore collapses *any* Pl_-prefixed label into "Loc",
# rather than an enumerated set of the six the corpus happens to use -- an
# enumeration silently lets the invented subtypes through, so they survive
# coarsening and are still scored as errors. This is the headline view for the
# document-level regime; the fine-grained view remains available by simply not
# calling this.
COARSE_LOCATION_PREFIX = "Pl_"

# The label set the classification prompts actually offer -- the "Classes:"
# line of src/meta.py ("Person, Organization, Object, Location,
# Place (Pl_<type>), Nature, Facility, and Other"), spelled as the corpus
# spells it and expanded over the Pl_* subtypes the gold annotations use.
# Model answers carry a long tail of invented labels on top of this ("Eve",
# "Pl_city", "Nature", ...); those are genuine precision errors, but as
# heatmap columns they are hundreds of near-empty cells, so notebook 03
# restricts the per-class views to the classes the prompt asked for.
PROMPT_CLASSES = [
    "Per", "Org", "Obj", "Nat", "Fac", "Loc",
    "Pl_capital", "Pl_civil", "Pl_country", "Pl_region", "Pl_state", "Pl_water",
    "Other",
]

# PROMPT_CLASSES after `coarsen_types` collapses the Pl_* subtypes into Loc.
PROMPT_CLASSES_COARSE = ["Per", "Org", "Obj", "Nat", "Fac", "Loc", "Other"]


def normalize_type_label(label):
    """Fold one type label to its corpus spelling, case-insensitively.

    Mirrors src/evaluate.py::normalize_type, except that a missing label stays
    missing here rather than becoming the string "N/A" -- the metric helpers
    below distinguish "no type predicted" from "a type outside the schema", and
    collapsing the two would make `ext_*` rows look like out-of-schema
    predictions. Labels the schema does not know are returned verbatim, so the
    reports keep showing what the model actually answered.
    """
    if not isinstance(label, str) or not label.strip():
        return label
    return _TYPE_LOOKUP.get(label.strip().lower(), label.strip())


def normalize_types(df: pd.DataFrame) -> pd.DataFrame:
    """Returns a copy of a detailed_results frame with pred_type/annt_type
    folded to their corpus spellings (see `normalize_type_label`)."""
    df = df.copy()
    for col in ("pred_type", "annt_type"):
        if col in df.columns:
            df[col] = df[col].map(normalize_type_label)
    return df


def coarsen_label(label):
    """Collapse any Pl_-prefixed location subtype into the generic "Loc"."""
    if isinstance(label, str) and label.startswith(COARSE_LOCATION_PREFIX):
        return "Loc"
    return label


def coarsen_types(df: pd.DataFrame) -> pd.DataFrame:
    """Returns a copy of a detailed_results frame with pred_type/annt_type
    location subtypes collapsed into "Loc" (see COARSE_LOCATION_PREFIX)."""
    df = df.copy()
    for col in ("pred_type", "annt_type"):
        if col in df.columns:
            df[col] = df[col].map(coarsen_label)
    return df


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def _drop_malformed(df: pd.DataFrame) -> pd.DataFrame:
    """Drop known-bad rows, e.g. results/test/english/results.csv has a row
    where `template` literally equals `model` ("gemma3_1b"/"gemma3_1b") with
    all-zero metrics -- a data export artifact, not a real result."""
    return df[df["template"] != df["model"]].reset_index(drop=True)


def _drop_excluded_models(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows for models in EXCLUDED_MODELS (see comment at definition)."""
    return df[~df["model"].isin(EXCLUDED_MODELS)].reset_index(drop=True)


def load_results(stage: str, language: str) -> pd.DataFrame:
    """Reads results/{stage}/{language}/results.csv (span-level P/R/F1/F1-r).

    results.csv reports the relaxed score under two averaging schemes,
    `f1_r_micro` (pooled over the corpus) and `f1_r_macro` (one F1 per
    document, then averaged). Every notebook, plot and legend in this package
    refers to a single "F1-r", and that name is bound here to the **macro**
    figure; the micro column stays on the frame as `f1_r_micro` for anyone who
    wants to compare the two. Change the assignment below to switch which
    scheme the whole package reports -- nothing downstream hard-codes it.
    """
    path = RESULTS_DIR / stage / language / "results.csv"
    df = pd.read_csv(path)
    if "f1_r_macro" not in df.columns:
        raise ValueError(
            f"{path} predates the corrected relaxed metrics (no 'f1_r_macro' "
            f"column). Re-run: python -m experiments.evaluate --mode {stage} "
            f"--language {language}"
        )
    df["f1_r"] = df["f1_r_macro"]
    df = _drop_malformed(df)
    df = _drop_excluded_models(df)
    df["stage"] = stage
    df["language"] = language
    return df


def load_detailed(stage: str, language: str) -> pd.DataFrame:
    """Reads results/{stage}/{language}/detailed_results.csv (per-prediction
    tp/fp/fn rows with pred_type/annt_type metadata).

    Type labels are normalized on load (`normalize_types`) so that analyses
    here agree with the pipeline's own spelling regardless of which version of
    src/evaluate.py wrote the file. Location granularity is *not* touched --
    call `coarsen_types` for the coarse view.
    """
    path = RESULTS_DIR / stage / language / "detailed_results.csv"
    df = pd.read_csv(path)
    df = df.rename(columns={"modelo": "model"})
    df = _drop_excluded_models(df)
    df = normalize_types(df)
    df["stage"] = stage
    df["language"] = language
    return df


def load_detailed_token(stage: str, language: str) -> pd.DataFrame:
    """Reads results/{stage}/{language}/detailed_results_token_level.csv
    (word-level LCS match rows with result_type EXACT/PARTIAL/MISS).

    Type labels are normalized on load, as in `load_detailed`.
    """
    path = RESULTS_DIR / stage / language / "detailed_results_token_level.csv"
    df = pd.read_csv(path)
    df = df.rename(columns={"modelo": "model"})
    df = _drop_excluded_models(df)
    df = normalize_types(df)
    df["stage"] = stage
    df["language"] = language
    return df


def save_best_templates(best_templates: dict) -> Path:
    """best_templates: {language: {model: template}}"""
    BEST_TEMPLATES_PATH.write_text(json.dumps(best_templates, indent=2, ensure_ascii=False))
    return BEST_TEMPLATES_PATH


def load_best_templates() -> dict:
    """{language: {model: template}}, produced by 01_prompt_importance.ipynb."""
    if not BEST_TEMPLATES_PATH.exists():
        raise FileNotFoundError(
            f"{BEST_TEMPLATES_PATH} not found -- run 01_prompt_importance.ipynb first."
        )
    return json.loads(BEST_TEMPLATES_PATH.read_text())


def get_best_template(best_templates: dict, language: str, model: str):
    return best_templates.get(language, {}).get(model)


def filter_to_best_templates(df: pd.DataFrame, best_templates: dict, verbose: bool = True) -> pd.DataFrame:
    """Keeps only rows whose (language, model, template) matches the best
    template selected for that (language, model) pair (from notebook 01's
    argmax-F1-on-prompt_selection choice).

    NOTE: this matches the *bare* template name and is therefore only
    appropriate for `prompt_selection`-stage frames. Test-stage run names
    additionally encode the decoding configuration
    (`cls_def_exp_temp0.3_nodelim_norole_nocot`), so nothing matches exactly
    there -- use `filter_to_best_configs` with `select_best_test_configs`
    instead for anything read out of `results/test/`.

    That choice can occasionally disagree with what was actually run in the
    `test` stage -- e.g. qwen3_4b/portuguese: prompt_selection F1 narrowly
    favors `ext_exp` (0.278) over `cls_def_exp` (0.276), a near-tie, but the
    test stage was only run with `cls_def_exp`. Silently filtering on the
    prompt_selection choice would then drop that (language, model) entirely.
    For any (language, model) present in `df` with zero matching rows, this
    falls back to that group's single non-ablation template -- in the `test`
    stage each model was run with exactly one such template -- and prints a
    note so the mismatch stays visible rather than silent.
    """
    def _is_best(row):
        return get_best_template(best_templates, row["language"], row["model"]) == row["template"]

    mask = df.apply(_is_best, axis=1)
    filtered = df[mask]

    present = set(zip(df["language"], df["model"]))
    matched = set(zip(filtered["language"], filtered["model"]))
    missing = present - matched
    if missing:
        non_ablation = df[~df["template"].astype(str).str.startswith("cls_def_exp_temp")]
        fallback_rows = []
        for lang, model in sorted(missing):
            group = non_ablation[(non_ablation["language"] == lang) & (non_ablation["model"] == model)]
            templates = group["template"].unique()
            if len(templates) == 1:
                if verbose:
                    print(
                        f"[filter_to_best_templates] {lang}/{model}: prompt_selection best "
                        f"template ({get_best_template(best_templates, lang, model)!r}) has no "
                        f"matching rows here; falling back to the single template actually run "
                        f"in this stage ({templates[0]!r})."
                    )
                fallback_rows.append(group)
            elif verbose and len(templates) > 1:
                print(f"[filter_to_best_templates] {lang}/{model}: ambiguous fallback ({len(templates)} candidate templates), skipping.")
        if fallback_rows:
            filtered = pd.concat([filtered] + fallback_rows, ignore_index=True)

    return filtered.reset_index(drop=True)


# ---------------------------------------------------------------------------
# Best (template, temperature) configuration for the test stage
# ---------------------------------------------------------------------------
#
# The prompt-selection stage varied the prompt *template* only. The test
# stage then took each model's best template forward and swept decoding
# temperature, encoding the whole configuration in the run name:
#
#     <template>_temp<T>_<delim>_<role>_<cot>
#     e.g. cls_def_exp_temp0.6_nodelim_norole_nocot
#
# So "the best template" is no longer enough to identify a single test-stage
# run -- notebooks 02-04 need the best (template, temperature) *pair*. The
# helpers below parse those run names, pick the argmax-F1 configuration per
# (language, model), and persist the choice to best_configs.json so all four
# notebooks analyse exactly the same runs.

_TEMP_RE = re.compile(r"^(?P<base>.+?)_temp(?P<temp>\d+(?:\.\d+)?)(?:_|$)")


def split_run_name(template: str):
    """Splits a test-stage run name into (base_template, temperature).

    >>> split_run_name("cls_def_exp_temp0.6_nodelim_norole_nocot")
    ('cls_def_exp', 0.6)
    >>> split_run_name("cls_def_exp")
    ('cls_def_exp', 0.3)

    Runs with no `_temp` suffix predate the sweep and ran at the pipeline
    default temperature, so they are reported as TEST_DEFAULT_TEMPERATURE.
    """
    m = _TEMP_RE.match(str(template))
    if m is None:
        return str(template), TEST_DEFAULT_TEMPERATURE
    return m.group("base"), float(m.group("temp"))


def add_run_config_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Returns a copy of `df` with `base_template`, `temperature` and
    `is_swept` (True when the run name carries an explicit `_temp` suffix)
    derived from the `template` column."""
    df = df.copy()
    parsed = df["template"].map(split_run_name)
    df["base_template"] = parsed.map(lambda t: t[0])
    df["temperature"] = parsed.map(lambda t: t[1])
    df["is_swept"] = df["template"].astype(str).str.contains(r"_temp\d", regex=True)
    return df


def select_best_test_configs(
    test_results: pd.DataFrame, best_templates: dict, verbose: bool = True
) -> pd.DataFrame:
    """Picks the argmax-F1 (template, temperature) test-stage run per
    (language, model).

    Selection proceeds in two steps per (language, model) group:

    1. Restrict to runs whose *base template* is the one notebook 01 selected
       on the prompt-selection stage. Where the test stage was actually run
       with a different template (e.g. PT/qwen3_4b, where prompt selection
       narrowly favoured `ext_exp` but the test stage only ever ran
       `cls_def_exp`), fall back to the single base template present in the
       test stage and record that in `template_source`.
    2. Among those, take the highest-F1 run. When the group contains both
       swept runs (explicit `_temp` suffix) and legacy unsuffixed runs, only
       the swept ones are considered, so the comparison varies temperature
       alone rather than mixing in the older runs' different delimiter/role/
       CoT settings.

    Note that step 2 selects on the test set itself, so the resulting F1 is
    an optimistic, best-configuration figure rather than a held-out estimate
    -- report it as such.

    Returns one row per (language, model) with columns: language, model,
    template (the full run name), base_template, temperature, f1, f1_r,
    n_candidates (how many configurations the argmax ranged over) and
    template_source ("prompt_selection" or "test_stage_fallback").
    """
    df = add_run_config_columns(test_results)
    rows = []

    for (language, model), group in df.groupby(["language", "model"], sort=True):
        wanted = get_best_template(best_templates, language, model)
        candidates = group[group["base_template"] == wanted]
        source = "prompt_selection"

        if candidates.empty:
            available = sorted(group["base_template"].unique())
            if len(available) != 1:
                if verbose:
                    print(
                        f"[select_best_test_configs] {language}/{model}: prompt-selection best "
                        f"template ({wanted!r}) absent from the test stage and the fallback is "
                        f"ambiguous ({available}); skipping."
                    )
                continue
            candidates = group
            source = "test_stage_fallback"
            if verbose:
                print(
                    f"[select_best_test_configs] {language}/{model}: prompt-selection best "
                    f"template ({wanted!r}) was never run in the test stage; falling back to the "
                    f"single template actually run there ({available[0]!r})."
                )

        swept = candidates[candidates["is_swept"]]
        if not swept.empty and len(swept) < len(candidates):
            dropped = sorted(set(candidates["template"]) - set(swept["template"]))
            if verbose:
                print(
                    f"[select_best_test_configs] {language}/{model}: ignoring pre-sweep run(s) "
                    f"{dropped} in favour of the {len(swept)} explicit temperature runs."
                )
            candidates = swept

        best = candidates.loc[candidates["f1"].idxmax()]
        rows.append(
            {
                "language": language,
                "model": model,
                "template": best["template"],
                "base_template": best["base_template"],
                "temperature": best["temperature"],
                "f1": best["f1"],
                "f1_r": best["f1_r"],
                "n_candidates": len(candidates),
                "template_source": source,
            }
        )

    return pd.DataFrame(rows).sort_values(["language", "model"]).reset_index(drop=True)


def save_best_configs(best_configs: pd.DataFrame) -> Path:
    """Persists `select_best_test_configs` output as
    {language: {model: {template, base_template, temperature, ...}}}."""
    payload: dict = {}
    for row in best_configs.to_dict(orient="records"):
        payload.setdefault(row["language"], {})[row["model"]] = {
            "template": row["template"],
            "base_template": row["base_template"],
            "temperature": row["temperature"],
            "f1": row["f1"],
            "f1_r": row["f1_r"],
            "n_candidates": int(row["n_candidates"]),
            "template_source": row["template_source"],
        }
    BEST_CONFIGS_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    return BEST_CONFIGS_PATH


def load_best_configs() -> dict:
    """{language: {model: {template, base_template, temperature, ...}}},
    produced by 01_prompt_importance.ipynb."""
    if not BEST_CONFIGS_PATH.exists():
        raise FileNotFoundError(
            f"{BEST_CONFIGS_PATH} not found -- run 01_prompt_importance.ipynb first."
        )
    return json.loads(BEST_CONFIGS_PATH.read_text())


def best_configs_frame(best_configs: dict) -> pd.DataFrame:
    """Flattens `load_best_configs` output back into a tidy DataFrame."""
    rows = [
        {"language": language, "model": model, **cfg}
        for language, models in best_configs.items()
        for model, cfg in models.items()
    ]
    return pd.DataFrame(rows).sort_values(["language", "model"]).reset_index(drop=True)


def filter_to_best_configs(df: pd.DataFrame, best_configs: dict, verbose: bool = True) -> pd.DataFrame:
    """Keeps only the rows of a test-stage frame (results, detailed_results or
    detailed_results_token_level) belonging to the best (template,
    temperature) run selected for each (language, model).

    Adds `base_template` and `temperature` columns so downstream plots can
    label the configuration without re-parsing run names. Any (language,
    model) present in `df` but absent from `best_configs` is reported rather
    than silently dropped.
    """
    wanted = {
        (language, model): cfg["template"]
        for language, models in best_configs.items()
        for model, cfg in models.items()
    }

    keys = list(zip(df["language"], df["model"]))
    mask = pd.Series(
        [wanted.get(k) == t for k, t in zip(keys, df["template"])], index=df.index
    )
    filtered = df[mask]

    missing = sorted(set(keys) - set(wanted))
    if missing and verbose:
        print(f"[filter_to_best_configs] no selected configuration for: {missing}")

    return add_run_config_columns(filtered).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Derived type-aware, per-class metric
# ---------------------------------------------------------------------------
#
# results.csv's f1/f1_r are span-level only for every template (see
# src/evaluate.py::strict_metrics -- TP/FP/FN sets are built from span text
# alone; pred_type/annt_type are recorded but never used to score). To
# analyse per-class (Person/Location/Organization/...) reliability we derive
# it here from detailed_results.csv:
#
#   - a TP row with pred_type == annt_type is a true positive for that class
#   - a TP row with pred_type != annt_type (span matched, type didn't) is a
#     false negative for annt_type (the correct class was missed) AND a
#     false positive for pred_type (the wrong class was claimed)
#   - fn rows (structural misses) are a false negative for annt_type
#   - fp rows (spurious spans) are a false positive for pred_type
#
# Rows where pred_type is NaN (extract-only `ext_*` templates never predict
# a type, and a handful of cls_* predictions fail to parse a type) cannot be
# attributed to any class and are excluded from class-level fp/tp counts
# rather than bucketed into a bogus "unknown" class. Rows where annt_type is
# NaN (a handful of fn rows, plus all fp rows by construction) are excluded
# in the same way from fn counts.

def split_span_outcomes(df: pd.DataFrame) -> dict:
    """Partition a detailed_results frame by the counting rule above.

    Returns the four disjoint frames the rule is stated over -- ``matched``
    (span and type both right), ``mismatched`` (span right, type wrong),
    ``fn_structural`` and ``fp_structural`` -- so the per-class and the
    micro-averaged views below cannot drift apart in how they classify a row.

    Note that `pred_type != annt_type` is True when either side is missing, so
    an unparsed type counts as a mismatch here. `compute_class_level_metrics`
    filters those out afterwards, because a row with no label cannot be
    attributed to a class; `compute_extraction_classification_metrics` keeps
    them, because at the micro level dropping them would shrink the
    classification denominators below the extraction ones and break the
    comparison between the two scores.
    """
    span_tp = df[df["result"] == "tp"]
    same = span_tp["pred_type"] == span_tp["annt_type"]
    return {
        "matched": span_tp[same],
        "mismatched": span_tp[~same],
        "fn_structural": df[df["result"] == "fn"],
        "fp_structural": df[df["result"] == "fp"],
    }


def compute_class_level_metrics(df: pd.DataFrame, group_cols=None) -> pd.DataFrame:
    """Type-aware per-class precision/recall/F1 from a detailed_results.csv
    frame (as returned by load_detailed). Pass group_cols (e.g. ["model"] or
    ["model", "language"]) to compute metrics per group; omit for a single
    overall breakdown across whatever rows are in `df`.

    Returns a DataFrame with columns group_cols + ["cls", "tp", "fp", "fn",
    "precision", "recall", "f1"].
    """
    group_cols = list(group_cols) if group_cols else []

    parts = split_span_outcomes(df)
    labelled = lambda frame: frame[frame["pred_type"].notna() & frame["annt_type"].notna()]
    matched = labelled(parts["matched"])
    mismatched = labelled(parts["mismatched"])
    fn_structural = parts["fn_structural"][parts["fn_structural"]["annt_type"].notna()]
    fp_structural = parts["fp_structural"][parts["fp_structural"]["pred_type"].notna()]

    def _counts(frame, type_col, label):
        cols = group_cols + [type_col]
        if frame.empty:
            return pd.DataFrame(columns=group_cols + ["cls", label])
        g = frame.groupby(cols).size().rename(label).reset_index()
        return g.rename(columns={type_col: "cls"})

    merge_cols = group_cols + ["cls"]

    tp_counts = _counts(matched, "annt_type", "tp")
    fn_counts = (
        pd.concat([_counts(fn_structural, "annt_type", "fn"), _counts(mismatched, "annt_type", "fn")], ignore_index=True)
        .groupby(merge_cols, as_index=False)["fn"].sum()
    )
    fp_counts = (
        pd.concat([_counts(fp_structural, "pred_type", "fp"), _counts(mismatched, "pred_type", "fp")], ignore_index=True)
        .groupby(merge_cols, as_index=False)["fp"].sum()
    )

    result = tp_counts.merge(fn_counts, on=merge_cols, how="outer").merge(fp_counts, on=merge_cols, how="outer")
    result[["tp", "fn", "fp"]] = result[["tp", "fn", "fp"]].fillna(0)

    denom_p = (result["tp"] + result["fp"]).replace(0, np.nan)
    denom_r = (result["tp"] + result["fn"]).replace(0, np.nan)
    result["precision"] = (result["tp"] / denom_p).fillna(0.0)
    result["recall"] = (result["tp"] / denom_r).fillna(0.0)
    denom_f1 = (result["precision"] + result["recall"]).replace(0, np.nan)
    result["f1"] = (2 * result["precision"] * result["recall"] / denom_f1).fillna(0.0)

    return result.sort_values(merge_cols).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Derived micro-averaged extraction and classification metrics
# ---------------------------------------------------------------------------
#
# The same counting rule as above, rolled up over all classes instead of
# reported per class, which yields the two headline scores:
#
#   F1-extraction     -- a prediction is correct when its *span* matches.
#                        This is what results.csv has always called `f1`; the
#                        name here only makes explicit what it measures.
#   F1-classification -- a prediction is correct when its span *and* its type
#                        match. A span hit with the wrong type is a false
#                        positive for the type claimed and a false negative
#                        for the type missed, so it is penalised on both
#                        sides rather than half-credited.
#
# The two share their denominators exactly -- tp+fp and tp+fn are identical
# between them, because every span-level outcome is counted in both, only
# sorted differently. That is what makes the pair comparable and the gap
# between them readable as the cost of typing: F1-classification can never
# exceed F1-extraction, and their ratio is the share of extraction
# performance that survives having to name the participant type.
#
# The classification score is undefined for `ext_*` templates, which never
# predict a type. It is returned as NaN there rather than 0.0, so that a
# template which was never asked to classify is not averaged in as one that
# tried and failed.

def _prf(tp: float, fp: float, fn: float) -> tuple:
    """Precision, recall and F1 from raw counts, 0.0 on an empty denominator."""
    precision = tp / (tp + fp) if tp + fp > 0 else 0.0
    recall = tp / (tp + fn) if tp + fn > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0.0
    return precision, recall, f1


def compute_extraction_classification_metrics(df: pd.DataFrame, group_cols=None) -> pd.DataFrame:
    """Micro-averaged extraction and classification P/R/F1 from a
    detailed_results.csv frame (as returned by `load_detailed`).

    Pass group_cols (e.g. ["language", "model"] or ["language", "model",
    "template"]) to compute one row per group; omit for a single row over
    whatever is in `df`.

    Apply `coarsen_types` to `df` first for the coarse-grained location view,
    which is the one the document-level analysis reports.

    Returns group_cols + ["tp_ext", "fp_ext", "fn_ext", "precision_ext",
    "recall_ext", "f1_ext", "tp_cls", "fp_cls", "fn_cls", "precision_cls",
    "recall_cls", "f1_cls"], with the `*_cls` columns NaN for groups whose
    template never predicts a type.
    """
    group_cols = list(group_cols) if group_cols else []

    def _one(group: pd.DataFrame) -> dict:
        parts = split_span_outcomes(group)
        tp_ext = len(parts["matched"]) + len(parts["mismatched"])
        fp_ext = len(parts["fp_structural"])
        fn_ext = len(parts["fn_structural"])
        p_ext, r_ext, f_ext = _prf(tp_ext, fp_ext, fn_ext)

        row = {
            "tp_ext": tp_ext, "fp_ext": fp_ext, "fn_ext": fn_ext,
            "precision_ext": p_ext, "recall_ext": r_ext, "f1_ext": f_ext,
        }

        # An extraction-only template predicts no type anywhere in the group.
        if not group["pred_type"].notna().any():
            row.update({
                "tp_cls": np.nan, "fp_cls": np.nan, "fn_cls": np.nan,
                "precision_cls": np.nan, "recall_cls": np.nan, "f1_cls": np.nan,
            })
            return row

        mismatch = len(parts["mismatched"])
        tp_cls = len(parts["matched"])
        fp_cls = fp_ext + mismatch
        fn_cls = fn_ext + mismatch
        p_cls, r_cls, f_cls = _prf(tp_cls, fp_cls, fn_cls)
        row.update({
            "tp_cls": tp_cls, "fp_cls": fp_cls, "fn_cls": fn_cls,
            "precision_cls": p_cls, "recall_cls": r_cls, "f1_cls": f_cls,
        })
        return row

    if not group_cols:
        return pd.DataFrame([_one(df)])

    rows = []
    for keys, group in df.groupby(group_cols, sort=True):
        keys = keys if isinstance(keys, tuple) else (keys,)
        rows.append({**dict(zip(group_cols, keys)), **_one(group)})

    return pd.DataFrame(rows).sort_values(group_cols).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Type metrics conditional on the span already being correct
# ---------------------------------------------------------------------------
#
# F1-classification above is bounded by F1-extraction and inherits every
# extraction failure, so it cannot say whether typing is itself a bottleneck
# or merely inherits one. Restricting to the matched-span subset answers that
# question directly: given a participant the model has already located, does
# it name the right type?
#
# On that subset every row carries exactly one gold type and one predicted
# type, so it is an ordinary closed confusion matrix, and micro-precision,
# micro-recall and accuracy all collapse to the same number. That number is a
# poor summary here: the gold prior is heavily skewed (Per/Org/Loc are about
# three quarters of all participants) and those same frequent classes are the
# ones the models handle well, so accuracy tracks the support-weighted F1 to
# within 0.005 and hides a tail of classes scoring below 0.5. `macro_f1`,
# which weights every class equally, is therefore the reported figure;
# `accuracy` is returned alongside only so the gap between them stays visible.
#
# Every class in `classes` is scored, with no exclusions -- `Other` and `Fac`
# included. Both are defined in the annotation guidelines, so a model is
# legitimately accountable for them. A class entirely absent from a group
# (neither annotated nor predicted) is skipped rather than counted as a zero,
# so groups are not penalised for classes their documents never contain.


def compute_conditional_type_metrics(
    df: pd.DataFrame,
    group_cols=None,
    classes=None,
    per_class: bool = False,
) -> pd.DataFrame:
    """Participant-type metrics over matched spans only.

    Takes any detailed_results-shaped frame (`load_detailed`, optionally
    filtered to the best configurations and/or passed through `coarsen_types`),
    so the same call serves the prompt-selection and test phases and any future
    document-level phase. Apply `coarsen_types` first for the coarse view --
    this function does not coarsen on your behalf, it only detects which label
    set to score against.

    Parameters
    ----------
    group_cols : list, optional
        e.g. ["language", "model"] or ["language", "template"]. One row (or one
        block of per-class rows) per group; omit for a single overall figure.
    classes : list, optional
        Label set to score. Defaults to PROMPT_CLASSES_COARSE when the frame
        has been coarsened and PROMPT_CLASSES when it has not. Restricting to
        the prompt's own label set keeps the long tail of invented labels out
        of the macro average, where a one-instance class would otherwise weigh
        as much as `Per`.
    per_class : bool
        False (default) returns group_cols + ["n_matched", "accuracy",
        "macro_precision", "macro_recall", "macro_f1"]. True returns
        group_cols + ["cls", "support", "tp", "fp", "fn", "precision",
        "recall", "f1"], the counts being included so a per-class score can be
        read against the confusion structure that produced it.
    """
    group_cols = list(group_cols) if group_cols else []

    if classes is None:
        present = set(df["annt_type"].dropna().unique()) | set(df["pred_type"].dropna().unique())
        has_fine = any(isinstance(x, str) and x.startswith(COARSE_LOCATION_PREFIX) for x in present)
        classes = PROMPT_CLASSES if has_fine else PROMPT_CLASSES_COARSE
    classes = list(classes)

    parts = split_span_outcomes(df)
    matched = pd.concat([parts["matched"], parts["mismatched"]])
    matched = matched[matched["annt_type"].notna() & matched["pred_type"].notna()]
    # Rows whose *gold* type falls outside `classes` are not scoreable; a
    # prediction outside it still counts against the class it was claimed for,
    # so those rows stay in and simply never register as a true positive.
    matched = matched[matched["annt_type"].isin(classes)]

    def _per_class(group: pd.DataFrame) -> pd.DataFrame:
        rows = []
        for label in classes:
            gold = group["annt_type"] == label
            pred = group["pred_type"] == label
            tp = int((gold & pred).sum())
            fp = int((~gold & pred).sum())
            fn = int((gold & ~pred).sum())
            if tp + fp + fn == 0:
                continue  # class absent from this group entirely
            precision, recall, f1 = _prf(tp, fp, fn)
            rows.append({
                "cls": label, "support": int(gold.sum()),
                "tp": tp, "fp": fp, "fn": fn,
                "precision": precision, "recall": recall, "f1": f1,
            })
        return pd.DataFrame(
            rows, columns=["cls", "support", "tp", "fp", "fn", "precision", "recall", "f1"]
        )

    def _summary(group: pd.DataFrame) -> pd.DataFrame:
        table = _per_class(group)
        if table.empty:
            row = {"n_matched": len(group), "accuracy": np.nan,
                   "macro_precision": np.nan, "macro_recall": np.nan, "macro_f1": np.nan}
        else:
            row = {
                "n_matched": len(group),
                "accuracy": float((group["pred_type"] == group["annt_type"]).mean()),
                "macro_precision": float(table["precision"].mean()),
                "macro_recall": float(table["recall"].mean()),
                "macro_f1": float(table["f1"].mean()),
            }
        return pd.DataFrame([row])

    build = _per_class if per_class else _summary

    if not group_cols:
        return build(matched).reset_index(drop=True)

    frames = []
    for keys, group in matched.groupby(group_cols, sort=True):
        keys = keys if isinstance(keys, tuple) else (keys,)
        part = build(group)
        if part.empty:
            continue
        for position, (col, value) in enumerate(zip(group_cols, keys)):
            part.insert(position, col, value)
        frames.append(part)

    if not frames:
        return pd.DataFrame(columns=group_cols)
    return pd.concat(frames, ignore_index=True)


# ---------------------------------------------------------------------------
# F1-post-ext-cls: classification scored only over correctly extracted spans
# ---------------------------------------------------------------------------
#
# F1-classification answers "how much of the annotated participant set did the
# model recover *and* type correctly", which is the figure that matters for the
# task as a whole but confounds two abilities. This function isolates the
# second: of the participants the model already located, how many did it type
# correctly? The population is the span-level true positives, so extraction
# failures are excluded by construction rather than inherited.
#
# The two scores compose exactly. Because extraction and classification share
# their denominators (see above), tp_cls / tp_ext is a single factor that
# scales precision and recall alike, and therefore scales their harmonic mean:
#
#     F1-classification = F1-extraction * micro-F1-post-ext-cls
#
# so the pair decomposes end-to-end performance into locating and typing. The
# notebooks assert this identity rather than take it on trust.
#
# Two averages are returned, and they are not interchangeable:
#
#   micro -- pooled over classes, counted by exactly the rule
#            `split_span_outcomes` applies: a span tp whose type is not the
#            annotated one is a false positive for the class claimed and a
#            false negative for the class missed. Every non-matched row is
#            therefore counted on both sides, tp+fp == tp+fn == n, and micro
#            precision, recall and F1 all coincide with accuracy. That is not a
#            defect: it is what makes the decomposition above an exact
#            algebraic identity rather than an approximation, since it is the
#            same rule the global F1-classification uses. The triple is
#            returned in full anyway, to mirror the other metric helpers and so
#            the coincidence can be verified rather than trusted.
#
#            It is a weak summary in its own right: the gold prior is dominated
#            by Per/Org/Loc, which are also the classes the models handle well.
#
#   macro -- every class weighted equally, delegated to
#            `compute_conditional_type_metrics` so there is exactly one macro
#            definition in this module. This is the figure to report.
#
# Two kinds of row are not scoreable on both sides, and counting them on both
# sides anyway is what keeps the identity exact. They are reported as separate
# diagnostic counts instead, so the information is not lost: `untyped_pec` is
# span tps whose *predicted* type failed to parse (they claim no class),
# `ungolded_pec` is span tps whose *gold* type is missing (there is no class to
# have claimed). Both are errors under any reading; only their attribution to a
# particular class is undefined. On the current runs untyped_pec is 0 and
# ungolded_pec is 6 of 7136.

def compute_post_extraction_classification_metrics(
    df: pd.DataFrame,
    group_cols=None,
    classes=None,
) -> pd.DataFrame:
    """Participant-type P/R/F1 over the correctly extracted spans only.

    Takes any detailed_results-shaped frame (as returned by `load_detailed`),
    optionally filtered and/or passed through `coarsen_types` first -- as with
    `compute_conditional_type_metrics`, this function does not coarsen on your
    behalf.

    Parameters
    ----------
    group_cols : list, optional
        e.g. ["language", "model", "template"]. One row per group; omit for a
        single row over whatever is in `df`.
    classes : list, optional
        Label set the macro average is taken over. Passed straight through to
        `compute_conditional_type_metrics`, which defaults it to
        PROMPT_CLASSES_COARSE or PROMPT_CLASSES depending on whether the frame
        has been coarsened. The micro counts ignore it: a prediction outside
        the schema is a genuine error and is counted as one.

    Returns group_cols + ["n_spans_pec", "untyped_pec", "ungolded_pec",
    "tp_pec", "fp_pec", "fn_pec", "micro_precision_pec", "micro_recall_pec",
    "micro_f1_pec", "macro_precision_pec", "macro_recall_pec",
    "macro_f1_pec"]. A group with no correctly extracted span scores NaN
    throughout rather than 0.0, since there is nothing to have typed.
    """
    group_cols = list(group_cols) if group_cols else []

    parts = split_span_outcomes(df)
    span_tp = pd.concat([parts["matched"], parts["mismatched"]])

    def _one(group: pd.DataFrame) -> dict:
        # As in `compute_extraction_classification_metrics`, a group that never
        # predicts a type was never asked to classify, so it scores NaN rather
        # than 0.0 and is not averaged in as a template that tried and failed.
        if group.empty or not group["pred_type"].notna().any():
            return {
                "n_spans_pec": len(group),
                "untyped_pec": len(group), "ungolded_pec": 0,
                "tp_pec": np.nan, "fp_pec": np.nan, "fn_pec": np.nan,
                "micro_precision_pec": np.nan, "micro_recall_pec": np.nan,
                "micro_f1_pec": np.nan,
            }
        # The same test `split_span_outcomes` uses to separate matched from
        # mismatched: False whenever either side is missing, so a row is a true
        # positive only when both are present and agree. Every other row is
        # counted on both sides, which is what keeps the decomposition exact.
        hit = group["pred_type"] == group["annt_type"]
        tp = int(hit.sum())
        errors = len(group) - tp
        precision, recall, f1 = _prf(tp, errors, errors)
        return {
            "n_spans_pec": len(group),
            "untyped_pec": int(group["pred_type"].isna().sum()),
            "ungolded_pec": int(group["annt_type"].isna().sum()),
            "tp_pec": tp, "fp_pec": errors, "fn_pec": errors,
            "micro_precision_pec": precision, "micro_recall_pec": recall,
            "micro_f1_pec": f1,
        }

    if not group_cols:
        micro = pd.DataFrame([_one(span_tp)])
    else:
        rows = []
        for keys, group in span_tp.groupby(group_cols, sort=True):
            keys = keys if isinstance(keys, tuple) else (keys,)
            rows.append({**dict(zip(group_cols, keys)), **_one(group)})
        micro = pd.DataFrame(rows)
        if micro.empty:
            return pd.DataFrame(columns=group_cols)

    renames = {
        "macro_precision": "macro_precision_pec",
        "macro_recall": "macro_recall_pec",
        "macro_f1": "macro_f1_pec",
    }
    macro = compute_conditional_type_metrics(df, group_cols=group_cols, classes=classes)
    if not set(renames).issubset(macro.columns):
        # No group had a scoreable row -- an `ext_*` template predicts no type
        # anywhere, so there is no confusion matrix to macro-average. The micro
        # side is still well defined (every span tp is an error), so return it
        # with the macro columns empty rather than failing.
        for column in renames.values():
            micro[column] = np.nan
        return micro.sort_values(group_cols).reset_index(drop=True) if group_cols else micro
    macro = macro[group_cols + list(renames)].rename(columns=renames)

    if not group_cols:
        return pd.concat([micro.reset_index(drop=True), macro.reset_index(drop=True)], axis=1)
    return micro.merge(macro, on=group_cols, how="left").sort_values(group_cols).reset_index(drop=True)


def class_distribution(
    df: pd.DataFrame,
    source: str = "gold",
    group_cols=None,
    classes=None,
    normalize: bool = True,
) -> pd.DataFrame:
    """Participant-type distribution over one of three populations.

    `source` selects which population is counted:

    * ``"gold"``      -- every annotated participant (span tp + fn), by
                         `annt_type`. This is the corpus prior.
    * ``"predicted"`` -- every span the model proposed (span tp + fp), by
                         `pred_type`. This is what the model actually emits.
    * ``"matched"``   -- the span-tp subset, by `annt_type`; the population
                         `compute_conditional_type_metrics` scores over.

    Returns group_cols + ["cls", "n"] and, when normalize=True, "share"
    computed within each group. Labels outside `classes` are pooled into
    "(other labels)" rather than dropped, so the shares still sum to 1 and the
    size of the invented-label tail stays visible.
    """
    populations = {
        "gold": (("tp", "fn"), "annt_type"),
        "predicted": (("tp", "fp"), "pred_type"),
        "matched": (("tp",), "annt_type"),
    }
    if source not in populations:
        raise ValueError(f"source must be one of {sorted(populations)}, got {source!r}")
    results, col = populations[source]

    group_cols = list(group_cols) if group_cols else []
    if classes is None:
        present = set(df["annt_type"].dropna().unique()) | set(df["pred_type"].dropna().unique())
        has_fine = any(isinstance(x, str) and x.startswith(COARSE_LOCATION_PREFIX) for x in present)
        classes = PROMPT_CLASSES if has_fine else PROMPT_CLASSES_COARSE

    frame = df[df["result"].isin(results)].copy()
    frame = frame[frame[col].notna()]
    if source == "matched":
        # Mirror `compute_conditional_type_metrics` exactly: a matched span
        # whose predicted type failed to parse is not scoreable, so it must
        # not appear in the distribution of the scored population either.
        frame = frame[frame["pred_type"].notna()]
    frame["cls"] = frame[col].where(frame[col].isin(list(classes)), "(other labels)")

    counts = frame.groupby(group_cols + ["cls"]).size().rename("n").reset_index()
    if normalize:
        if group_cols:
            totals = counts.groupby(group_cols)["n"].transform("sum")
        else:
            totals = counts["n"].sum()
        counts["share"] = counts["n"] / totals
    return counts.sort_values(group_cols + ["n"], ascending=[True] * len(group_cols) + [False]).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Plot styling
# ---------------------------------------------------------------------------

def style_axis(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#DDDDDD", linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    return ax


def save_fig(fig, name: str, tight: bool = True) -> Path:
    if tight:
        fig.tight_layout()
    path = FIGURES_DIR / f"{name}.pdf"
    fig.savefig(path, format="pdf", bbox_inches="tight")
    print(f"Saved {path}")
    return path
