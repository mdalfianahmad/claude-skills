---
name: frontend-ui-engineering
description: Builds production-quality user interfaces that look engineered, not AI-generated. Use whenever the user is building or changing anything user-facing — a component, page, layout, form, dashboard, screen, modal, table, navigation, or any visual element. Trigger on "build a UI for...", "make a page that...", "create a component", "design this screen", "lay out the...", "add a form/modal/table", "style this", "make it look less generic / less AI", "fix the spacing/contrast/states", "make it responsive", or any request whose output is something a user looks at and clicks. Trigger even when the user names no framework and even when they only describe the feature ("a settings panel", "a checkout flow") without saying "UI". Do NOT use for backend logic, data modeling, API design, or for gathering design inspiration before building (that is ui-reference-gatherer).
---

# Frontend UI Engineering

Build interfaces that look like a design-aware engineer made them — not a model. Real design-system adherence, real accessibility, real interaction states. Framework-agnostic: the principles below hold whether the stack is React, Vue, Svelte, web components, or plain HTML/CSS.

## Definition

- **Name:** frontend-ui-engineering
- **Scope:** Produces production-quality user-facing UI — component architecture, layout, state strategy, accessibility (WCAG 2.1 AA), responsive behavior, and design-system discipline. Covers the *how it's built and how it looks/behaves*. Does NOT cover backend logic, API/data-model design, choosing a framework for the user, or sourcing visual inspiration (use `ui-reference-gatherer` for that). Does NOT generate finished visual design assets — it implements them.
- **Context:** Fire when the deliverable is something a user sees and interacts with: components, pages, layouts, forms, modals, tables, nav, dashboards, screens. Fire on framework-named requests ("React component") and framework-silent ones ("a settings panel", "make this less generic"). Fire on polish/fix requests about spacing, contrast, states, or responsiveness.

## When to use

- Building a new component, page, screen, or layout.
- Modifying an existing user-facing interface.
- Adding interactivity, state, or transitions.
- Fixing visual/UX issues: spacing, contrast, hierarchy, missing states.
- Making a UI responsive or accessible.
- A request to make UI "look less AI-generated" or "more production-quality."

## Component Architecture

**Colocate what belongs together.** Keep a component's implementation, tests, complex-state logic, and local types in one place. One folder per non-trivial component.

**Compose, don't over-configure.** Build from small nestable pieces (`Card` > `CardHeader` > `CardTitle`) rather than one component with twenty props (`variant`, `headerSize`, `bodyPadding`...). Composition scales; configuration calcifies.

**One component, one job.** A list item renders a list item. If it also fetches data, formats currency, and manages a modal, split it.

**Separate data from presentation.** A container handles loading/error/empty and data fetching; a presentation component takes already-resolved data and renders it. This keeps presentation components pure, testable, and reusable.

```
Container  → fetches data, decides: loading? error? empty? → picks what to render
Presentation → receives clean data → renders markup only
```

## State Strategy

Pick the simplest tool that works. Escalating order:

```
Local state         → state used by one component only
Lifted state        → shared between 2–3 sibling components
Context / provide    → theme, auth, locale (read often, written rarely)
URL / query params  → filters, pagination, tabs — anything shareable or bookmarkable
Server-state cache  → remote data needing caching/refetch/invalidation
Global store        → complex client state shared app-wide (last resort)
```

Don't pass props through components that don't use them past ~3 levels. If you are, restructure or use context/provide.

Put shareable UI state (filters, current tab, pagination) in the URL, not local state. It makes views linkable and survives reload.

## Design System Adherence

### Kill the AI Aesthetic

Generated UI has tells. Avoid every one:

| AI default | Why it's a problem | Do instead |
|---|---|---|
| Purple/indigo everything | Models default to a "safe" palette; every app ends up identical | Use the project's actual palette |
| Gradients everywhere | Visual noise; clashes with most systems | Flat, or one subtle gradient that matches the system |
| Max rounding on everything | Uniform `rounded-2xl` erases the radius hierarchy real designs use | One consistent radius scale |
| Generic hero sections | Template layout disconnected from the actual content/need | Content-first layout |
| Placeholder-style filler copy | Hides real-content problems: length, wrapping, overflow | Realistic content while building |
| Oversized padding everywhere | Equal generous padding destroys hierarchy, wastes space | A consistent spacing scale |
| Stock uniform card grids | Ignores information priority and scan patterns | Purpose-driven layout |
| Shadow-heavy depth | Competes with content, slow on low-end devices | Subtle/no shadow unless the system specifies |

### Spacing

Use a fixed scale (e.g. 0.25rem increments, or whatever the project defines). Never invent off-scale values like `13px` or `2.3rem`.

### Typography

Respect hierarchy: one page title, then section, then subsection, then body, then helper text. Don't skip levels. Don't borrow a heading style for non-heading text.

### Color

- Use semantic tokens (`text-primary`, `bg-surface`, `border-default`), not raw hex inline.
- Meet contrast minimums: 4.5:1 normal text, 3:1 large text.
- Never use color as the *only* signal of state — pair it with text, icon, or shape.

## Accessibility (WCAG 2.1 AA)

Non-negotiable. Full checklist in `references/accessibility-checklist.md`. Minimums:

- **Keyboard:** every interactive element reachable and operable by keyboard. Prefer native `<button>`/`<a>` over click-handlered `<div>`s. If you must fake it, add `role`, `tabindex`, and key handlers (Enter + Space).
- **Labels:** every icon-only control gets an accessible name (`aria-label`). Every input gets an associated `<label>` or `aria-label`.
- **Focus:** move focus to newly opened dialogs/menus; trap it while open; restore it on close. Visible focus ring always.
- **States:** never render a blank screen. Handle loading, error, and empty explicitly with meaningful copy and a next action.

## Responsive Design

Mobile-first. Start single-column, expand at breakpoints. Test at 320, 768, 1024, 1440px. Real content at the narrow end reveals wrapping/overflow problems early.

## Loading & Transitions

- Use skeletons for content placeholders, not spinners — they preserve layout and reduce perceived wait.
- Use optimistic updates for actions the user expects to be instant (toggles, likes); roll back on error.
- Animate with restraint. Motion should clarify state change, not decorate.

## Edge cases

- **No design system provided** → use sensible neutral defaults (system spacing scale, one accent color, one radius) and state the assumption. Do not default to the AI-aesthetic palette.
- **"It's just a prototype"** → still handle empty/error/loading and keyboard access. Prototypes ship.
- **Existing codebase** → match its conventions over these defaults. Read before writing.
- **User asks for an off-scale/raw-hex value explicitly** → comply, but flag it as off-system once.

## Red Flags

- A component over ~200 lines → split it.
- Inline styles or arbitrary pixel values off the scale.
- Missing error/loading/empty states.
- Color as the sole state indicator.
- The generic AI look (purple gradients, oversized cards, stock grids).

## Verification

- [ ] Renders without console errors.
- [ ] Every interactive element is keyboard-reachable (tab through it).
- [ ] Screen reader conveys structure and content.
- [ ] Works at 320 / 768 / 1024 / 1440px.
- [ ] Loading, error, and empty states all present.
- [ ] Spacing, color, and type follow the project's system.
- [ ] No a11y warnings from dev tools / axe-core.

## Notes

- This skill implements UI; it does not source inspiration. For reference gathering, use `ui-reference-gatherer` first.
- Framework specifics live in the project's own conventions, not here. Adapt the patterns to the stack in use.
