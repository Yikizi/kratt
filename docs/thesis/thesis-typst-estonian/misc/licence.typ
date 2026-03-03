#import "../style.typ": *

#let supervisor_word_est = if has_cosupervisor { "juhendajad" } else { "juhendaja" }

#if is_eng {
  if authors().len() == 1 {
    [
      I #cfg.author_name

      + Grant Tallinn University of Technology free licence (non-exclusive licence) for my thesis "#cfg.thesis_title_eng", supervised by #supervisor_list(conj: "and")
        + to be reproduced for the purposes of preservation and electronic publication of the graduation thesis, incl. to be entered in the digital collection of the library of Tallinn University of Technology until expiry of the term of copyright.
        + to be published via the web of Tallinn University of Technology, incl. to be entered in the digital collection of the library of Tallinn University of Technology until expiry of the term of copyright.
      + I am aware that the author also retains the rights specified in clause 1 of the non-exclusive licence.
      + I confirm that granting the non-exclusive licence does not infringe other persons' intellectual property rights, the rights arising from the Personal Data Protection Act or rights arising from other legislation.
    ]
  } else {
    [
      We #authors_inline(conj: "and")

      + Grant Tallinn University of Technology free licence (non-exclusive licence) for our thesis "#cfg.thesis_title_eng", supervised by #supervisor_list(conj: "and")
        + to be reproduced for the purposes of preservation and electronic publication of the graduation thesis, incl. to be entered in the digital collection of the library of Tallinn University of Technology until expiry of the term of copyright.
        + to be published via the web of Tallinn University of Technology, incl. to be entered in the digital collection of the library of Tallinn University of Technology until expiry of the term of copyright.
      + We are aware that the authors also retain the rights specified in clause 1 of the non-exclusive licence.
      + We confirm that granting the non-exclusive licence does not infringe other persons' intellectual property rights, the rights arising from the Personal Data Protection Act or rights arising from other legislation.
    ]
  }
} else {
  if authors().len() == 1 {
    [
      Mina, #cfg.author_name

      + Annan Tallinna Tehnikaülikoolile tasuta loa (lihtlitsentsi) enda loodud teose "#cfg.thesis_title_est", mille #supervisor_word_est on #supervisor_list(conj: "ja")
        + reprodutseerimiseks lõputöö säilitamise ja elektroonse avaldamise eesmärgil, sh Tallinna Tehnikaülikooli raamatukogu digikogusse lisamise eesmärgil kuni autoriõiguse kehtivuse tähtaja lõppemiseni.
        + üldsusele kättesaadavaks tegemiseks Tallinna Tehnikaülikooli veebikeskkonna kaudu, sealhulgas Tallinna Tehnikaülikooli raamatukogu digikogu kaudu kuni autoriõiguse kehtivuse tähtaja lõppemiseni.
      + Olen teadlik, et käesoleva lihtlitsentsi punktis 1 nimetatud õigused jäävad alles ka autorile.
      + Kinnitan, et lihtlitsentsi andmisega ei rikuta teiste isikute intellektuaalomandi ega isikuandmete kaitse seadusest ning muudest õigusaktidest tulenevaid õigusi.
    ]
  } else {
    [
      Meie, #authors_inline(conj: "ja")

      + Anname Tallinna Tehnikaülikoolile tasuta loa (lihtlitsentsi) enda loodud teose "#cfg.thesis_title_est", mille #supervisor_word_est on #supervisor_list(conj: "ja")
        + reprodutseerimiseks lõputöö säilitamise ja elektroonse avaldamise eesmärgil, sh Tallinna Tehnikaülikooli raamatukogu digikogusse lisamise eesmärgil kuni autoriõiguse kehtivuse tähtaja lõppemiseni.
        + üldsusele kättesaadavaks tegemiseks Tallinna Tehnikaülikooli veebikeskkonna kaudu, sealhulgas Tallinna Tehnikaülikooli raamatukogu digikogu kaudu kuni autoriõiguse kehtivuse tähtaja lõppemiseni.
      + Oleme teadlikud, et käesoleva lihtlitsentsi punktis 1 nimetatud õigused jäävad alles ka autoritele.
      + Kinnitame, et lihtlitsentsi andmisega ei rikuta teiste isikute intellektuaalomandi ega isikuandmete kaitse seadusest ning muudest õigusaktidest tulenevaid õigusi.
    ]
  }
}

#v(0.5cm)
#cfg.signature_date
