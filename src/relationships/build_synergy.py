import polars as pl

def build_synergy_relationships(
        annotation_evidence: pl.DataFrame,
        role_links: list[tuple[str, str, str, str]]
    ) -> pl.DataFrame:

    role_links_df = pl.DataFrame(
        role_links,
        schema=[
            "source_role",
            "target_role",
            "relationship",
            "layer"
        ],
        orient="row"
    )

    source_roles_df = annotation_evidence.select(
        pl.col("id").alias("source_id"),
        pl.col("oracle_id").alias("source_oracle_id"),
        pl.col("name").alias("source_name"),
        pl.col("roles").alias("source_role"),
    )

    target_roles_df = annotation_evidence.select(
        pl.col("id").alias("target_id"),
        pl.col("oracle_id").alias("target_oracle_id"),
        pl.col("name").alias("target_name"),
        pl.col("roles").alias("target_role"),
    )

    edges_df = source_roles_df.join(
        role_links_df,
        on="source_role",
        how="inner"
    ).join(
        target_roles_df,
        on="target_role",
        how="inner"
    ).filter(
        pl.col("source_id") != pl.col("target_id")
    ).select(
        [
            "source_id",
            "target_id",
            "source_oracle_id",
            "target_oracle_id",
            "source_name",
            "target_name",
            "source_role",
            "target_role",
            "relationship",
            "layer"
        ]
    ).unique()

    return edges_df