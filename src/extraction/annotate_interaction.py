import json
import re
import unicodedata
import polars as pl
from ollama import chat
from pydantic import ValidationError
from configs.interaction_definitions import InteractionEffect, CardInteractionAnnotation, INTERACTION_DEFINITIONS
from tqdm import tqdm

SYSTEM_PROMPT = f"""
You are an expert Magic: The Gathering analyst.

Your task is to identify and label the mechanical effects of interactive cards.

You will be provided one or more roles that a card has been labelled with, along with the card text.

The cards have been labelled with one or more of the following four categories based on their associated definitions:

"removal": "Removes the opponent's cards, usually destroy, exile, or deal damage effects.",
"disruption": "Disrupts opponents permanents without removing them, for example tapping creatures, preventing activated abilities from being activated, reducing creature power, etc.",
"counterspell": "Counters a spell before it resolves.",
"protection": "Protects creatures or permanents from removal or combat."

You will provide a list of annotations for each card.

Where a card has multiple effects, or has modal options, return one annotation for each distinct mode, option, or effect.

You must identify every distinct effect, including conditional and modal effects.

Do not invent restrictions that are not present in the original text of the card.

Each annotation will have the following structure:

"effect_id": Integer used to number each annotation in the list.
"mechanism": The mechanism through which the interaction spell operates.
The possible mechanisms and their associated definitions are {INTERACTION_DEFINITIONS.get("mechanism")}
"target_scopes": A list of possible targets.
The list of possible target scopes are {INTERACTION_DEFINITIONS.get("target_scope")}
"outcome": What happens to the affected object.
The list of possible outcomes and their associated definitions are {INTERACTION_DEFINITIONS.get("outcome")}
"timing": The timing of the effect.
The list of possible timings and their associated definitions are {INTERACTION_DEFINITIONS.get("timing")}
"restrictions": A list of any additional restrictions. If no additional restrictions, return an empty list.
"conditions": A list of any conditions. If no additional conditions, return an empty list.
"damage_amount": If the mechanism is damage, return the amount of damage. Otherwise, return None.
"evidence": A list of evidence supporting the annotation. Each element of this list must be text quoted verbatim from the card, with no abbreviations or shorthand. At least one piece of evidence must be returned.
"""

def classify_interactive_card(
        card_text: str,
        role_assignments: list[str] = [],
        llmodel: str = "qwen3:14b"
    ) -> CardInteractionAnnotation:
    user_message = f"""
    Assigned roles: {role_assignments}
    Card Text:
    {card_text}
    """
    response = chat(
        model=llmodel,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        format=CardInteractionAnnotation.model_json_schema(),
        think=False,
        options={
            "temperature": 0,
            "num_predict": 512,
            "repeat_penalty": 1.1,
            "repeat_last_n": 128
        }
    )

    try:
        result_dict = json.loads(response.message.content)
        # consolidated_result = consolidate_roles(result_dict)
        # TODO: Export the results that needed to be consolidated
        result = CardInteractionAnnotation.model_validate(
            result_dict
        )
    except ValidationError as e:
        print("Card annotation validation failed:")
        print(e)
        print(response.message.content)
        raise

    return result

def extract_interaction_roles(
    normalised_cards: pl.DataFrame,
    annotated_cards: pl.DataFrame,
    annotation_llmodel: str = "qwen3:14b"
    ) -> pl.DataFrame:
    # Join and filter data
    interaction_cards_df = annotated_cards.filter(
        pl.col("roles").is_in(
            [
                "removal",
                "disruption",
                "counterspell",
                "protection"
            ]
        )
    ).select(
        pl.col("id"), pl.col("roles")
    ).group_by("id").agg("roles")
    candidate_df = normalised_cards.join(
        interaction_cards_df,
        on="id",
        how="inner"
    )

    annotations = []

    for card in tqdm(candidate_df.to_dicts()):
        card_text = card.get("card_text")
        role_assignments = card.get("roles")
        try:
            result = classify_interactive_card(
                card_text=card_text,
                role_assignments=role_assignments,
                llmodel=annotation_llmodel
            )
        except (ValueError, ValidationError) as e:
            print(f"\nInvalid annotation for {card.get("name")}: {e}")
            print(f"Card text:\n{card_text}")

        for interaction_annotation in result.effects:
            for target_scope in interaction_annotation.target_scopes:
                annotations.append(
                    {
                        "id": card.get("id"),
                        "oracle_id": card.get("oracle_id"),
                        "name": card.get("name"),
                        "mechanism": interaction_annotation.mechanism.value,
                        "target_scope": target_scope.value,
                        "outcome": interaction_annotation.outcome.value,
                        "timing": interaction_annotation.timing.value,
                        "restrictions": interaction_annotation.restrictions,
                        "conditions": interaction_annotation.conditions,
                        "damage_amount": interaction_annotation.damage_amount,
                        "evidence": interaction_annotation.evidence
                    }
                )

    return pl.DataFrame(annotations)

