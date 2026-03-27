#!/usr/bin/env python3
"""Hard negative phrases for wake word discrimination training.

These phrases are phonetically close to "Kuule Kratt" and should NOT trigger detection.
Organized by confusion pattern.
"""

# Pattern 1: "kuule" + kr-words (closest confusion)
KUULE_KR = [
    "Kuule kraam",
    "Kuule kraad",
    "Kuule kruvi",
    "Kuule kriit",
    "Kuule kriips",
    "Kuule krats",  # very close!
    "Kuule kraft",
    "Kuule krahh",
    "Kuule kraana",
    "Kuule kroon",
    "Kuule kruus",
    "Kuule kross",
    "Kuule krupp",
    "Kuule kram",
    "Kuule krant",
    "Kuule kraps",
    "Kuule krabin",
    "Kuule krae",
    "Kuule krepp",
    "Kuule kringel",
]

# Pattern 2: "kuule" + k-words (medium confusion)
KUULE_K = [
    "Kuule kass",
    "Kuule koer",
    "Kuule kott",
    "Kuule kook",
    "Kuule kala",
    "Kuule kell",
    "Kuule kaart",
    "Kuule kallas",
    "Kuule kallis",
    "Kuule kodu",
    "Kuule kohv",
    "Kuule kuidas",
    "Kuule kust",
    "Kuule küll",
    "Kuule kõik",
    "Kuule kord",
    "Kuule kuhu",
    "Kuule kiire",
    "Kuule keegi",
    "Kuule kaua",
]

# Pattern 3: rhymes with "kratt" (ratt, matt, etc.)
KUULE_RHYME = [
    "Kuule ratt",
    "Kuule matt",
    "Kuule pratt",
    "Kuule plaat",
    "Kuule rott",
    "Kuule traat",
    "Kuule kraht",  # aspirated
    "Kuule trall",
    "Kuule trumm",
    "Kuule prääks",
]

# Pattern 4: "kuule" alone or with non-k words
KUULE_OTHER = [
    "Kuule siin",
    "Kuule nüüd",
    "Kuule mind",
    "Kuule palun",
    "Kuule tule",
    "Kuule vaata",
    "Kuule oota",
    "Kuule ära",
    "Kuule siia",
    "Kuule jah",
    "Kuule ei",
    "Kuule mis",
    "Kuule see",
    "Kuule kas",
    "Kuule no",
]

# Pattern 5: partial "kratt" embedded in longer words/phrases
EMBEDDED_KRAT = [
    "Kratside",
    "Kratsima",
    "Kratsin seda",
    "See on kraam",
    "Kraadi mõõtmine",
    "Kraft paber",
    "Kraan tilgub",
    "Krooni väärtus",
]

# Pattern 6: similar-sounding non-Estonian (English leaks)
FOREIGN_SIMILAR = [
    "Kuule crash",
    "Kuule craft",
    "Kuule crap",
    "Kuule crack",
    "Kuule cross",
    "Kuule great",
    "Kuule grab",
    "Kuule grant",
    "Kuule grass",
    "Kuule grill",
]

# Pattern 7: just "kratt" in different contexts (not wake word)
KRATT_CONTEXT = [
    "See kratt",
    "Mis kratt",
    "Kas kratt",
    "Üks kratt",
    "Minu kratt",
    "Sinu kratt",
    "Too kratt",
    "Vana kratt",
    "Uus kratt",
    "Väike kratt",
]

# Pattern 8: speed/mumble variations of "kuule" prefix
KUULE_VARIANTS = [
    "Kule koer",
    "Kule kass",
    "Kule rott",
    "Kuuule kass",
    "Kuuule koer",
    "Kle kass",
    "Kle koer",
]

ALL_PHRASES = (
    KUULE_KR
    + KUULE_K
    + KUULE_RHYME
    + KUULE_OTHER
    + EMBEDDED_KRAT
    + FOREIGN_SIMILAR
    + KRATT_CONTEXT
    + KUULE_VARIANTS
)

if __name__ == "__main__":
    print(f"Total hard negative phrases: {len(ALL_PHRASES)}")
    print()
    for category, phrases in [
        ("kuule + kr-words", KUULE_KR),
        ("kuule + k-words", KUULE_K),
        ("kuule + rhymes", KUULE_RHYME),
        ("kuule + other", KUULE_OTHER),
        ("embedded krat", EMBEDDED_KRAT),
        ("foreign similar", FOREIGN_SIMILAR),
        ("kratt context", KRATT_CONTEXT),
        ("kuule variants", KUULE_VARIANTS),
    ]:
        print(f"{category}: {len(phrases)}")
        for p in phrases:
            print(f"  - {p}")
        print()
