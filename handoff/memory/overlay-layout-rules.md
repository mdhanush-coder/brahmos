---
name: overlay-layout-rules
description: "User's standing rules for explainer videos: on-screen text must never cover the 3D model; scenes need a designed background, not a flat stage"
metadata:
  node_type: memory
  type: feedback
  originSessionId: a78e9ddf-286f-4b3a-9c8a-244792cef2af
  modified: 2026-11-08T11:39:29.699Z
---

1. On-screen text must never obstruct the 3D model, at any frame.
2. Every 3D scene gets a good designed background (not a flat charcoal floor/wall).
3. The user reviews close-ups and will catch small part errors (an LED outside its window, parts off a PCB edge): verify
   small parts against their housing before showing.

4. (2026-11-08, Headphones chunk 3 v7) NEVER put a black gradient/panel behind text and never shift/shrink a 3D clip
   to make a text column: the clip's edge then cuts the model in half. Show 3D/diagrams full frame, text on top as its
   own overlay layer. This overrides "keep words in a column clear of the device" when they conflict.

**Why:** said 2026-11-07 while reviewing the Temple video ("the text should not obstruct it keep that in mind and add a good
background"); followed by catching an LED sticking out of the optical window.
**How to apply:** render plates transparent (shadow catcher floor), composite over a palette background in Motion Graphic,
measure the device's screen box per frame (keepout.json) and check every text element against it before rendering
(projects/temple/keepout_check.py); keep words in a column clear of the device. See [[temple-video-project]].
