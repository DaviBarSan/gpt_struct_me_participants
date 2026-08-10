#!/bin/bash
# Sentence-level counterpart of run_experiments.sh.
#
# For each model/language/temperature it runs the three-request sentence loop,
# compiles the raw answers into per-document artefacts, and scores the two
# phases (extraction, classification) with the existing parse/evaluate scripts.
#
# Cron-ready, same as run_experiments.sh: it refuses to start while another
# Python job of the same user is running, and reports start/success/failure to
# Slack via SLACK_WEBHOOK_URL.
#
# Environment overrides:
#   SLEEP     seconds to pause after each request (default 0). The driver issues
#             up to three requests per sentence (~610 sentences per language), so
#             the document-level pipeline's hardcoded 20s would add days to a
#             run. Keep 0 for the local vLLM models, raise only for the
#             rate-limited hosted APIs.
#   JOB_USER  user whose Python processes block a new run (default davibarrel).

set -u

# --- LOAD ENVIRONMENT VARIABLES ---
if [ -f .env ]; then
    source .env
else
    echo "Error: .env file not found!"
    exit 1
fi

SLACK_WEBHOOK="${SLACK_WEBHOOK_URL:-}"

MODELS=("gemini")
LANGUAGES=("portuguese" "english")
TEMPERATURES=("0.3")
SLEEP="${SLEEP:-0}"
JOB_USER="${JOB_USER:-davibarrel}"
CONFIG="experiments/exp_config.yaml"

# Post to Slack, if a webhook is configured. Deliberately cannot fail the run:
# a notification problem must not abort a multi-hour experiment, and an unset
# webhook should degrade to console-only logging rather than crash under set -u.
notify() {
    local text="$1"
    if [ -z "$SLACK_WEBHOOK" ]; then
        return 0
    fi
    curl -s -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"${text}\"}" \
        "$SLACK_WEBHOOK" > /dev/null || true
}

# Abort the whole batch, announcing which stage broke. Mirrors
# run_experiments.sh: one failing model/language stops everything, rather than
# leaving a half-scored results tree behind.
fail() {
    local stage="$1"
    local detail="$2"
    echo "[FATAL ERROR] ${stage}: ${detail}"
    notify "Failed pipeline :(\nExecution FAILED for Phase=sentence_${stage} | Model=${MID:-?} | Language=${LANG:-?} | Temp=${TEMP:-?}\n${detail}"
    exit 1
}

# --- OVERLAP PROTECTION ---
# Check if the user has any active python processes.
if pgrep -u "$JOB_USER" python > /dev/null; then
    echo "[$(date)] A Python job is already running for $JOB_USER. Skipping this cron execution."
    notify "Job Schedule: There is a pipeline already in progess, skipping the scheduled execution."
    exit 0
else
    echo "[$(date)] No active Python job found for $JOB_USER. Proceeding with execution."
fi

TIMESTAMP=$(date +%Y%m%d_%H%M)
mkdir -p ./logs

for MID in "${MODELS[@]}"; do
    for LANG in "${LANGUAGES[@]}"; do
        for TEMP in "${TEMPERATURES[@]}"; do

            LOG_FILE="./logs/log_test_sentence_${MID}_${LANG}_temp${TEMP}_${TIMESTAMP}.log"
            echo "[$(date)] Generating: Model=$MID | Language=$LANG | Temp=$TEMP | Sleep=$SLEEP"
            notify "Starting pipeline for Phase=sentence_level | Model=$MID | Language=$LANG | Temp=$TEMP | Sleep=$SLEEP"

            python -u -m experiments.test_sentence \
                --mid "$MID" --language "$LANG" --shot_language "$LANG" \
                --config_path "$CONFIG" --temp "$TEMP" --sleep "$SLEEP" \
                > "$LOG_FILE" 2>&1
            if [ $? -ne 0 ]; then
                fail "generation" "Driver exited non-zero. See $LOG_FILE"
            fi

            # Same completion check as run_experiments.sh: the last logged
            # iteration must be the final one.
            LAST_ITER=$(grep 'INFO:__main__:Iteration' "$LOG_FILE" | tail -n 1)
            if [[ "$LAST_ITER" =~ Iteration\ ([0-9]+)/([0-9]+) ]]; then
                CURRENT=${BASH_REMATCH[1]}
                TOTAL=${BASH_REMATCH[2]}
                if [ "$CURRENT" -ne $((TOTAL - 1)) ]; then
                    fail "generation" "Run stopped early at $CURRENT/$TOTAL. See $LOG_FILE"
                fi
            else
                fail "generation" "No iterations logged. See $LOG_FILE"
            fi

            # Every sentence hitting an existing answer file means this phase was
            # already complete before this execution started. The compile and
            # scoring steps below still run - they are cheap, idempotent, and
            # regenerate the artefacts - but Slack is spared a "succeeded"
            # message for a run that generated nothing.
            ALREADY_DONE_COUNT=$(grep -c "answer already exists" "$LOG_FILE")
            NOTHING_NEW=0
            if [ "$ALREADY_DONE_COUNT" -eq "$TOTAL" ]; then
                NOTHING_NEW=1
                echo "[$(date)] Nothing new generated: every sentence was already answered in a previous execution."
            fi

            echo "[$(date)] Compiling raw answers for $MID | $LANG"
            python -u -m experiments.compile_sentence --language "$LANG" --mid "$MID" \
                >> "$LOG_FILE" 2>&1
            if [ $? -ne 0 ]; then
                fail "compile" "Compilation failed. See $LOG_FILE"
            fi

            for PHASE in ext cls; do
                echo "[$(date)] Scoring $PHASE phase for $MID | $LANG"
                PHASE_LOG="./logs/log_sentence_${PHASE}_${MID}_${LANG}_temp${TEMP}_${TIMESTAMP}.log"

                python -u -m experiments.parse \
                    --mode "sentence_level/${PHASE}" --language "$LANG" --model "$MID" \
                    > "$PHASE_LOG" 2>&1
                if [ $? -ne 0 ]; then
                    fail "parse_${PHASE}" "Parse failed. See $PHASE_LOG"
                fi

                python -u -m experiments.evaluate \
                    --mode "sentence_level/${PHASE}" --language "$LANG" \
                    >> "$PHASE_LOG" 2>&1
                if [ $? -ne 0 ]; then
                    fail "evaluate_${PHASE}" "Evaluate failed. See $PHASE_LOG"
                fi
            done

            if [ "$NOTHING_NEW" -eq 1 ]; then
                echo "[$(date)] Done (no new generations): $MID | $LANG | temp $TEMP"
            else
                echo "[$(date)] Done: $MID | $LANG | temp $TEMP"
                notify "Succeeded pipeline :)\nExecution SUCCEEDED for Phase=sentence_level | Model=$MID | Language=$LANG | Temp=$TEMP"
            fi
            echo "----------------------------------------"
        done
    done
done
