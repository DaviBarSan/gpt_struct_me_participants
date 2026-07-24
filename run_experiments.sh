#!/bin/bash

# --- OVERLAP PROTECTION ---
# Check if user 'davibarrel' has any active python processes
if pgrep -u davibarrel python > /dev/null; then
    echo "[$(date)] A Python job is already running for davibarrel. Skipping this cron execution."
    exit 0
else
    echo "[$(date)] No active Python job found for davibarrel. Proceeding with execution."
fi

# Define your experiment variables
PHASES=("experiments.prompt_selection" "experiments.test")
MODELS=("qwen3_14b")  # Add all your model IDs here
LANGUAGES=("portuguese" "english")

# Get the start time once so all logs in this batch share the same timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M)

# Ensure logs directory exists to prevent "No such file or directory" errors
mkdir -p ./logs 

for MID in "${MODELS[@]}"; do
    for LANG in "${LANGUAGES[@]}"; do
        for PHASE in "${PHASES[@]}"; do
            
            # This strips the "experiments." prefix
            PHASE_NAME=${PHASE#*.}
            LOG_FILE="log_${PHASE_NAME}_${MID}_${LANG}_${TIMESTAMP}.log"

            START_TIME=$(date +"%Y-%m-%d %H:%M:%S")
            echo "[$START_TIME] Starting: Phase=$PHASE_NAME | Model=$MID | Language=$LANG"

            # Run the python script
            python -u -m $PHASE --mid $MID --language $LANG > "./logs/$LOG_FILE" 2>&1 

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
                if [ "$CURRENT" -eq "$TOTAL" ]; then
                    SUCCESS=1
                fi
            fi

            # 4. Handle the result
            if [ "$SUCCESS" -eq 1 ]; then
                END_TIME=$(date +"%Y-%m-%d %H:%M:%S")
                echo "[$END_TIME] Successfully finished $LOG_FILE ($CURRENT/$TOTAL)"
                echo "----------------------------------------"
            else
                # If the numbers don't match, or if it crashed before printing any iterations
                echo "[FATAL ERROR] Task crashed or OOM detected!"
                echo "Last recorded log: ${LAST_ITER:-None found}"
                echo "Aborting the entire batch script immediately."
                
                # This instantly stops the Bash script. No further phases/models will run.
                exit 1 
            fi

        done
    done
done
