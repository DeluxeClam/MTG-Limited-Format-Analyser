from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, field_validator

class CardRole(str, Enum):
    SACRIFICE_OUTLET = "sacrifice_outlet"
    SACRIFICE_FODDER = "sacrifice_fodder"
    SACRIFICE_PAYOFF = "sacrifice_payoff"

    REANIMATION_EFFECT = "reanimation_effect"
    GRAVEYARD_RECURSION = "graveyard_recursion"
    GRAVEYARD_FILLER = "graveyard_filler"
    GRAVEYARD_PAYOFF = "graveyard_payoff"

    CREATURE_TOKEN_GENERATOR = "creature_token_generator"
    CREATURE_PAYOFF = "creature_payoff"
    CREATURE_RECURSION = "creature_recursion"
    EVASION = "evasion"
    EVASION_ENABLER = "evasion_enabler"
    # AGGRESSIVE_CREATURE = "aggressive_creature"

    ARTIFACT_ENABLER = "artifact_enabler"
    ARTIFACT_PAYOFF = "artifact_payoff"

    CARD_DRAW = "card_draw"
    CARD_SELECTION = "card_selection"

    RAMP = "ramp"
    MANA_FIXING = "mana_fixing"
    MANA_SINK = "mana_sink"

    REMOVAL = "removal"
    DISRUPTION = "disruption"
    COUNTERSPELL = "counterspell"
    PROTECTION = "protection"

    SELF_MILL = "self_mill"
    DISCARD_OUTLET = "discard_outlet"
    DISCARD_PAYOFF = "discard_payoff"
    TUTOR = "tutor"

class RoleAssignment(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: CardRole
    evidence: list[str] = Field(
        min_length=1,
        description="Specific rules text supporting this role. Include at least one relevant supporting passage quoted from the card text."
    )

class CardAnnotation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    roles: list[RoleAssignment] = Field(
        description="Unique mechanical roles applicable to this card, with supporting evidence for each role."
    )

    @field_validator("roles")
    @classmethod
    def unique_roles(cls, roles):
        role_values = [assignment.role for assignment in roles]
        if len(role_values) != len(set(role_values)):
            raise ValueError("Duplicate roles are not permitted.")
        return roles

class RoleReview(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: CardRole
    supported: bool = Field(
        description="Whether the supplied card text and evidence demonstrate the assigned mechanical role."
    )
    reason: str = Field(
        description="A brief explanation of why the evidence does or does not support the assigned role."
    )

class CardReview(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reviews: list[RoleReview]

ROLE_DEFINITIONS = {
    "graveyard_filler": "Moves cards from a library or hand into a graveyard.",
    "graveyard_payoff": "Provides a benefit when one or more cards enter or leave the graveyard, or a benefit based on the size or contents of graveyards.",
    "reanimation_effect": "Returns a creature from a graveyard directly to the battlefield.",
    "graveyard_recursion": "Returns cards from a graveyard to a hand, library or another usable zone.",
    
    "sacrifice_outlet": "Allows its controller to sacrifice one or more permanents, either voluntarily or as part of an activated or triggered ability.",
    "sacrifice_fodder": "Provides expendable permanents through an explicit mechanical effect, such as creating creature tokens, generating replacement permanents when creatures die, or recurring permanents that can be sacrificed repeatedly. The card's own rules text must establish this functionality. Do not assign this role merely because a creature is inexpensive, has low toughness, has low power, or would be a convenient sacrifice target. Ordinary creatures, including vanilla creatures with no abilities, are not sacrifice fodder.",
    "sacrifice_payoff": "Provides a benefit when one or more permanents are sacrificed.",
    
    "creature_payoff": "Provides a benefit which rewards its controllor for having creatures. It might provide an increase to power and toughness of other creatures, provide a benefit when other creatures enter, leverage creatures into card advantage, reward having a big creature, etc.",
    "creature_token_generator": "Creates one or more creature tokens.",
    "creature_recursion": "Allows its controller to recur creatures, usually from the graveyard.",
    "evasion": "Is a creature with some sort of intrinsic ability making it difficult to block, such as flying or menace.",
    "evasion_enabler": "Provides evasion to other creatures.",
    # "aggressive_creature": "Is a creature that is cheap, has good stats and/or abilities that reward attacking.",
    
    "artifact_enabler": "Is an artifact or allows its controller access to additional artifacts, sometimes through token creation, card selection, mana generation/reduction, etc.",
    "artifact_payoff": "Provides abilities or benefits that work with artifacts or are more powerful with artifacts.",
    
    "card_draw": "Allows its controller to draw cards.",
    "card_selection": "Allows its controller to look at and select from more cards than the card advantage generated.",
    
    "ramp": "Provides additional mana, and/or additional land access.",
    "mana_fixing": "Provides access to additional colors of mana.",
    "mana_sink": "Provides an ability which is expensive, usually repeatable.",
    
    "removal": "Removes the opponent's cards, usually destroy, exile, or deal damage effects.",
    "disruption": "Disrupts opponents permanents without removing them, for example tapping creatures, preventing activated abilities from being activated, reducing creature power, etc.",
    "counterspell": "Counters a spell before it resolves.",
    "protection": "Protects creatures or permanents from removal or combat.",
    
    "discard_outlet": "Enables its controller to discard one or more cards.",
    "discard_payoff": "Provides its controller a benefit when they or their opponent discards cards.",
    "tutor": "Allows its controller to search their library for a card and put it into hand, graveyard, or onto the battlefield.",
}
