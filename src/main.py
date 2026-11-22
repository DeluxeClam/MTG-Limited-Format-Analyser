# import packages
import argparse
import os
import polars as pl

from configs.load_configs import load_config
from configs.role_relationships import ROLE_LINKS

from extraction.sets import extract_set
from extraction.normalise_cards import noramlise_set
from extraction.annotate_cards import annotate_set
from extraction.annotate_interaction import extract_interaction_roles

from relationships.build_synergy import build_synergy_relationships
from relationships.build_interaction import build_interaction_relationships


# main
def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--config",
        required=True,
        help="Path to environment config file"
    )

    parser.add_argument(
        "--normalise-cards",
        required=False,
        action='store_true',
        help="Convert Scryfall data into normalised format"
    )

    parser.add_argument(
        "--extract-roles",
        required=False,
        action='store_true',
        help="Call an LLM to extract roles"
    )

    parser.add_argument(
        "--extract-interaction-roles",
        required=False,
        action='store_true',
        help="Call an LLM to label interaction"
    )

    parser.add_argument(
        "--create-synergy-relationships",
        required=False,
        action='store_true',
        help="Generate synergy edges between cards"
    )

    parser.add_argument(
        "--create-interaction-relationships",
        required=False,
        action='store_true',
        help="Generate interaction edges between cards"
    )

    args = parser.parse_args()
    config = load_config(args.config)

    # create env data path if not exist
    env_data_path = f"data\\environments\\{config.set_code.lower()}\\"
    os.makedirs(env_data_path, exist_ok=True)
    rel_data_path = f"data\\relationships\\{config.set_code.lower()}\\"
    os.makedirs(rel_data_path, exist_ok=True)

    cards = extract_set(config.set_code)

    if args.normalise_cards:
        normalised_cards = noramlise_set(cards)
        normalised_cards.write_parquet(
            env_data_path+"normalised_cards.parquet"
        )
    else:
        normalised_cards = pl.read_parquet(
            env_data_path+"normalised_cards.parquet"
        )

    if args.extract_roles:
        # models: qwen3:14b, qwen3:4b
        annotation_model = "qwen3:14b"
        review_model = "qwen3:14b"
        annotated_set, annotation_evidence, rejected_evidence = annotate_set(
            normalised_cards=normalised_cards,
            annotation_llmodel=annotation_model,
            review_llmodel=review_model
        )
        annotated_set.write_parquet(
            env_data_path+"annotated_cards.parquet"
        )
        annotation_evidence.write_parquet(
            env_data_path+"annotation_evidence.parquet"
        )
        rejected_evidence.write_parquet(
            env_data_path+"rejected_evidence.parquet"
        )
    else:
        annotated_set = pl.read_parquet(
            env_data_path+"annotated_cards.parquet"
        )
        annotation_evidence = pl.read_parquet(
            env_data_path+"annotation_evidence.parquet"
        )
        rejected_evidence = pl.read_parquet(
            env_data_path+"rejected_evidence.parquet"
        )

    if args.extract_interaction_roles:
        annotation_model = "qwen3:14b"
        review_model = "qwen3:14b"
        annotated_interaction_df = extract_interaction_roles(
            normalised_cards=normalised_cards,
            annotated_cards=annotation_evidence,
            annotation_llmodel=annotation_model
        )
        annotated_interaction_df.write_parquet(
            env_data_path+"interaction_roles.parquet"
        )
    else:
        annotated_interaction_df = pl.read_parquet(
            env_data_path+"interaction_roles.parquet"
        )

    if args.create_synergy_relationships:
        synergy_relationships_df = build_synergy_relationships(
            annotation_evidence=annotation_evidence,
            role_links=ROLE_LINKS
            )
        synergy_relationships_df.write_parquet(
            rel_data_path+"synergy_edges.parquet"
        )
    else:
        synergy_relationships_df = pl.read_parquet(
            rel_data_path+"synergy_edges.parquet"
        )

    if args.create_interaction_relationships:
        interaction_relationships_df = build_interaction_relationships(
            cards=cards,
            annotation_evidence=annotated_interaction_df,
            )
        interaction_relationships_df.write_parquet(
            rel_data_path+"interaction_edges.parquet"
        )
    else:
        interaction_relationships_df = pl.read_parquet(
            rel_data_path+"interaction_edges.parquet"
        )

    print("annotated_set shape: ", annotated_set.shape)
    print(annotated_set.head())
    print("annotation_evidence shape: ", annotation_evidence.shape)
    print(annotation_evidence.head())
    print("rejected_evidence shape: ", rejected_evidence.shape)
    print(rejected_evidence.head())
    print("synergy_edges shape: ", synergy_relationships_df.shape)
    print(synergy_relationships_df.head())

    pass


if __name__ == "__main__":
    main()
