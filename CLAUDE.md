# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projekti kirjeldus

**Kratt** - Eestikeelne privaatne nutikodu häälassistent. Bakalaureusetöö projekt TalTech-is.

Töötlusjada: kõne → tekst (STT) → AI (LLM) → tekst → kõne (TTS)

Privaatsuse tagamiseks kasutatakse telefoni liidest (analoog/VoIP) - süsteem kuulab ainult helistamise ajal.

## Praegune faas

**Uurimisetapp ja prototüüpimine** (30h) - eesmärk on valideerida, kas projekt on piisava mahuga bakalaureusetöö jaoks.

Kriitiline küsimus: Kas lõputöö on uus tarkvara loomine või olemasoleva konfigureerimine?

## Tehnoloogiad

- **STT**: kiirkirjutaja (Tanel Alumäe, töötab, ~1s latentsus, 3GB RAM)
- **LLM**: OpenAI GPT, Anthropic Claude, Ollama (lokaalsed mudelid)
- **TTS**: Eestikeelsed kõnesünteesi lahendused (uurimata)
- **Nutikodu**: Home Assistant, Wyoming protokoll, REST API
- **Telefon**: SIP/VoIP, Asterisk, FreeSWITCH

## Kasulikud käsud

```bash
# Kiirkirjutaja streaming (lokaalne mikrofon)
parec --format=s16le --rate=16000 --channels=1 --raw | docker exec -i kiirkirjutaja python main.py -

# Kiirkirjutaja Docker (4GB shm)
docker run -d --name kiirkirjutaja --shm-size 4G -v /home/mattias/data:/data alumae/kiirkirjutaja:latest tail -f /dev/null

# Home Assistant API test (asenda URL ja token)
curl -H "Authorization: Bearer TOKEN" http://homeassistant.local:8123/api/states
```

## GitLab töövoog

- Üks milestone: "Uurimisetapp ja prototüüpimine"
- Issue'd 1-3h suurused
- Aja jälgimine: `/spend Xh` käsk issue'del
- Labels: `taust`, `prototüüp`, `home-assistant`, `dokumentatsioon`
- Aja statistika: `./scripts/gitlab-time-stats.sh`

## Clockify

- Workspace ID: `654b80c1c7d5882517e4f0f1`
- Project ID (Kratt): `693b3fbbb903c31b0e4cb932`

## Edukriteeriumid (30h lõpuks)

1. Selge arusaam, kas projekt on teostatav bakalaureuse mahus
2. Töötav STT→LLM→TTS prototüüp (kasvõi lihtne)
3. Home Assistant integratsiooni keerukuse hinnang
4. Dokumenteeritud järeldused ja soovitused edasise kohta
