ROLE_RELATIONSHIPS = {
    "sacrifice_outlet": [
        "sacrifice_fodder"
    ],
    "sacrifice_fodder": [
        "sacrifice_outlet",
        "sacrifice_payoff"
    ],
    "reanimation_effect": [
        "graveyard_filler",
        "graveyard_payoff"
    ],
    "graveyard_filler": [
        "reanimation_effect",
        "graveyard_recursion"
    ],
    "creature_token_generator": [
        "sacrifice_outlet",
        "creature_payoff"
    ]
}

ROLE_RELATIONSHIPS = {
    "graveyard_filler": [
        "graveyard_payoff",
        "reanimation_effect",
        "graveyard_recursion"
    ],
    "graveyard_payoff": [],
    "reanimation_effect": [],
    "graveyard_recursion": [],
    
    "sacrifice_outlet": [],
    "sacrifice_fodder": [],
    "sacrifice_payoff": [],
    
    "creature_payoff": [],
    "creature_token_generator": [],
    "creature_recursion": [],
    "evasion": [],
    "evasion_enabler": [],
    # "aggressive_creature": "Is a creature that is cheap, has good stats and/or abilities that reward attacking.",
    
    "artifact_enabler": [],
    "artifact_payoff": [],
    
    "card_draw": [],
    "card_selection": [],
    
    "ramp": [],
    "mana_fixing": [],
    "mana_sink": [],
    
    "removal": [],
    "disruption": [],
    "counterspell": [],
    "protection": [],
    
    "self_mill": [],
    "discard_outlet": [],
    "discard_payoff": [],
    "tutor": [],
}