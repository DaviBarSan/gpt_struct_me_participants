"""Run the best prompt for each model/entity pair on the test set."""

import os
import time
import logging

import fire
import dotenv
from fsspec import config
import openai
import yaml
from experiments.constants import (
    BEST_TEMPLATES,
    ENTITIES,
    EXAMPLERS,
    RESOURCE_PATH,
    ROOT,
    SAMPLE_DOCS_IDS
)

from src.prompts import Prompter
from src.reader import read_lusa, read_lusa_en

from experiments.utils import mid2model

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dotenv.load_dotenv(ROOT / ".env")
openai.api_key = os.getenv("OPENAI_API_KEY")

RESULTS_PATH = ROOT / "results" / "test"


def main(mid: str = "chatgpt", language: str = "english", shot_language: str = "english", config_path: str = "config.yaml", temp: float = 0.3):
    """Main script."""
    model = mid2model(mid)
    logger.info(f"Using temperature: {temp}")
    entities = ENTITIES[language]
    sample_docs = SAMPLE_DOCS_IDS[language]
    examples = EXAMPLERS[shot_language]
    best_templates = BEST_TEMPLATES[language]
    config = yaml.safe_load(open(config_path))
    print(f"Config: {config}")
    if language == "portuguese":
        dataset = read_lusa(RESOURCE_PATH / "lusa_news")
    elif language == "english":
        dataset = read_lusa_en(RESOURCE_PATH / "lusa_en")
    
    if shot_language == "english":
        shot_dataset = read_lusa_en(RESOURCE_PATH / "lusa_en")
    elif shot_language == "portuguese":
        shot_dataset = read_lusa(RESOURCE_PATH / "lusa_news")
        
    docs2drop = sample_docs + list(examples.values())
    test_docs = [doc for doc in dataset if doc.id not in docs2drop]

    n_iter = len(entities) * len(test_docs)
    iter = 0
    for entity in entities:
        logger.info(f"Entity: {entity}")

        tid = best_templates[(mid, entity)]
        task = "classification" if "cls" in tid else "extraction"
        if "exp" in tid:
            try:
                print(f"Looking for example doc id: {examples[entity]}")
                example_doc_id = examples[entity]
                example = [doc for doc in shot_dataset if doc.id == example_doc_id][0]
            except IndexError:
                print(f"Missing doc_id {example_doc_id} in annotations.")
                continue
        else:
            example = None
        definition = "def" in tid

        for experiment_config in config["prompt_configs"]:
            prompt_config = experiment_config["experiment"]
            prompter = Prompter(
                entity=entity,
                task=task,
                example=example,
                definition=definition,
                delimiter=prompt_config["delimiters"],
                role=prompt_config["role"],
                language=language,
                constraints=prompt_config["constraints"],
                chain_of_thought=prompt_config["chain_of_thought"]
             )

            exp_name = f"{tid}_temp{temp}_{'delim' if prompt_config['delimiters'] else 'nodelim'}_{'role' if prompt_config['role'] else 'norole'}_{'cot' if prompt_config['chain_of_thought'] else 'nocot'}"
            for doc in test_docs:
                logger.info(f"Iteration {iter}/{n_iter}")

                prompt = prompter.generate(doc.text)

                answer_path = RESULTS_PATH / language / mid / entity / tid / exp_name / f"{doc.id}.txt"
                if not answer_path.exists():
                    answer_path.parent.mkdir(parents=True, exist_ok=True)
                    answer = model(prompt, temp=temp)
                    answer_path.write_text(answer)
                    logger.info(f"{mid} Answer:\n{answer}")
                    time.sleep(20)

                else:
                    logger.info(f"{mid} answer already exists.")

                iter += 1


if __name__ == "__main__":
    fire.Fire(main)
