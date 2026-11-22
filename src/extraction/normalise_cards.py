import polars as pl

def normalise_card(card: dict):
      def clean(value):
            if value is None:
                  return ""
            return str(value)

      def format_face(face):
            fields = [
                  ("Name", face.get("name")),
                  ("Mana Cost", face.get("mana_cost")),
                  ("Type", face.get("type_line")),
                  ("Oracle Text", face.get("oracle_text")),
                  ("Power", face.get("power")),
                  ("Toughness", face.get("toughness")),
                  ("Loyalty", face.get("loyalty")),
                  ("Keywords", ", ".join(face.get("keywords") or []))
            ]
            return "\n".join(
                  f"{name}: {clean(value)}"
                  for name, value in fields
                  if value not in (None, "")
            )

      faces = card.get("card_faces")

      if isinstance(faces, (list, tuple)) and faces:
            card_text = "\n\n".join(
                  f"FACE {i + 1}:\n{format_face(face)}"
                  for i, face in enumerate(faces)
            )
      else:
            card_text = format_face(card)

      return {
            "id": card.get("id"),
            "oracle_id": card.get("oracle_id"),
            "name": card.get("name"),
            "colors": card.get("colors"),
            "cmc": card.get("cmc"),
            "layout": card.get("layout"),
            "card_text": card_text
      }

def noramlise_set(
        set: pl.DataFrame
    ) -> pl.DataFrame:
    cards = [
          normalise_card(card)
          for card in set.to_dicts()
    ]
    return pl.DataFrame(cards)
    