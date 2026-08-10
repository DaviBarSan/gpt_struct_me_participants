"""Build prompts for query the models."""

import json
from string import Template

from src.base import Document
from src.meta import ENTITIES


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
        candidates: bool = False
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
        """
        self.task = task
        self.entity = entity
        self.expects_candidates = candidates and task == "classification"
        self.candidates_label = f"{self.entity.capitalize()} to classify"
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
            output_format = "JSON-parseable list of strings only with the JSON array and nothing else. Do not include any introductory text, explanation, or markdown code fences."
            self.annotation_extraction = self._get_extraction_annotation

        elif task == "classification":
            template.append(f"Task:\n")
            if self.expects_candidates:
                template.append(f"Classify each of the {self.entity} listed under \"{self.candidates_label}\", "
                                f"according to how it is used in the input.\n\n"
                                f"Classes:\n"
                                f"{ENTITIES[self.entity]['classes']}")
            else:
                template.append(f"Extract and classify all {self.entity}\n\n"
                                f"Classes:\n"
                                f"{ENTITIES[self.entity]['classes']}")
            if delimiter:
                template.append(f"----------------------------------")
            output_format = "JSON-parseable list where each element is a list with two strings, only with the JSON array and nothing else. Do not include any introductory text, explanation, or markdown code fences." \
                            "The first string is the entity and the second is the class. Place the JSON parsable list inside <Output> tags."
            if self.expects_candidates:
                output_format += " Return exactly one element for every entity listed above, " \
                                 "repeating the entity string verbatim as the first string."
            self.annotation_extraction = self._get_classification_annotation

        elif task == "detection":
            # Binary gate for the sentence-level pipeline: the extraction and
            # classification requests are only spent on a sentence the model
            # says mentions the entity. Always zero-shot - a whole-article
            # example (the only kind the corpus readers provide) would just be
            # an article the answer is trivially "yes" for.
            example = None
            template.append(f"Task:\n"
                            f"Determine whether the input mentions any {self.entity}.")
            if delimiter:
                template.append(f"----------------------------------")
            output_format = "a single word, either yes or no, and nothing else. Do not include any introductory text, explanation, or markdown code fences."
            self.annotation_extraction = self._get_extraction_annotation

        else:
            raise ValueError(f"Task {task} not supported.")

        if definition:
            if delimiter:
                template.append(f"----------------------------------")
            template.append(f"Definition:\n"
                            f"{ENTITIES[self.entity]['definition']}")

        if example is not None:
            example_text = example.text.replace("$", "$$") # Escape $ for Template
            if delimiter:
                template.append(f"----------------------------------")
            example_annt = self.annotation_extraction(example)  
            example_annt_str = json.dumps(example_annt, ensure_ascii=False).replace("$", "$$")
            template.append(f"Example:\n"
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
