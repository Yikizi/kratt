# Deep Research prompt: validate TalTech BSc thesis writing best practices

Use this prompt in ChatGPT Deep Research or another web-capable research agent.

---

You are a research assistant validating thesis-writing and formal-compliance best practices for a TalTech Informatics bachelor thesis.

## Goal

Validate, using live online research, which thesis-document writing practices are officially required or strongly supported for a **Tallinn University of Technology (TalTech), School of Information Technologies / Informatics bachelor thesis**. The output will be used to check and improve a bachelor thesis about an Estonian wake-word system (`Kratt`).

Important: distinguish clearly between:

1. TalTech-wide rules,
2. School of Information Technologies / IT faculty rules,
3. Informatics curriculum-specific rules,
4. template-specific conventions,
5. general academic best practice that is not an official TalTech requirement.

Do not invent requirements. If a rule cannot be verified from official or high-confidence sources, mark it as **not verified**.

## Sources to prioritize

Prioritize current official sources:

- TalTech official pages under `taltech.ee`.
- TalTech document repository / PDFs under `haldus.taltech.ee` or equivalent official TalTech domains.
- TalTech School of Information Technologies pages.
- TalTech Informatics bachelor programme page.
- TalTech thesis/task-description forms and instructions.
- TalTech official thesis templates or library guidance, if available.
- TalTech AI-use, academic ethics, data protection, and graduation-thesis publication guidance, if available.

Known starting points to verify:

- `https://taltech.ee/infotehnoloogia-teaduskond/bakalaureuseope/informaatika#p11828`
- `https://haldus.taltech.ee/sites/default/files/2022-01/IAIB%20Bakalaureuset%C3%B6%C3%B6%20%C3%BClesandep%C3%BCstitus%20alates%20kevad%202022_0.pdf`

Also search the web for current documents using Estonian and English queries such as:

- `site:taltech.ee lõputöö vormistamise nõuded infotehnoloogia teaduskond`
- `site:taltech.ee bakalaureusetöö vormistamise nõuded TalTech IT teaduskond pdf`
- `site:haldus.taltech.ee lõputöö vormistamise nõuded infotehnoloogia teaduskond pdf`
- `site:taltech.ee informaatika lõputöö hindamispõhimõtted`
- `site:taltech.ee TalTech lõputöö tehisintellekti kasutamine deklaratsioon`
- `site:taltech.ee TalTech akadeemiline eetika tehisintellekt lõputöö`
- `site:taltech.ee TalTech lõputöö lihtlitsents digikogu`
- `site:taltech.ee TalTech bakalaureusetöö annotatsioon abstract`
- `site:taltech.ee TalTech thesis template LaTeX`

## Practices to validate

Validate the following current working assumptions. For each, say whether it is confirmed, partly confirmed, contradicted, outdated, or not found.

1. A strong thesis should clearly state the problem, goal, research questions, scope, and contribution in the introduction.
2. The conclusion/summary should explicitly answer the research questions and distinguish achieved, partially achieved, and unachieved goals.
3. The thesis should avoid overclaiming: claims must match available evidence.
4. Methodology must describe data, metrics, validation procedure, and how results are checked/validated.
5. For an engineering/ML thesis, results should be traceable to experiments, tables, figures, source code, logs, or cited literature.
6. Formal structure should include title page, author declaration, task description if required/used, Estonian and English abstracts/annotations, table of contents, lists of figures/tables where applicable, main chapters, bibliography, appendices, and licence/publication declaration as required by TalTech.
7. Abstracts/annotations should include the thesis language, page count, chapter count, figure count, and table count if required by TalTech template/rules.
8. Figures and tables must be numbered, captioned, and referenced in the text before or near presentation.
9. References must be consistent; every bibliography entry should be cited in the text; avoid placeholder/example references.
10. All non-original claims should be cited, with preference for scientific sources where applicable.
11. AI/tool use should be transparently declared if TalTech currently requires or recommends it.
12. If human participants or audio/personal data are involved, ethics, consent, GDPR, anonymisation/pseudonymisation, and data-retention/publication constraints must be addressed.
13. The thesis text should use consistent Estonian terminology and avoid unnecessary English/Estonian hybrids.
14. The final PDF must compile cleanly, with no template placeholders, broken references, unresolved TODOs, or missing required front/back matter.
15. For grading, Informatics emphasizes content/analysis, task setup, topic relevance/novelty, validation of results, work volume/complexity, process, formatting, citation, clarity, balance, and defense quality.

## Output requirements

Produce the report in Estonian.

Use this structure:

1. **Executive summary** — 5–10 bullets: what is officially confirmed and what remains uncertain.
2. **Official-source inventory** — table with columns: source title, owner/unit, URL, date/version if visible, accessed date, scope, reliability.
3. **Validation matrix** — table with columns:
   - practice / claim,
   - status: confirmed / partly confirmed / contradicted / outdated / not found,
   - exact supporting quote or paraphrase,
   - source URL,
   - scope: TalTech-wide / IT faculty / Informatics / template / general academic,
   - implications for the Kratt thesis.
4. **Conflicts and uncertainties** — list any contradictions between sources, missing dates, outdated PDFs, or rules that appear template-specific rather than official.
5. **Action checklist for the Kratt thesis before submission** — prioritize P0/P1/P2. Focus on changes that improve compliance and grading without adding new experiments.
6. **Search log** — list search queries used and notable sources excluded, with reason.

## Critical rules

- Use live web research.
- Prefer primary TalTech sources over summaries, blogs, or LLM-generated documents.
- Quote exact text where possible, especially for formal requirements and grading criteria.
- If a source is a PDF, read the PDF itself, not just the search snippet.
- Do not claim a rule is official unless the source clearly comes from TalTech or an official TalTech unit.
- If you cannot verify the current formal rules, recommend asking the supervisor/programme coordinator and state exactly what to ask.
- Do not make broad thesis-quality recommendations unless they are traceable to official criteria or clearly labelled as general academic best practice.
