"""All the constants that are defined a priori."""

ENTITIES = {
    "event triggers": {

        "definition": "An event refers to any occurrence, incident, action or state that takes place or holds within a specified period of time. This includes both concrete actions, such as physical movements and behaviors, as well as more abstract events, such as changes in emotional states or the passage of time or stative situations that hold during a time interval. Events have temporal relevance and can be directly related to temporal expressions. Events can be related to changes in the text and are often used to advance the plot and develop characters, but also to describe characters, objects, circumstances, places or states.",

        "classes": "State, Occurrence, Reporting, Perception, Aspectual, Intensional Action, and Intensional State"
    },

    "participants": {

        "definition": "Participants refer to individuals, groups, organizations, or other entities that are actively involved in or impacted by an event or state. They are typically identified based on their relevance and significance to the situation, and may be explicitly mentioned or inferred from the context. Participants can take on a variety of roles, such as actors, agents, patients, victims, or observers, and their actions and interactions can shape the course of events.",

        "classes": "Person, Organization, Object, Location, Place (Pl_<type>), Nature, Facility, and Other",

        # The annotation scheme's full label set with the guideline definitions,
        # used by the sentence-level pipeline in place of the generic names above.
        # Two deliberate choices:
        #
        # 1. Labels are spelled exactly as the corpus annotations spell them
        #    ("Per", "Nat", "Pl_capital"), not in the guideline's upper case.
        #    `src.evaluate.normalize_type` only case-folds six full labels and
        #    compares anything else verbatim, so a model answering "NAT" would
        #    miss the gold "Nat" on casing alone.
        # 2. Pl_celestial, Pl_mountain and Pl_mount_range are kept even though no
        #    Lusa document uses them: they are part of the scheme, and omitting
        #    them would describe a different guideline than the annotators used.
        "class_definitions":
            "In the examples below the entity is marked with #...#.\n"
            "Per - entities that are human individuals or fictitious human characters and divine entities. Ex. #O rapaz# leu o livro.\n"
            "Org - entities with an organizational structure (e.g. companies, governments, teams, institutions). Ex. #A EDP# subiu os precos.\n"
            "Obj - entities that represent any kind of tangible, manmade objects. Ex. O Joao partiu #a cadeira#.\n"
            "Nat - entities that are not manmade and occur naturally (e.g. animals, plants). Ex. #O cao# mordeu o dono.\n"
            "Fac - facilities.\n"
            "Veh - vehicles.\n"
            "Path - a location that consists of a series of locations; it has the potential for traversal; it can function as a boundary; it has no inherent directionality. Ex. autoestrada A1, nacional 222, rua, rio.\n"
            "Pl_water - Ex. rio, ribeira, mar, oceano, lago, canal.\n"
            "Pl_celestial - Ex. sol, lua, Marte, Andromeda.\n"
            "Pl_mountain - a mountain.\n"
            "Pl_civil - a political region or administrative area, usually sub-national. Ex. Regiao Autonoma dos Acores, Uniao Europeia, Lisboa, area metropolitana do Porto, Minho.\n"
            "Pl_country - a country.\n"
            "Pl_mount_range - a mountain range.\n"
            "Pl_capital - the capital of a country.\n"
            "Pl_region - a non-political or non-administrative region. Ex. deserto, ilha.\n"
            "Pl_state - a first-order administrative division within a country (with ISO 3166-2 codes).\n"
            "Loc - places that do not fit any of the other Pl_ values (e.g. web pages).\n"
            "Other - entities that do not fit into the other categories. Ex. O Joao sentiu #um cheiro a queimado#."
    },

    "time expressions": {

        "definition": "Temporal expressions are linguistic elements that allow us to communicate information about time. In addition to representing specific points in time, they can also be used to classify time periods according to units such as seconds, minutes, hours, days, weeks, months, and years.",

        "classes": "Date, Time, Duration, and Set"
    }
}
