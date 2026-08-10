#!/bin/bash
# Sentence-level counterpart of run_experiments.sh.
#
# For each model/language/temperature it runs the three-request sentence loop,
# compiles the raw answers into per-document artefacts, and scores the two
# phases (extraction, classification) with the existing parse/evaluate scripts.
#
# Deliberately lean: no cron overlap protection and no Slack notifications. If
# you want this on the cron schedule, graft the corresponding blocks from
# run_experiments.sh onto it.
#
# Note on SLEEP: the driver issues up to three requests per sentence (~610
# sentences per language), so the document-level pipeline's hardcoded 20s pause
# would add days to a run. Keep it at 0 for the local vLLM models and only raise
# it for the rate-limited hosted APIs.

set -u

if [ -f .env ]; then
    source .env
fi

MODELS=("gemini")
LANGUAGES=("portuguese" "english")
TEMPERATURES=("0.3")
SLEEP="${SLEEP:-0}"
CONFIG="experiments/exp_config.yaml"

TIMESTAMP=$(date +%Y%m%d_%H%M)
mkdir -p ./logs

for MID in "${MODELS[@]}"; do
    for LANG in "${LANGUAGES[@]}"; do
        for TEMP in "${TEMPERATURES[@]}"; do

            LOG_FILE="./logs/log_test_sentence_${MID}_${LANG}_temp${TEMP}_${TIMESTAMP}.log"
            echo "[$(date)] Generating: Model=$MID | Language=$LANG | Temp=$TEMP | Sleep=$SLEEP"

            python -u -m experiments.test_sentence \
                --mid "$MID" --language "$LANG" --shot_language "$LANG" \
                --config_path "$CONFIG" --temp "$TEMP" --sleep "$SLEEP" \
                > "$LOG_FILE" 2>&1
            if [ $? -ne 0 ]; then
                echo "[FATAL ERROR] Generation failed for $MID | $LANG | temp $TEMP. See $LOG_FILE"
                exit 1
            fi

            # Same completion check as run_experiments.sh: the last logged
            # iteration must be the final one.
            LAST_ITER=$(grep 'INFO:__main__:Iteration' "$LOG_FILE" | tail -n 1)
            if [[ "$LAST_ITER" =~ Iteration\ ([0-9]+)/([0-9]+) ]]; then
                CURRENT=${BASH_REMATCH[1]}
                TOTAL=${BASH_REMATCH[2]}
                if [ "$CURRENT" -ne $((TOTAL - 1)) ]; then
                    echo "[FATAL ERROR] Run stopped early at $CURRENT/$TOTAL. See $LOG_FILE"
                    exit 1
                fi
            else
                echo "[FATAL ERROR] No iterations logged. See $LOG_FILE"
                exit 1
            fi

            echo "[$(date)] Compiling raw answers for $MID | $LANG"
            python -u -m experiments.compile_sentence --language "$LANG" --mid "$MID" \
                >> "$LOG_FILE" 2>&1
            if [ $? -ne 0 ]; then
                echo "[FATAL ERROR] Compilation failed for $MID | $LANG. See $LOG_FILE"
                exit 1
            fi

            for PHASE in ext cls; do
                echo "[$(date)] Scoring $PHASE phase for $MID | $LANG"
                PHASE_LOG="./logs/log_sentence_${PHASE}_${MID}_${LANG}_temp${TEMP}_${TIMESTAMP}.log"

                python -u -m experiments.parse \
                    --mode "sentence_level/${PHASE}" --language "$LANG" --model "$MID" \
                    > "$PHASE_LOG" 2>&1
                if [ $? -ne 0 ]; then
                    echo "[FATAL ERROR] Parse failed for $PHASE | $MID | $LANG. See $PHASE_LOG"
                    exit 1
                fi

                python -u -m experiments.evaluate \
                    --mode "sentence_level/${PHASE}" --language "$LANG" \
                    >> "$PHASE_LOG" 2>&1
                if [ $? -ne 0 ]; then
                    echo "[FATAL ERROR] Evaluate failed for $PHASE | $MID | $LANG. See $PHASE_LOG"
                    exit 1
                fi
            done

            echo "[$(date)] Done: $MID | $LANG | temp $TEMP"
            echo "----------------------------------------"
        done
    done
done
