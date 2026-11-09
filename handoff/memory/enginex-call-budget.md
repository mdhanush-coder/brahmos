---
name: enginex-call-budget
description: "User's manager caps EngineX usage at 500 calls per video; never double-run Blender jobs"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 8b83479b-2d04-496b-8b85-1567529957cf
  modified: 2026-11-05T20:50:10.747Z
---

EngineX calls are budgeted: at most 500 per video (manager's rule). Never re-run or duplicate a Blender job.

**Why:** cost control set by the user's manager; earlier work ran many exploratory/duplicate jobs.
**How to apply:** plan the call list before starting, batch montage/sign_output, predict output keys instead of polling,
use idempotencyKey on every run, preview gates before any long render, and report how many calls were used.
Related: [[branch-style-target]].
