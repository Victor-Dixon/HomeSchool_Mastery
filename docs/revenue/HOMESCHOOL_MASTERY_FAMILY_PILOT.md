# HomeSchool Mastery Family Pilot Readiness

Status: `PILOT-PACKAGED / READINESS-GATED / NOT MARKET-VALIDATED`

## Purpose

This document packages the existing HomeSchool Mastery application as a bounded family design-partner pilot without claiming production readiness, market validation, pricing validation, customers, revenue, partners, or full curriculum coverage.

The canonical product is the existing `lessons_lan/` Flask/Jinja/SQLite application. It is local-first and intended to serve a household over a home LAN.

## Existing product proof

Current repository documentation already identifies these implemented product surfaces:

- daily lessons and checklist completion;
- TEKS/STAAR-aligned Math and Reading/ELAR practice;
- learning games;
- XP, mastery gates, boss fights, and gear rewards;
- student feedback and parent/admin review;
- parent/admin lesson and account management;
- optional local Ollama coaching;
- SQLite-backed local learner data.

These are repository claims only. They are not evidence of external adoption, learning outcomes, customer demand, or complete standards coverage.

## Candidate pilot

A bounded pilot would evaluate whether one authorized household can operate the current local-first product safely and consistently enough to generate product evidence.

### Pilot scope

1. Install the canonical `lessons_lan/` application on one household-controlled computer.
2. Create parent/admin and student accounts for explicitly authorized participants.
3. Configure a small, clearly identified lesson/practice set using existing application capabilities.
4. Run normal student workflows: Today checklist, lessons, practice, games, mastery/rewards, and feedback.
5. Run parent/admin workflows: lesson management, account management, and feedback review.
6. Collect only product-operation evidence that the household explicitly agrees to provide.
7. Produce a closeout report separating observed behavior, participant feedback, defects, and future recommendations.

## Required readiness gate before an external pilot

The repository's current `PRODUCTION_READINESS.md` still leaves the following items open, so an external paid or design-partner pilot must remain gated until they are verified or explicitly bounded out:

- canonical `lessons_lan/` test gate passes on the pilot candidate;
- backup/export path is documented and verified;
- restore plus smoke-test procedure is documented and verified;
- admin/student route boundaries have targeted tests;
- destructive reset is proven unavailable to student flows;
- canonical test gate has CI or an equivalent repeatable verification record.

A pilot may not silently convert an unresolved readiness item into a production claim.

## Safety and privacy boundaries

- Household learner data remains local unless the household explicitly authorizes a different handling path.
- Never use real learner data for public demos, marketing examples, screenshots, fixtures, or model prompts without explicit authorization.
- Back up `lessons_lan/instance/homeschool.db` before destructive maintenance.
- Do not expose the app publicly to the internet as part of this pilot package.
- Optional Ollama use remains local/optional; no paid cloud AI dependency is required by the pilot contract.
- Do not claim educational efficacy, guaranteed score improvement, complete TEKS coverage, or professional educational accreditation.

## Pilot evidence to collect

The useful evidence is operational rather than promotional:

- install/start/stop repeatability;
- backup and restore proof;
- successful parent/admin and student workflow completion;
- route/access-control defects;
- lesson/practice completion reliability;
- household-reported usability friction;
- student engagement observations explicitly labeled as anecdotal participant feedback;
- defects and requested features;
- willingness to continue using the product;
- only after real conversations: willingness to pay and acceptable pricing structure.

## Commercialization truth gate

The following remain `UNKNOWN` until independently evidenced:

- paying customers;
- validated price or pricing model;
- external design partners;
- measurable learning-outcome improvement;
- market size or demand;
- parent acquisition channel;
- support burden per household;
- retention;
- curriculum breadth sufficient for a broader launch.

Do not replace `UNKNOWN` with optimistic assumptions.

## Potential future commercial forms

These are hypotheses, not current offers or validated pricing:

- assisted household setup/support;
- local-first family subscription or support plan;
- curriculum/content packs;
- homeschool-coop deployment/support;
- self-hosted family license;
- optional local-AI configuration/support.

Each requires buyer evidence, scope definition, pricing validation, privacy review, and a support model before it becomes a real offer.

## Revenue gate

This lane advances only when at least one of the following changes:

- `READINESS_GATE_PASSED`;
- `PILOT_AUTHORIZED`;
- `BUYER_SIGNAL_RECEIVED`;
- `OUTREACH_AUTHORIZED`;
- `VALIDATED_PRICING_FEEDBACK`;
- `COMPLETED_EXTERNAL_PILOT`.

Until then, the correct autonomous work is product/readiness proof, not additional revenue copy.
