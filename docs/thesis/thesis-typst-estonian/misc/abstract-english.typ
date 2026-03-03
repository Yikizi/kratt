#import "../style.typ": *

[YOUR TEXT GOES HERE]

The thesis is in #labels.lang_eng and contains #cfg.main_text_pages pages of text, #cfg.chapter_count chapters#if cfg.figure_count > 0 {
  [, #cfg.figure_count #if cfg.figure_count == 1 { "figure" } else { "figures" }]
}#if cfg.table_count > 0 {
  [, #cfg.table_count #if cfg.table_count == 1 { "table" } else { "tables" }]
}.
