# Recursion Diagram Atlas

An interactive design space for recursion diagrams, built from textbook figures (LYAH, SICP, HtDP, DCIC, CLRS, MIT 6.102) and LeetCode solutions with 5 or more votes from this scraper.

- `index.html` – the site. Open it in a browser, or serve this folder (`python3 -m http.server`). Click a coding to see the source figures behind it; filter by source at the top.
- `data.json` – codings, examples, image list and review notes (the site embeds the same data).
- `img/` – source images, resized to WebP. Textbook figures come from the group’s “Recursion 2” notes; LeetCode images come from `output/image_review/`.
- `figure/` – the static design-space figure (Figure 9 style): editable SVG, vector PDF and PNG. `_en` / `_zh` follow the concept-first structure (`tools/fig_from_data.py`, then `shot.py` and `to_svg.py`, which need Playwright); the unsuffixed `recursion_design_space.*` is an earlier draft with the old dimensions.
- `tools/` – scripts that generated the site and the figure (`gen_data.py`, `review.py`, `template.html`; `build.py`, `data_v3.py`, `to_svg.py`). Paths inside are from the environment they were run in; adjust before re-running.

The codings are organised concept first: the recursion type (structural vs. generative, linear vs. tree, recursive vs. iterative process; from HtDP, MIT 6.102 and SICP) is a property of the problem; each concept (self-referential data, decomposition, return & combine, base case) lists the ways it is drawn; global choices, code correspondence and other marks sit outside the concepts. `tools/restructure.py` migrated the earlier codings to this structure, and `tools/build_pages.py` renders both pages from `data.json` (run `tools/zh.py` first).

Coding is a first pass by one reviewer. Each LeetCode diagram was checked against the solution’s recursive code; three solutions with misleading or no recursion diagrams (3431696, 1345716, 1059115) were left out. Votes are the scrape snapshot.
