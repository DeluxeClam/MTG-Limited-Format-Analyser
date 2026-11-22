import re
import polars as pl

def can_answer(effect, target) -> bool:
    if effect["mechanism"] == "destroy":
        if "indestructible" in target["keywords"]:
            return False

    if "target" in effect["evidence"]:
        if "hexproof" in target["keywords"] | "shroud" in target["keywords"]:
            return False

    

    if effect["mechanism"] == "damage":
        if "creature" in target["type_line"] & "creature" == effect["target_scope"]:
            return effect["damage_amount"] >= target["toughness"]

    return True



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