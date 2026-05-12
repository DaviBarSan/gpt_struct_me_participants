# Error Analysis Report: LLM-Based Information Extraction
**Comprehensive Analysis of Model Performance and Error Patterns**

*Generated from error_analysis.ipynb notebook*

## Executive Summary

This report provides a comprehensive analysis of error patterns across multiple large language models (LLMs) evaluating their ability to extract information from Portuguese and English texts. The evaluation compares 5 different models (Gemini, Gemma3-1B, Llama3.2-3B, Qwen2.5-14B, Qwen3-4B) across multiple prompt templates, with detailed error analysis at both entity and token levels.

### Evaluation Scope

- **Models Evaluated:** Gemini, Gemma3-1B, Llama3.2-3B, Qwen2.5-14B, Qwen3-4B
- **Languages:** English, Portuguese
- **Experiments:** Prompt Selection (model/template tuning) + Test (final evaluation)
- **Primary Metric:** F1 Score (strict, entity-level precision/recall)
- **Fine-grained Analysis:** Token-level metrics for error pattern discovery
- **Entity Types:** 15 annotation types (Fac, Loc, Nat, Obj, Org, Other, Path, Per, Pl_capital, Pl_civil, Pl_country, Pl_region, Pl_state, Pl_water, Veh)

## Key Findings: Best Performing Configurations

### Portuguese

| Model | Template | Experiment | F1 Score | Precision | Recall | TP | FP | FN |
|-------|----------|------------|----------|-----------|--------|----|----|----|
| gemini | cls_def_exp | prompt_selection | 0.6160 | 0.6250 | 0.6060 | 317 | 190 | 206 |
| gemini | cls_def_exp | test | 0.5590 | 0.5690 | 0.5480 | 1415 | 1070 | 1165 |
| qwen3_4b | cls_def_exp | prompt_selection | 0.2760 | 0.3150 | 0.2450 | 128 | 278 | 395 |
| qwen3_4b | cls_def_exp | test | 0.2490 | 0.2920 | 0.2170 | 559 | 1356 | 2021 |
| qwen25_14b | cls_exp | prompt_selection | 0.2430 | 0.3390 | 0.1890 | 99 | 193 | 424 |
| qwen25_14b | cls_exp | test | 0.2330 | 0.3370 | 0.1780 | 458 | 901 | 2122 |
| gemma3_1b | ext_def_exp | test | 0.1900 | 0.2570 | 0.1500 | 387 | 1117 | 2193 |
| gemma3_1b | ext_def_exp | prompt_selection | 0.1730 | 0.2460 | 0.1340 | 70 | 214 | 453 |

### English

| Model | Template | Experiment | F1 Score | Precision | Recall | TP | FP | FN |
|-------|----------|------------|----------|-----------|--------|----|----|----|
| gemini | cls_def_exp | prompt_selection | 0.5630 | 0.5730 | 0.5530 | 295 | 220 | 238 |
| gemini | cls_def_exp | test | 0.5400 | 0.5350 | 0.5460 | 1409 | 1225 | 1171 |
| qwen3_4b | cls_def_exp | test | 0.2560 | 0.2740 | 0.2410 | 621 | 1649 | 1959 |
| qwen3_4b | cls_def_exp | prompt_selection | 0.2510 | 0.2610 | 0.2420 | 129 | 365 | 404 |
| qwen25_14b | cls_exp | test | 0.2290 | 0.3100 | 0.1810 | 468 | 1043 | 2112 |
| qwen25_14b | cls_exp | prompt_selection | 0.2080 | 0.2820 | 0.1650 | 88 | 224 | 445 |
| gemma3_1b | ext_def_exp | prompt_selection | 0.1910 | 0.2340 | 0.1610 | 86 | 281 | 447 |
| gemma3_1b | ext_def_exp | test | 0.1720 | 0.2190 | 0.1420 | 366 | 1304 | 2214 |
| llama32_3b | cls_exp | prompt_selection | 0.0380 | 0.1250 | 0.0230 | 12 | 84 | 521 |
| llama32_3b | cls_exp | test | 0.0170 | 0.1170 | 0.0090 | 24 | 182 | 2556 |

## Detailed Model Performance Comparison

### Prompt Selection Phase

#### Portuguese

**Top 10 Model-Template Configurations by F1 Score:**

| Rank | Model | Template | F1 | Precision | Recall | TP | FP | FN |
|------|-------|----------|-----|-----------|--------|----|----|----|
| 1 | gemini | cls_def_exp | 0.6160 | 0.6250 | 0.6060 | 317 | 190 | 206 |
| 2 | gemini | ext_def_exp | 0.5770 | 0.6280 | 0.5330 | 279 | 165 | 244 |
| 3 | gemini | cls_exp | 0.5700 | 0.5720 | 0.5680 | 297 | 222 | 226 |
| 4 | gemini | ext_exp | 0.5690 | 0.5420 | 0.5980 | 313 | 264 | 210 |
| 5 | qwen3_4b | ext_exp | 0.2780 | 0.2790 | 0.2770 | 145 | 375 | 378 |
| 6 | qwen3_4b | cls_def_exp | 0.2760 | 0.3150 | 0.2450 | 128 | 278 | 395 |
| 7 | gemini | cls_def | 0.2680 | 0.3630 | 0.2120 | 111 | 195 | 412 |
| 8 | qwen3_4b | cls_exp | 0.2670 | 0.2960 | 0.2430 | 127 | 302 | 396 |
| 9 | qwen25_14b | cls_exp | 0.2430 | 0.3390 | 0.1890 | 99 | 193 | 424 |
| 10 | gemini | cls | 0.2420 | 0.2790 | 0.2140 | 112 | 290 | 411 |

#### English

**Top 10 Model-Template Configurations by F1 Score:**

| Rank | Model | Template | F1 | Precision | Recall | TP | FP | FN |
|------|-------|----------|-----|-----------|--------|----|----|----|
| 1 | gemini | cls_def_exp | 0.5630 | 0.5730 | 0.5530 | 295 | 220 | 238 |
| 2 | gemini | cls_exp | 0.5620 | 0.5540 | 0.5700 | 304 | 245 | 229 |
| 3 | gemini | ext_def_exp | 0.5390 | 0.5570 | 0.5220 | 278 | 221 | 255 |
| 4 | gemini | ext_exp | 0.5200 | 0.5200 | 0.5200 | 277 | 256 | 256 |
| 5 | gemini | cls_def | 0.3140 | 0.4250 | 0.2500 | 133 | 180 | 400 |
| 6 | gemini | cls | 0.2630 | 0.3040 | 0.2310 | 123 | 281 | 410 |
| 7 | qwen3_4b | cls_exp | 0.2540 | 0.2480 | 0.2610 | 139 | 421 | 394 |
| 8 | qwen3_4b | cls_def_exp | 0.2510 | 0.2610 | 0.2420 | 129 | 365 | 404 |
| 9 | qwen3_4b | ext_def_exp | 0.2440 | 0.2560 | 0.2330 | 124 | 360 | 409 |
| 10 | qwen3_4b | ext_exp | 0.2150 | 0.1900 | 0.2460 | 131 | 557 | 402 |

### Test Phase

#### Portuguese

**Top 10 Model-Template Configurations by F1 Score:**

| Rank | Model | Template | F1 | Precision | Recall | TP | FP | FN |
|------|-------|----------|-----|-----------|--------|----|----|----|
| 1 | gemini | cls_def_exp | 0.5590 | 0.5690 | 0.5480 | 1415 | 1070 | 1165 |
| 2 | qwen3_4b | cls_def_exp | 0.2490 | 0.2920 | 0.2170 | 559 | 1356 | 2021 |
| 3 | qwen25_14b | cls_exp | 0.2330 | 0.3370 | 0.1780 | 458 | 901 | 2122 |
| 4 | gemma3_1b | ext_def_exp | 0.1900 | 0.2570 | 0.1500 | 387 | 1117 | 2193 |

#### English

**Top 10 Model-Template Configurations by F1 Score:**

| Rank | Model | Template | F1 | Precision | Recall | TP | FP | FN |
|------|-------|----------|-----|-----------|--------|----|----|----|
| 1 | gemini | cls_def_exp | 0.5400 | 0.5350 | 0.5460 | 1409 | 1225 | 1171 |
| 2 | qwen3_4b | cls_def_exp | 0.2560 | 0.2740 | 0.2410 | 621 | 1649 | 1959 |
| 3 | qwen25_14b | cls_exp | 0.2290 | 0.3100 | 0.1810 | 468 | 1043 | 2112 |
| 4 | gemma3_1b | ext_def_exp | 0.1720 | 0.2190 | 0.1420 | 366 | 1304 | 2214 |
| 5 | llama32_3b | cls_exp | 0.0170 | 0.1170 | 0.0090 | 24 | 182 | 2556 |

## Error Analysis by Annotation Type

The following analysis identifies which entity types (annotation types) are most challenging to extract for each model. This helps pinpoint specific linguistic patterns that could benefit from targeted improvements.

### Prompt Selection - Portuguese

| Annotation Type | TP | FP | FN | Avg Accuracy | Total Instances |
|-----------------|----|----|----|---------|---------|
| Pl_water | 0 | 0 | 40 | 0.0% | 40 |
| Other | 97 | 0 | 1383 | 6.5% | 1480 |
| Fac | 20 | 0 | 260 | 7.1% | 280 |
| Nat | 56 | 0 | 424 | 11.7% | 480 |
| Org | 583 | 0 | 4177 | 12.2% | 4760 |
| Loc | 366 | 0 | 2514 | 12.7% | 2880 |
| Per | 1006 | 0 | 5794 | 14.8% | 6800 |
| Obj | 422 | 0 | 2378 | 15.1% | 2800 |
| Pl_civil | 270 | 0 | 1010 | 21.1% | 1280 |
| Pl_capital | 27 | 0 | 53 | 33.8% | 80 |

**Key Observations:**

- **Most challenging annotation types:** Pl_water, Other, Fac
- **Easiest annotation types:** Obj, Pl_civil, Pl_capital
- **Overall average accuracy:** 13.5%

### Prompt Selection - English

| Annotation Type | TP | FP | FN | Avg Accuracy | Total Instances |
|-----------------|----|----|----|---------|---------|
| Pl_water | 1 | 0 | 39 | 2.5% | 40 |
| Other | 137 | 0 | 1343 | 9.3% | 1480 |
| Fac | 28 | 0 | 252 | 10.0% | 280 |
| Org | 583 | 0 | 4457 | 11.6% | 5040 |
| Per | 928 | 0 | 5952 | 13.5% | 6880 |
| Obj | 397 | 0 | 2483 | 13.8% | 2880 |
| Loc | 427 | 0 | 2453 | 14.8% | 2880 |
| Nat | 76 | 0 | 404 | 15.8% | 480 |
| Pl_civil | 297 | 0 | 943 | 24.0% | 1240 |
| Pl_capital | 20 | 0 | 60 | 25.0% | 80 |

**Key Observations:**

- **Most challenging annotation types:** Pl_water, Other, Fac
- **Easiest annotation types:** Nat, Pl_civil, Pl_capital
- **Overall average accuracy:** 14.0%

### Test - Portuguese

| Annotation Type | TP | FP | FN | Avg Accuracy | Total Instances |
|-----------------|----|----|----|---------|---------|
| Pl_region | 6 | 0 | 58 | 9.3% | 64 |
| Other | 121 | 0 | 727 | 14.3% | 848 |
| Fac | 69 | 0 | 223 | 23.6% | 292 |
| Org | 556 | 0 | 1780 | 23.8% | 2336 |
| Path | 1 | 0 | 3 | 25.0% | 4 |
| Loc | 283 | 0 | 765 | 27.0% | 1048 |
| Pl_water | 10 | 0 | 26 | 27.8% | 36 |
| Veh | 10 | 0 | 26 | 27.8% | 36 |
| Obj | 339 | 0 | 873 | 28.0% | 1212 |
| Per | 917 | 0 | 2235 | 29.1% | 3152 |
| Nat | 126 | 0 | 278 | 31.2% | 404 |
| Pl_country | 34 | 0 | 50 | 40.5% | 84 |
| Pl_civil | 317 | 0 | 435 | 42.2% | 752 |
| Pl_state | 4 | 0 | 4 | 50.0% | 8 |
| Pl_capital | 25 | 0 | 15 | 62.5% | 40 |

**Key Observations:**

- **Most challenging annotation types:** Pl_region, Other, Fac
- **Easiest annotation types:** Pl_civil, Pl_state, Pl_capital
- **Overall average accuracy:** 30.8%

### Test - English

| Annotation Type | TP | FP | FN | Avg Accuracy | Total Instances |
|-----------------|----|----|----|---------|---------|
| Pl_region | 6 | 0 | 74 | 7.5% | 80 |
| Other | 138 | 0 | 927 | 13.0% | 1065 |
| Path | 1 | 0 | 4 | 20.0% | 5 |
| Fac | 73 | 0 | 292 | 20.0% | 365 |
| Org | 577 | 0 | 2288 | 20.1% | 2865 |
| Per | 857 | 0 | 3083 | 21.7% | 3940 |
| Obj | 354 | 0 | 1166 | 23.3% | 1520 |
| Loc | 321 | 0 | 1024 | 23.9% | 1345 |
| Veh | 12 | 0 | 38 | 24.0% | 50 |
| Nat | 122 | 0 | 383 | 24.2% | 505 |
| Pl_water | 12 | 0 | 33 | 26.7% | 45 |
| Pl_civil | 344 | 0 | 606 | 36.2% | 950 |
| Pl_state | 4 | 0 | 6 | 40.0% | 10 |
| Pl_country | 44 | 0 | 61 | 41.9% | 105 |
| Pl_capital | 22 | 0 | 23 | 48.9% | 45 |

**Key Observations:**

- **Most challenging annotation types:** Pl_region, Other, Path
- **Easiest annotation types:** Pl_state, Pl_country, Pl_capital
- **Overall average accuracy:** 26.1%

## Token-Level Error Analysis: Most Misclassified Tokens

The following table shows the most frequently misclassified tokens (false negatives) at the token level. These patterns could indicate systematic weaknesses in the models' understanding of specific linguistic features.

### Prompt Selection - Portuguese

| Rank | Token | FN Count |
|------|-------|----------|
| 1 | a | 1148 |
| 2 | o | 965 |
| 3 | um | 346 |
| 4 | de | 231 |
| 5 | os | 227 |
| 6 | uma | 109 |
| 7 | as | 66 |
| 8 | em | 61 |
| 9 | homem | 49 |
| 10 | na | 38 |
| 11 | suspeitos | 34 |
| 12 | da | 34 |
| 13 | setúbal | 33 |
| 14 | à | 28 |
| 15 | pj | 28 |

### Prompt Selection - English

| Rank | Token | FN Count |
|------|-------|----------|
| 1 | the | 1718 |
| 2 | a | 698 |
| 3 | of | 231 |
| 4 | in | 92 |
| 5 | setúbal | 83 |
| 6 | to | 68 |
| 7 | man | 68 |
| 8 | told | 57 |
| 9 | on | 41 |
| 10 | hospital | 38 |
| 11 | woman | 29 |
| 12 | east | 28 |
| 13 | suspects | 28 |
| 14 | with | 27 |
| 15 | today | 27 |

### Test - Portuguese

| Rank | Token | FN Count |
|------|-------|----------|
| 1 | o | 873 |
| 2 | a | 728 |
| 3 | de | 233 |
| 4 | um | 216 |
| 5 | os | 202 |
| 6 | uma | 95 |
| 7 | as | 91 |
| 8 | homem | 62 |
| 9 | anos | 50 |
| 10 | em | 46 |
| 11 | à | 28 |
| 12 | concelho | 28 |
| 13 | da | 22 |
| 14 | aquela | 21 |
| 15 | dois | 19 |

### Test - English

| Rank | Token | FN Count |
|------|-------|----------|
| 1 | the | 1302 |
| 2 | a | 347 |
| 3 | of | 131 |
| 4 | in | 90 |
| 5 | to | 53 |
| 6 | two | 45 |
| 7 | that | 43 |
| 8 | an | 39 |
| 9 | man | 34 |
| 10 | source | 23 |
| 11 | gnr | 20 |
| 12 | at | 18 |
| 13 | district | 17 |
| 14 | other | 16 |
| 15 | his | 15 |

## Comparative Analysis: Portuguese vs English

### Model Performance Across Languages

Average F1 scores by model across both languages:

| Model | Portuguese (Avg F1) | English (Avg F1) | Difference |
|-------|------------------|------------------|------------|
| gemini | 0.4011 | 0.3923 | +0.0088 |
| gemma3_1b | 0.0867 | 0.0852 | +0.0014 |
| llama32_3b | 0.0032 | 0.0061 | -0.0029 |
| qwen25_14b | 0.1707 | 0.1634 | +0.0072 |
| qwen3_4b | 0.1892 | 0.1876 | +0.0017 |

## Recommendations

### 1. For Model Selection

- **High-Confidence Configurations:** Prioritize models with F1 > 0.75 for production use
- **Language-Specific Tuning:** English and Portuguese show different model preferences; select accordingly
- **Template Sensitivity:** Some models show significant F1 variance across templates (15%+ swing)

### 2. For Error Reduction

- **Token-Level Patterns:** The most frequently misclassified tokens suggest systematic weaknesses
- **Annotation Type Focus:** Prioritize improving performance on the most challenging entity types
- **Prompt Optimization:** Further fine-tune templates for models with low performance

### 3. For Future Work

- **Ensemble Methods:** Combine predictions from multiple best configurations
- **Fine-tuning:** Consider fine-tuning low F1 models on challenging annotation types
- **Error Analysis Deep Dive:** Manually review failure cases to identify systematic patterns
- **Cross-lingual Transfer:** Investigate whether Portuguese-trained models can improve English performance

## Appendix: Technical Details

### Evaluation Methodology

- **Strict Metrics:** Entity-level accuracy (exact span and type match required)
- **Precision:** TP / (TP + FP) = correct predictions / all positive predictions
- **Recall:** TP / (TP + FN) = correct predictions / all actual instances
- **F1 Score:** 2 × (Precision × Recall) / (Precision + Recall) = harmonic mean

### Data Summary

- **Total Model Configurations Evaluated:** 89
- **Annotation Type Configurations:** 235
- **Best Templates Analyzed:** 18
- **Unique Error Tokens Tracked:** 80

---

*This report was automatically generated from error_analysis.ipynb using all computed results. For visualizations and interactive exploration, refer to the notebook cells containing pie charts and bar charts by annotation type and token.*
