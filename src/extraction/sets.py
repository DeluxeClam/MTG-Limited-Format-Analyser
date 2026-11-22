import polars as pl

def extract_set(
        set_code: str,
        paper_only: bool = True,
        booster_only: bool = True,
        include_promos: bool = False,
        all_columns: bool = False
    ) -> pl.DataFrame:

    cards = pl.scan_parquet(
          "data\\scryfall\\all-cards-en.parquet"
    )
    
    result = cards.filter(
        pl.col("set") == set_code.lower()
    )

    if paper_only:
        result = result.filter(
            pl.col("games").list.contains("paper")
        )

    if booster_only:
            result = result.filter(
                pl.col("booster") == True
            )

    if not include_promos:
            result = result.filter(
                pl.col("promo") == False
            )

    result = result.filter(
          ~pl.col("layout").is_in(
                [
                      "token",
                      "double_faced_token",
                      "art_series",
                      "emblem",
                      "augment",
                      "host",
                      "planar",
                      "scheme",
                      "vanguard"
                ]
          )
    )

    result = result.sort(
          ["oracle_id", "id"]
    ).unique(
          subset=["oracle_id"],
          keep="first",
          maintain_order=True
    )

    if not all_columns:
          # clean data
          result = result.select(
                [
                  "id",
                  "name",
                  "oracle_id",
                  "layout",
                  "type_line",
                  "oracle_text",
                  "mana_cost",
                  "cmc",
                  "colors",
                  "color_identity",
                  "power",
                  "toughness",
                  "loyalty",
                  "defense",
                  "keywords",
                  "produced_mana",
                  "card_faces",
                  "rarity",
                  "set"
                ]
          )


    return result.collect()
