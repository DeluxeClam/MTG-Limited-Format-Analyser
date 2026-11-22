from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator

class InteractionMechanism(str, Enum):
    DESTROY = "destroy"
    EXILE = "exile"
    DAMAGE = "damage"
    BOUNCE = "bounce"
    TAP_OR_DISABLE = "tap_or_disable"
    COUNTER = "counter"
    DISCARD = "discard"
    STEAL_OR_CONTROL = "steal_or_control"
    SACRIFICE = "sacrifice"
    PROTECTION = "protection"

class InteractionTargetScope(str, Enum):
    CREATURE = "creature"
    ARTIFACT = "artifact"
    ENCHANTMENT = "enchantment"
    PLANESWALKER = "planeswalker"
    PERMANENT = "permanent"
    SPELL = "spell"
    PLAYER = "player"
    ANY_TARGET = "any_target"
    MULTIPLE_OBJECTS = "multiple_objects"
    NONLAND_PERMANENT = "nonland_permanent"

class InteractionOutcome(str, Enum):
    DESTROY = "destroy"
    EXILE = "exile"
    DAMAGE = "damage"
    BOUNCE = "bounce"
    DISABLE = "disable"
    COUNTER = "counter"
    CONTROL_CHANGE = "control_change"
    SACRIFICE = "sacrifice"

class InteractionTiming(str, Enum):
    INSTANT = "instant"
    SORCERY = "sorcery"

INTERACTION_PATTERNS = [
    {
        "pattern": r"destroy target creature",
        "mechanism": "destroy",
        "target_scopes": ["creature"],
    },
    {
        "pattern": r"exile target creature",
        "mechanism": "exile",
        "target_scopes": ["creature"],
    },
    {
        "pattern": r"counter target spell",
        "mechanism": "counter",
        "target_scopes": ["spell"],
    },
    {
        "pattern": r"return target creature to its owner's hand",
        "mechanism": "bounce",
        "target_scopes": ["creature"],
    },
]

INTERACTION_MECHANISM_DEFINITIONS = {
    "destroy": "Sends the target to the graveyard from the battlefield. Will explicitly say 'destroy'.",
    "exile": "Sends the target to the exile zone. Will explicitly say 'exile' or 'if ... would die, exile it instead'.",
    "damage": "Deals damage to the target.",
    "bounce": "Returns the target to the opponent's hand or library.",
    "tap_or_disable": "Taps the target or otherwise disables it. Will leave the target on the battlefield.",
    "counter": "Counters the spell after it is cast, while it is on the stack, before it enters the battlefield.",
    "discard": "Forces the owner to discard the card from their hand.",
    "steal_or_control": "Temporarily or permanently changes the controller of the target.",
    "sacrifice": "Causes the controller to sacrifice one or more permanents.",
    "protection": "Prevents other interactive effects from being effective. For example, granting a toughness boost protects against damage, granting indestructible protects against destroy effects, etc."
}

INTERACTION_OUTCOME_DEFINITIONS = {
    "destroy": "The target is sent to the graveyard from the battlefield.",
    "exile": "The target is sent to exile.",
    "damage": "The target is dealt damage.",
    "bounce": "The target is returned to the owner's hand or library.",
    "disable": "The target remains on the battlefield, but is reduced in effectiveness (e.g. can't attack or block, is tapped, etc.).",
    "counter": "The target is countered before it resolves.",
    "control_change": "The target's controller changes.",
    "sacrifice": "One or more permanents are sacrificed.",
}

INTERACTION_TARGET_SCOPE_DEFINITIONS = [
    "creature",
    "artifact",
    "enchantment",
    "planeswalker",
    "permanent",
    "spell",
    "player",
    "any_target",
    "multiple_objects"
    "nonland_permanent"
]

INTERACTION_TIMING_DEFINITIONS = {
    "instant": "Effect operates at instant speed. Not limited to Instant card types. Examples include permanents with flash, activated abilities without timing restrictions, etc.",
    "sorcery": "Effect only operates at sorcery speed. Examples include sorcery spells, ETB abilities of creatures or permanents without flash, etc."
}

INTERACTION_DEFINITIONS = {
    "mechanism": INTERACTION_MECHANISM_DEFINITIONS,
    "outcome": INTERACTION_OUTCOME_DEFINITIONS,
    "target_scope": INTERACTION_TARGET_SCOPE_DEFINITIONS,
    "timing": INTERACTION_TIMING_DEFINITIONS
}


class InteractionEffect(BaseModel):
    model_config = ConfigDict(extra="forbid")

    effect_id: int

    mechanism: InteractionMechanism
    target_scopes: list[InteractionTargetScope]

    outcome: InteractionOutcome

    timing: InteractionTiming

    restrictions: list[str] = Field(default_factory=list)
    conditions: list[str] = Field(default_factory=list)

    damage_amount: Optional[int] = None

    evidence: list[str] = Field(min_length=1)


class CardInteractionAnnotation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    effects: list[InteractionEffect]