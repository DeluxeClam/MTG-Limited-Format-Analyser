# from ollama import chat

# root_prompt: str = """
# You are a text classification assistant.
# Your task is to classify Magic: The Gathering cards.
# Identify the primary mechanical function
# described in the supplied text.

# Be concise and return only the classification.
# """

# query_prompt: str = """
# This card allows you to draw two cards
# when a creature enters the battlefield.
# """

# response = chat(
#     model="qwen3:14b",
#     messages=[
#         {
#             "role": "system",
#             "content": root_prompt
#         },
#         {
#             "role": "user",
#             "content": query_prompt
#         }
#     ]
# )

# print(response.message.content)

from configs.LLMs.qwen3_14b.qwen3_14b_annotater import classify_card

if __name__ == "__main__":
    test_card = """
    CARD: Recurring Nightmare

    Name: Recurring Nightmare
    Mana Cost: {2}{B}
    Type: Enchantment

    Oracle Text:
    {2}{B}, Sacrifice a creature, Return Recurring
    Nightmare to its owner's hand: Return target
    creature card from your graveyard to the battlefield.
    Activate only as a sorcery.
    """

    result = classify_card(test_card)

    print(result.model_dump())

