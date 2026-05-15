# TalTech online-validation delta for Kratt thesis closeout — 2026-05-11

Source report imported from ChatGPT Deep Research:

- `docs/research/taltech-thesis-best-practices-online-validation-2026-05-11.md`

Prompt used:

- `docs/research/taltech-thesis-best-practices-deep-research-prompt.md`

## Key official-source updates

1. **Use the 2025 IT faculty thesis guide as the current formal baseline**, not the older 2020 wording used in some prior automated audits.
   - Official page: `https://taltech.ee/infotehnoloogia-teaduskond/lopetajale`
   - Guide PDF: `https://haldus.taltech.ee/sites/default/files/2025-08/IT-teaduskonna%20l%C3%B5put%C3%B6%C3%B6%20koostamise%20ja%20vormindamise%20juhend.pdf`

2. **IAIB task description is required as a process document, but not clearly a required part of the final thesis PDF.**
   - Do not add it to the thesis body/lisad unless supervisor/programme practice requires it.
   - Existing IAIB PDF remains useful for validating problem/goal/method/validation framing.

3. **Introduction and conclusion requirements are officially supported.**
   - Introduction must cover topic, goal, problem/research questions, starting conditions/scope, special conditions, and structure.
   - Conclusion/summary must answer the questions raised in the introduction and honestly state unachieved goals/deficiencies.

4. **Abstract/annotation count sentence is confirmed.**
   - Both languages should include thesis language, main-text pages, chapter count, figure count, and table count.

5. **Citation hygiene is official, not optional.**
   - Bibliography should contain only sources actually used/cited.
   - Use original/real sources; no placeholder/example references.
   - All non-original ideas/data/text/paraphrases need attribution unless genuinely common knowledge.
   - Official source guide: `https://haldus.taltech.ee/sites/default/files/2024-04/Allikate%20kasutamise%20juhend%2016042024.pdf`

6. **AI-use declaration is nuanced.**
   - Pure language polishing of own text does not require citation.
   - Substantive AI-generated text/code/images/analysis should be cited or described, and large-scale use should be described in methodology/introduction.
   - AI is not a source for factual claims; cite human/original sources.

7. **Human voice/audio data requires a data-protection treatment, but a single IAIB-specific ethics-permit trigger was not verified.**
   - Still document consent, pseudonymisation/anonymisation, retention, audio publication limits, and whether a thesis-publication access restriction is needed.
   - Ask supervisor/programme if formal ethics review is required for the actual user-test setup.

8. **IAIB grading criteria are confirmed.**
   - Highest weight: substantive solution and analysis, including task setup, relevance/novelty, alternatives, validation.
   - Also: work volume/complexity, process, formatting, citation quality, clarity, balance, and defense.
   - IAIB explicitly says thesis text length is not the measure of work volume.

## P0 closeout actions for Kratt

1. **Update formal-compliance references in our internal notes** from “TalTech IT faculty guide (2020)” to the current 2025 IT faculty guide where applicable.
2. **Final PDF structure check:** title page, author declaration, Estonian + English abstracts, TOC, main chapters, bibliography, licence; figure/table lists if applicable.
3. **Introduction check:** ensure problem, goal, research questions, scope/starting conditions, and thesis structure are explicit.
4. **Summary check:** add/keep explicit research-question answers and status: achieved / partially achieved / not achieved.
5. **Bibliography check:** remove `example-reference`, unused BibTeX entries that appear in the printed bibliography, and any unverified source placeholders.
6. **Figure/table check:** every figure/table is numbered, captioned, and referenced before it appears.
7. **AI-use note:** add a short, honest declaration if substantive AI assistance affected code/text/analysis.
8. **Voice-data note:** keep/strengthen consent, GDPR, pseudonymisation, retention, and publication-limit prose.

## P1 closeout actions

1. Keep the contribution hierarchy conservative: evaluation protocol/prototype first, not production-ready model.
2. Prefer compression over expansion: IAIB criteria reward substance and validation, not page count.
3. Run terminology cleanup for English/Estonian hybrids.
4. Treat user-test status precisely: completed evidence vs planned/partial evidence must not blur.

## Questions to ask supervisor/programme only if still ambiguous

1. Should the IAIB task description be included in the final PDF as an appendix, or only submitted in Protsessor?
2. Is any formal ethics review needed for the specific Kratt user-test/audio protocol, beyond consent and data-protection documentation?
3. What exact form does IAIB prefer for substantive AI-use disclosure?
