# Script formula (Branch-style, engaging, sync-ready)

## Length
Words = minutes x 146 (that rate already includes the pauses). Lint enforces +-7 %. A 6-minute video is ~875 words,
~60 sentences, ~60 beats.

## Chapter skeleton (plan_video.py sets the exact word counts)
| Share | Chapter | What it does | Visual world |
|---|---|---|---|
| 8 % | Hook | the device in a real place; a surprising fact about something ordinary; the question | photoreal room |
| 6 % | Open it | "Inside this ... are N systems"; name them in order; this is the map of the video | housing opens / explode |
| 60 % | Systems (2-6) | one system per chapter, in the order energy or information flows through the device | dark-void internals |
| 10 % | Dive | inside the most surprising system: down to the physics (atoms, fields, charges, signals) | scale dive, then diagram |
| 10 % | Connect | the same idea in a second, bigger device, or the full chain working together | real object again |
| 6 % | Close | back to the opening scene; one-line recap; why it matters to the viewer | photoreal room |

## Sentence rules
- One idea per sentence, 8-22 words (lint: max 28). Two sentences per line = one thought.
- Name a part the first time in Title Case inside braces: `{Driver Gear}`. That is the cue for the camera and the
  label. Use the same name every time after (no synonyms: not "the little gear" later).
- Define every term in the same or next sentence: "a {Quartz Crystal Tuning Fork}, a tiny fork cut from quartz".
- Acronym: full form first, ", or VCO" after it. Never an unexplained acronym.
- Numbers as spoken words ("thirty-two thousand seven hundred sixty-eight"); the digits go in the visual directive
  (`|| number=32,768`), so the screen shows digits while the voice says words.
- Concrete before abstract: what it does, then how, then why. A comparison from daily life before a mechanism
  ("like pushing a kid on a swing, at the right moment, in both directions").
- When simplifying, say so once: "This is complicated, but here's one way to think about it."
- Contractions and plain words; no dashes (use commas); "!" almost never.

## Engagement devices (use them, they are measured in the lint)
- **Open loop** in the hook, closed in the close ("...and the same trick runs your phone a billion times a second").
- **Question every 60-90 s** (lint warns if 220 words pass without a "?").
- **Surprise numbers** with a scale comparison ("thirty thousand to one hundred fifty thousand times faster").
- **Callback**: the second subject reuses the first ("just like the counter in the wall clock").
- **Signposting** between chapters ("Now that we've covered the gear train, let's dive into...").
- **Pattern break** per chapter (dive, x-ray, schematic, number slam).
Avoid: channel housekeeping before the hook, stacking three facts in one sentence, unsupported superlatives.

## Annotated format (what script_lint.py reads)
```
# How a Quartz Watch Keeps Time
## 1. Hook || shot=room
Every quartz watch hides a tiny fork that vibrates thirty-two thousand times a second. || number=32,768 Hz
So how does a fork turn into a clock?
[pause]
## 2. Open it || shot=explode
Inside this watch are four systems. The {Battery}, the {Crystal Oscillator}, the {Integrated Circuit} and the {Stepper Motor}. || chip=FOUR SYSTEMS
## 3. The Crystal || shot=focus
The {Crystal Oscillator} sits in a metal can smaller than a grain of rice. || chip=CRYSTAL OSCILLATOR
```
- `## N. Title || shot=...` starts a chapter (shots: room, explode, focus, macro, dive, schematic, numbers, return).
- Text after `||` on a line is for the picture only (`chip=`, `number=`, `shot=`, `note=`); never spoken.
- `{Part Name}` -> spoken without braces; mapped to Blender object `part_name`.
- `[pause]` / `[long pause]` on their own line only. No other brackets (the lint adds the delivery brief).
