from pathlib import Path


ROOT = Path(__file__).parent.parent
RESOURCE_PATH = ROOT / "resources"
RESULTS_PATH = ROOT / "results"


SAMPLE_DOCS_IDS = {
    "portuguese": [
        "lusa_1",
        "lusa_2",
#        "lusa_3",
#        "lusa_4",
#        "lusa_5",
#        "lusa_6",
#        "lusa_7",
#        "lusa_8",
#        "lusa_9",
#        "lusa_10",
#        "lusa_11",
#        "lusa_12",
#        "lusa_13",
#        "lusa_14",
#        "lusa_15",
#        "lusa_16",
#        "lusa_17",
#        "lusa_18",
#        "lusa_19",
#        "lusa_20",
    ],

    "english": [
        "wsj_0551",
        "wsj_0815",
        "wsj_0135",
        "wsj_1042",
        "wsj_0266",
        "wsj_0924",
        "PRI19980306.2000.1675",
        "wsj_0332",
        "wsj_0176",
        "wsj_0348",
        "wsj_0144",
        "wsj_0670",
        "ABC19980114.1830.0611",
        "wsj_0674",
        "wsj_0376",
        "VOA19980305.1800.2603",
        "APW19980301.0720",
        "wsj_0938",
        "wsj_0745",
        "wsj_0584",
    ]
}
EXAMPLERS = {
    "portuguese": {
        "participants": "lusa_2"
    },
    "english": {
        "event triggers": "APW19980213.1310",
        "time expressions": "APW19980306.1001",
    }
}

ENTITIES = {
    "portuguese": [
        # "event triggers",
        "participants",
        # "time expressions",
    ],
    "english": [
        "event triggers",
        "time expressions",
    ]
}

BEST_TEMPLATES = {
    "portuguese": {
               
        # ("gemini", "event triggers"): "ext_exp",
        ("gemini", "participants"): "ext_exp",
        ("qwen3_4b", "participants"): "cls_exp",
        # ("gemini", "time expressions"): "ext_exp",
    },

    "english": {

        ("llama2-70b-chat", "event triggers"): "ext_def_exp",
        ("llama2-70b-chat", "time expressions"): "ext",
    }
}
