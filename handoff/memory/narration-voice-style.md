---
name: narration-voice-style
description: "Approved narration style for ALL videos - linked-clause lines + \"explaining to a friend\" brief (Temple ch4 retake, 2026-11-07)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: a78e9ddf-286f-4b3a-9c8a-244792cef2af
  modified: 2026-11-06T22:28:35.254Z
---

The user approved the Temple ch4 retake (job b73db2e1-748c-49ef-a1df-b3945054d4ab, raghav) as "very good" and asked to use
this kind of audio for every video from now on.

The recipe:
- Brief on every paragraph: `[a documentary narrator explaining to a friend, warm and clear, steady pace]` (max 80 chars).
- Lines written as linked clauses, not short facts split by full stops. Join with जो / जिसे / जहाँ / और (or who / which /
  where / and in English) plus commas where breath goes. About 2 sentences a line, and every line flows like
  "…बदल देता है, जिसका नाम है ब्रेन फ़्लो।"
- `lineGapMs` 350, `paragraphGapMs` 900, `continuity: true`, no emotion tags, one tone and pace.

**Why:** the first take (short separate statements, brief "calm and clear, one steady pace", lineGapMs 450) sounded
robotic/flat to the user even at normal pace. The linked-clause retake sounded human.
**How to apply:** use this for every Emotive Speech narration, in Hindi and English. Write the script in this shape before
voicing, not as a fix afterwards. See [[temple-video-project]] and [[branch-style-target]].
