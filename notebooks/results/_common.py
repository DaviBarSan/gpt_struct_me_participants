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

# llama32_3b's results are invalid (near-zero precision/recall across every
# template/language -- see notebook 01's combined boxplot, where it stood
# out as flat near zero while every other model showed the expected
# *_exp-prompt improvement) and are excluded from all four notebooks via the
# loaders below, rather than filtered ad hoc in each notebook.
EXCLUDED_MODELS = ["llama32_3b", "gemma3_1b", "qwen25_12b"] 

# Gold annotations use fine-grained location subtypes (Pl_capital, Pl_civil,
# Pl_country, Pl_region, Pl_state, Pl_water) that model outputs never
# reproduce -- predictions only ever use the generic "Loc". Left as-is this
# shows up as a wall of false negatives on every Pl_* class that is really a
# label-granularity mismatch, not an extraction failure. COARSE_CLASS_MAP
# lets notebook 03 also show a coarse-grained view where those collapse into
# "Loc" for a fairer comparison, alongside the raw fine-grained view.

COARSE_CLASS_MAP = {
    "Pl_capital": "Loc",
    "Pl_civil": "Loc",
    "Pl_country": "Loc",
    "Pl_region": "Loc",
    "Pl_state": "Loc",
    "Pl_water": "Loc",
}

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

# PROMPT_CLASSES after COARSE_CLASS_MAP collapses the Pl_* subtypes into Loc.
PROMPT_CLASSES_COARSE = ["Per", "Org", "Obj", "Nat", "Fac", "Loc", "Other"]


def coarsen_types(df: pd.DataFrame) -> pd.DataFrame:
    """Returns a copy of a detailed_results frame with pred_type/annt_type
    location subtypes collapsed via COARSE_CLASS_MAP."""
    df = df.copy()
    df["pred_type"] = df["pred_type"].replace(COARSE_CLASS_MAP)
    df["annt_type"] = df["annt_type"].replace(COARSE_CLASS_MAP)
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
    tp/fp/fn rows with pred_type/annt_type metadata)."""
    path = RESULTS_DIR / stage / language / "detailed_results.csv"
    df = pd.read_csv(path)
    df = df.rename(columns={"modelo": "model"})
    df = _drop_excluded_models(df)
    df["stage"] = stage
    df["language"] = language
    return df


def load_detailed_token(stage: str, language: str) -> pd.DataFrame:
    """Reads results/{stage}/{language}/detailed_results_token_level.csv
    (word-level LCS match rows with result_type EXACT/PARTIAL/MISS)."""
    path = RESULTS_DIR / stage / language / "detailed_results_token_level.csv"
    df = pd.read_csv(path)
    df = df.rename(columns={"modelo": "model"})
    df = _drop_excluded_models(df)
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

def compute_class_level_metrics(df: pd.DataFrame, group_cols=None) -> pd.DataFrame:
    """Type-aware per-class precision/recall/F1 from a detailed_results.csv
    frame (as returned by load_detailed). Pass group_cols (e.g. ["model"] or
    ["model", "language"]) to compute metrics per group; omit for a single
    overall breakdown across whatever rows are in `df`.

    Returns a DataFrame with columns group_cols + ["cls", "tp", "fp", "fn",
    "precision", "recall", "f1"].
    """
    group_cols = list(group_cols) if group_cols else []

    tp_all = df[(df["result"] == "tp") & df["pred_type"].notna() & df["annt_type"].notna()]
    matched = tp_all[tp_all["pred_type"] == tp_all["annt_type"]]
    mismatched = tp_all[tp_all["pred_type"] != tp_all["annt_type"]]
    fn_structural = df[(df["result"] == "fn") & df["annt_type"].notna()]
    fp_structural = df[(df["result"] == "fp") & df["pred_type"].notna()]

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
