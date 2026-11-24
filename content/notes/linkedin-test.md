---
title: Prompt engineering is not the leverage point in Claude Code
date: 2026-08-24
slug: prompt-claude-code
description: "I know that sounds like a hot take. It isn't."
tags: [Prompt Engineering]
draft: False
# Optional: link to the original LinkedIn discussion.
source_url: https://lnkd.in/p/eAXzTFE8
---


The leverage is one layer up. Three things, and prompts aren't among them:

→ **Context architecture:** what the model knows on every turn (not per session, *per turn*)  
→ **Permission boundaries:** which of the tools the model is allowed to reason about  
→ **Validation loops:** the grading agents and hooks that catch the model before it ships

The gap between a team that invests in these three and a team that keeps rewriting `CLAUDE.md` is measurable:

- **3–5x** lower per-session cost
- **+10.1 percentage points** on hard task success (no model change required)
- **6x** task completion on repeated workflows (Harvey pilot data)

None of these came from a better model.

All of them came from better architecture around the model that already existed.