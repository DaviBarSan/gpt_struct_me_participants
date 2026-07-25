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
               
        ("gemini", "participants"): "cls_def_exp",
        ("qwen3_4b", "participants"): "cls_def_exp",
        ("gemma3_1b", "participants"): "ext_def_exp",
        ("qwen25_14b", "participants"): "cls_exp",
    },

    "english": {
        ("qwen3_4b", "participants"): "cls_def_exp",
        ("qwen25_14b", "participants"): "cls_exp",
        ("gemma3_1b", "participants"): "ext_def_exp",
        ("gemini", "participants"): "cls_def_exp",
        
    }
}

# 1. Definição original dos conjuntos
WORD_CATEGORIES_EN = word_to_category = {
    'a': 'Articles',
    'an': 'Articles',
    'the': 'Articles',
    
    'at': 'Prepositions & Connectives',
    'by': 'Prepositions & Connectives',
    'for': 'Prepositions & Connectives',
    'from': 'Prepositions & Connectives',
    'in': 'Prepositions & Connectives',
    'of': 'Prepositions & Connectives',
    'on': 'Prepositions & Connectives',
    'to': 'Prepositions & Connectives',
    'with': 'Prepositions & Connectives',
    'without': 'Prepositions & Connectives',
    
    'area': 'Spatial & Jurisdictional Terms',
    'city': 'Spatial & Jurisdictional Terms',
    'country': 'Spatial & Jurisdictional Terms',
    'county': 'Spatial & Jurisdictional Terms',
    'district': 'Spatial & Jurisdictional Terms',
    'region': 'Spatial & Jurisdictional Terms',
    'state': 'Spatial & Jurisdictional Terms',
    'street': 'Spatial & Jurisdictional Terms',
    'zone': 'Spatial & Jurisdictional Terms',
    
    'boy': 'Generic Actors',
    'child': 'Generic Actors',
    'girl': 'Generic Actors',
    'man': 'Generic Actors',
    'officer': 'Generic Actors',
    'people': 'Generic Actors',
    'person': 'Generic Actors',
    'police': 'Generic Actors',
    'source': 'Generic Actors',
    'suspect': 'Generic Actors',
    'victim': 'Generic Actors',
    'woman': 'Generic Actors',
    
    'age': 'Numerals & Quantifiers',
    'both': 'Numerals & Quantifiers',
    'four': 'Numerals & Quantifiers',
    'many': 'Numerals & Quantifiers',
    'one': 'Numerals & Quantifiers',
    'some': 'Numerals & Quantifiers',
    'three': 'Numerals & Quantifiers',
    'two': 'Numerals & Quantifiers',
    'years': 'Numerals & Quantifiers',
    
    'he': 'Pronouns',
    'her': 'Pronouns',
    'his': 'Pronouns',
    'its': 'Pronouns',
    'she': 'Pronouns',
    'that': 'Pronouns',
    'their': 'Pronouns',
    'these': 'Pronouns',
    'they': 'Pronouns',
    'this': 'Pronouns',
    'those': 'Pronouns'
}

WORD_CATEGORIES_PT = ord_to_category_pt = {
    # Artigos
    'a': 'Artigos', 
    'as': 'Artigos', 
    'o': 'Artigos', 
    'os': 'Artigos', 
    'um': 'Artigos', 
    'uma': 'Artigos', 
    'uns': 'Artigos', 
    'umas': 'Artigos',

    # Preposições e Contrações
    'ao': 'Preposições e Contrações', 
    'aos': 'Preposições e Contrações', 
    'com': 'Preposições e Contrações', 
    'da': 'Preposições e Contrações', 
    'das': 'Preposições e Contrações', 
    'de': 'Preposições e Contrações', 
    'do': 'Preposições e Contrações', 
    'dos': 'Preposições e Contrações', 
    'em': 'Preposições e Contrações', 
    'na': 'Preposições e Contrações', 
    'nas': 'Preposições e Contrações', 
    'no': 'Preposições e Contrações', 
    'nos': 'Preposições e Contrações', 
    'pela': 'Preposições e Contrações', 
    'pelas': 'Preposições e Contrações', 
    'pelo': 'Preposições e Contrações', 
    'pelos': 'Preposições e Contrações', 
    'por': 'Preposições e Contrações', 
    'sem': 'Preposições e Contrações', 
    'à': 'Preposições e Contrações', 
    'às': 'Preposições e Contrações',

    # Termos Espaciais e Jurisdicionais
    'avenida': 'Termos Espaciais e Jurisdicionais', 
    'cidade': 'Termos Espaciais e Jurisdicionais', 
    'concelho': 'Termos Espaciais e Jurisdicionais', 
    'distrito': 'Termos Espaciais e Jurisdicionais', 
    'estado': 'Termos Espaciais e Jurisdicionais', 
    'local': 'Termos Espaciais e Jurisdicionais', 
    'país': 'Termos Espaciais e Jurisdicionais', 
    'região': 'Termos Espaciais e Jurisdicionais', 
    'rua': 'Termos Espaciais e Jurisdicionais', 
    'zona': 'Termos Espaciais e Jurisdicionais',

    # Substantivos Genéricos (Atores)
    'agentes': 'Substantivos Genéricos (Atores)', 
    'autoridade': 'Substantivos Genéricos (Atores)', 
    'criança': 'Substantivos Genéricos (Atores)', 
    'fonte': 'Substantivos Genéricos (Atores)', 
    'homem': 'Substantivos Genéricos (Atores)', 
    'indivíduo': 'Substantivos Genéricos (Atores)', 
    'jovem': 'Substantivos Genéricos (Atores)', 
    'mulher': 'Substantivos Genéricos (Atores)', 
    'pessoas': 'Substantivos Genéricos (Atores)', 
    'vítima': 'Substantivos Genéricos (Atores)',

    # Numerais e Quantificadores
    'ambos': 'Numerais e Quantificadores', 
    'anos': 'Numerais e Quantificadores', 
    'cerca': 'Numerais e Quantificadores', 
    'dois': 'Numerais e Quantificadores', 
    'duas': 'Numerais e Quantificadores', 
    'idade': 'Numerais e Quantificadores', 
    'mil': 'Numerais e Quantificadores', 
    'quatro': 'Numerais e Quantificadores', 
    'três': 'Numerais e Quantificadores',

    # Pronomes Demonstrativos/Possessivos
    'aquela': 'Pronomes Demonstrativos/Possessivos', 
    'aquelas': 'Pronomes Demonstrativos/Possessivos', 
    'aquele': 'Pronomes Demonstrativos/Possessivos', 
    'aqueles': 'Pronomes Demonstrativos/Possessivos', 
    'esta': 'Pronomes Demonstrativos/Possessivos', 
    'estas': 'Pronomes Demonstrativos/Possessivos', 
    'este': 'Pronomes Demonstrativos/Possessivos', 
    'estes': 'Pronomes Demonstrativos/Possessivos', 
    'seu': 'Pronomes Demonstrativos/Possessivos', 
    'sua': 'Pronomes Demonstrativos/Possessivos'
}   

def word_to_category(token, dict_words):
    if not isinstance(token, str):
        return 'Others (Core/Specifics)'
    
    token = token.lower().strip()
    
    # Utiliza o método .get() para retornar o valor, ou 'Others' caso a chave não exista
    return dict_words.get(token, 'Nao definido')