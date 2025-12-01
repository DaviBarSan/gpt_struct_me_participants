from LinguAligner import AlignmentPipeline

"""
(By default, the first method used is string matching. If unsuccessful, the alignment pipeline is employed.)
Methods:
- lemma: Lemmatization
- M_Trans: Multiple Translations of a word
- word_aligner: mBERT-based word aligner
- gestalt: Gestalt pattern matching (character-based)
- levenshtein: Levenshtein distance (character-based)
"""

config= {
    "pipeline": [ "lemma", "M_Trans", "word_aligner","gestalt","leveinstein"], # can be changed according to the desired pipeline
    "spacy_model": "pt_core_news_lg", # change according to the language
    "WAligner_model": "bert-base-multilingual-uncased", # needed for word_aligner
}

aligner = AlignmentPipeline(config)

src_sentence = "The soldiers were ordered to fire their weapons."
src_annotation = "fire"
translated_sentence = "Os soldados receberam ordens para disparar as suas armas."
translated_annotation = "incêndio"

target_annotation = aligner.align_annotation(src_sentence, src_annotation, translated_sentence, translated_annotation)
print(target_annotation)

