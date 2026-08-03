---
name: parse-paper
description: >
  Ingests a single academic paper into the project's literature collection: resolves metadata,
  downloads the PDF, converts to Markdown via markitdown, saves to Notes/Literatures/, and
  appends a structured summary to Literatures.md. Use this skill whenever a user provides a
  paper URL, DOI, arXiv ID, title, or local PDF file and wants it added to their literature
  collection. Also invoked by the literature-search skill during bulk paper processing, and
  by thinkidea when the user wants to discuss a paper not yet in the collection.
---

# Parse Paper

You handle the full pipeline for ingesting a single academic paper into the project's
literature collection: resolve metadata, find PDF, download, convert to Markdown, store
a summary entry, and verify everything landed on disk.

## Inputs

Callers provide paper information in different forms:

- **From literature-search (bulk)**: Full metadata (title, authors, year, venue, abstract,
  PDF URL) already resolved. Skip to Step 3 (Download PDF).
- **From thinkidea or user (single paper)**: Partial info — a URL, DOI, arXiv ID, or title.
  Start from Step 1 (Resolve Metadata).
- **Local PDF file**: The user provides a PDF file path directly (e.g., dragged into chat
  or pasted a path). Skip Steps 1-3 — go straight to Step 4 (Convert to Markdown), using
  the local file as input. Then try to extract metadata from the converted Markdown for
  Step 5 (title and authors are typically on the first page). If you can extract the title,
  also try a Semantic Scholar lookup to fill in year, venue, and abstract.

The caller also provides:
- **project_root**: Path to the project root directory
- **skill_dir**: Path to this skill's directory (for referencing bundled scripts)

## Step 1: Resolve Metadata (if needed)

Skip this step if the caller already provided full metadata (title, authors, year, venue,
abstract, PDF URL).

The `S2_API_KEY` environment variable is set via `.claude/settings.local.json` and is
available in the shell. Always include it as `-H "x-api-key: $S2_API_KEY"` in Semantic
Scholar API calls — this provides higher rate limits and avoids 429 errors.

**arXiv ID or URL** (e.g., `2301.00001` or `https://arxiv.org/abs/2301.00001`):
```bash
curl -s "http://export.arxiv.org/api/query?id_list=<arxiv_id>"
```
Parse the Atom XML for title, authors, abstract, published date.
PDF URL: `https://arxiv.org/pdf/<arxiv_id>.pdf`

**DOI**:
```bash
curl -s -H "x-api-key: $S2_API_KEY" "https://api.semanticscholar.org/graph/v1/paper/DOI:<doi>?fields=title,authors,year,venue,abstract,openAccessPdf"
```

**Semantic Scholar URL** (`https://www.semanticscholar.org/paper/.../<paper_id>`):
Extract the paper ID from the URL tail and query:
```bash
curl -s -H "x-api-key: $S2_API_KEY" "https://api.semanticscholar.org/graph/v1/paper/<paper_id>?fields=title,authors,year,venue,abstract,openAccessPdf"
```

**Title only**: Search Semantic Scholar:
```bash
curl -s -H "x-api-key: $S2_API_KEY" "https://api.semanticscholar.org/graph/v1/paper/search?query=<url_encoded_title>&limit=3&fields=title,authors,year,venue,abstract,openAccessPdf"
```
Pick the closest match by title similarity.

**Direct PDF URL**: Download first, extract metadata from the converted Markdown later
(title and author blocks are usually on the first page).

If metadata resolution fails partially, proceed with whatever you have — a paper with
incomplete metadata is better than a skipped paper.

## Step 2: Find PDF URL (if needed)

Skip if PDF URL is already known.

Try these sources in order:
1. `openAccessPdf.url` from the Semantic Scholar response
2. arXiv: `https://arxiv.org/pdf/<arxiv_id>.pdf`
3. Unpaywall (requires DOI):
   ```bash
   curl -s "https://api.unpaywall.org/v2/<DOI>?email=literature-search@example.com"
   ```
   Look for `best_oa_location.url_for_pdf`.

If no PDF is available, skip Steps 3-4 and go straight to Step 5 — create the
Literatures.md entry with a note that full text was unavailable.

## Step 3: Download PDF (if needed)

```bash
mkdir -p "{project_root}/.tmp"
python "<skill-dir>/scripts/download_pdf.py" \
  --url "<pdf_url>" \
  --output "{project_root}/.tmp/<sanitized_title>.pdf"
```

**Filename sanitization**: Replace `:`, `/`, `\`, `?`, `*`, `"`, `<`, `>`, `|` with
underscores. Collapse whitespace. Truncate to ~100 characters.

If the download fails after retries, treat the paper as "full text unavailable" and
continue to Step 5.

## Step 4: Convert to Markdown

The PDF source depends on how the paper was provided:
- **Downloaded PDF** (from Step 3): `{project_root}/.tmp/<sanitized_title>.pdf`
- **Local PDF** (user provided a file path): use the path as-is

Then, invoke `markitdown` skill to convert the PDF to markdown.

If the title isn't known yet (local PDF with no prior metadata), use the PDF filename
(minus extension) as a provisional name for the output `.md` file. After conversion,
read the first ~50 lines of the Markdown to extract the actual title and author names —
academic papers almost always have these on the first page. If you find the real title,
rename the `.md` file accordingly and use it for the Literatures.md entry. You can also
search Semantic Scholar by extracted title to fill in year, venue, and abstract.

After successful conversion, clean up temp files:
- **Downloaded PDF**: delete it (`rm -f "{project_root}/.tmp/<sanitized_title>.pdf"`)
- **Local PDF**: leave the original file untouched — it belongs to the user

When processing a single paper (not part of a bulk run), also remove the temp directory
if empty:
```bash
rmdir "{project_root}/.tmp" 2>/dev/null
```

When called from literature-search during bulk processing, leave `.tmp/` cleanup to the
caller — it will delete the directory after all papers are processed.

## Step 5: Append Summary to Literatures.md

### Ensure directory and file exist

Check if `{project_root}/Notes/Literatures/` exists. If not, create it.
Check if `{project_root}/Notes/Literatures/Literatures.md` exists. If not, copy the
template from `skills/thinkidea/templates/Literatures/Literatures.md`.

### Check for duplicates

Read the existing Literatures.md and check if this paper is already listed (match by title).
If found, skip the append and report it as a duplicate.

### Append the entry

Add this block to the end of Literatures.md:

```
---
- **Title**: {paper title}
- **Author(s)**: {comma-separated author names}
- **Year**: {publication year}
- **Venue**: {journal, conference, or "arXiv preprint"}
- **Summary**: {2-4 sentence summary covering main ideas, methodology, key findings}
- **Relevance**:
---
```

Leave **Relevance** blank — the calling agent (thinkidea or the user) fills it in with
project-specific context that this skill doesn't have.

If the full text was unavailable, append to the Summary line:
`(Note: Full text was not available for download and conversion.)`

## Step 6: Verify Storage

Before returning, confirm:
1. The `.md` file exists in `Notes/Literatures/` (if PDF was available)
2. The new entry appears in `Literatures.md`

If either check fails, fix it before returning.

## Output

Return a text summary to the caller:

```
## Paper Processed

- **Title**: {title}
- **Author(s)**: {authors}
- **Year**: {year}
- **Venue**: {venue}
- **Markdown saved**: Notes/Literatures/<filename>.md (or "N/A — PDF unavailable")
- **Literatures.md**: Entry appended (or "Skipped — duplicate")
```

## Important Notes

- **Rate limiting**: Add a 1-second delay before API calls to avoid being blocked.
- **Error tolerance**: If metadata resolution or PDF download fails, still create the
  Literatures.md entry with available info. Partial entries are useful — the user or
  calling agent can fill gaps later.
- **Deduplication**: Always check Literatures.md before appending. If the paper already
  exists, report it and skip.
