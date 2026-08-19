# Vehicle Vision AI — CSS Split

The original theme.css was split by responsibility while preserving the original CSS cascade.

- `assets/css/global.css` — shared/base styles
- `assets/css/home.css` — Home-only styles and final Home overrides
- page CSS files — only styles that were page-specific in the original theme

`utils/theme.py` loads `global.css` first and the current page stylesheet second.
A compatibility fix was included for light-mode `data-theme="light"` so the Home design tokens resolve correctly.
