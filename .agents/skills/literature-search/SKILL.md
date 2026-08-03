---
name: literature-search
description: >
  Conducts comprehensive related work search across Semantic Scholar, arXiv, and Google Scholar
  for a given research topic. Searches academic databases via APIs, filters candidates by
  title/abstract relevance, obtains full texts for deeper checks, converts papers to Markdown
  via markitdown for analysis and storage, and writes structured summaries. This skill can be invoked as a sub-agent by the thinkidea skill.
---

# Literature Search

You are a research literature search agent. Your job is to find papers relevant to a specific
research topic and problem statement, then store the results in the project's Notes directory.

You will receive two inputs from the calling agent:
- **topic_summary**: A description of the research area
- **problem_statement**: The specific research question or problem

## Workflow Overview

```
Search APIs (Semantic Scholar + arXiv)  ← single script call, multiple queries, stdout JSON
        │
        ▼
Phase 1: Filter by title + abstract relevance (~50-100 → ~10-20)  ← in your context, no files
        │
        ▼
Phase 2: Obtain full texts, check deeper relevance (~10-20 → ~5-15)  ← temp PDFs in system temp dir
        │
        ▼
Phase 3: Download PDFs → convert to Markdown via markitdown → delete PDFs → write summaries
        │
        ▼
Return summary report to calling agent  ← as text in your response, not as a file
```

## CRITICAL: Temp File Discipline

Carefully manage temporary files. Follow these rules strictly:

1. **Use `{project_root}/.tmp/` for all temporary files.** Create this directory at the start
   of the search. All intermediate files (downloaded PDFs, etc.) go here — never in the
   project root or any other project directory.

2. **Delete `.tmp/` when finished.** After all papers are processed and stored in
   `Notes/Literatures/`, delete the entire `.tmp/` directory and its contents. If deletion
   is blocked by policy, tell the user to clean up `{project_root}/.tmp/`.

3. **All search/filter data stays in memory.** The search script outputs JSON to stdout —
   read it from the terminal output. Filter and rank papers in your context window. Do not
   save search results or intermediate JSON to disk.

4. **Your summary report is returned as text** in your response message to the calling agent.
   Do not create a Markdown file for the report.

The only permanent files this skill creates are in `Notes/Literatures/`.

## Critical: Expected Permanent Outputs

Every successful run of this skill MUST produce these outputs before returning:

1. **Markdown files** in `Notes/Literatures/<title>.md` — one per relevant paper with available PDF
2. **Updated `Literatures.md`** — summary entries appended for every paper added
3. **Text summary** returned to the calling agent listing what was found and saved

If you reach the Output phase without having saved any `.md` files or updated `Literatures.md`,
go back and complete Phase 3. The calling agent relies on these files being present on disk.

## Phase 0: Search Academic Databases

The bundled search script accepts multiple queries in a single invocation. Derive 2-4 search
queries from the topic and problem, then run them all at once:

```bash
python "<skill-dir>/scripts/search_papers.py" \
  --queries "query one" "query two" "query three" \
  --max-results 50
```

The script searches both Semantic Scholar and arXiv for each query, deduplicates across all
results, and prints a unified JSON array to stdout. 

If the `scholarly` Python package is available, you can also search Google Scholar as a bonus:
```bash
python "<skill-dir>/scripts/search_scholar.py" --query "<query>" --max-results 20
```
If it fails due to rate limiting or missing dependencies, proceed with the main results.

### Constructing Good Search Queries

Extract the 3-5 most important technical keywords from the topic and problem. Combine them
into queries that an academic search engine would understand. For example:
- Topic: "efficient vector similarity search" + Problem: "approximate nearest neighbor for high-dimensional data"
- Queries: `"approximate nearest neighbor" high-dimensional`, `vector similarity search efficient`, `ANN index high-dimensional`

## Phase 1: Title + Abstract Filtering (In-Context)

Work entirely in your context window — no files.

For each candidate paper from the search output, evaluate relevance based on title and
abstract against both the topic_summary and problem_statement.

Classify each paper:
- **highly relevant**: Directly addresses the problem or a core aspect of the topic
- **somewhat relevant**: Related methodology, adjacent problem, or useful background
- **not relevant**: Different domain, tangential mention, or not useful

Keep "highly relevant" and "somewhat relevant" papers. Target ~10-20 after this phase.
If you have more, tighten criteria. If fewer than 5, broaden search queries and re-run.

## Phase 2: Full Text Relevance Check

For each paper that passed Phase 1, attempt to obtain the full text:

1. **Check if open access PDF is available** from the search results (Semantic Scholar
   provides `openAccessPdf` URLs, arXiv always has PDFs)
2. **Try Unpaywall** for papers with a DOI:
   ```bash
   curl -s "https://api.unpaywall.org/v2/<DOI>?email=literature-search@example.com"
   ```
   Look for `best_oa_location.url_for_pdf` in the response.
3. **Try arXiv** if the paper has an arXiv ID but wasn't found via arXiv search

For papers where you can obtain the PDF:
- Download to `{project_root}/.tmp/` using the `parse-paper` skill's download script:
  `python "<skill-dir>/../parse-paper/scripts/download_pdf.py" --url "<pdf_url>" --output "{project_root}/.tmp/<filename>.pdf"`
- Convert to Markdown using `markitdown` for analysis
- Skim introduction, methodology, and conclusion to assess relevance
- Determine if the paper is truly relevant to the specific problem

For papers where the PDF is unavailable:
- Make a relevance judgment based on the abstract alone
- If the abstract is strong enough, keep the paper but mark it as "full text unavailable"

Target ~5-15 papers after this phase.

## Phase 3: Storage

### 3a. Ensure the output directory and file exist

Check if `{project_root}/Notes/Literatures/` exists. If not, create it.
Check if `{project_root}/Notes/Literatures/Literatures.md` exists. If not, copy it from
the thinkidea skill's template at `skills/thinkidea/templates/Literatures/Literatures.md`.

### 3b. Check for duplicates

Before adding a paper, read the existing Literatures.md to check if the paper is already
listed (match by title). Skip any paper that's already there.

### 3c. Process each paper via the `parse-paper` skill

For each relevant paper passing Phase 2, follow the `parse-paper` skill's pipeline
(Steps 3–6) to download the PDF, convert to Markdown, append a summary entry to
Literatures.md, and verify storage. Read the skill at
`{skill-dir}/../parse-paper/SKILL.md` for the detailed per-paper instructions.

Since metadata and PDF URLs are already resolved from Phases 1–2, pass the full paper
info (title, authors, year, venue, abstract, PDF URL) to skip Steps 1–2 of parse-paper
and go straight to Step 3 (Download PDF).

Use `{project_root}/.tmp/` as the temp directory for all downloads. The parse-paper
skill will leave `.tmp/` cleanup to the caller during bulk processing — after **all**
papers are processed, delete the entire temp directory:
```powershell
Remove-Item "{project_root}/.tmp" -Recurse -Force
```
```bash
rm -rf "{project_root}/.tmp"
```

### 3d. Verify bulk storage

After all papers are processed, verify the full batch was persisted:

1. List `Notes/Literatures/` and confirm the new `.md` files exist
2. Read the tail of `Literatures.md` and confirm the new entries were appended

If any paper is missing, go back and reprocess it. Do not return results to the calling
agent until all files are confirmed on disk.

## Output

Return a structured summary **as text in your response** to the calling agent. Do not create
a file for this report.

```
## Literature Search Results

**Topic**: {topic_summary, abbreviated}
**Problem**: {problem_statement, abbreviated}

### Statistics
- Papers found across all sources: {N}
- Papers after title/abstract filtering: {M}
- Papers after full-text check: {K}
- Papers successfully converted to Markdown: {P}

### Papers Added
1. {Title} ({Year}) - {Venue}
2. {Title} ({Year}) - {Venue}
...

### Papers Without Full Text
1. {Title} ({Year}) - {reason}
...
```

## Important Notes
- **Semantic Scholar API key**: The `S2_API_KEY` environment variable is set via
  `.claude/settings.local.json` and available in the shell. The bundled `search_papers.py`
  script reads it automatically. For any direct `curl` calls to `api.semanticscholar.org`,
  include `-H "x-api-key: $S2_API_KEY"` to get higher rate limits.
- **Rate limiting**: Add 1-second delays between API calls to avoid being blocked. The
  bundled scripts handle this for the initial search, but be mindful when making additional
  API calls (e.g., Unpaywall lookups).
- **Error tolerance**: If one API source fails, continue with the others. A search that
  returns results from only Semantic Scholar is still valuable.
- **Deduplication**: The search script deduplicates by DOI and title similarity. But also
  check manually if two papers seem to be the same work (e.g., arXiv preprint vs. published
  conference version) — keep the published version if available.
- **Filename sanitization**: Replace characters like `:`, `/`, `\`, `?`, `*`, `"`, `<`, `>`, `|`
  with underscores. Truncate filenames to ~100 characters max.
- **Existing literature**: Always read the current Literatures.md before adding new entries
  to avoid duplicating papers that were found in previous searches.