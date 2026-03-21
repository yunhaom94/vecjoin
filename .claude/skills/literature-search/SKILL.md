---
name: literature-search
description: >
  Conducts comprehensive related work search across Semantic Scholar, arXiv, and Google Scholar
  for a given research topic. Searches academic databases via APIs, filters candidates by
  title/abstract relevance, obtains full texts for deeper checks, downloads PDFs, and stores
  structured summaries. This skill is invoked as a sub-agent by the thinkidea skill during
  the literature management phase — it is not user-invocable.
---

# Literature Search

You are a research literature search agent. Your job is to find papers relevant to a specific
research topic and problem statement, then store the results in the project's Notes directory.

You will receive two inputs from the calling agent:
- **topic_summary**: A description of the research area
- **problem_statement**: The specific research question or problem

## Workflow Overview

```
Search APIs (Semantic Scholar + arXiv)
        │
        ▼
Phase 1: Filter by title + abstract relevance (~50-100 → ~10-20)
        │
        ▼
Phase 2: Obtain full texts, check deeper relevance (~10-20 → ~5-15)
        │
        ▼
Phase 3: Download PDFs + write summaries to Literatures.md
        │
        ▼
Return summary report to calling agent
```

## Phase 0: Search Academic Databases

Run the bundled search script to query Semantic Scholar and arXiv in parallel. The script
handles API calls, rate limiting, deduplication, and returns a unified JSON list of candidates.

```bash
python "<skill-dir>/scripts/search_papers.py" \
  --query "<search query terms derived from topic and problem>" \
  --max-results 50
```

You should derive 2-3 different search queries from the topic_summary and problem_statement to
maximize coverage. Run the script once per query and merge the results (the script handles
dedup by title similarity and DOI matching).

If the `scholarly` Python package is available, you can also search Google Scholar:
```bash
python "<skill-dir>/scripts/search_scholar.py" --query "<query>" --max-results 20
```
Google Scholar is a bonus source — if it fails due to rate limiting or missing dependencies,
proceed with Semantic Scholar + arXiv results alone.

### Constructing Good Search Queries

Extract the 3-5 most important technical keywords from the topic and problem. Combine them
into queries that an academic search engine would understand. For example:
- Topic: "efficient vector similarity search" + Problem: "approximate nearest neighbor for high-dimensional data"
- Queries: `"approximate nearest neighbor" high-dimensional`, `vector similarity search efficient`, `ANN index high-dimensional`

## Phase 1: Title + Abstract Filtering

For each candidate paper returned by the search scripts, evaluate relevance based on its
title and abstract against both the topic_summary and the problem_statement.

Classify each paper into one of three categories:
- **highly relevant**: Directly addresses the problem or a core aspect of the topic
- **somewhat relevant**: Related methodology, adjacent problem, or useful background
- **not relevant**: Different domain, tangential mention, or not useful

Keep papers classified as "highly relevant" or "somewhat relevant". Target ~10-20 papers
after this phase. If you have more, tighten your criteria. If fewer than 5, broaden your
search queries and try again.

Process papers in batches of 10-15 to avoid overwhelming your context. For each batch,
list the titles and abstracts, then reason about relevance.

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
- Download it temporarily
- Use the `markitdown` skill or `Read` tool to extract text from the PDF
- Skim the introduction, methodology, and conclusion sections
- Determine if the paper is truly relevant to the specific problem

For papers where the PDF is unavailable:
- Make a relevance judgment based on the abstract alone
- If the abstract is strong enough, keep the paper but mark it as "PDF unavailable"

Target ~5-15 papers after this phase.

## Phase 3: Storage

### 3a. Ensure the output directory and file exist

Check if `{project_root}/Notes/Literatures/` exists. If not, create it.
Check if `{project_root}/Notes/Literatures/Literatures.md` exists. If not, create it with
this header:

```markdown
# Literatures
This document contains a list of literatures that is relevant to this project. Each literature is formatted in the following way, and each literature is separated by a horizontal line (---). The ./Notes/Literatures/ folder contains the full papers of the literatures listed in this file, with name format "{title}.pdf".
```

### 3b. Check for duplicates

Before adding a paper, read the existing Literatures.md to check if the paper is already
listed (match by title). Skip any paper that's already there.

### 3c. Download PDFs

For each relevant paper with an available PDF URL:
```bash
python "<skill-dir>/scripts/download_pdf.py" \
  --url "<pdf_url>" \
  --output "{project_root}/Notes/Literatures/<sanitized_title>.pdf"
```

The title should be sanitized for use as a filename (remove special characters, truncate
if very long). The download script handles retries and validates the file is actually a PDF.

### 3d. Append summaries to Literatures.md

For each relevant paper, append an entry to the end of Literatures.md in this exact format:

```
---
- **Title**: {paper title}
- **Author(s)**: {comma-separated author names}
- **Year**: {publication year}
- **Venue**: {journal, conference, or "arXiv preprint"}
- **Summary**: {2-4 sentence summary covering main ideas, methodology, key findings}
- **Relevance**: {1-2 sentence explanation of how this paper relates to the research topic}
---
```

If the PDF was unavailable, add a note at the end of the Summary:
`(Note: Full text PDF was not available for download.)`

## Output

When finished, return a structured summary to the calling agent:

```
## Literature Search Results

**Topic**: {topic_summary, abbreviated}
**Problem**: {problem_statement, abbreviated}

### Statistics
- Papers found across all sources: {N}
- Papers after title/abstract filtering: {M}
- Papers after full-text check: {K}
- PDFs successfully downloaded: {P}

### Papers Added
1. {Title} ({Year}) - {Venue}
2. {Title} ({Year}) - {Venue}
...

### Papers Without PDF
1. {Title} ({Year}) - {reason}
...
```

## Important Notes

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
