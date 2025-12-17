# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projekti kirjeldus

**Kratt** - Eestikeelne privaatne nutikodu häälassistent. Bakalaureusetöö projekt TalTech-is.

Töötlusjada: kõne → tekst (STT) → AI (LLM) → tekst → kõne (TTS)

Privaatsuse tagamiseks kasutatakse telefoni liidest (analoog/VoIP) - süsteem kuulab ainult helistamise ajal.

## Praegune faas

**Uurimisetapp ja prototüüpimine** (30h) - eesmärk on valideerida, kas projekt on piisava mahuga bakalaureusetöö jaoks.

Kriitiline küsimus: Kas lõputöö on uus tarkvara loomine või olemasoleva konfigureerimine?

## Tehnoloogiad (uurimise all)

- **STT**: OpenAI Whisper, TalTech tekstiks.ee
- **LLM**: OpenAI GPT, Anthropic Claude, Ollama (lokaalsed mudelid)
- **TTS**: Eestikeelsed kõnesünteesi lahendused
- **Nutikodu**: Home Assistant, Wyoming protokoll, REST API
- **Telefon**: SIP/VoIP, Asterisk, FreeSWITCH

## Kasulikud käsud

```bash
# Whisper testimine (kui installitud)
whisper audio.wav --language Estonian --model medium

# Home Assistant API test (asenda URL ja token)
curl -H "Authorization: Bearer TOKEN" http://homeassistant.local:8123/api/states
```

## GitLab töövoog

- Üks milestone: "Uurimisetapp ja prototüüpimine"
- Issue'd 1-3h suurused
- Aja jälgimine: `/spend Xh` käsk issue'del
- Labels: `taust`, `prototüüp`, `home-assistant`, `dokumentatsioon`

## Edukriteeriumid (30h lõpuks)

1. Selge arusaam, kas projekt on teostatav bakalaureuse mahus
2. Töötav STT→LLM→TTS prototüüp (kasvõi lihtne)
3. Home Assistant integratsiooni keerukuse hinnang
4. Dokumenteeritud järeldused ja soovitused edasise kohta
