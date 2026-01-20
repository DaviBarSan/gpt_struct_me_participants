from pathlib import Path


ROOT = Path(__file__).parent.parent
RESOURCE_PATH = ROOT / "resources"
RESULTS_PATH = ROOT / "results"


SAMPLE_DOCS_IDS = {
    "portuguese": [
        "lusa_1",
        "lusa_2",
        "lusa_3",
        "lusa_4",
        "lusa_5",
        "lusa_6",
        "lusa_7",
        "lusa_8",
        "lusa_9",
        "lusa_10",
        "lusa_11",
        "lusa_12",
        "lusa_13",
        "lusa_14",
        "lusa_15",
        "lusa_16",
        "lusa_17",
        "lusa_18",
        "lusa_19",
        "lusa_20",
    ],

    "english": [
        "lusa_1",
        "lusa_2",
        "lusa_3",
        "lusa_4",
        "lusa_5",
        "lusa_6",
        "lusa_7",
        "lusa_8",
        "lusa_9",
        "lusa_10",
        "lusa_11",
        "lusa_12",
        "lusa_13",
        "lusa_14",
        "lusa_15",
        "lusa_16",
        "lusa_17",
        "lusa_18",
        "lusa_19",
        "lusa_20",
    ]
}
EXAMPLERS = {
    "portuguese": {
        "participants": "lusa_2"
    },
    "english": {
        "participants": "lusa_2"
    }
}

ENTITIES = {
    "portuguese": [
        # "event triggers",
        "participants",
        # "time expressions",
    ],
    "english": [
        "participants",
        ]
}

BEST_TEMPLATES = {
    "portuguese": {
               
        # ("gemini", "event triggers"): "ext_exp",
        ("gemini", "participants"): "ext_exp",
        ("qwen3_4b", "participants"): "cls_exp",
        ("gemma3_1b", "participants"): "ext_exp",
        ("llama32_3b", "participants"): "cls_def",
        ("qwen25_14b", "participants"): "cls_exp",
        # ("gemini", "time expressions"): "ext_exp",
    },

    "english": {
<<<<<<< HEAD

        ("qwen3_4b", "participants"): "cls_def_exp",
=======
        ("qwen3_4b", "participants"): "ext_def_exp",
        ("qwen25_14b", "participants"): "ext_def_exp",
        ("llama32_3b", "participants"): "cls_def",
        ("gemma3_1b", "participants"): "ext_def_exp",
>>>>>>> 59b73e5e9960ce07aad7b318bddbcb5e6333f6ce
    }
}
