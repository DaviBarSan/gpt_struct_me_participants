"""Parse models predictions."""

import json
from pathlib import Path

import fire
import pandas as pd

from experiments.constants import RESOURCE_PATH, ROOT, WORD_CATEGORIES_EN, WORD_CATEGORIES_PT

from src.reader import read_lusa, read_timebank, read_lusa_en
from src.evaluate import strict_metrics, relaxed_metrics


RESULTS_PATH = ROOT / "results"


def read_predicions(path: Path) -> dict:
    """Read and structure the predictions of the models."""
    predictions_path = path / "predictions.json"
    content = json.loads(predictions_path.read_text(encoding='utf-8'))

    # print(f"Loaded prediction contents: {content}")
    predictions = {}
    for prediction in content:
        model = prediction["model"]
        template = prediction["template"]
        doc = prediction["doc"]
        entity = prediction["entity"]
        pred = prediction["entities"]
        answer = prediction["answer"]

        if model not in predictions:
            predictions[model] = {}
        if template not in predictions[model]:
            predictions[model][template] = {}
        if entity not in predictions[model][template]:
            predictions[model][template][entity] = {}
        if doc not in predictions[model][template][entity]:
            predictions[model][template][entity][doc] = []
        
        # predictions[model][template][entity][doc] = pred
        # print(f"\n\nEntity: {entity}, template: {template}, Doc: {doc}\n Asnwer: {answer}\n")
        predictions[model][template][entity][doc] = answer

    
    # print(f"Structured predictions: {predictions}")
    return predictions


def read_annoations(path: Path) -> dict:
    """Read and structure the annotations of the corpus."""
    if path.name == "lusa_en":
        documents = read_lusa_en(path)
    elif path.name == "lusa_news":
        documents = read_lusa(path)    

    annotations = {}
    annotations["event triggers"] = {
        doc.id: [event.text for event in doc.events]
        for doc in documents
    }

    annotations["participants"] = {
        doc.id: [(annotation.get("text"), 
                  annotation.get("participant_type_domain"), 
                  annotation.get("id"), 
                  annotation.get("full_news_article"))
        for annotation in doc.annotations if annotation.get("type") == "Participant"]
        for doc in documents
    }
    # print("Participant Annotations:", annotations["participants"])
    
    annotations["time expressions"] = {
        doc.id: [timex.text for timex in doc.timexs]
        for doc in documents
    }
    return annotations


def evaluate(predicitons: dict, annotations: dict, dict_words: dict) -> list:
    """Evaluate the predictions of the models."""
    results = []
    results_details = [('modelo', 'entity','doc_id','template', 'token','pred_type', 'annt_type', 'result', 'f1_r_score')]
    result_detailts_token_level = [('modelo', 'entity','doc_id','template','complete_prediction', 
                                    'token','pred_type','matched_annotation', 'full_matched_sentence', 'ann_entity_id','annt_type','result',
                                    'word_category', 'pct_tp_participant_level', 'result_type')]
    for model, templates in predicitons.items():
        for template, entities in templates.items():
            for entity, prediction in entities.items():
                print(f"Evaluating {model} - {entity} - {template}")
                annotation = annotations[entity]
                strict, details = strict_metrics(prediction, annotation, template, model)
                relaxed, token_details = relaxed_metrics(prediction, annotation, template, model, dict_words)
                results.append({
                    "model": model,
                    "template": template,
                    "entity": entity,
                    "strict": strict,
                    "relaxed": relaxed
                })
                results_details.append(details)
                result_detailts_token_level.append(token_details)
    #  = [item for sublist in results_details if isinstance(sublist, list) for item in sublist]
    headers = list(results_details[0])
    # 2. Flatten the remaining lists of sets into one list of sets
    data_rows = [item for sublist in results_details[1:] for item in sublist]
    # 3. Create the DataFrame
    # Since the rows are sets (unordered), we convert them to lists.
    # Note: This assumes the set elements match the header count.
    df_results_details = pd.DataFrame([list(row) for row in data_rows], columns=headers)
    # print("Detailed results:", results_details)
    
    headers_token_level = list(result_detailts_token_level[0])
    data_rows_token_level = [item for sublist in result_detailts_token_level[1:] for item in sublist]
    df_results_token_level = pd.DataFrame([list(row) for row in data_rows_token_level], columns=headers_token_level)
    
    return results, df_results_details, df_results_token_level


def make_results_table(results: list) -> pd.DataFrame:
    for result in results:
        strict = result.pop("strict")
        result["precision"] = strict["precision"]
        result["recall"] = strict["recall"]
        result["f1"] = strict["f1"]

        relaxed = result.pop("relaxed")
        result["f1_r"] = relaxed["f1"]
    df = pd.DataFrame(results)
    return df



def main(mode: str = "test", language: str = "portuguese", store_table: bool = True) -> None:
    path = RESULTS_PATH / mode / language
    predictions = read_predicions(path)
    # print("Predictions loaded: ", predictions)
    if language == "portuguese":
        ann_path = RESOURCE_PATH / "lusa_news"
        dict_words = WORD_CATEGORIES_PT
    elif language == "english":
        ann_path =  RESOURCE_PATH / "lusa_en"
        dict_words = WORD_CATEGORIES_EN

    # print(ann_path)
    annotations = read_annoations(ann_path)
    results, details_df, details_token_level_df = evaluate(predictions, annotations, dict_words)

    output_path = path / "results.json"
    json.dump(results, output_path.open("w"), indent=4)
    
    details_output_path = path / "detailed_results.csv"
    # details_df = pd.DataFrame(details, columns=['modelo', 'entity','doc_id','template', 'token','pred_type', 'annt_type', 'result', 'f1_r_score'])
    details_df.to_csv(details_output_path, index=False)
    
    details_token_level_output_path = path / "detailed_results_token_level.csv"
    details_token_level_df.to_csv(details_token_level_output_path, index=False)
    
    if store_table:
        table = make_results_table(results)
        
        if mode == "test":
            table.sort_values(["entity", "model"], inplace=True)
            table.reset_index(drop=True, inplace=True)
        elif mode == "prompt_selection":
            table.sort_values(["model", "entity", "f1"], inplace=True)
            table.reset_index(drop=True, inplace=True)
        
        print(table.to_string())
        table.to_csv(path / "results.csv", index=False)
        

if __name__ == "__main__":
    fire.Fire(main)
