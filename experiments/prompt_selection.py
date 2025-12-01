"""Select the best template for each model/entity pair on the test set."""

import logging
import os
import time

import dotenv
import openai
import fire

from src.prompts import Prompter
from src.reader import read_lusa, read_timebank

<<<<<<< HEAD
from experiments.utils import mid2model
from experiments.constants import (
=======
from utils import mid2model
from constants import (
>>>>>>> origin/main
    ENTITIES,
    EXAMPLERS,
    RESOURCE_PATH,
    ROOT,
    SAMPLE_DOCS_IDS
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RESULTS_PATH = ROOT / "results" / "prompt_selection"

dotenv.load_dotenv(ROOT / ".env")
openai.api_key = os.getenv("OPENAI_API_KEY")


def main(mid: str = "llama2-7b", language: str = "english"):
<<<<<<< HEAD
    print(language)
=======
>>>>>>> origin/main
    model = mid2model(mid)
    entities = ENTITIES[language]
    sample_docs = SAMPLE_DOCS_IDS[language]
    examples = EXAMPLERS[language]
    if language == "portuguese":
        dataset = read_lusa(RESOURCE_PATH / "lusa_news")
    elif language == "english":
        dataset = read_timebank(RESOURCE_PATH / "timebank")

    docs = [doc for doc in dataset if doc.id in sample_docs]
    tids = ["cls", "cls_def", "cls_def_exp", "cls_exp", "ext", "ext_def", "ext_def_exp", "ext_exp"]
<<<<<<< HEAD
    print(entities)
=======

>>>>>>> origin/main
    n_iter = len(entities) * len(docs) * len(tids)
    iter = 0
    for entity in entities:
        logger.info(f"Entity: {entity}")

        example_doc_id = examples[entity]
        example_doc = [doc for doc in dataset if doc.id == example_doc_id][0]
<<<<<<< HEAD
        
=======
>>>>>>> origin/main

        for tid in tids:
            logger.info(f"Template: {tid}")

            task = "classification" if "cls" in tid else "extraction"
            example = example_doc if "exp" in tid else None
            definition = "def" in tid

            prompter = Prompter(
                entity=entity,
                task=task,
                example=example,
                definition=definition,
            )

            for doc in docs:
                logger.info(f"Iteration {iter}/{n_iter}")

                prompt = prompter.generate(doc.text)
            
                answer_path = RESULTS_PATH / language / mid / entity / tid / f"{doc.id}.txt"
                if not answer_path.exists():
                    answer_path.parent.mkdir(parents=True, exist_ok=True)
                    answer = model(prompt)
<<<<<<< HEAD
                    print(f"Generated answer: {answer}")
                    print(f"Writing answer to {answer_path}")
                    answer_path.write_text(answer, encoding='utf-8')
=======
                    answer_path.write_text(answer)
>>>>>>> origin/main
                    logger.info(f"{mid} Answer:\n{answer}")
                    time.sleep(10)
                else:
                    logger.info(f"{mid} answer already exists.")

                iter += 1


if __name__ == "__main__":
    fire.Fire(main)
