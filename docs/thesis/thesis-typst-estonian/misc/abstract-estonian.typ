#import "../style.typ": *

[ANNOTATSIOONI TEKST LÄHEB SIIA]

Lõputöö on kirjutatud #labels.lang_est keeles ning sisaldab teksti #cfg.main_text_pages leheküljel, #cfg.chapter_count peatükki#if cfg.figure_count > 0 {
  [, #cfg.figure_count #if cfg.figure_count == 1 { "joonis" } else { "joonist" }]
}#if cfg.table_count > 0 {
  [, #cfg.table_count #if cfg.table_count == 1 { "tabel" } else { "tabelit" }]
}.
