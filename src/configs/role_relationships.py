from collections import defaultdict

def build_role_relationships(
    role_links
    ) -> dict[str, list[dict[str, str]]]:
    relationships = defaultdict(list)

    for source, target, relationship, layer in role_links:

        relationships[source].append({
            "target": target,
            "relationship": relationship,
            "layer": layer
        })

    return dict(relationships)

ROLE_LINKS = [
    # Graveyard
    ("graveyard_filler", "graveyard_payoff", "enables", "graveyard"),
    ("graveyard_filler", "reanimation_effect", "supplies_targets", "graveyard"),
    ("graveyard_filler", "graveyard_recursion", "supplies_targets", "graveyard"),
    ("graveyard_filler", "creature_recursion", "supplies_targets", "graveyard"),
    ("graveyard_filler", "reanimation_effect", "supplies_targets", "graveyard"),

    # Sacrifice
    ("sacrifice_outlet", "sacrifice_fodder", "uses", "sacrifice"),
    ("sacrifice_outlet", "sacrifice_payoff", "triggers", "sacrifice"),
    ("sacrifice_fodder", "sacrifice_payoff", "enables", "sacrifice"),

    # Creatures
    ("creature_token_generator", "creature_payoff", "enables", "creatures"),
    ("creature_token_generator", "sacrifice_fodder", "provides", "sacrifice"),
    ("creature_token_generator", "sacrifice_outlet", "supplies", "sacrifice"),
    ("creature_token_generator", "sacrifice_payoff", "supplies", "sacrifice"),
    ("creature_recursion", "creature_payoff", "reuses", "creatures"),

    # Artifacts
    ("artifact_enabler", "artifact_payoff", "enables", "artifacts"),

    # Evasion
    # ("evasion_enabler", "evasion", "grants", "combat"),

    # Discard
    ("discard_outlet", "discard_payoff", "triggers", "discard"),
    ("discard_outlet", "reanimation_effect", "enables", "graveyard"),

    # Mana
    ("ramp", "mana_sink", "supplies_mana", "mana"),
]

ROLE_RELATIONSHIPS = build_role_relationships(ROLE_LINKS)

ROLE_FAMILIES = {
    "graveyard": [
        "graveyard_filler",
        "graveyard_payoff",
        "reanimation_effect",
        "graveyard_recursion",
        "creature_recursion",
        "self_mill"
    ],

    "sacrifice": [
        "sacrifice_outlet",
        "sacrifice_fodder",
        "sacrifice_payoff"
    ],

    "creatures": [
        "creature_payoff",
        "creature_token_generator",
        "creature_recursion"
    ],

    "artifacts": [
        "artifact_enabler",
        "artifact_payoff"
    ],

    "combat": [
        "evasion",
        "evasion_enabler"
    ],

    "discard": [
        "discard_outlet",
        "discard_payoff"
    ],

    "mana": [
        "ramp",
        "mana_fixing",
        "mana_sink"
    ],

    "card_advantage": [
        "card_draw",
        "card_selection",
        "tutor"
    ],

    "interaction": [
        "removal",
        "disruption",
        "counterspell",
        "protection"
    ]
}

def validate_role_links(role_definitions, role_links):

    defined_roles = set(role_definitions)

    linked_roles = {
        role
        for source, target, _, _ in role_links
        for role in (source, target)
    }

    unlinked_roles = defined_roles - linked_roles

    if unlinked_roles:
        print("Roles without relationships:", sorted(unlinked_roles))
