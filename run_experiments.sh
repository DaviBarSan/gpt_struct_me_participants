#!/bin/bash

# --- LOAD ENVIRONMENT VARIABLES ---
if [ -f .env ]; then
    source .env
else
    echo "Error: .env file not found!"
    exit 1
fi

SLACK_WEBHOOK=$SLACK_WEBHOOK_URL

# --- OVERLAP PROTECTION ---
# Check if user 'davibarrel' has any active python processes
if pgrep -u davibarrel python > /dev/null; then
    echo "[$(date)] A Python job is already running for davibarrel. Skipping this cron execution."
    curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"Job Schedule: There is a pipeline already in progess, skipping the scheduled execution.\"}" \
            $SLACK_WEBHOOK
exit 0
else
    echo "[$(date)] No active Python job found for davibarrel. Proceeding with execution."
fi

# Define your experiment variables
PHASES=("experiments.prompt_selection" "experiments.test")
MODELS=("amalia")  # Add all your model IDs here
LANGUAGES=("portuguese" "english")
TEMPERATURES=("0.3" "0.6" "1")  # Swept only for the test phase; prompt_selection always runs at temp=0.3

# Get the start time once so all logs in this batch share the same timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M)

# Ensure logs directory exists to prevent "No such file or directory" errors
mkdir -p ./logs

for MID in "${MODELS[@]}"; do
    for LANG in "${LANGUAGES[@]}"; do
        for PHASE in "${PHASES[@]}"; do

            # This strips the "experiments." prefix
            PHASE_NAME=${PHASE#*.}

            # Only the test phase sweeps over temperatures; prompt_selection
            # always runs at a fixed temp=0.3.
            if [ "$PHASE" == "experiments.test" ]; then
                PHASE_TEMPS=("${TEMPERATURES[@]}")
            else
                PHASE_TEMPS=("0.3")
            fi

            for TEMP in "${PHASE_TEMPS[@]}"; do
                LOG_FILE="log_${PHASE_NAME}_${MID}_${LANG}_temp${TEMP}_${TIMESTAMP}.log"

                START_TIME=$(date +"%Y-%m-%d %H:%M:%S")
                echo "[$START_TIME] Starting: Phase=$PHASE_NAME | Model=$MID | Language=$LANG | Temp=$TEMP"
                curl -X POST -H 'Content-type: application/json' \
                --data "{\"text\":\"Starting pipeline for Phase=$PHASE_NAME | Model=$MID | Language=$LANG | Temp=$TEMP\"}" \
                $SLACK_WEBHOOK

                if [ "$PHASE" == "experiments.test" ]; then
                    echo "Executing: python -u -m $PHASE --mid $MID --language $LANG --shot_language $LANG --config_path experiments/exp_config.yaml --temp $TEMP"
                    python -u -m $PHASE --mid $MID --language $LANG --shot_language $LANG --config_path experiments/exp_config.yaml --temp $TEMP > "./logs/$LOG_FILE" 2>&1
                else
                    # Run the python script
                    echo "Executing: python -u -m $PHASE --mid $MID --language $LANG --temp $TEMP"
                    python -u -m $PHASE --mid $MID --language $LANG --temp $TEMP > "./logs/$LOG_FILE" 2>&1
                fi
                echo "Logging output to: ./logs/$LOG_FILE"

                # 1. Grab the very last iteration log line printed in the file
                LAST_ITER=$(grep 'INFO:__main__:Iteration' "./logs/$LOG_FILE" | tail -n 1)
                echo "Last iteration found: $LAST_ITER"

                # Assume failure by default
                SUCCESS=0

                # 2. Use Bash regex to extract the current and total iteration numbers
                if [[ "$LAST_ITER" =~ Iteration\ ([0-9]+)/([0-9]+) ]]; then
                    CURRENT=${BASH_REMATCH[1]}
                    TOTAL=${BASH_REMATCH[2]}

                    # 3. Check if the current iteration matches the total (e.g., 152 == 152)
                    if [ "$CURRENT" -eq $((TOTAL - 1)) ]; then
                        SUCCESS=1
                    fi
                fi

                # 4. Handle the result
                if [ "$SUCCESS" -eq 1 ]; then
                    # Every iteration hit an existing answer file means this phase
                    # was already fully done before this execution started (nothing
                    # new was generated), so this run's log and the downstream
                    # parse/eval/best-template logs would be pure noise.
                    ALREADY_DONE_COUNT=$(grep -c "answer already exists" "./logs/$LOG_FILE")

                    if [ "$ALREADY_DONE_COUNT" -eq "$TOTAL" ]; then
                        rm -f "./logs/$LOG_FILE"
                        echo "Phase already completed in a previous execution - skipping log for $LOG_FILE"
                        echo "----------------------------------------"
                    else
                        END_TIME=$(date +"%Y-%m-%d %H:%M:%S")
                        echo "[$END_TIME] Successfully finished $LOG_FILE ($CURRENT/$TOTAL)"
                        curl -X POST -H 'Content-type: application/json' \
                        --data "{\"text\":\"Succeeded pipeline :)\nExecution SUCCEEDED for Phase=$PHASE_NAME | Model=$MID | Language=$LANG | Temp=$TEMP\"}" \
                        $SLACK_WEBHOOK
                        echo "----------------------------------------"

                        # Required step: before the test phase can run, the best prompt
                        # template (highest F1) for this model/language must be selected
                        # and written into BEST_TEMPLATES in experiments/constants.py.
                        if [ "$PHASE" == "experiments.prompt_selection" ]; then
                            PARSE_EVAL_LOG="prmpt_sel_parse_eval_${MID}_${LANG}_temp${TEMP}_${TIMESTAMP}.log"
                            BEST_TMPLT_LOG="best_tmplt_sel_${MID}_${LANG}_temp${TEMP}_${TIMESTAMP}.log"

                            echo "[$(date)] Parsing/evaluating prompt_selection results for $MID | $LANG"
                            bash ./scripts/promp_selection_pos_exec_scripts.sh "$LANG" > "./logs/$PARSE_EVAL_LOG" 2>&1
                            if [ $? -ne 0 ]; then
                                echo "[FATAL ERROR] Failed to parse/evaluate prompt_selection results for $MID | $LANG. Aborting."
                                exit 1
                            fi

                            echo "[$(date)] Selecting best prompt template (highest F1) for $MID | $LANG"

                            python -u -m experiments.select_best_templates --mid "$MID" --language "$LANG" > "./logs/$BEST_TMPLT_LOG" 2>&1
                            if [ $? -ne 0 ]; then
                                echo "[FATAL ERROR] Failed to select best prompt template for $MID | $LANG. Aborting."
                                exit 1
                            fi
                        fi
                    fi
                else
                    # If the numbers don't match, or if it crashed before printing any iterations
                    echo "[FATAL ERROR] Task crashed or OOM detected!"
                    echo "Last recorded log: ${LAST_ITER:-None found}"
                    echo "Aborting the entire batch script immediately."
                    curl -X POST -H 'Content-type: application/json' \
                    --data "{\"text\":\"Failed pipeline :(\nExecution FAILED for Phase=$PHASE_NAME | Model=$MID | Language=$LANG | Temp=$TEMP\"}" \
                    $SLACK_WEBHOOK
                    # This instantly stops the Bash script. No further phases/models will run.
                    exit 1
                fi

            done

        done
    done
done
