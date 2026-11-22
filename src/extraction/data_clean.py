import polars as pl

# Data source: Scryfall bulk download: "https://data.scryfall.io/all-cards/all-cards-20261102222402.jsonl.gz"
scryfall_data_path = 'data\\scryfall\\'
# json_file = 'all-cards-20261102222402.jsonl'
parquet_file = 'all-cards-20261102.parquet'
# df = pl.read_ndjson(f"{scryfall_data_path}{json_file}", infer_schema_length=None)
# df.write_parquet(f"{scryfall_data_path}{parquet_file}")

lf = pl.scan_parquet(f"{scryfall_data_path}{parquet_file}").filter(pl.col("lang")=="en")

lf.sink_parquet(f"{scryfall_data_path}all-cards-en.parquet")
# lf.sink_csv(f"{scryfall_data_path}all-cards-en.csv")

# relevant_cols = [
#     "oracle_id",
#     "name",
#     "mana_cost",
#     "cmc",
#     "type_line",
#     "power",
#     "toughness",
#     "loyalty",
#     "defense",
#     "oracle_text",
#     "colors",
#     "color_identity",
#     "keywords",
#     "produced_mana"
# ]

# id_name_lf = lf.select(
#     [
#         "id",
#         "oracle_id",
#         "name",
#         "set",
#         "rarity",
#         "card_faces"
#     ]
# )

# test_lf = lf.filter(
#     ~pl.col('type_line').str.contains('Token'),
#     pl.col('layout')!="front_card",
# ).select(relevant_cols).unique()

# id_name_lf.sink_parquet("data\\all-cards-id-cols-20261102.parquet")
# test_lf.sink_parquet("data\\mtg-cards-20261102.parquet")
