# import packages
import argparse
import os
import polars as pl
from extraction.sets import extract_set
from extraction.normalise_cards import noramlise_set
from configs.load_configs import load_config
from extraction.annotate_cards import annotate_set


# main
def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--config",
        required=True,
        help="Path to environment config file"
    )

    parser.add_argument(
        "--extract-roles",
        required=False,
        action='store_true',
        help="Call an LLM to extract roles"
    )

    args = parser.parse_args()
    config = load_config(args.config)

    # create env data path if not exist
    env_data_path = f"data\\environments\\{config.set_code.lower()}\\"
    os.makedirs(env_data_path, exist_ok=True)

    cards = extract_set(config.set_code)
    normalised_cards = noramlise_set(cards)
    normalised_cards.write_parquet(
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

    print(annotated_set.shape)
    print(annotated_set.head())
    print(annotation_evidence.shape)
    print(annotation_evidence.head())
    print(rejected_evidence.shape)
    print(rejected_evidence.head())


if __name__ == "__main__":
    main()
