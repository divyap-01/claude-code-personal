---
name: design-extractor
description: Use when the user provides a URL or screenshot of an existing website and wants to extract its design system — CSS variables, Tailwind configurations, color palette, typography, spacing, and component structure — into a reusable design-system.md.
user-invocable: true
---

# Design Extractor Skill

When the user provides a URL or an image of an existing website:
1. Use the `WebFetch` tool or Chrome integration to read the page source.
2. Analyze the CSS to identify:
   - Primary, secondary, and accent colors (HEX/RGB).
   - Typography (font families, sizes, weights).
   - Spacing patterns (padding/margin scales).
   - Component architecture (Navbar, Hero, Cards, etc.).
3. Output a `design-system.md` file in the project root.
4. Ask the user which specific component they want to build first based on this system.
