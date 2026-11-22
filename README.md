# MTG Limited Format Analyser

## What is it

I want to build a system to analyse MTG limited formats. The purpose of this is to:
- Predict card win rates.
- Identify and distinguish between well-supported and under-supported archetypes.
- Identify power outliers, format speed, how good it is.

I want to extend this to predict features about cube environments

Eventually I want to build a GraphRAG system to analyse limited formats.

## The Plan

1. Extract card data from [Scryfall](https://scryfall.com/docs/api/bulk-data).
2. Build a card interaction network for each set.
