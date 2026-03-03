#import "config/config.typ": cfg

#set page(
  paper: "a4",
  margin: (top: 25mm, bottom: 25mm, left: 30mm, right: 30mm),
  numbering: "1",
)
#set text(font: "Times New Roman", size: 12pt)
#set par(
  first-line-indent: 0pt,
  spacing: 12pt,
  leading: 0.65em,
  justify: true,
)
#set heading(numbering: "1.")
#show heading.where(level: 1): set text(size: 16pt, weight: "bold")
#show heading.where(level: 2): set text(size: 14pt, weight: "bold")
#show heading.where(level: 3): set text(size: 12pt, weight: "bold")
#show heading.where(level: 4): set text(size: 12pt, weight: "bold")
#set list(marker: [■], indent: 0.63cm)
#set enum(indent: 0.63cm)

#let is_eng = cfg.lang == "ENG"
#let has_second_author = cfg.author_name_two != "[Second Author name]"
#let has_third_author = cfg.author_name_three != "[Third Author name]"
#let has_cosupervisor = cfg.cosupervisor_name != "[Co-Supervisor's Name]" and cfg.cosupervisor_name != "[Kaasjuhendaja nimi]"

#let authors() = (
  (name: cfg.author_name, code: cfg.studentcode),
) + (if has_second_author { ((name: cfg.author_name_two, code: cfg.studentcode_two),) } else { () }) + (if has_third_author { ((name: cfg.author_name_three, code: cfg.studentcode_three),) } else { () })

#let thesis_type_est = if cfg.thesis_type == "Bachelor's Thesis" {
  "Bakalaureusetöö"
} else if cfg.thesis_type == "Master's Thesis" {
  "Magistritöö"
} else {
  "Bakalaureusetöö / Magistritöö"
}

#let labels = if is_eng {
  (
    thesis_title: cfg.thesis_title_eng,
    abstract_thesis_title: cfg.thesis_title_est,
    lang_est: "inglise",
    lang_eng: "English",
    author_declaration_title: "Author's declaration of originality",
    abstract_title: "Abstract",
    second_abstract_title: "Annotatsioon",
    list_of_terms_title: "List of abbreviations and terms",
    table_of_contents_title: "Table of contents",
    list_of_figures_title: "List of figures",
    list_of_tables_title: "List of tables",
    references_title: "References",
    appendix_title: "Appendix",
    licence_title: "Non-exclusive licence for reproduction and publication of a graduation thesis",
    licence_footnote: "The non-exclusive licence is not valid during the validity of access restriction indicated in the student's application for restriction on access to the graduation thesis that has been signed by the school's dean, except in case of the university's right to reproduce the thesis for preservation purposes only. If a graduation thesis is based on the joint creative activity of two or more persons and the co-author(s) has/have not granted, by the set deadline, the student defending his/her graduation thesis consent to reproduce and publish the graduation thesis in compliance with clauses 1.1 and 1.2 of the non-exclusive licence, the non-exclusive licence shall not be valid for the period.",
    supervisor: "Supervisor",
    cosupervisor: "Co-Supervisor",
  )
} else {
  (
    thesis_title: cfg.thesis_title_est,
    abstract_thesis_title: cfg.thesis_title_eng,
    lang_est: "eesti",
    lang_eng: "Estonian",
    author_declaration_title: "Autorideklaratsioon",
    abstract_title: "Annotatsioon",
    second_abstract_title: "Abstract",
    list_of_terms_title: "Lühendite ja mõistete sõnastik",
    table_of_contents_title: "Sisukord",
    list_of_figures_title: "Jooniste loetelu",
    list_of_tables_title: "Tabelite loetelu",
    references_title: "Kasutatud kirjandus",
    appendix_title: "Lisa",
    licence_title: "Lihtlitsents lõputöö reprodutseerimiseks ja lõputöö üldsusele kättesaadavaks tegemiseks",
    licence_footnote: "Lihtlitsents ei kehti juurdepääsupiirangu kehtivuse ajal vastavalt üliõpilase taotlusele lõputööle juurdepääsupiirangu kehtestamiseks, mis on allkirjastatud teaduskonna dekaani poolt, välja arvatud ülikooli õigus lõputööd reprodutseerida üksnes säilitamise eesmärgil. Kui lõputöö on loonud kaks või enam isikut oma ühise loomingulise tegevusega ning lõputöö kaas- või ühisautor(id) ei ole andnud lõputööd kaitsvale üliõpilasele kindlaksmääratud tähtajaks nõusolekut lõputöö reprodutseerimiseks ja avalikustamiseks vastavalt lihtlitsentsi punktidele 1.1. ja 1.2, siis lihtlitsents nimetatud tähtaja jooksul ei kehti.",
    supervisor: "Juhendaja",
    cosupervisor: "Kaasjuhendaja",
  )
}

#let abstract_page_number = if is_eng { 3 } else { 2 }
#let thesis_type_local = if is_eng { cfg.thesis_type } else { thesis_type_est }

#let authors_inline(conj: "and") = {
  let names = authors().map(a => a.name)
  if names.len() == 1 {
    names.at(0)
  } else if names.len() == 2 {
    names.at(0) + " " + conj + " " + names.at(1)
  } else {
    names.at(0) + ", " + names.at(1) + " " + conj + " " + names.at(2)
  }
}

#let supervisor_list(conj: "and") = if has_cosupervisor {
  cfg.supervisor_name + " " + conj + " " + cfg.cosupervisor_name
} else {
  cfg.supervisor_name
}

#let title_page(lang: "EST") = [
  #let page_is_eng = lang == "ENG"
  #let university = if page_is_eng { "TALLINN UNIVERSITY OF TECHNOLOGY" } else { "TALLINNA TEHNIKAÜLIKOOL" }
  #let school = if page_is_eng { "School of Information Technologies" } else { "Infotehnoloogia teaduskond" }
  #let supervisor_label = if page_is_eng { "Supervisor" } else { "Juhendaja" }
  #let cosupervisor_label = if page_is_eng { "Co-Supervisor" } else { "Kaasjuhendaja" }
  #let thesis_type = if page_is_eng { cfg.thesis_type } else { thesis_type_est }
  #let thesis_title = if page_is_eng { cfg.thesis_title_eng } else { cfg.thesis_title_est }

  #align(center)[
    #university#linebreak()
    #school

    #v(4.5cm)

    #for a in authors() [
      #a.name #h(0.5em) #a.code#linebreak()
    ]

    #v(1.5cm)
    #text(size: 20pt, weight: "bold")[#thesis_title]

    #v(1.5cm)
    #thesis_type
  ]

  #v(0.6cm)
  #align(right)[
    #supervisor_label: #cfg.supervisor_name#linebreak()
    #cfg.supervisor_title
    #if has_cosupervisor [
      #v(0.2cm)
      #linebreak()
      #cosupervisor_label: #cfg.cosupervisor_name#linebreak()
      #cfg.cosupervisor_title
    ]
  ]

  #v(5cm)
  #align(center)[Tallinn #cfg.year]
]
