import json
import re
import unicodedata
import polars as pl
from ollama import chat
from pydantic import ValidationError
from configs.role_definitions import CardAnnotation, ROLE_DEFINITIONS, CardReview, RoleReview
from tqdm import tqdm

role_descriptions = "\n".join(
    f"- {role}: {description}"
    for role, description in ROLE_DEFINITIONS.items()
)

def normalise_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(
        str.maketrans(
            {
                "\u2018": "'",
                "\u2019": "'",
                "\u201c": '"',
                "\u201d": '"'
            }
        )
    )
    text = text.replace('"', "").replace("'", "")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)
    return text.strip().casefold()

def consolidate_roles(annotation: dict) -> dict:
    consolidated = {}
    for assignment in annotation.get("roles", []):
        role = assignment.get("role")
        if role not in consolidated:
            consolidated[role] = []
        consolidated[role].extend(assignment.get("evidence"))

    return {
        "roles": [
            {
                "role": role,
                "evidence": list(dict.fromkeys(evidence))
            }
            for role, evidence in consolidated.items()
        ]
    }



SYSTEM_PROMPT = f"""
You are an expert Magic: The Gathering analyst.

Classify cards according to their mechanical roles.

Permitted roles and definitions:

{role_descriptions}

CLASSIFICATION OUTPUT RULES:
Only assign a role when the card's rules text explicitly supports that role.

Every role assignment must contain at least one piece of evidence quoted verbatim from the supplied card text. Do not infer a role that is not based explicitly on a verbatim extract from the card text.

Do not paraphrase or abbreviate card text when providing evidence. Use exact quotes from the text, verbatim. Do not use ellipses to abbreviate evidence.

Never assign a role based on speculation, thematic association, card type, colour, or assumed interactions.

If no roles apply, return an empty roles list.

Do not invent evidence or create role assignments with empty evidence lists.

Each role must appear at most once. If multiple pieces of evidence support the same role, group them into one assignment. Do not assign each role more than once.

ROLE GROUPING REQUIREMENTS:

Each permitted role must appear exactly zero or one times in the output.

A role represents a classification of the entire card, not an individual ability.

A card may have multiple separate abilities that support the same role.

When multiple abilities support the same role, include all relevant evidence passages in the evidence list of a SINGLE role assignment.

Never create separate role assignments for separate abilities, even when those abilities independently support the same role.

Before returning the annotation, consolidate all evidence belonging to the same role.

Before returning the annotation, verify that every assigned role is supported by its associated evidence.
"""

def classify_card(
        card_text: str,
        llmodel: str = "qwen3:14b"
    ) -> CardAnnotation:
    response = chat(
        model=llmodel,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": card_text
            }
        ],
        format=CardAnnotation.model_json_schema(),
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
        consolidated_result = consolidate_roles(result_dict)
        # TODO: Export the results that needed to be consolidated
        result = CardAnnotation.model_validate(
            consolidated_result
        )
    except ValidationError as e:
        print("Card annotation validation failed:")
        print(e)
        print(response.message.content)
        raise

    return result

REVIEW_SYSTEM_PROMPT = f"""
You are a quality-control reviewer for Magic: The Gathering card role annotations.

Your task is to evaluate whether each proposed mechanical role is genuinely supported by the supplied card text.

You will receive:
- The card's name and rules text.
- A list of proposed roles.
- The evidence supplied by the original classifier for each role.
- Definitions of the permitted mechanical roles.

For every proposed role, determine whether the supplied evidence demonstrates that the card mechanically performs the function described by the role definition.

Review requirements:

1. Only accept a role if the card's rules text establishes the relevant mechanical functionality.
2. The evidence must directly support the assigned role.
3. Do not infer roles from mana cost, power, toughness, rarity, colour, creature type, or perceived usefulness in a particular deck.
4. Do not confuse a card that could benefit from an interaction with a card that mechanically enables that interaction.
5. Do not accept a role simply because the card could be used in a particular way by its controller.
6. Be especially strict about roles involving sacrifice, graveyard interactions, discard, and other specific mechanics.
7. If a card's text does not demonstrate a role, reject that role.
8. Do not invent additional roles or modify the original annotation.
9. Evaluate every proposed role independently.
10. Provide a short explanation for each decision.

An empty list of proposed roles requires no review decisions.

Return exactly one review decision for each proposed role. Do not omit or duplicate any roles.
"""

def review_annotation(card, annotation, llmodel):
    if not annotation.roles:
        return CardReview(reviews=[])
    review_input = {
        "card_name": card.get("name"),
        "card_text": card.get("text"),
        "proposed_roles": [
            {
                "role": assignment.role.value,
                "definition": ROLE_DEFINITIONS.get(assignment.role.value),
                "evidence": assignment.evidence
            }
            for assignment in annotation.roles
        ]
    }
    response = chat(
        model=llmodel,
        messages=[
            {
                "role":"system",
                "content":REVIEW_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": json.dumps(review_input)
            }
        ],
        format=CardReview.model_json_schema(),
        think=False,
        options={
            "temperature": 0,
            "num_predict": 512,
            "repeat_penalty": 1.1,
        }
    )
    review = CardReview.model_validate_json(
        response.message.content
    )
    return review

def validate_review(annotation, review):
    expected = {
        assignment.role
        for assignment in annotation.roles
    }
    actual = [
        decision.role
        for decision in review.reviews
    ]
    if len(actual) != len(set(actual)):
        raise ValueError("Reviewer returned duplicate roles")

    if set(actual) != expected:
        raise ValueError(
            "Reviewer did not return exactly one decision for every proposed role"
        )
    return True

def validate_evidence(annotation: CardAnnotation, card_text: str):
    normalised_card_text = normalise_text(card_text)
    for assignment in annotation.roles:
        for evidence in assignment.evidence:
            normalised_evidence = normalise_text(evidence)
            if normalised_evidence not in normalised_card_text:
                raise ValueError(
                    f"\nInvalid evidence for {assignment.role.value}: {evidence}"
                )
    return True


def annotate_set(
    normalised_cards: pl.DataFrame,
    annotation_llmodel: str = "qwen3:14b",
    review_llmodel: str = "qwen3:14b"
    ) -> tuple[pl.DataFrame, pl.DataFrame]:
    annotations = []
    annotation_evidence = []
    rejected_evidence = []
    for card in tqdm(normalised_cards.to_dicts()):
        card_text = card.get("card_text")
        try:
            result = classify_card(card_text, annotation_llmodel)
            validate_evidence(result, card_text)
            review = review_annotation(card, result, review_llmodel)
            validate_review(result, review)
            accepted_roles = [
                decision.role.value
                for decision in review.reviews
                if decision.supported
            ]
            rejected_roles = [
                decision
                for decision in review.reviews
                if not decision.supported
            ]
            accepted_evidence = {
                role.role.value:role.evidence
                for role in result.roles
                if role.role.value in accepted_roles
            }
        except (ValueError, ValidationError) as e:
            print(f"\nInvalid annotation for {card.get("name")}: {e}")
            print(f"Card text:\n{card_text}")

        annotations.append(
            {
                "id": card.get("id"),
                "oracle_id": card.get("oracle_id"),
                "name": card.get("name"),
                "roles": accepted_roles
            }
        )

        for role in accepted_roles:
            annotation_evidence.append(
                {
                    "id": card.get("id"),
                    "oracle_id": card.get("oracle_id"),
                    "name": card.get("name"),
                    "roles": role,
                    "evidence": accepted_evidence.get(role)
                }
            )
        for decision in rejected_roles:
            rejected_evidence.append(
                {
                    "id": card.get("id"),
                    "oracle_id": card.get("oracle_id"),
                    "name": card.get("name"),
                    "roles": decision.role.value,
                    "evidence": decision.reason
                }
            )
    return pl.DataFrame(annotations), pl.DataFrame(annotation_evidence), pl.DataFrame(rejected_evidence)
