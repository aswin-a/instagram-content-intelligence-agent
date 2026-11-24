---
name: claims-check
description: Checks text against the brand's claims rules. In tagger mode it flags competitor health, efficacy and unverified endorsement claims as risks for report section F. In gate mode it blocks our own ideas until each passes, is rewritten with a safe, showable alternative, or is dropped. Use on any competitor claim recorded, on every idea before it enters section D, and when producing section F.
---

# Claims check

A product-risk control, not a style check. When unsure, flag it: a false positive costs an edit, a false negative costs a complaint. This list is a floor. The brand is responsible for checking which advertising and food rules apply (see [docs/guardrails.md](../../docs/guardrails.md)).

## Inputs
- `brand-profile` claims rules (including endorsements the brand has confirmed are backed up)
- **Tagger mode:** competitor captions, on-screen text, bios, hashtags
- **Gate mode:** our draft ideas (concept, hook, caption, on-screen text, hashtags, CTA)

## Flag as HIGH risk (never copy or suggest)
- The product **prevents, treats or cures** a disease or condition (cancer, allergies, kidney disease, skin conditions, etc.)
- Guaranteed **longer life** or specific health outcomes
- "Vet approved", "clinically proven", "recommended by vets" **unless the brand has confirmed it's backed up**

## Flag as MEDIUM risk (rewrite, or confirm with the brand)
- Implied health outcomes ("no more itching", "fixes digestion")
- Before/after health transformations
- Customer testimonials used without clear permission
- Trending audio with unclear licensing for a business account

## Safe, showable claims (prefer these)
Ingredients named plainly, macros/calories, freshness and cook-to-order, delivery area and speed, real customer reviews (with permission), process transparency (kitchen, lab testing if documented).

## Outputs
- **F. Risk flags** table: `Source (competitor post URL / our idea ID) | Claim or element | Risk level | Why | Safe alternative`
- **Gate mode:** for each idea, `pass`, `rewritten: <what changed>`, or `dropped: <why>`

## Stop conditions
- **Tagger:** done when every recorded competitor claim has a row. Competitor claims are never passed on as tactics.
- **Gate:** no idea with an open HIGH flag reaches section D. MEDIUM flags are rewritten, or listed for the brand to confirm.
