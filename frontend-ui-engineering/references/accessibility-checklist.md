# Accessibility Checklist (WCAG 2.1 AA)

Reference for `frontend-ui-engineering`. Stack-agnostic — applies to any framework or plain HTML/CSS.

## Keyboard

- [ ] Every interactive element is reachable with Tab and operable with Enter/Space (and Arrow keys for composite widgets like menus, tabs, sliders).
- [ ] Tab order follows visual/reading order. No keyboard traps (except intentional, escapable ones like modals).
- [ ] Prefer native interactive elements (`<button>`, `<a href>`, `<input>`, `<select>`). They come with focus, keyboard, and semantics for free.
- [ ] Faked controls (a clickable `<div>`) must add `role`, `tabindex="0"`, and key handlers for Enter and Space. Avoid when a native element exists.
- [ ] Visible focus indicator on every focusable element. Never remove the focus outline without replacing it.

## Names, Roles, Values

- [ ] Icon-only controls have an accessible name (`aria-label` or visually-hidden text).
- [ ] Every form input has a programmatically associated label (`<label for>`, wrapping `<label>`, or `aria-label`).
- [ ] Custom widgets expose correct `role` and state (`aria-expanded`, `aria-selected`, `aria-checked`, `aria-pressed`).
- [ ] Decorative images have empty alt (`alt=""`); meaningful images have descriptive alt.
- [ ] Don't override native semantics with conflicting ARIA. No ARIA is better than wrong ARIA.

## Focus Management

- [ ] Opening a dialog/menu/popover moves focus into it.
- [ ] Focus is trapped inside an open modal and returns to the trigger on close.
- [ ] Route/view changes move focus to a sensible landmark (heading or main region).
- [ ] Dynamically revealed content receives focus when appropriate.

## Color & Contrast

- [ ] Normal text contrast ≥ 4.5:1; large text (≥ 24px, or ≥ 19px bold) ≥ 3:1.
- [ ] UI components and graphical objects (icons, input borders, focus rings) ≥ 3:1 against adjacent colors.
- [ ] State is never conveyed by color alone — pair with text, icon, underline, or shape.
- [ ] UI is usable at 200% zoom and in high-contrast / forced-colors mode.

## Content Structure

- [ ] One `<h1>` per page; heading levels nest without skipping.
- [ ] Landmark regions used (`header`, `nav`, `main`, `footer`, or ARIA equivalents).
- [ ] Lists use list markup; tables use `<th>`, scope, and captions where relevant.
- [ ] Reading order in the DOM matches the visual order.

## Dynamic Content

- [ ] Status messages and async results announced via `aria-live` (`polite` for non-urgent, `assertive` for urgent).
- [ ] Loading states announced (`aria-busy`, or a live-region status), not silent.
- [ ] Error messages are programmatically tied to their field (`aria-describedby`) and announced.

## Forms

- [ ] Labels visible and associated; placeholder is never the only label.
- [ ] Required fields indicated in text, not color/asterisk alone.
- [ ] Validation errors are specific, text-based, and linked to the field.
- [ ] Related controls grouped (`fieldset`/`legend` or `role="group"` with a name).

## Motion & Timing

- [ ] Honor `prefers-reduced-motion`; reduce or remove non-essential animation.
- [ ] No content flashes more than 3 times per second.
- [ ] Time limits are adjustable, extendable, or avoidable.

## Testing

- [ ] Tab through the entire page using only the keyboard.
- [ ] Run an automated checker (axe-core, Lighthouse, or equivalent) — zero violations.
- [ ] Spot-check with a screen reader (VoiceOver, NVDA, or TalkBack) on key flows.
- [ ] Verify at 320px width and at 200% zoom.
