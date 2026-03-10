# E2E Demo: Discord Voice -> OpenClaw -> STT (INT8) -> LLM -> TTS (Neurokõne) -> Discord Voice

**Status**: working prototype (E2E demo)

See ei ole lõputöö põhitracki järgi core-nõue, aga on väga hea *demonstrator*, sest näitab eestikeelse voice assistendi pipeline'i algusest lõpuni.

## Eesmärk
- Kasutaja räägib Discord voice channelis eesti keeles.
- Süsteem transkribeerib (STT), tekitab vastuse (LLM) ja räägib eesti keeles vastu (TTS).

## Arhitektuur
1. Discord voice channel (audio input/output)
2. OpenClaw gateway + Discord extension (audio capture + playback)
3. STT teenus homelabis: Kiirkirjutaja INT8 (Wyoming)
4. Agent/LLM: Claude läbi OpenClaw agent runtime
5. TTS teenus homelabis: Neurokõne/TartuNLP TTS stack (docker-compose)

## Komponendid
### OpenClaw
- Local source: `/Users/mattias/openclaw-src2`
- Konf: `~/.openclaw/openclaw.json`
- Gateway teenus homelabis: `openclaw-gateway` (systemd --user)

### STT (Kiirkirjutaja INT8)
- Jooksev konteiner homelabis: `kiirkirjutaja-wyoming`
- Wyoming STT port: `10300` (proto, mitte HTTP)

### TTS (Neurokõne)
- Homelabis `~/tts/docker-compose.yml`
- TartuNLP text-to-speech worker + API (compose)
- Mudelid: tõmmatakse release'ist (vt `wake-word/data/collection/NEUROKONE_OPTIONS.md`)

## Setup (kõrgtasemel)
1. STT konteiner tööle (Wyoming)
2. TTS stack tööle (docker compose)
3. OpenClaw gateway tööle + Discord plugin configure
4. Join Discord voice channel ja testi

## Debug / logid
### Gateway logid (homelab)
```bash
ssh homelab "journalctl --user -u openclaw-gateway -f --no-pager"
ssh homelab "journalctl --user -u openclaw-gateway --no-pager --since '2 min ago'"
```

### STT logid (homelab)
```bash
ssh homelab "docker logs kiirkirjutaja-wyoming --tail 50"
```

### Docker üldine seis (homelab)
```bash
ssh homelab "docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'"
```

## Tüüpilised vead
- Voice agent jookseb eraldi kontekstis: vaja on eraldi auth-profiili (nt `openclaw agents add <id>` või kopeerida `auth-profiles.json`).
- Discord plugin path/config mismatch: kontrolli plugin id ja teekonnad.
- "Nothing is happening": alusta gateway logidest, siis STT/TTS container logidest.

## Miks see sobib lõputöö lisana
- Näitab E2E süsteemi kasutatavust ja latentsust.
- Demonstreerib praktikas integratsiooni: audio transport, teenused, logimine/operatsioon.
- Saab lisada Appendix/prototüübi peatükina ilma wake-word põhifookust lõhkumata.
