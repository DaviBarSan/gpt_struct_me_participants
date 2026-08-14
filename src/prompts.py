"""Build prompts for query the models."""

import json
from itertools import zip_longest
from string import Template

from src.base import Document
from src.meta import ENTITIES
from src.sentences import split_sentences_with_offsets


class Prompter:
    """Prompt generator."""

    def __init__(
        self,
        entity: str,
        task: str = "extraction",
        example: Document = None,
        definition: bool = False,
        delimiter: bool = False,
        role: bool = False,
        language: str = "english",
        constraints: bool = False,
        chain_of_thought: bool = False,
        candidates: bool = False,
        detection_negatives: list = None,
        class_definitions: bool = False,
        confidence: bool = False
    ):
        """Initialize the prompter.
        Args:
            entity: ["event triggers", "time expressions", "participants"]
            task: ["extraction", "classification", "detection"]
            example: A document to be used as an example.
            definition: Whether to include the definition of the entity.
            candidates: Classification only. Whether the entities to classify
                are supplied with the input instead of being extracted by the
                model, as in the sentence-level pipeline
                (experiments/test_sentence.py), where classification is
                conditioned on the spans the extraction step returned.
            detection_negatives: Detection only. Sentences that mention no
                entity, to demonstrate the negative case alongside the positive
                sentences taken from `example`. See
                `experiments.constants.DETECTION_NEGATIVES` for why they are
                supplied instead of mined from `example`.
            class_definitions: Classification only. List the classes with the
                annotation guideline's definition of each, instead of naming them
                only. Opt-in, so the document-level prompts - the baseline the
                sentence-level runs are contrasted against - stay unchanged.
            confidence: Ask for a confidence in [0, 1] alongside every
                prediction: one for the verdict in detection, one per entity in
                extraction, one per class in classification. Widens the answer by
                one value per element; `src.confidence` reads both the widened and
                the original shapes. Opt-in, for the same reason as above.
        """
        self.task = task
        self.entity = entity
        self.expects_candidates = candidates and task == "classification"
        self.candidates_label = f"{self.entity.capitalize()} to classify"
        self.detection_examples = []
        # The examples deliberately carry no confidence. Showing one anchors the
        # answer on it: demonstrating the gold annotations with 1.0 - the only
        # honest value for them, since gold carries no uncertainty - made gemini
        # answer 1.0 for all 37 predictions of a smoke run. Inventing varied
        # values instead would put fabricated judgements in the prompt, so the
        # shape is specified in the format section and the examples are left as
        # they are, with a note saying so.
        if not confidence:
            example_note = ""
        elif task == "detection":
            example_note = (" The example outputs omit the confidence; your answer"
                            " must include it.")
        else:
            example_note = (" The example output omits the confidence; your answer"
                            " must include one for every element.")
        template = []
        if role:
            if language == "english":
                template.append(f"You are a helpful and precise assistant for extracting information about {self.entity} from news articles.\n"
                                f"Think as a grammatical expert and pay attention to the entities lexical components like pronouns and articles.")
                if delimiter is True:
                    template.append(f"----------------------------------")
            elif language == "portuguese":
                template.append(f"Você é um assistente útil e preciso para extrair informações sobre {self.entity} de artigos de notícias.\n"
                                f"Pense como um especialista gramatical e preste atenção aos componentes lexicais das entidades, como pronomes e artigos.")
                if delimiter:
                    template.append(f"----------------------------------")
        if task == "extraction":
            template.append(f"Task:\n"
                            f"Extract all {self.entity}.")
            if delimiter:
                template.append(f"----------------------------------")
            if confidence:
                output_format = "JSON-parseable list where each element is a list of two values, the entity as a string and a number between 0 and 1 with your confidence that it is correct, only with the JSON array and nothing else. For example: [[\"first entity\", 0.85], [\"second entity\", 0.6]]. Do not include any introductory text, explanation, or markdown code fences."
            else:
                output_format = "JSON-parseable list of strings only with the JSON array and nothing else. Do not include any introductory text, explanation, or markdown code fences."
            self.annotation_extraction = self._get_extraction_annotation

        elif task == "classification":
            # With definitions the classes are spelled as the corpus spells them
            # ("Per", "Pl_capital"), so a compliant answer needs no mapping to be
            # compared against the gold label.
            classes = ENTITIES[self.entity]["classes"]
            if class_definitions:
                classes = ENTITIES[self.entity].get("class_definitions", classes)
            template.append(f"Task:\n")
            if self.expects_candidates:
                template.append(f"Classify each of the {self.entity} listed under \"{self.candidates_label}\", "
                                f"according to how it is used in the input.\n\n"
                                f"Classes:\n"
                                f"{classes}")
            else:
                template.append(f"Extract and classify all {self.entity}\n\n"
                                f"Classes:\n"
                                f"{classes}")
            if delimiter:
                template.append(f"----------------------------------")
            if confidence:
                output_format = "JSON-parseable list where each element is a list of three values, only with the JSON array and nothing else. Do not include any introductory text, explanation, or markdown code fences." \
                                "The first value is the entity as a string, the second is the class as a string, and the third is a number between 0 and 1 with your confidence in that class. For example: [[\"first entity\", \"its class\", 0.85], [\"second entity\", \"its class\", 0.6]]. Place the JSON parsable list inside <Output> tags."
            else:
                output_format = "JSON-parseable list where each element is a list with two strings, only with the JSON array and nothing else. Do not include any introductory text, explanation, or markdown code fences." \
                                "The first string is the entity and the second is the class. Place the JSON parsable list inside <Output> tags."
            if self.expects_candidates:
                output_format += " Return exactly one element for every entity listed above, " \
                                 "repeating the entity string verbatim as the first string."
            self.annotation_extraction = self._get_classification_annotation

        elif task == "detection":
            # Binary gate for the sentence-level pipeline: the extraction and
            # classification requests are only spent on a sentence the model
            # says mentions the entity. The demonstrations are single sentences,
            # not whole articles - an article example (the only kind the corpus
            # readers provide) would be one the answer is trivially "yes" for -
            # so they are built here and the shared example block is bypassed.
            self.detection_examples = self._get_detection_examples(
                example, detection_negatives
            )
            example = None
            template.append(f"Task:\n"
                            f"Determine whether the input mentions any {self.entity}.")
            if delimiter:
                template.append(f"----------------------------------")
            if confidence:
                output_format = "the word yes or no, then a space, then a number between 0 and 1 with your confidence in that answer, and nothing else. For example: yes 0.85. Do not include any introductory text, explanation, or markdown code fences."
            else:
                output_format = "a single word, either yes or no, and nothing else. Do not include any introductory text, explanation, or markdown code fences."
            self.annotation_extraction = self._get_extraction_annotation

        else:
            raise ValueError(f"Task {task} not supported.")

        if definition:
            if delimiter:
                template.append(f"----------------------------------")
            template.append(f"Definition:\n"
                            f"{ENTITIES[self.entity]['definition']}")

        if self.detection_examples:
            if delimiter:
                template.append(f"----------------------------------")
            block = [f"Examples:{example_note}"]
            for sentence, mentions in self.detection_examples:
                # Sentence and verdict only. The annotated mentions decide which
                # verdict an example carries, but printing them would demonstrate
                # an output the request never asks for, and the answer this step
                # is parsed for is a single word.
                sentence_text = sentence.replace("$", "$$")
                block.append(f"\tInput:\n"
                             f"\t\"{sentence_text}\"\n"
                             f"\tOutput:\n"
                             f"\t{'yes' if mentions else 'no'}\n")
            template.append("\n".join(block))

        if example is not None:
            example_text = example.text.replace("$", "$$") # Escape $ for Template
            if delimiter:
                template.append(f"----------------------------------")
            example_annt = self.annotation_extraction(example)
            example_annt_str = json.dumps(example_annt, ensure_ascii=False).replace("$", "$$")
            template.append(f"Example:{example_note}\n"
                            f"\tInput:\n"
                            f"\t\"{example_text}\"\n")
            if delimiter:
                template.append(f"----------------------------------")
            if self.expects_candidates:
                # The example has to demonstrate the candidate-conditioned
                # shape too, otherwise it teaches a format the request does not
                # follow: input, then the list to classify, then the pairs.
                example_candidates = json.dumps(
                    [annt[0] for annt in example_annt], ensure_ascii=False
                ).replace("$", "$$")
                template.append(f"\t{self.candidates_label}:\n"
                                f"\t{example_candidates}\n")
            template.append(f"\tOutput:\n"
                            f"\t{example_annt_str}")
        if delimiter:
            template.append(f"----------------------------------")
        template.append(f"Format:\n"
                        f"{output_format}"
                        f"\nUse encoding: utf-8.")
        if chain_of_thought:
            if delimiter:
                template.append(f"----------------------------------")
            if language == "english":
                template.append(f"REASONING: Before generating the final JSON, you must analyze the text step-by-step. Identify potential entities, evaluate their context, and match them against the allowed Classes. Place this analysis inside <Thought> tags.")
            elif language == "portuguese":
                template.append(f"RAZÃO: Antes de gerar o JSON final, você deve analisar o texto passo a passo. Identifique entidades potenciais, avalie seu contexto e compare-as com as Classes permitidas. Coloque essa análise dentro de tags <Thought>.")
        if constraints:
            if delimiter:
                template.append(f"----------------------------------")
            if language == "english":
                template.append(
                                f"<Constraints>\n"
                                f"1. CRITICAL: Output ONLY a JSON-parseable array of lists. No preamble, no markdown, no explanation.\n"
                                f"2. VERBATIM: Extract entities exactly as they appear in the text.\n"
                                f"3. GROUNDING: Extract ONLY participants explicitly mentioned. Do not assume or infer others.\n"
                                f"4. ABSTENTION: If unsure of a classification or if a participant is missing data, exclude them. If no participants exist, return [].\n"
                                f"</Constraints>")
            elif language == "portuguese":
                template.append(
                                f"<Restrições>\n"
                                f"1. CRÍTICO: Saída APENAS um array de listas JSON-parseável. Sem preâmbulo, sem markdown, sem explicação.\n"
                                f"2. VERBATIM: Extraia as entidades exatamente como aparecem no texto.\n"
                                f"3. GROUNDING: Extraia APENAS participantes explicitamente mencionados. Não assuma ou infira outros.\n"
                                f"4. ABSTENÇÃO: Se tiver dúvidas sobre uma classificação ou se um participante estiver faltando dados, exclua-os. Se não existirem participantes, retorne [].\n"
                                f"</Restrições>")

        template = "\n\n".join(template)
        if self.expects_candidates:
            self.template = Template(
                f"{template}\n\nInput:\n\"$text\"\n\n{self.candidates_label}:\n$candidates\n\nOutput:\n"
            )
        else:
            self.template = Template(
                f"{template}\n\nInput:\n\"$text\"\n\nOutput:\n"
            )

    def _get_annotated_entities(self, doc):
        """The annotated entity objects of `self.entity` in `doc`."""
        if self.entity == "event triggers":
            return doc.events
        elif self.entity == "time expressions":
            return doc.timexs
        elif self.entity == "participants":
            return doc.participants
        else:
            raise ValueError(f"Entity {self.entity} not supported.")

    def _get_detection_examples(self, doc, negatives, n_per_class: int = 3):
        """Build the sentence-level demonstrations for the detection task.

        Positives come from `doc`: its first `n_per_class` sentences carrying a
        gold annotation of `self.entity`. A sentence is positive when an
        annotation *starts* inside it - stricter than searching for the mention
        string, which would also mark a later sentence that merely repeats a span
        without being annotated there. The mentions are returned for inspection
        but are not rendered into the prompt: they only decide the verdict.

        Negatives are supplied by the caller instead of mined from `doc`, since
        no document of the prompt-selection set has three participant-free
        sentences (see `experiments.constants.DETECTION_NEGATIVES`).

        Args:
            doc: The exampler document, or None for a zero-shot gate.
            negatives: Sentences mentioning no entity, or None.
            n_per_class: How many positive and negative examples to show.

        Returns:
            `(sentence, mentions)` pairs, positives and negatives interleaved so
            the yes/no alternation carries no positional pattern to latch onto.
            `mentions` is empty exactly for the negatives.
        """
        positives = []
        if doc is not None:
            entities = self._get_annotated_entities(doc)
            for _, sentence, start, end in split_sentences_with_offsets(doc.text):
                mentions = [
                    ent.text for ent in entities
                    if isinstance(ent.offset, (tuple, list))
                    and start <= ent.offset[0] < end
                    and isinstance(ent.text, str) and ent.text.strip()
                ]
                if mentions:
                    positives.append((sentence, list(dict.fromkeys(mentions))))
                if len(positives) == n_per_class:
                    break

        negatives = [(sentence, []) for sentence in (negatives or [])[:n_per_class]]

        examples = []
        for pair in zip_longest(positives, negatives):
            examples.extend(item for item in pair if item is not None)
        return examples

    def _get_extraction_annotation(self, doc):
        """Get the annotation for the extraction task."""
        if self.entity == "event triggers":
            return [ent.text for ent in doc.events]
        elif self.entity == "time expressions":
            return [ent.text for ent in doc.timexs]
        elif self.entity == "participants":
            return [ent.text for ent in doc.participants]
        else:
            raise ValueError(f"Entity {self.entity} not supported.")

    def _get_classification_annotation(self, doc):
        """Get the annotation for the classification task."""
        if self.entity == "event triggers":
            return [
                (ent.text, ent.class_) if hasattr(ent, "class_")
                else (ent.text, None)
                for ent in doc.events
            ]
        elif self.entity == "time expressions":
            return [
                (ent.text, ent.time_type) if hasattr(ent, "time_type")
                else (ent.text, None)
                for ent in doc.timexs
            ]
        elif self.entity == "participants":
            return [
                (ent.text, ent.participant_type_domain) if hasattr(ent, "participant_type_domain")
                else (ent.text, None)
                for ent in doc.participants
            ]
        else:
            raise ValueError(f"Entity {self.entity} not supported.")

    def generate(self, text: Document, candidates: list = None) -> str:
        """Generate a zero shot prompt.

        Args:
            text: The input to place in the prompt.
            candidates: The entities to classify, required when the prompter was
                built with `candidates=True` and ignored otherwise.
        """
        if self.expects_candidates:
            if not candidates:
                raise ValueError(
                    "This prompter expects the entities to classify to be "
                    "passed as `candidates`."
                )
            return self.template.substitute(
                text=text,
                candidates=json.dumps(list(candidates), ensure_ascii=False),
            )
        prompt = self.template.substitute(text=text)
        return prompt
