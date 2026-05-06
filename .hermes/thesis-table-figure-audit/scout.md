# Thesis table/figure audit (LaTeX `main.log` correlation)

Scope: `docs/thesis/thesis-tex-estonian`. Source audit found 14 `table`, 2 `figure`, and 1 `longtable` environments. `main.log` has float/table overfull hits only in `chapters/second_chapter.tex`; no underfull warning falls inside a table/figure/longtable.

| file:line | label | issue | suggested fix type |
|---|---|---|---|
| `chapters/second_chapter.tex:54-69` | `tab:model-versions` | OK; no `main.log` warning. | None. |
| `chapters/second_chapter.tex:87-101` | `tab:fair-comparison` | OK; no `main.log` warning. | None. |
| `chapters/second_chapter.tex:107-112` | `fig:faph-recall-pareto` | caption too long; no over/underfull, but caption is ~600 chars and will bloat LoF. | Add short optional caption; move metric/filter details to prose or figure note. |
| `chapters/second_chapter.tex:124-138` | `tab:full-comparison` | OK; no `main.log` warning. | None. |
| `chapters/second_chapter.tex:173-192` | `tab:fair-comparison-holdout` | too dense; no warning because `\scriptsize` + `\resizebox{\textwidth}`, but 9 data columns with CIs. | Split recall/FPR/FAPH into separate tables or appendix full table; keep short summary in text. |
| `chapters/second_chapter.tex:245-257` | `tab:cross-language-faph` | likely too wide; `main.log:2362` Overfull `\hbox` 79.16pt at lines 249--257. | Use `tabularx`/`p{}` wrapping for Corpus/Allikas, or shorten first corpus label. |
| `chapters/second_chapter.tex:309-325` | `tab:expert-individual` | likely too wide; `main.log:2367` Overfull `\hbox` 107.05pt at lines 313--322. | Abbreviate model names/headers; use wrapped first column or `resizebox`/smaller table font. |
| `chapters/second_chapter.tex:335-349` | `tab:expert-consensus` | caption too long; no table-width warning, but caption is ~1100 chars. | Add short optional caption; move definitions/CI rules to a table note or preceding paragraph. |
| `chapters/second_chapter.tex:359-364` | `fig:det-v6-v15-v16c-experta` | OK; no `main.log` warning and caption is moderate. | None. |
| `chapters/second_chapter.tex:401-413` | `tab:residual-ablation` | likely too wide; `main.log:2382` Overfull `\hbox` 93.37pt at lines 405--413. | Shorten headers (`Rec A/B`, `HN A`), or wrap with `tabularx`/`resizebox`. |
| `chapters/second_chapter.tex:426-440` | `tab:specaug-ablation` | likely too wide; `main.log:2387` Overfull `\hbox` 104.15pt at lines 430--440. | Shorten headers and move definitions out of cells/caption; use wrapped columns. |
| `chapters/second_chapter.tex:472-489` | `tab:positive-pollution` | likely too wide; `main.log:2398` Overfull `\hbox` 169.05pt at lines 477--489, caused by long `\texttt{}` paths. | Replace full paths with aliases + base-path note; use `p{}`/`tabularx` with breakable monospace. |
| `chapters/second_chapter.tex:530-550` | `tab:v18-family-results` | figure missing-opportunity; no warning due `\scriptsize` + `\resizebox`, but 12 metrics make it hard to read. | Keep compact table or appendix; add heatmap/trade-off plot for main comparison. |
| `chapters/second_chapter.tex:595-614` | `tab:checkpoint-headline` | too dense; no warning inside table, but 12 columns are squeezed; nearby prose warning `main.log:2416` is lines 593--594, not the table. | Split into recall/FPR/FAPH subtables or add plot; shorten caption. |
| `chapters/second_chapter.tex:629-650` | `tab:checkpoint-consensus` | caption too long; no warning due `\resizebox`, caption is ~560 chars and table is dense. | Short optional caption + table note; consider splitting FAPH columns from recall/FPR. |
| `misc/terms_abbreviations.tex:1-13` | none | OK; longtable has no `main.log` warning. | None. |

Unassigned `main.log` warnings near the audited area: `main.log:2392` lines 462--463, `main.log:2403` lines 496--497, `main.log:2409` lines 584--585, and `main.log:2416` lines 593--594 are prose warnings outside float environments. Remaining warnings are in later prose files, not tables/figures.
