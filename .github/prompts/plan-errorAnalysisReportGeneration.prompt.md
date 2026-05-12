# Plan: Summarize Error Analysis Results for LLM Report Generation

**TL;DR**: Create a detailed Markdown document that extracts and aggregates your notebook results—combining summary statistics, embedded visualizations, and tabular data—into a cohesive narrative that Gemini Gems can enhance into a polished report. This approach separates data extraction from presentation, making it easy to iterate with the LLM.

## Steps

### 1. Extract and aggregate summary statistics (*independent task*)

- Use the 'error_analysis.ipynb' notebook to extract all the following data:
- (strict metrics) for all 4 language-experiment combinations (Portuguese/English × prompt_selection/test)
- token-level FN patterns for all annotation types and models across both languages
- Find model performance by template, error breakdown by annotation type, confusion patterns Python DataFrames for markdown export.

### 2. Export all visualization charts (*parallel with step 1*)

- Save all matplotlib figures from the notebook (pie charts for TP/FN by annotation type, bar charts for FN tokens) as PNG files
- Organize into a `report_assets/` folder by experiment/language

### 3. Create the Markdown document scaffold (*depends on steps 1–2*)

- Structure: Executive Summary → Model Comparison → Error Analysis (strict & token-level) → Best Configuration Recommendations → Appendix with raw data tables
- Embed PNG charts inline at relevant sections
- Include summary data tables (model F1 scores, error counts by type)
- Use clear markdown formatting with headers, lists, and callout sections

### 4. Extract key insights and observations (*depends on step 3*)

- Calculate derived metrics: which annotation types have highest error rates per model, which templates perform best, language-specific patterns
- Identify patterns: tokens with most FN errors, model-template combinations to recommend, outliers


### 5. Prepare for LLM handoff

- Markdown file ready to paste into Gemini Gems for report enhancement
- Include a prompt template with context: "Here are my detailed results. Please synthesize these into a polished scientific report with narrative flow, clear conclusions, and actionable recommendations."

## Relevant Files

- **src/evaluate.py** — check for existing metrics & aggregation patterns you can better understand the evaluation logic
- **results/prompt_selection/english/detailed_results.csv** and token-level variants — raw data to extract
- **results/test/portuguese/detailed_results.csv** and token-level variants — raw data to extract
- **notebooks/error_analysis.ipynb** — contains all visualizations and all the main results

## Important considerations
1. Which metrics to highlight?
The notebook has both strict (entity-level TP/FN) and relaxed (token-level) metrics. Should the report prioritize one, or give equal weight?
> You should focus in the F1 score (strict) as the main performance metric. The relaxed token-level metrics can be used to provide additional context and insights into error patterns that can be tried to be reduced by model finetunning.

2. Best configurations
The notebook has `BEST_TEMPLATES` defined. Should the report focus on these, or compare all 5×N templates systematically?
> You should feature the best-performing templates prominently in the main report, but also include a comprehensive comparison grid in an appendix for transparency and to allow readers to explore all configurations.

3. Narrative framing
Should the report be structured as "Model A vs B vs C," "Template effectiveness across models," or "Per-annotation-type performance"?
> Start with a high-level model comparison to set the stage, then dive into template effectiveness within each model, and finally analyze performance by annotation type to uncover specific strengths and weaknesses.

## Data Overview

### Results Structure
- **4 experiment/language combinations**: 
  - `results/prompt_selection/{english|portuguese}/`
  - `results/test/{english|portuguese}/`

### CSV Files (3 per combination = 12 total)
1. **results.csv** — Summary aggregated metrics by model/template
2. **detailed_results.csv** — Entity-level predictions (strict metrics)
3. **detailed_results_token_level.csv** — Token-by-token analysis (relaxed metrics)

### Key Columns
- **Aggregate**: modelo, template, entity, precision, recall, f1, f1_r
- **Entity-level**: modelo, entity, doc_id, template, token, pred_type, annt_type, result (tp/fp/fn), f1_r_score
- **Token-level**: modelo, entity, doc_id, template, complete_prediction, token, pred_type, matched_annotation, annt_type, result

## Verification Checklist

- [ ] Markdown file generated with no broken image links
- [ ] All summary tables contain expected rows (5 models × templates, 15 annotation types)
- [ ] PNG exports match visualizations from notebook
- [ ] Copy-paste test: place entire markdown + images folder into Gemini Gems and verify display

## Design Decisions

- **Markdown over Jupyter export**: Cleaner for LLM consumption, separates data from presentation, renders in any editor/platform

## Parameters for Report Generation

- **Report Format**: Markdown (.md)
- **Target LLM**: Gemini Gems
- **Scope**: Comprehensive analysis (model comparison + error analysis + best configurations)
- **Detail Level**: Detailed (include data tables, charts, fine-grained analysis)
- **Visualizations**: Embed all charts/graphs as images
- **Models Evaluated**: Gemini, Gemma3-1B, Llama3.2-3B, Qwen2.5-14B, Qwen3-4B
- **Languages**: English, Portuguese
- **Experiments**: Prompt Selection (tuning) + Test (final evaluation)
