#import "config/config.typ": cfg
#import "style.typ": *

#show: doc => {
  // Optional first page in English if thesis language is English.
  if is_eng {
    title_page(lang: "ENG")
    pagebreak()
  }

  // Estonian title page is always present.
  title_page(lang: "EST")
  pagebreak()

  // Match LaTeX page numbering offset (2 for EST thesis, 3 for ENG thesis).
  counter(page).update(abstract_page_number)

  heading(level: 1, numbering: none)[#labels.author_declaration_title]
  include "misc/authordeclaration.typ"

  pagebreak()
  heading(level: 1, numbering: none)[#labels.abstract_title]
  if is_eng {
    include "misc/abstract-english.typ"
  } else {
    include "misc/abstract-estonian.typ"
  }

  pagebreak()
  heading(level: 1, numbering: none)[
    #labels.second_abstract_title#linebreak()
    #labels.abstract_thesis_title
  ]
  if is_eng {
    include "misc/abstract-estonian.typ"
  } else {
    include "misc/abstract-english.typ"
  }

  pagebreak()
  heading(level: 1, numbering: none)[#labels.list_of_terms_title]
  include "misc/terms_abbreviations.typ"

  pagebreak()
  outline(title: [#labels.table_of_contents_title], depth: 3)

  if cfg.figure_count > 0 {
    pagebreak()
    outline(
      title: [#labels.list_of_figures_title],
      target: figure.where(kind: image),
    )
  }

  if cfg.table_count > 0 {
    pagebreak()
    outline(
      title: [#labels.list_of_tables_title],
      target: figure.where(kind: table),
    )
  }

  pagebreak()
  include "chapters/chapters_main.typ"

  pagebreak()
  bibliography("references.bib", title: [#labels.references_title])

  pagebreak()
  heading(level: 1, numbering: none)[
    #labels.appendix_title 1 -- #labels.licence_title#footnote[#labels.licence_footnote]
  ]
  include "misc/licence.typ"

  include "appendices/appendices_main.typ"
}
