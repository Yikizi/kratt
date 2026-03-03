#import "../style.typ": *

#if is_eng {
  if authors().len() == 1 {
    [
      I hereby certify that I am the sole author of this thesis and that this thesis has not been presented for examination or submitted for defense anywhere else. All used materials, references to the literature, and work of others have been cited.

      Author: #cfg.author_name
    ]
  } else {
    [
      We hereby certify that we are the sole authors of this thesis and that this thesis has not been presented for examination or submitted for defense anywhere else. All used materials, references to the literature, and work of others have been cited.

      Authors: #authors_inline(conj: "and")
    ]
  }
} else {
  if authors().len() == 1 {
    [
      Kinnitan, et olen koostanud antud lõputöö iseseisvalt ning seda ei ole kellegi teise poolt varem kaitsmisele esitatud. Kõik töö koostamisel kasutatud teiste autorite tööd, olulised seisukohad, kirjandusallikatest ja mujalt pärinevad andmed on töös viidatud.

      Autor: #cfg.author_name
    ]
  } else {
    [
      Kinnitame, et oleme koostanud antud lõputöö iseseisvalt ning seda ei ole kellegi teise poolt varem kaitsmisele esitatud. Kõik töö koostamisel kasutatud teiste autorite tööd, olulised seisukohad, kirjandusallikatest ja mujalt pärinevad andmed on töös viidatud.

      Autorid: #authors_inline(conj: "ja")
    ]
  }
}

#v(0.5cm)
#cfg.signature_date
