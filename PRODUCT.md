# Product

## Register

product

## Users

Registered users (patients, clinicians, or evaluators) using the Stroke Risk Calculator web application to manage stroke risk history, private medical documents, and RSA-encrypted data sharing across accounts.

## Product Purpose

Provide a privacy-preserving clinical risk estimation and encrypted data-sharing workflow: calculate stroke risk (WOE + Logistic Regression), store encrypted records/files, and share access out-of-band via RSA-2048 key exchange. Success means users can check access status, request or approve data sharing, manage documents, and handle RSA keys quickly with minimal cognitive overhead.

## Brand Personality

Clean, clinical, utilitarian — focused on clarity, task speed, and trustworthy restraint (inspired by Linear and Stripe dashboards), avoiding decorative noise, marketing fluff, emojis, or intrusive tooltips.

## Anti-references

- Marketing-style hero banners pushing primary workspace tools below the fold
- Ghost-card clutter (heavy drop shadows combined with borders, nested cards, oversized radii)
- Decorative gradients, emojis, or multi-step modal wizards for simple inline actions

## Design Principles

1. **Task-first compactness**: Minimize vertical chrome so core actions and request tables appear immediately above the fold.
2. **Structural clarity**: Group related controls into predictable 2-column adaptive panels on desktop and clean single-column flow on mobile.
3. **Restrained hierarchy**: Rely on weight, spacing, hairline borders, and one primary accent (`#2563eb`) rather than decorative color or containers.
4. **Factual, concise copy**: Keep labels, status badges, and empty states strictly objective, neutral, and action-oriented.

## Accessibility & Inclusion

- WCAG AA contrast (at least 4.5:1 for body and muted text against light surfaces)
- Clear keyboard focus-visible indicators on all controls, tabs, and links
- Respect `prefers-reduced-motion: reduce`
- Comfortable touch targets on mobile breakpoints and responsive tables without horizontal overflow
