# Model Error Correlation Analysis

**Date:** 2026-04-21
**Method:** Jaccard similarity of per-clip error sets at threshold 0.996
**Purpose:** Select consensus combo partners with decorrelated errors

## Key Finding

Models trained with similar objectives make **correlated mistakes**.
Two models that both fail on the same clips give zero consensus benefit.
The best combo pairs models that fail in **different places**.

## Error Correlation Matrix (Jaccard similarity of error sets)

Lower = more decorrelated = better combo partner.

|              | expert-a | expert-b2 |   v8 |  v10 | ex3a |  v14 | v6-res |  v15 |
|--------------|----------|-----------|------|------|------|------|--------|------|
| **expert-a** |     1.00 |      0.11 | 0.14 | 0.17 | 0.52 | 0.44 |   0.47 | 0.38 |
| **expert-b2**|     0.11 |      1.00 | 0.26 | 0.37 | 0.08 | 0.20 |   0.15 | 0.28 |
| **v8**       |     0.14 |      0.26 | 1.00 | 0.26 | 0.16 | 0.18 |   0.14 | 0.25 |
| **v10**      |     0.17 |      0.37 | 0.26 | 1.00 | 0.12 | 0.25 |   0.19 | 0.29 |
| **ex3a**     |     0.52 |      0.08 | 0.16 | 0.12 | 1.00 | 0.38 |   0.39 | 0.33 |
| **v14**      |     0.44 |      0.20 | 0.18 | 0.25 | 0.38 | 1.00 |   0.55 | 0.43 |
| **v6-res**   |     0.47 |      0.15 | 0.14 | 0.19 | 0.39 | 0.55 |   1.00 | 0.44 |
| **v15**      |     0.38 |      0.28 | 0.25 | 0.29 | 0.33 | 0.43 |   0.44 | 1.00 |

## Error Profiles

Models cluster into two error types:

| Model     | Pos miss | HN false+ | Total | Profile |
|-----------|----------|-----------|-------|---------|
| expert-a  |       30 |        57 |    87 | Recall-good, HN-weak |
| expert-b2 |      124 |        10 |   134 | Recall-weak, HN-good |
| v8        |      102 |        14 |   116 | Recall-weak, HN-good |
| v10       |       83 |        14 |    97 | Recall-moderate, HN-good |
| ex3a      |       33 |        61 |    94 | Recall-good, HN-weak |
| v14       |       74 |        60 |   134 | Middle-ground |
| v6-res    |       78 |        59 |   137 | Middle-ground |
| v15       |      106 |        57 |   163 | Recall-weak, HN-weak |

## Why expert-a + v14 was a bad combo choice

Jaccard = 0.44 — high correlation. Both models:
- Trained without hard negatives (hn=0)
- Both residual ON
- Similar positive data (mic + TTS)
- Both fail on the same hard negative clips

## Best pairs by decorrelation

| Pair                  | Jaccard | Shared errors | Why decorrelated |
|-----------------------|---------|---------------|------------------|
| expert-b2 + ex3a      |   0.081 |            17 | Opposite profiles (recall vs precision) |
| expert-a + expert-b2  |   0.111 |            22 | Opposite profiles |
| v10 + ex3a            |   0.124 |            21 | v10 has HN training data, ex3a doesn't |
| expert-a + v8         |   0.140 |            25 | v8 trained WITH hard neg feature set |
| v8 + v6-residual      |   0.145 |            32 | Different data, v8 has hard negs |

## Design Principle

Decorrelation comes from **different training objectives**, not just different data:
- Model A (proposer): no hard negatives, high recall, tolerates false positives
- Model B (verifier): hard negatives + "kuule-only" negatives, strict rejection

If both models lack hard negatives, their errors on confusable phrases are correlated.

## Implication for Ensemble Design

1. Current expert-a + v14 combo works "by accident" (two decent models > one)
2. True consensus benefit requires complementary error profiles
3. Best existing pair: **expert-a + v8** (Jaccard 0.14, v8 has hard neg training)
4. Optimal pair (not yet trained): recall-proposer + kuule-only-negative verifier
