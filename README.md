# Eestikeelne nutikodu assistent “Kratt”

## Lühikokkuvõte

Selle projekti eesmärk on jõuda *Home Assistanti* lisandini, mis pakub eestikeelset kõnetuvastust *Wyoming* protokolli kaudu ning on kasutajale võimalikult lihtsasti paigaldatav.

Varase prototüüpimise käigus selgus, et *Whisper*-põhised lahendused ei sobinud minu katsetes reaalaja kasutusjuhtudeks, kuna latentsus oli suur ja kasutuskogemus ebastabiilne. Seetõttu on keskne uurimis- ja arendussuund *Kiirkirjutaja* kasutamine ja selle sidumine *Home Assistanti* häältöötlusahelaga.

Täisväärtusliku kasutatavuse jaoks on oluline ka äratussõna tuvastus koos kõneaktiivsuse tuvastusega (*VAD*). Praegu ei ole mulle teadaolevalt laialt kättesaadavat eestikeelset äratussõna mudelit; üks võimalik suund on treenida äratusfraas “Kuule Kratt” või “Hei Kratt” sobivas raamistikus, näiteks *openWakeWord* või *microWakeWord*.

## Projekti struktuur

- `experiments/` – varased katsed ja prototüübid
- `docs/` – taustamaterjalid ja failid
- `scripts/` – abiskriptid projekti ajahaldamiseks

## Töökorraldus

Töö on jaotatud väikesteks ülesanneteks *GitLab* issue’de kaudu.
Milestone: “Uurimisetapp ja prototüüpimine”.

Aja kokkuvõtteks on skript:

```bash
./scripts/gitlab-time-stats.sh
```

## Järgmised sammud

- *Home Assistanti* lisandi vormistamine ja pakendamine, et paigaldus oleks kasutajale lihtne
- Mõõtmised ja analüüs: latentsus, ressursikasutus ja kvaliteet
- Äratussõna tuvastuse suuna valideerimine ning vajadusel treeningandmestiku ja mudeli loomine

