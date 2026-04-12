# docs/

Project documentation. Split from `notes/` (working diary) — here lives maintained, reviewed content.

## Structure

```
docs/
├── thesis/                     # LaTeX thesis source (Estonian)
│   ├── thesis-tex-estonian/    # Active: chapters, figures, references.bib
│   ├── evaluation/             # LLM comparison notes
│   ├── presentation/           # Defence slides brief
│   └── sections/               # Standalone sections (benchmarks, RQs)
│
├── architecture/
│   └── decision-records/       # ADRs (e.g. 0001-ekspressiivne-tts-markup)
│
├── research/                   # Evaluation methodology, MVP plans
├── user-testing/               # Test plan, questionnaire, portable setup
├── notebooklm-pack/            # Exported briefs for NotebookLM
├── stitch-taltech-pack/        # TalTech brand assets for slide generation
├── PROJECT_TODO.md             # Master task tracker (source of truth)
├── GIT_STRATEGY.md             # Branching and workflow decisions
└── projekti_kirjeldus.md       # Thesis proposal (Estonian)
```

## Conventions

- Thesis in Estonian, everything else in English
- BibTeX citations in `thesis/thesis-tex-estonian/references.bib`
- Figures: 300 DPI, Estonian labels, stored in `thesis-tex-estonian/figures/`
- ADRs: one file per decision, numbered sequentially
