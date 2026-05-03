# Ablatsioonikatse: foneetilise eristuse parandamine

> **Historical plan:** this was an early v6-era ablation plan. Current model/evaluation status lives in `docs/PROJECT_TODO.md`, `wake-word/docs/MODEL_LINEAGE.md`, and `wake-word/DATA_STRATEGY.md`.

## Baseline: v6 (parim senine mudel)
- clip_duration_ms: 1500
- pointwise_filters: 48,48,48,48
- mixconv_kernel_sizes: [5],[9],[13],[21]
- residual_connection: 0,0,0,0
- spatial_attention: 0
- stride: 1
- SpecAugment: OFF
- Andmestik: v6 (2475 pos, 10228 neg)

## Mõõdetavad meetrikad (iga eksperimendi kohta)
1. Recall @0.9 (pos_mic1, pos_mic2)
2. FPR @0.9 (neg_cv, neg_korvo2)
3. **Hard neg FPR @0.9** (TTS "kuule kraam", "kuule rott" jne) ← UUS
4. Mudeli suurus (KB)
5. ESP32 tensor_arena_size vajadus

## Eksperimendid (üks muutuja korraga)

### A: Kontekstiaken
- A1: clip_duration_ms=2000 (v6 andmestik)
- A2: clip_duration_ms=2500

### B: Mudeli suurus
- B1: pointwise_filters=64,64,64,64 (suurem)
- B2: pointwise_filters=32,32,32,32 (väiksem, kontrolleks)

### C: Arhitektuur
- C1: residual_connection=1,1,1,1
- C2: spatial_attention=1
- C3: residual + spatial koos

### D: Treening
- D1: SpecAugment ON (v6 andmestik)
- D2: training_steps=20000 (rohkem treeningut)
- D3: negative_class_weight=10 (väiksem neg kaal)

### E: Andmestik (v6 baasil)
- E1: + hard neg v2 (ainult kuule_kr* 20 fraasi = 1200 klippi)
- E2: + SSML positiivsed (972 klippi)
- E3: E1 + E2 koos

## Oodatav tulemus
Tabel kus iga rida on eksperiment ja veerud on meetrikad.
Parim kombinatsioon → v8 kandidaat.
