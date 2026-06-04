---
name: speclet-review
description: Reviews a speclet document against the team's agreed speclet structure (see speclet-rules.html). Checks that every required section is present and adequately filled in, flags missing pieces, and suggests concrete expansions. USE WHEN the user asks to review, check, audit, validate, or improve a speclet, or asks "is my speclet complete?", "what's missing from this speclet?", "does this follow our speclet rules?". Works on Markdown, HTML, Word, Confluence exports, or pasted text.
---

# Speclet Review Skill

You are reviewing a speclet against the team's agreed structure. Your job is to verify every required section exists, judge whether the content is substantive (not just a heading with one line), and give concrete, actionable suggestions for what to add or expand.

## Inputs you need

Before reviewing, make sure you have:
1. The speclet itself (file path, pasted text, or link). If not provided, ask the user for it.
2. (Optional) Any team-specific context the user wants you to weigh.

If the speclet is very long, read it in full anyway — partial reads cause false "missing" verdicts.

## Required structure (the rubric)

Score each item as **PASS / PARTIAL / MISSING** and explain why.

### 1. Table of Contents
- [ ] Present at the top
- [ ] Links/anchors actually map to the sections that follow
- [ ] Order matches the body

### 2. Intro / Background / Scope
- [ ] States what the speclet covers and why it matters
- [ ] **Use cases** subsection that covers all three angles:
  - [ ] Why it's complicated
  - [ ] How it's currently being done — listing **all** existing capabilities
  - [ ] How it's going to be done — and **how much** of those capabilities the new approach captures

### 3. Boundaries
- [ ] **Device limitations** — what the hardware physically cannot do
- [ ] **Implementation / automation limitations** — what the automation does not (yet) support even though the device can
- [ ] **Manual vs Automated capability/feature matrix** — a real table, not prose
  - [ ] Every feature appears in the matrix
  - [ ] Features locked off in automation are explicitly called out
- [ ] Tables / specific use cases included where relevant

### 4. Requirements / Pre-requisites
- [ ] **Hardware**
  - [ ] Pictures of individual parts
  - [ ] Model numbers for each part
  - [ ] **Protections** (optional) — current/voltage/etc. protections noted if applicable
- [ ] **Software tools**
  - [ ] Each tool listed with an install link

### 5. Setup Steps
- [ ] Picture of the overall setup
- [ ] Steps (or links) for downloading software
- [ ] Order is reproducible by someone new

### 6. How to Use It
- [ ] **TL;DR** at the top for a quick running reminder
- [ ] Step-by-step with full details
- [ ] Any commands shown verbatim (copy-pasteable, in code blocks)
- [ ] Any AI prompts shown verbatim if AI is part of the flow

### 7. Common Errors
- [ ] At least the errors hit during setup are documented
- [ ] Each error has a fix or workaround, not just a description

## How to run the review

1. **Skim for structure first.** Identify which of the 7 sections exist. Note any extra sections (fine — just record them).
2. **Map content to the rubric.** Go item-by-item. A heading alone is not a PASS.
3. **Judge substance, not just presence.** Examples:
   - A "Common Errors" section with one entry and no fix → PARTIAL.
   - A capability matrix in prose form ("most features work manually...") → PARTIAL; suggest converting to a table.
   - "See attached image" with no image → MISSING.
4. **Look for things the rules don't explicitly require but a reader will need.** Flag them as suggestions, not failures. Common ones:
   - Owner / point of contact and last-updated date
   - Glossary or acronym list if jargon-heavy
   - Safety/ESD notes if hardware is fragile
   - Versioning of firmware/software the steps were validated against
   - Expected runtime / how long each step takes
   - Pass/fail criteria — how the user knows it worked
   - Cleanup / teardown steps
   - Links to related speclets, dashboards, or test plans

## Output format

Return your review in this exact shape:

```
# Speclet Review: <name of speclet>

**Overall verdict:** Ready to share / Needs revisions / Major gaps

## Summary
<2–4 sentence summary of the strongest and weakest areas.>

## Section-by-section scorecard

| # | Section | Status | Notes |
|---|---------|--------|-------|
| 1 | Table of Contents | PASS / PARTIAL / MISSING | … |
| 2 | Intro / Background / Scope | … | … |
| 3 | Boundaries | … | … |
| 4 | Requirements / Pre-requisites | … | … |
| 5 | Setup Steps | … | … |
| 6 | How to Use It | … | … |
| 7 | Common Errors | … | … |

## Required fixes (must address before sharing)
1. …
2. …

## Suggested expansions (nice to have)
1. …
2. …

## Extras the rules don't require but you should consider
- …
```

## Rules of engagement

- **Be specific.** "Add more detail to setup" is useless. "Add the exact `pip install` command and the COM-port discovery step before step 3" is useful.
- **Quote the speclet** when pointing out a problem so the author can find it.
- **Don't invent content.** If a section is missing, say so — do not write the missing content unless the user explicitly asks you to draft it.
- **Stay neutral on style.** Only push back on style if it blocks comprehension (e.g., wall-of-text with no headings).
- **If the speclet is for a different domain** (pure software, no hardware), mark hardware-only items as **N/A** with a one-line justification rather than MISSING.
