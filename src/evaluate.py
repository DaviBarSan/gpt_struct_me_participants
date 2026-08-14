"""Evaluation functions."""

from typing import Dict, Set
import difflib

from src.utils import get_full_sentence, string_overlap, tokenize, get_best_match
from experiments.constants import word_to_category


# Full participant labels as they appear in the prompts, mapped to the
# abbreviations used by the corpus annotations.
TYPE_ABBREVIATIONS = {
    "Object": "Obj",
    "Facility": "Fac",
    "Location": "Loc",
    "Person": "Per",
    "Event": "Eve",
    "Organization": "Org",
}

# Lookup accepting either spelling of a label, case-insensitively.
_TYPE_LOOKUP = {full.lower(): abbr for full, abbr in TYPE_ABBREVIATIONS.items()}
_TYPE_LOOKUP.update({abbr.lower(): abbr for abbr in TYPE_ABBREVIATIONS.values()})


def normalize_type(pred_type: str) -> str:
    """Normalize a predicted participant type to the corpus abbreviation.

    Models answer with either the full label ("Organization") or the already
    abbreviated one ("Org"), so a plain lookup on the full-label mapping would
    turn every abbreviated answer into "N/A". Labels outside the schema are
    returned verbatim so the reports reflect what the model actually predicted.
    """
    if pred_type is None:
        return "N/A"
    label = str(pred_type).strip()
    if not label:
        return "N/A"
    return _TYPE_LOOKUP.get(label.lower(), label)


def recall_score(tp: int, fn: int) -> float:
    """Compute the recall score."""
    return tp / (tp + fn) if tp + fn > 0 else 0


def precision_score(tp: int, fp: int) -> float:
    """Compute the precision score."""
    return tp / (tp + fp) if tp + fp > 0 else 0


def f1_score(tp: int, fp: int, fn: int) -> float:
    """Compute the F1 score."""
    p = precision_score(tp, fp)
    r = recall_score(tp, fn)
    return 2 * (p * r) / (p + r) if p + r > 0 else 0


def strict_metrics(prediction: list, annotation: list, template: str, modelo: str) -> dict:
    """Compute micro-averaged metrics for a given entity.
    ('modelo', 'entity','doc_id','template', 'token','pred_type', 'annt_type', 'result', 'f1_r_score')
    """
    tps, fns, fps = 0, 0, 0
    detailed_results = []
    for doc_id in prediction:
        if "cls" in template:
            # print("Template with classification detected.")
            preds = {(item[0]) for item in prediction[doc_id]}
            preds_dicts = {item[0]: normalize_type(item[1]) for item in prediction[doc_id]}
            annts = {item[0] for item in annotation[doc_id]}            
            annts_dict = {f'{item[0]}': item[1] for item in annotation[doc_id]}            
        else:
            # print("Template of extraction detected.")
            preds = {item for item in prediction[doc_id]}
            preds_dicts = {}
            annts = {item[0] for item in annotation[doc_id]}
            annts_dict = {item[0]: item[1] for item in annotation[doc_id]}            
            
        # print(f"Evaluating document ID: {doc_id}")
        # print("Preds:", preds)
        # print("Annts:", annts)
        # print("TP:", preds.intersection(annts))
        # print(f"prediction: {prediction}")

        # True Positives: In both
        for item in preds.intersection(annts):
            if "cls" in template:
                detailed_results.append((modelo, 'participants', doc_id, template, item, preds_dicts.get(item, "N/A"), annts_dict.get(item, "N/A"), "tp", ""))
            elif "ext" in template:
                detailed_results.append((modelo, 'participants', doc_id, template, item, "", annts_dict.get(item, "N/A"), "tp", ""))

        # False Positives: In prediction but not in annotation
        for item in preds.difference(annts):
            if "cls" in template:
                detailed_results.append((modelo, 'participants', doc_id, template, item, preds_dicts.get(item, "N/A"), "", "fp", ""))
            elif "ext" in template:
                detailed_results.append((modelo, 'participants', doc_id, template, item, "", "", "fp", ""))
            
        # False Negatives: In annotation but not in prediction
        for item in annts.difference(preds):
            if "cls" in template:
                detailed_results.append((modelo, 'participants', doc_id, template, item, "", annts_dict.get(item, "N/A"), "fn", ""))
            elif "ext" in template:
                detailed_results.append((modelo, 'participants', doc_id, template, item, "", annts_dict.get(item, "N/A"), "fn", ""))
            
        # Calculate counts for metrics
        # print("Detailed results for doc_id", doc_id, ":", detailed_results)
        tp = len(preds.intersection(annts))
        fp = len(preds.difference(annts))
        fn = len(annts.difference(preds))
        
        # try:
        #     pred = set(prediction[doc_id])
        #     annt = set(annotation[doc_id])
        # except KeyError:
        #     print(f"Missing doc_id {doc_id} in annotations.")
        #     continue
        # tp, fp, fn = exact_match(pred, annt)
        
        tps += tp
        fps += fp
        fns += fn

    recall = recall_score(tps, fns)
    precision = precision_score(tps, fps)
    f1 = f1_score(tps, fps, fns)
    
    # print("\n\n\nFalse Positives:")
    # for item in fp_raw_list:
    #     print(item)
    # print("\n\n\nFalse Negatives:")
    # for item in fn_raw_list:
    #     print(item)

    return {"recall": recall, "precision": precision, "f1": f1}, detailed_results


def exact_match(prediction: set, annotation: set, template: str) -> tuple:
    """Compute the TP, FP, FN for a set of predictions and annotations."""
    
    #store the type of entity for FP and FN reporting
    if "cls" in template:
        # print("Template with classification detected.")
        type_entity = prediction[1]
        prediction = prediction[0]   
    # print("Preds:", prediction)
    # print("Annts:", annotation)
    # print("TP:", prediction.intersection(annotation))
    # print(f"prediction: {prediction}")    
    
    tp = len(prediction.intersection(annotation))
    fp = len(prediction.difference(annotation))
    fn = len(annotation.difference(prediction))
    return tp, fp, fn


def relaxed_metrics(prediction: Dict, annotation: Dict, template: str, model: str, dict_words: dict) -> dict:
    """Compute micro-averaged metrics for a given entity."""
    f1 = 0
    # print("Computing relaxed metrics...")
    detailed_results_token_level = []
    for doc_id in prediction:
        print(f"prediction[doc_id]: {prediction[doc_id]}")
        print(f"annotation[doc_id]: {annotation[doc_id]}")
        if "cls" in template:
            # print("Template with classification detected. Relaxed metrics")
            preds = {item[0] for item in prediction[doc_id]}
            annts = {tuple(item) for item in annotation[doc_id]}
            # print("Template with classification detected.")
            preds = {(item[0], normalize_type(item[1])) for item in prediction[doc_id]}
            
        else:
            # print("Template of extraction detected. Relaxed metrics")
            preds = {item for item in prediction[doc_id]}
            annts = {item for item in annotation[doc_id]}
                 
        # print(f"Evaluating document ID: {doc_id}")
        # print("Preds:", preds)
        # print("Annts:", annts)
        # try:
        #     pred = set(prediction[doc_id])
        #     annt = set(annotation[doc_id])
        # except KeyError:
        #     print(f"Missing doc_id {doc_id} in annotations.")
        #     continue
        f1 += macro_averaged_f1_score(preds, annts, template, model, doc_id, detailed_results_token_level, dict_words)
    f1 /= len(prediction)
    return {"f1": f1}, detailed_results_token_level


def macro_averaged_f1_score(pred: Set[str], annt: Set[str], template: str, model: str, doc_id: str, detailed_results_token_level: list, dict_words: dict) -> float:
    """Compute the macro-averaged F1 score for a set of predictions and annotations.
            ('modelo', 'entity','doc_id','template','complete_prediction',
            'token','pred_type','matched_annotation',  'full_matched_sentence', 'ann_entity_id','annt_type','result',
            'word_category', 'pct_tp_participant_level', 'result_type')
    """
    f1 = 0
    # print("Complete pred:", pred)
    # print("Complete annt:", annt)
    for pred_entity in pred:
        # print(f"Pred in macro avg f1:", pred_entity)
        # print(f"Evaluating predicted entity: {pred_entity}")
        # print (f"Against annotations: {annt}")
        # Tokens that are in the prediction.
        if 'cls' in template:
            # print("Tokenizing predicted entity:", pred_entity[0])
            tkns_pred = list(tokenize(pred_entity[0]))
            # print(f"Tokens in prediction: {tkns_pred}")
        # Annotated tokens that overlap with the prediction.

            # match_entites = [
            #     annt_entity[0]
            #     for annt_entity in annt
            #     if string_overlap(pred_entity[0], annt_entity[0])
            # ]
            # print(f"Matching annotated entities: {match_entites}")
            (best_matched_annt, best_matched_anno_type, 
             best_matched_entity_id, best_full_matched_sentence) = get_best_match(tkns_pred, annt)
            # print(f"Best matched annotated entity: {best_matched_annt} with has entity id {best_matched_entity_id}")
            # 2. Get the diff
            diff = list(difflib.ndiff(tkns_pred, tokenize(best_matched_annt)))
            # Calcular o rácio nativo do difflib
            matcher = difflib.SequenceMatcher(None, tkns_pred, tokenize(best_matched_annt))
            pct_tp_participant_level = matcher.ratio()
            if pct_tp_participant_level == 0:
                result_type = 'MISS'
            elif pct_tp_participant_level == 1:
                result_type = 'EXACT'
            else:
                result_type = 'PARTIAL'
            # print(f"Diff between prediction and matched annotations: {diff}")
                        
            seen = set()
            tp_list = []
            fp_list = []
            fn_list = []
            # Categorize based on the ndiff prefixes
            for line in diff:
                tag = line[:2]    # '  ', '+ ', or '- '
                token = line[2:].strip()
                
                # Only process if we haven't handled this specific token string yet
                if token not in seen:
                    word_category = word_to_category(token, dict_words)
                    if tag == '  ':   # Match
                        tp_list.append(token)
                        seen.add(token)
                        # detailed_results_token_level.append((model, 'participants', doc_id, 
                        #                                      template, tkns_pred, pred_entity[0], token, pred_entity[1], 
                        #                                      best_matched_annt, best_matched_anno_type, "tp"))
                        detailed_results_token_level.append((model, 'participants', doc_id, 
                                                             template, tkns_pred, token, pred_entity[1], 
                                                             best_matched_annt, best_full_matched_sentence, best_matched_entity_id, best_matched_anno_type, "tp",
                                                             word_category, pct_tp_participant_level, result_type))
                    elif tag == '- ': # In prediction only
                        fp_list.append(token)
                        seen.add(token)
                        detailed_results_token_level.append((model, 'participants', doc_id, 
                                                             template, tkns_pred, token, pred_entity[1],
                                                             best_matched_annt, best_full_matched_sentence, best_matched_entity_id, best_matched_anno_type, "fp",
                                                             word_category, pct_tp_participant_level, result_type))
                    elif tag == '+ ': # In annotation only
                        fn_list.append(token)
                        seen.add(token)
                        detailed_results_token_level.append((model, 'participants', doc_id, 
                                                             template, tkns_pred, token, pred_entity[1],
                                                             best_matched_annt, best_full_matched_sentence, best_matched_entity_id, best_matched_anno_type, "fn",
                                                             word_category, pct_tp_participant_level, result_type))
            # print(f"TP: {tp_list}")
            # print(f"FP: {fp_list}")
            # print(f"FN: {fn_list}")
            tp = len(tp_list)
            fp = len(fp_list)
            fn = len(fn_list)

            f1 += f1_score(tp, fp, fn)
        elif 'ext' in template:
            # print(">>>>Tokenizing predicted entity:", pred_entity)
            tkns_pred = list(tokenize(pred_entity))
            # print(f"Tokens in prediction: {tkns_pred}")            
            # print(f"Evaluating predicted entity: {pred_entity}")
            # print(f"Against annotations: {annt}")

            # match_entites = [
            #     annt_entity[0]
            #     for annt_entity in annt
            #     if string_overlap(pred_entity, annt_entity[0])
            # ]
            (best_matched_annt, best_matched_anno_type, 
             best_matched_entity_id, best_full_matched_sentence) = get_best_match(tkns_pred, annt)
            # print(f"Best matched annotated entity: {best_matched_annt}")
            # 2. Get the diff
            diff = list(difflib.ndiff(tkns_pred, tokenize(best_matched_annt)))
            # Calcular o rácio nativo do difflib
            matcher = difflib.SequenceMatcher(None, tkns_pred, tokenize(best_matched_annt))
            pct_tp_participant_level = matcher.ratio()
            if pct_tp_participant_level == 0:
                result_type = 'MISS'
            elif pct_tp_participant_level == 1:
                result_type = 'EXACT'
            else:
                result_type = 'PARTIAL'
            # tkns_match = set(tokenize(" ".join(match_entites)))
            # print(f"Tokens prediction: {tkns_pred}")
            # print(f"Diff between prediction and matched annotations: {diff}")
            
            seen = set()
            tp_list = []
            fp_list = []
            fn_list = []
            # Categorize based on the ndiff prefixes
            for line in diff:
                tag = line[:2]    # '  ', '+ ', or '- '
                token = line[2:].strip()
                
                # Only process if we haven't handled this specific token string yet
                if token not in seen:
                    word_category = word_to_category(token, dict_words)
                    if tag == '  ':   # Match
                        tp_list.append(token)
                        seen.add(token)
                        detailed_results_token_level.append((model, 'participants', doc_id, 
                                                             template, tkns_pred, token, "", 
                                                             best_matched_annt, best_full_matched_sentence, best_matched_entity_id, best_matched_anno_type, "tp",
                                                             word_category, pct_tp_participant_level, result_type))
                    elif tag == '- ': # In prediction only
                        fp_list.append(token)
                        seen.add(token)
                        detailed_results_token_level.append((model, 'participants', doc_id, 
                                                             template, tkns_pred, token, "",
                                                             best_matched_annt, best_full_matched_sentence, best_matched_entity_id, best_matched_anno_type, "fp",
                                                             word_category, pct_tp_participant_level, result_type))
                    elif tag == '+ ': # In annotation only
                        fn_list.append(token)
                        seen.add(token)
                        detailed_results_token_level.append((model, 'participants', doc_id, 
                                                             template, tkns_pred, token, "",
                                                             best_matched_annt, best_full_matched_sentence, best_matched_entity_id, best_matched_anno_type, "fn",
                                                             word_category, pct_tp_participant_level, result_type))
            # print(f"TP: {tp_list}")
            # print(f"FP: {fp_list}")
            # print(f"FN: {fn_list}")
            tp = len(tp_list)
            fp = len(fp_list)
            fn = len(fn_list)
            f1 += f1_score(tp, fp, fn)            
            
    macro_avg_f1 = f1 / len(pred) if len(pred) > 0 else 0
    return macro_avg_f1
