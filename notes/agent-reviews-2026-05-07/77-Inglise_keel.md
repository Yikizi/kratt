---
source_prompt: 08_Keeletoimetaja/Inglise_keel.txt
prompt_type: copy-editing
generated: 2026-05-07
---

# Inglise keele toimetus

## Toimetaja märkmed

- Standardiseerisin teksti Briti inglise keelele, sh muutsin `specialized` kujule `specialised`.
- Parandasin akadeemilist idiomaatilisust ja lausevoolu: näiteks `whose target is local detection` → `which aims to detect`, `support gap` → `gap in ... support`, ning `evidence discipline` → `discipline in the use of evidence`.
- Säilitasin autori mõtte, tehnilise sisu ja LaTeX-käsud/viited muutmata; muudatused on keelelised ja stiililised.

## Toimetatud tekst

```tex
This bachelor's thesis investigates how to build and evaluate an Estonian wake-word detector for a resource-constrained smart-home microcontroller. The work focuses on the \enquote{Kratt} project, which aims to detect the phrase \enquote{Kuule Kratt} locally on an ESP32-S3 class device without relying on cloud services. The practical motivation is the gap in voice-assistant support for small languages: Estonian speech-to-text already has viable local solutions, whereas local wake-word detection remains the front-end component that determines the usability of the whole voice pipeline.

The thesis reconstructs and refines a \texttt{microWakeWord}-based training and evaluation pipeline and validates it through a public control experiment on the \texttt{Speech Commands} dataset. The initial clip-level evaluation gave a misleadingly optimistic view because negative examples leaked into the evaluation setup. To mitigate this risk, independent held-out test sets were constructed, explicit train--test disjointness checks were added, and streaming evaluation with FAPH (false activations per hour) was adopted as the central false-trigger metric.

The refined evaluation shows that model quality cannot be described by recall or by clip-level false-positive rate alone: the strongest models vary across metrics. In diagnostic experiments, consensus among specialised expert models and combinations of checkpoints substantially reduced ambient-speech FAPH, but no current model or combination satisfies recall, selectivity against target-similar negatives, prefix and confusable cases, and FAPH requirements simultaneously.

The main contribution of the thesis is to show that, in small-language local wake-word development, the central challenge is not only model training but also methodologically sound evaluation and discipline in the use of evidence. The outcome is a reproducible pipeline, a documented data and evaluation protocol, and an empirical mapping of the trade-offs between recall, target-similar negative rejection, prefix and confusable false positives, and false activations for the Estonian wake phrase \enquote{Kuule Kratt}.


% No need to change this
The thesis is in \langEng~and contains \calculatepages pages of text, 
\total{totalchapters} chapters\ifthenelse{\equal{\totvalue{figure}}{0}}{}{% If no figures, do nothing
, \total{figure} \ifnum\totvalue{figure}=1 figure\else figures\fi%
}\ifthenelse{\equal{\totvalue{table}}{0}}{}{% If no tables, do nothing
, \total{table} \ifnum\totvalue{table}=1 table\else tables\fi%
}.
```
