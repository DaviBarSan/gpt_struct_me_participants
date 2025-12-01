from pathlib import Path


ROOT = Path(__file__).parent.parent
RESOURCE_PATH = ROOT / "resources"
RESULTS_PATH = ROOT / "results"


SAMPLE_DOCS_IDS = {
    "portuguese": [
<<<<<<< HEAD
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
=======
        "lusa_189",
        "lusa_100",
        "lusa_197",
        "lusa_161",
        "lusa_116",
        "lusa_176",
        "lusa_195",
        "lusa_173",
        "lusa_172",
        "lusa_13",
        "lusa_142",
        "lusa_126",
        "lusa_188",
        "lusa_107",
        "lusa_203",
        "lusa_191",
        "lusa_170",
        "lusa_133",
        "lusa_179",
        "lusa_155",
>>>>>>> origin/main
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
<<<<<<< HEAD
        # "event triggers": "lusa_43",
        # "time expressions": "lusa_11",
        "participants": "lusa_2"
=======
        "event triggers": "lusa_119",
        "time expressions": "lusa_11",
        "participants": "lusa_156"
>>>>>>> origin/main
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
        ("chatgpt", "event triggers"): "ext_def_exp",
        ("chatgpt", "participants"): "ext_def_exp",
        ("chatgpt", "time expressions"): "ext",

        ("gpt3", "event triggers"): "ext_exp",
        ("gpt3", "participants"): "cls_exp",
        ("gpt3", "time expressions"): "ext_exp",

        ("gpt4", "event triggers"): "ext_def_exp",
        ("gpt4", "participants"): "ext_def_exp",
        ("gpt4", "time expressions"): "ext_exp",

        ("llama2-7b", "event triggers"): "ext_exp",
        ("llama2-7b", "participants"): "cls_def_exp",
        ("llama2-7b", "time expressions"): "cls_exp",

        ("llama2-7b-chat", "event triggers"): "cls_exp",
        ("llama2-7b-chat", "participants"): "cls_def_exp",
        ("llama2-7b-chat", "time expressions"): "cls_def_exp",

        ("llama2-13b", "event triggers"): "ext_def_exp",
        ("llama2-13b", "participants"): "ext_exp",
        ("llama2-13b", "time expressions"): "ext",

        ("llama2-13b-chat", "event triggers"): "cls_def_exp",
        ("llama2-13b-chat", "participants"): "cls_exp",
        ("llama2-13b-chat", "time expressions"): "ext",

        ("llama2-70b", "event triggers"): "ext_exp",
        ("llama2-70b", "participants"): "ext_def_exp",
        ("llama2-70b", "time expressions"): "ext_exp",

        ("llama2-70b-chat", "event triggers"): "cls_def_exp",
        ("llama2-70b-chat", "participants"): "ext_def_exp",
        ("llama2-70b-chat", "time expressions"): "ext_exp",
<<<<<<< HEAD
               
        # ("gemini", "event triggers"): "ext_exp",
        ("gemini", "participants"): "ext_exp",
        # ("gemini", "time expressions"): "ext_exp",
=======
>>>>>>> origin/main
    },

    "english": {
        ("chatgpt", "event triggers"): "cls_def_exp",
        ("chatgpt", "time expressions"): "ext_def_exp",

        ("gpt3", "event triggers"): "ext_def_exp",
        ("gpt3", "time expressions"): "ext_def_exp",

        ("gpt4", "event triggers"): "cls_def_exp",
        ("gpt4", "time expressions"): "cls_def",

        ("llama2-7b", "event triggers"): "ext_def_exp",
        ("llama2-7b", "time expressions"): "ext_def_exp",

        ("llama2-7b-chat", "event triggers"): "ext_def_exp",
        ("llama2-7b-chat", "time expressions"): "ext_def",

        ("llama2-13b", "event triggers"): "ext_def_exp",
        ("llama2-13b", "time expressions"): "ext_def",

        ("llama2-13b-chat", "event triggers"): "ext_exp",
        ("llama2-13b-chat", "time expressions"): "ext_def",

        ("llama2-70b", "event triggers"): "ext_exp",
        ("llama2-70b", "time expressions"): "ext_exp",

        ("llama2-70b-chat", "event triggers"): "ext_def_exp",
        ("llama2-70b-chat", "time expressions"): "ext",
    }
}
