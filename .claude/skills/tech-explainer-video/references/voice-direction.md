# Voice direction (human, Branch pace, no emotion tags)

Sources: EngineX `enginex-emotive-speech` skill (main page, voices.md, narration.md category 4 and 2, tools.md) and the
Branch measurement (146 wpm, ~0.6 s between sentences, ~97 pauses in 15.5 min).

## Casting
- `owen` - recorded, male, "clear and measured, a tech explainer"; listed for documentary and science explainers;
  held as one voice with `continuity: true`. Default.
- `henry` - recorded, "low and measured"; backup if owen sounds flat on a take.
- Never clone a narrator from someone else's video (the voice guide: "only a voice the person has the right to use").
  If the user records their own 10-20 s clean clip, clone THAT (`reference` + `referenceText`).
- Never `oliver`, `leo` (voice changes between lines), never synthetic voices.

## Exact call (ONE for the whole video: one take = one consistent voice, one transcribe)
```json
{"engine":"emotive-speech","operation":"speak","params":{"voice":"owen","text":"<all chapters/NN.speak.txt joined by a blank line>",
 "lineGapMs":450,"paragraphGapMs":900,"continuity":true,"format":"wav","tier":"gpu",
 "idempotencyKey":"<project>-vo-v1"},"waitMs":0}
```
Limit 20,000 characters (~20 min at 146 wpm). Each chapter starts a paragraph (blank line) with the same neutral brief,
so chapter breaks get the 900 ms paragraph gap. Chapter start/end times come from the result's `lines`.
No `temperature`, no `emotion`, `speed` left normal (tempo change is a last resort and only `slow`).

## Why it will not sound robotic without emotion tags
- The only bracket per paragraph is a neutral delivery brief, added by the lint:
  `[a documentary narrator explaining to a friend, warm and clear, steady pace]` (user-approved standard for ALL videos,
  2026-11-07; the older "clear and measured" / "calm and clear" briefs came out flat). It sets pace and warmth, not feeling.
- `lineGapMs` 350 (not 450): the shorter gap keeps linked lines flowing.
- **Line shape does the acting**: one thought per line (two sentences, up to ~230 characters / ~15 s), so the voice
  joins them with its own breath; never one short sentence per line (that is what sounds like a machine).
- Commas where a person breathes; questions end with "?" (the voice lifts and the gap grows by 250 ms).
- `[pause]` line before a reveal or a surprising number (adds 500 ms); `[long pause]` only before the closing line.
- Contractions, "we" and "you", plain words.

## Hindi narration (measured on Temple, 2026-11-07)
- Voices offered (recorded, Hindi): `arnav` (friendly explainer, the Hindi default), `raghav` (steady documentary: the user's
  pick), `aarav` (even e-learning), `nandini` (warm, female; no first-person verbs in the script, so no gender edits needed).
  Give the user several takes of the SAME script and let them choose by ear: 4 takes cost 4 speak calls and ~1 min each.
- Brief on every paragraph, nothing else: `[a documentary narrator explaining to a friend, warm and clear, steady pace]`
  (approved; the first Temple take used "calm and clear, one steady pace" and parts sounded flat); `[pause]` before the
  reveal lines, `[long pause]` before the last line. `lineGapMs` 350, `paragraphGapMs` 900, `continuity: true`, `tier` OMITTED
  (Emotive Speech has CPU pods only).
- Text: Devanagari Hinglish, numbers/units/acronyms in words (सी ई ओ, पी पी जी, ज़ीरो पॉइंट आठ), ~13 characters a second
  (3,863 characters -> 4:51 to 5:03 by voice). The job reads each line back (`checked.lines`): all 32 matched on every take.
- **Robotic/flat lines = short separate statements, not pace.** On Temple ch4 the user called three lines robotic while the
  next line was "good"; the pace was normal (163-194 wpm vs 205). The good line was ONE linked sentence
  ("…बदल देता है, जिसका नाम है…"); the flat ones were full stops between short facts ("…बँधी है। इसे कहते हैं…").
  Fix: join the facts with जो / जिसे / जहाँ / और plus commas (same words, same facts), `lineGapMs` 350, brief
  `[a documentary narrator explaining to a friend, warm and clear, steady pace]`. Re-take ONLY that chapter, include the
  good line after it so the flow carries, keep it within the chapter's slot so nothing after it moves.
- A direction in `[ ]` is at most **80 characters** (longer is refused by validation).

## Pace check (from the transcript of each chapter)
wpm = words / (last word end - first word start) x 60. Target 140-152 (Branch 146).
- Too fast (> 152): add `[pause]` lines between thoughts, raise `lineGapMs` to 550. Never speed up a slow read with
  `speed: fast`.
- Too slow (< 140): join sentences of one thought onto one line, `lineGapMs` 350.
- Gaps: median gap between sentences should be 0.4-0.8 s.
- Word check: every script line present in order (not just total length); a missing or repeated line = re-take that
  chapter only (new idempotency key `-v2`).
