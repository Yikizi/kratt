# TalTech Thesis Template (Typst)

Typst conversion of `docs/thesis/thesis-tex-estonian`.

## Structure

- `main.typ` - main thesis document
- `config/config.typ` - all template variables
- `style.typ` - page layout and helper functions
- `misc/` - title/declaration/abstract/terms/licence sections
- `chapters/` - thesis chapter files
- `appendices/` - appendices
- `references.bib` - bibliography for `main.typ`
- `ylesandepystitus.typ` - Typst version of thesis proposal
- `ylesandepystitus.bib` - bibliography for proposal
- `figures/` - figures used in sample content

## Compile

```bash
cd docs/thesis/thesis-typst-estonian
typst compile main.typ
typst compile ylesandepystitus.typ
```

## Customization

1. Edit `config/config.typ`.
2. Replace placeholder text in:
   - `misc/abstract-estonian.typ`
   - `misc/abstract-english.typ`
   - `chapters/third_chapter.typ`
   - `chapters/summary.typ`
3. Add/update citations in `references.bib`.

## Notes

- `main_text_pages`, `chapter_count`, `figure_count`, and `table_count` in config are manual fields to keep output deterministic.
- Estonian title page is always included; English title page is added when `lang: "ENG"`.
