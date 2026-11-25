# Data understanding — summary

## 1. Documents and participants

| language | partition | documents | participants |
| --- | --- | ---: | ---: |
| portuguese | exampler | 1 | 23 |
| portuguese | prompt_selection | 19 | 589 |
| portuguese | test | 97 | 2918 |
| english | exampler | 1 | 23 |
| english | prompt_selection | 19 | 589 |
| english | test | 96 | 2890 |
| portuguese | **all** | 117 | 3530 |
| english | **all** | 116 | 3502 |

## 2. Participant classes

Fine-grained counts:

| class | portuguese | english |
| --- | ---: | ---: |
| Per | 1087 | 1079 |
| Org | 792 | 782 |
| Obj | 412 | 411 |
| Loc | 398 | 397 |
| Other | 266 | 266 |
| Pl_civil | 263 | 258 |
| Nat | 134 | 134 |
| Fac | 87 | 86 |
| Pl_country | 28 | 27 |
| Pl_capital | 20 | 19 |
| Pl_region | 17 | 17 |
| Veh | 11 | 11 |
| Pl_water | 10 | 10 |
| (no type attribute) | 2 | 2 |
| Pl_state | 2 | 2 |
| Path | 1 | 1 |

Coarse counts (Pl_* -> Loc):

| class | portuguese | english |
| --- | ---: | ---: |
| Per | 1087 | 1079 |
| Org | 792 | 782 |
| Loc | 738 | 730 |
| Obj | 412 | 411 |
| Other | 266 | 266 |
| Nat | 134 | 134 |
| Fac | 87 | 86 |
| Veh | 11 | 11 |
| (no type attribute) | 2 | 2 |
| Path | 1 | 1 |

Share held by the three most frequent coarse classes: portuguese 74.1%, english 74.0%.

Gold labels the classification prompt never offers: Veh, Path.

## 3. Words and lexical categories

| category | portuguese tokens | portuguese % | english tokens | english % |
| --- | ---: | ---: | ---: | ---: |
| Articles & Determiners | 2147 | 23.4 | 1821 | 21.4 |
| Places & Facilities | 1423 | 15.5 | 1409 | 16.6 |
| Other Content Words | 1115 | 12.1 | 1167 | 13.7 |
| Generic Person Nouns | 905 | 9.9 | 939 | 11.1 |
| Prepositions & Connectives | 1142 | 12.4 | 666 | 7.8 |
| Organizations & Institutions | 869 | 9.5 | 839 | 9.9 |
| Numbers & Quantities | 654 | 7.1 | 712 | 8.4 |
| Objects & Substances | 501 | 5.5 | 476 | 5.6 |
| Pronouns | 220 | 2.4 | 258 | 3.0 |
| Person Names | 210 | 2.3 | 210 | 2.5 |

Vocabulary concentration:

| language | vocabulary | top1 % | top5 % | top15 % | top50 % | hapax % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| portuguese | 1674 | 8.2 | 27.6 | 38.9 | 51.9 | 50.5 |
| english | 1628 | 16.3 | 26.2 | 34.9 | 48.2 | 50.0 |

Most frequent words:

- **portuguese**: o (755, Articles & Determiners), de (734, Prepositions & Connectives), a (666, Articles & Determiners), um (214, Articles & Determiners), os (167, Articles & Determiners), homem (150, Generic Person Nouns), gnr (122, Organizations & Institutions), uma (120, Articles & Determiners), anos (107, Numbers & Quantities), da (106, Prepositions & Connectives), fonte (106, Generic Person Nouns), do (86, Prepositions & Connectives), as (84, Articles & Determiners), que (78, Pronouns), local (77, Places & Facilities)

- **english**: the (1387, Articles & Determiners), a (304, Articles & Determiners), of (257, Prepositions & Connectives), man (150, Generic Person Nouns), gnr (128, Organizations & Institutions), source (110, Generic Person Nouns), police (92, Organizations & Institutions), old (87, Numbers & Quantities), year (79, Numbers & Quantities), that (74, Pronouns), in (67, Prepositions & Connectives), de (65, Prepositions & Connectives), district (60, Places & Facilities), command (53, Organizations & Institutions), lusa (53, Organizations & Institutions)

