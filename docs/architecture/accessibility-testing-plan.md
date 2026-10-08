# Accessibility Testing Plan

## Why this matters more than usual for this project
The target users explicitly include low-income, rural, elderly, and low-literacy populations — accessibility here isn't just a WCAG checkbox, it's core to whether the platform reaches the people it's meant for. A few implications beyond standard a11y practice:
- Many users will be on low-end Android devices with small screens and slow connections — accessibility and performance overlap heavily here.
- Voice input/output (future milestone) matters as much for low-literacy users as for users with disabilities.
- Text should default to large, high-contrast, simple language — not just technically WCAG-compliant, but genuinely readable by someone with limited formal education.

## Standard: WCAG 2.1 AA
Baseline target for all citizen-facing pages (chat, disease explorer, schemes, video library). Admin/doctor portal pages target AA where practical but are lower priority since they're used by a smaller, more technical audience.

## Test checklist
| Category | Checks |
|---|---|
| Color contrast | All text meets 4.5:1 (normal) / 3:1 (large text) contrast ratio — verify emerald-700/red-700 accent colors against white/gray backgrounds used throughout the UI |
| Keyboard navigation | Every interactive element (chat input, send button, category filters, appointment actions) reachable and operable via keyboard alone, visible focus states |
| Screen reader | Semantic HTML (proper heading hierarchy, `<button>` not `<div onClick>`, form `<label>` associations) — audit `ChatWindow.tsx` and form pages for missing `aria-label`s on icon-only buttons |
| Touch targets | Minimum 44x44px tap targets — relevant given the low-end-mobile-device assumption above |
| Text scaling | Layout doesn't break at 200% browser zoom (common for low-vision users and older users) |
| Motion | No essential information conveyed by animation alone (Framer Motion, once added, must respect `prefers-reduced-motion`) |
| Language/reading level | Emergency response copy and disease info reviewed for plain-language clarity, not just grammatical correctness — a difference from typical a11y audits |

## Tooling
- **axe-core** (automated) integrated into the frontend CI job — catches contrast, missing labels, and ARIA misuse automatically on every PR.
- **Manual screen reader pass** (NVDA or VoiceOver) on the chat flow and appointment booking flow before each major release — automated tools catch maybe 30-40% of real accessibility issues; the conversational chat UI in particular needs a manual pass since screen reader behavior on dynamically-appearing chat messages (`aria-live` regions) can't be fully validated by static analysis.

## Known gap to fix
`ChatWindow.tsx` (built in Milestone 20) currently has no `aria-live` region on the message list — a screen reader user won't be automatically notified when a new assistant message arrives. Flagging this now as a concrete fix for the next frontend-touching milestone rather than leaving it implicit.
