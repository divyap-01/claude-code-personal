# Design & UI Rules (read-on-demand)

> **KitchenHQ, 2026-10-17:** that repo's own `DESIGN.md` (the October 2026 direction) is the
> design authority and outranks this file; the rulebook no longer points here. This file
> stays for projects that have no design file of their own.

Moved out of the always-loaded `CLAUDE.md` on 2026-07-11 — **nothing was changed, only relocated.**
These rules apply in full whenever you touch anything visual. The always-loaded file keeps the
BLOCKING triggers that tell you to come and read this.

**Read this file before:** any mockup, comp, new screen, component, redesign, layout change,
new flow or wizard, "make this look better", or any empty/loading/error state work.

---

## 14. UI/UX Design
*These are strong defaults — follow them on any visual or interface work unless there's a clear, stated reason to deviate. If you do deviate, say why.*

### Use the design skills, don't wing it
- **BLOCKING — read the project's design standards BEFORE making any mockup, comp, or UI. Never design from memory or assumptions.** Before producing a single pixel (mockup, HTML preview, redesign, new screen), FIRST locate and read the project's `PRODUCT.md` and `DESIGN.md` (and any `design-system`/`MASTER.md` or tokens file). In auntyskitchen these live per-feature under `.worktrees/<feature>/PRODUCT.md` and `DESIGN.md`. Ground every colour, font, radius, shadow, spacing, and component choice in those files — they are the source of truth (and the code is the tiebreaker over the docs). Then run the design skills (`/ui-ux-pro-max` to plan, `/impeccable` to build — `impeccable` auto-loads these standards). Making a mockup with invented colours/fonts/styles before reading these files is a hard failure; I did exactly that on the receive-flow mockup (used green as the action colour when the brand action colour is warm orange, used warm neutrals instead of cool slate, the wrong fonts, nested cards, and a banned side-stripe accent) and it had to be thrown away. Cost of reading two files: two minutes. Cost of skipping them: a discarded mockup and lost trust.
- **Always use the design skills for UI implementations — no exceptions for "small" work that touches layout, components, or visual structure.** Default pairing for ALL implementations: invoke **`/ui-ux-pro-max`** during planning to shape the layout, UX, hierarchy, and component choices, AND **`/impeccable`** during the build to enforce visual polish, spacing, typography, and anti-generic discipline. Both skills run on every meaningful UI task — planning skill first, then implementation skill — not one or the other.
- **Mandatory whenever any of these apply:** new screen, page, modal, drawer, or panel; new component or redesign of an existing one; layout/structure change to an existing screen; new flow or wizard; any "make this look better / more premium / less generic" ask; empty/loading/error states being added or reworked.
- **A quick visual tweak is not "UI work."** Copy edits, a single colour swap, moving one button — just do those. The skills are for anything where the look, feel, structure, or flow is the point.
- **When unsure whether a task counts as UI work, default to invoking both skills.** Say so out loud and pick them rather than silently skipping the skill step.

### Visual taste & standards
- **Aim for premium and intentional, never generic "AI-looking" UI.** Avoid the default cookie-cutter look — cramped spacing, clashing or muddy colours, inconsistent type sizes, everything boxed in identical cards.
- **Be disciplined with the basics:** generous, consistent spacing; a clear typographic hierarchy (a few deliberate sizes, not ten random ones); a restrained colour palette used consistently; alignment that lines up on a grid.
- **Match the existing product.** New screens should look like they belong in KitchenIQ — reuse the existing components, colours, and patterns already in the app rather than inventing a new style island.
- **Polish is part of "done."** Loading states, empty states, error states, and the obvious mobile/responsive view all count — a screen that only looks right on a wide desktop with perfect data isn't finished.

### Process & workflow
- **Show the design before building the whole thing.** For any non-trivial UI, describe (or mock up) the layout and the key choices in plain English first, and get a thumbs-up before writing the full implementation. Don't disappear and return with a finished screen I never agreed to.
- **Offer options at real forks.** When there's a genuine design choice (layout direction, where something lives, how a flow works), present 2–3 options with plain-English trade-offs and a recommendation — same as Section 8.
- **Check in at natural points.** For multi-screen or multi-step UI, pause between pieces so I can course-correct early rather than after everything's built.

### Showing me mockups & previews — NEVER just a file link (BLOCKING)
- **A link/path to a local `.html` mockup does NOT work for me.** In my environment, clicking a file path only opens the raw source code in the editor — it never renders the page. Telling me to "open this file in a browser" has failed every single time. Stop doing it.
- **Deliver every rendered preview as an actual image I can see.** When you want me to look at a mockup, screen, or any HTML preview, render it and show me a **screenshot (PNG) inline in the chat** — that's the default. Take the screenshot yourself (e.g. headless browser / Playwright / the chrome-devtools tools) from the rendered page, don't hand me the file.
- **Or give me a live, already-running URL** (e.g. the dev server on localhost, or a deployed preview link) that renders when clicked — not a `file://` or repo path.
- This applies to mockups, design comps, before/after shots, and any "have a look at this" UI moment. The only thing a plain file link is acceptable for is **plain-text files I just need to read or copy** (like a migration `.sql`), not anything that has to be rendered to make sense.

### Kitchen-first usability (this is who actually uses it)
- **Real users are in a kitchen** — often rushed, with messy hands, noise, and varying reading/language comfort. A screen that's technically correct but fiddly to use has failed.
- **Big touch targets, one-tap primary actions, minimal navigation.** The common task should be one obvious tap; advanced stuff can be tucked away.
- **Plain kitchen language in everything users see** — "cook day," "prep," "count," "order guide" — not internal/technical terms.
- **Don't bury people in menus or stacked pop-ups.** Avoid modal-inside-modal and deep menu digging for routine tasks.
- **Keep sensitive info manager-only by default** (costs, performance, labour numbers) — cook-facing screens show only what the cook needs to get the job done.
- **Never use the browser's raw `confirm`/`alert`/`prompt` pop-ups** — they show the bare web address instead of the restaurant's branding. Use the in-app confirmation dialog the codebase already has.

---

## 17. 🚨 CRITICAL UI & LAYOUT ENFORCEMENT (STOP BROKEN REFACTORING)
Strictly follow these structural rules to prevent disorganized layouts, broken responsive views, and theme bugs:

1. **The Layout Wrapper Rules (No Free-Floating Content)**
   - EVERY page or major layout block must use a strict, explicit wrapper grid.
   - Never use arbitrary absolute positioning or manual margins (e.g., `ml-[24px]`) to shift layouts.
   - Use: `<div className="grid grid-cols-1 md:grid-cols-12 gap-4 w-full max-w-7xl mx-auto p-4">`

2. **Explicit Column Spanning (No Layout Guesswork)**
   - Every single structural card, form container, or list component must explicitly declare its grid span for BOTH mobile and desktop.
   - Example: `<div className="col-span-1 md:col-span-8 bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-xl p-6">`

3. **Kitchen-First Interactive Targets**
   - All action buttons and touch points must have an explicit minimum height of `h-12` or `h-14` to prevent shrinking or collapsing on small screens.
   - Use `flex items-center justify-between` or `justify-center` for layout rows to keep icons and labels perfectly centered across all device viewports.

4. **The Strict Dark Mode Twin Rule**
   - You are FORBIDDEN from writing a light-mode color class without immediately pairing its dark-mode equivalent.
   - CORRECT: `bg-zinc-50 dark:bg-zinc-900 text-zinc-900 dark:text-zinc-50 border-zinc-200 dark:border-zinc-800`
   - INCORRECT: `bg-gray-100 text-black border-gray-200`

5. **Text Layout Protection**
   - Prevent text elements from wrapping chaotically or breaking containers when scaled up on kitchen monitors.
   - Force use of `truncate` or `line-clamp-2` on dynamic strings like menu names, employee profiles, or inventory item tags.


---

## 18. 🛑 SYSTEM-WIDE UI SAFETY RAILS (PREVENT OVERLAPS & CRAMMING)
Completely avoid crammed, broken layouts like overlapping text/numbers, colliding columns, or forcing desktop components onto small screens.

1. **Mandatory Mobile Breakpoints for Data Views**
   - Complex data layouts (such as Calendars, Schedulers, and Multi-Column Tables) MUST drop down to a single-column view or a dedicated mobile component below the `md` breakpoint.
   - You are FORBIDDEN from rendering side-by-side monthly calendars on screens narrower than `md: (768px)`. Mobile view must show exactly one month at a time or a rolling weekly view.

2. **No Layout Guessing / No Forced Fixed Widths**
   - Never use fixed pixel widths on container elements (e.g., `w-[500px]`) that can exceed the screen size. Use fluid width utilities (`w-full`, `max-w-md`, `max-w-xl`).
   - Grid and flex item containers must always wrap if content size cannot be guaranteed. Use `flex-wrap` and explicit grid-column allocations (`grid-cols-7` for date grids, with `gap-1` or `gap-2`).

3. **Explicit Row and Cell Sizing**
   - Individual cells containing dynamic text or interactive numbers (like calendar date buttons) must use uniform, explicit boundaries to prevent collision.
   - Example date cell wrapper: `<div className="aspect-square flex items-center justify-center p-1 w-full min-w-[32px] text-center text-sm">`

4. **Component Isolation Rules**
   - Interactive popovers, date pickers, or modals must use proper portal wrappers (`@radix-ui` or `shadcn` Primitives) so they scale and position relative to the screen viewport, not the parent container.

