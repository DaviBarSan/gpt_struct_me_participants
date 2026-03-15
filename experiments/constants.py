from pathlib import Path


ROOT = Path(__file__).parent.parent
RESOURCE_PATH = ROOT / "resources"
RESULTS_PATH = ROOT / "results"


SAMPLE_DOCS_IDS = {
    "portuguese": [
        'lusa_97',
        'lusa_4',
        'lusa_67',
        'lusa_20',
        'lusa_83',
        'lusa_104',
        'lusa_80',
        'lusa_79',
        'lusa_34',
        'lusa_47',
        'lusa_30',
        'lusa_96',
        'lusa_11',
        'lusa_112',
        'lusa_100',
        'lusa_77',
        'lusa_38',
        'lusa_86',
        'lusa_60'
    ],

    "english": [
        'lusa_97',
        'lusa_4',
        'lusa_67',
        'lusa_20',
        'lusa_83',
        'lusa_104',
        'lusa_80',
        'lusa_79',
        'lusa_34',
        'lusa_47',
        'lusa_30',
        'lusa_96',
        'lusa_11',
        'lusa_112',
        'lusa_100',
        'lusa_77',
        'lusa_38',
        'lusa_86',
        'lusa_60'
    ]
}
EXAMPLERS = {
    "portuguese": {
        "participants": "lusa_117"
    },
    "english": {
        "participants": "lusa_117"
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
        ("qwen3_4b", "participants"): "ext_def_exp",
        ("qwen25_14b", "participants"): "ext_def_exp",
        ("llama32_3b", "participants"): "cls_def",
        ("gemma3_1b", "participants"): "ext_def_exp",
        ("gemini", "participants"): "cls_def_exp",
        
    }
}
