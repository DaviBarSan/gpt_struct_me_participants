#!/bin/bash
# Parse and evaluate prompt_selection results for a given language.
# Usage: ./scripts/promp_selection_pos_exec_scripts.sh [language]
LANGUAGE="${1:-portuguese}"

python -m experiments.parse prompt_selection --language "$LANGUAGE"
python -m experiments.evaluate prompt_selection --language "$LANGUAGE"
