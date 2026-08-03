#!/usr/bin/env python3
"""
Search academic papers across Semantic Scholar and arXiv APIs.
Returns a unified, deduplicated JSON list of candidate papers.

Usage:
    python search_papers.py --query "approximate nearest neighbor" --max-results 50
    python search_papers.py --queries "query one" "query two" "query three" --max-results 30
    python search_papers.py --query "vector similarity search" --max-results 30 --sources semantic_scholar,arxiv
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from difflib import SequenceMatcher

# Semantic Scholar API key from environment (set via .claude/settings.local.json env field)
S2_API_KEY = os.environ.get('S2_API_KEY', '')


def get_s2_headers() -> dict:
    """Return headers for Semantic Scholar API requests, including API key if available."""
    headers = {'User-Agent': 'LiteratureSearch/1.0'}
    if S2_API_KEY:
        headers['x-api-key'] = S2_API_KEY
    return headers


def normalize_title(title: str) -> str:
    """Normalize a title for deduplication comparison."""
    title = title.lower().strip()
    title = re.sub(r'[^a-z0-9\s]', '', title)
    title = re.sub(r'\s+', ' ', title)
    return title


def titles_match(t1: str, t2: str, threshold: float = 0.85) -> bool:
    """Check if two titles are similar enough to be the same paper."""
    n1, n2 = normalize_title(t1), normalize_title(t2)
    return SequenceMatcher(None, n1, n2).ratio() >= threshold


def api_request_with_retry(url: str, max_retries: int = 4, base_delay: float = 2.0, headers: dict | None = None) -> dict | None:
    """Make an API request with exponential backoff on rate limit (429) and server errors (5xx)."""
    if headers is None:
        headers = {'User-Agent': 'LiteratureSearch/1.0'}
    for attempt in range(max_retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code == 429 or e.code >= 500:
                if attempt < max_retries:
                    delay = base_delay * (2 ** attempt)
                    print(f"[WARN] HTTP {e.code}, retrying in {delay:.0f}s (attempt {attempt+1}/{max_retries})", file=sys.stderr)
                    time.sleep(delay)
                    continue
                else:
                    print(f"[WARN] HTTP {e.code} after {max_retries} retries, giving up", file=sys.stderr)
                    return None
            else:
                print(f"[WARN] HTTP {e.code}: {e.reason}", file=sys.stderr)
                return None
        except Exception as e:
            print(f"[WARN] Request failed: {e}", file=sys.stderr)
            return None
    return None


def search_semantic_scholar(query: str, max_results: int = 50) -> list:
    """Search Semantic Scholar API for papers."""
    papers = []
    fields = "title,abstract,year,authors,venue,externalIds,openAccessPdf,url"
    offset = 0
    batch_size = min(max_results, 100)

    while len(papers) < max_results:
        params = urllib.parse.urlencode({
            'query': query,
            'limit': batch_size,
            'offset': offset,
            'fields': fields
        })
        url = f"https://api.semanticscholar.org/graph/v1/paper/search?{params}"

        data = api_request_with_retry(url, headers=get_s2_headers())
        if data is None or not data.get('data'):
            break

        for item in data['data']:
            authors = []
            for a in (item.get('authors') or []):
                if a.get('name'):
                    authors.append(a['name'])

            doi = None
            arxiv_id = None
            ext_ids = item.get('externalIds') or {}
            if ext_ids.get('DOI'):
                doi = ext_ids['DOI']
            if ext_ids.get('ArXiv'):
                arxiv_id = ext_ids['ArXiv']

            pdf_url = None
            oap = item.get('openAccessPdf')
            if oap and oap.get('url'):
                pdf_url = oap['url']

            papers.append({
                'title': item.get('title', ''),
                'abstract': item.get('abstract', ''),
                'year': item.get('year'),
                'authors': authors,
                'venue': item.get('venue', ''),
                'doi': doi,
                'arxiv_id': arxiv_id,
                'pdf_url': pdf_url,
                'url': item.get('url', ''),
                'source': 'semantic_scholar'
            })

        offset += batch_size
        if offset >= data.get('total', 0):
            break

        time.sleep(3)  # Rate limiting between pagination requests

    return papers[:max_results]


def search_arxiv(query: str, max_results: int = 50) -> list:
    """Search arXiv API for papers."""
    papers = []

    # arXiv uses a specific query syntax
    search_query = urllib.parse.quote(f'all:{query}')
    url = f"http://export.arxiv.org/api/query?search_query={search_query}&start=0&max_results={max_results}&sortBy=relevance&sortOrder=descending"

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'LiteratureSearch/1.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            xml_data = resp.read().decode('utf-8')

        root = ET.fromstring(xml_data)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}

        for entry in root.findall('atom:entry', ns):
            title_el = entry.find('atom:title', ns)
            title = title_el.text.strip().replace('\n', ' ') if title_el is not None else ''

            abstract_el = entry.find('atom:summary', ns)
            abstract = abstract_el.text.strip().replace('\n', ' ') if abstract_el is not None else ''

            authors = []
            for author_el in entry.findall('atom:author', ns):
                name_el = author_el.find('atom:name', ns)
                if name_el is not None:
                    authors.append(name_el.text.strip())

            published_el = entry.find('atom:published', ns)
            year = None
            if published_el is not None:
                year = int(published_el.text[:4])

            # Extract arXiv ID from the entry ID URL
            id_el = entry.find('atom:id', ns)
            arxiv_id = None
            arxiv_url = ''
            if id_el is not None:
                arxiv_url = id_el.text.strip()
                match = re.search(r'abs/(.+)$', arxiv_url)
                if match:
                    arxiv_id = match.group(1)

            # PDF link
            pdf_url = None
            for link in entry.findall('atom:link', ns):
                if link.get('title') == 'pdf':
                    pdf_url = link.get('href')
                    break
            if not pdf_url and arxiv_id:
                pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

            # Try to get DOI from arxiv metadata
            doi = None
            doi_el = entry.find('{http://arxiv.org/schemas/atom}doi')
            if doi_el is not None:
                doi = doi_el.text.strip()

            # Venue: use primary category
            venue = 'arXiv preprint'
            primary_cat = entry.find('{http://arxiv.org/schemas/atom}primary_category')
            if primary_cat is not None:
                venue = f"arXiv ({primary_cat.get('term', '')})"

            papers.append({
                'title': title,
                'abstract': abstract,
                'year': year,
                'authors': authors,
                'venue': venue,
                'doi': doi,
                'arxiv_id': arxiv_id,
                'pdf_url': pdf_url,
                'url': arxiv_url,
                'source': 'arxiv'
            })

    except Exception as e:
        print(f"[WARN] arXiv search failed: {e}", file=sys.stderr)

    return papers


def deduplicate(papers: list) -> list:
    """Remove duplicate papers based on DOI and title similarity."""
    unique = []
    seen_dois = set()
    seen_titles = []

    for paper in papers:
        # Check DOI dedup
        if paper.get('doi'):
            if paper['doi'] in seen_dois:
                # Merge: prefer the version with a PDF url
                for existing in unique:
                    if existing.get('doi') == paper['doi']:
                        if not existing.get('pdf_url') and paper.get('pdf_url'):
                            existing['pdf_url'] = paper['pdf_url']
                        # Prefer published venue over arXiv
                        if existing.get('source') == 'arxiv' and paper.get('source') == 'semantic_scholar':
                            if paper.get('venue') and 'arxiv' not in paper['venue'].lower():
                                existing['venue'] = paper['venue']
                        break
                continue
            seen_dois.add(paper['doi'])

        # Check title similarity dedup
        is_dup = False
        for i, seen_title in enumerate(seen_titles):
            if titles_match(paper.get('title', ''), seen_title):
                # Merge PDF url if the existing one doesn't have it
                if not unique[i].get('pdf_url') and paper.get('pdf_url'):
                    unique[i]['pdf_url'] = paper['pdf_url']
                is_dup = True
                break

        if not is_dup:
            unique.append(paper)
            seen_titles.append(paper.get('title', ''))

    return unique


def main():
    parser = argparse.ArgumentParser(description='Search academic papers across APIs')
    parser.add_argument('--query', help='Single search query string')
    parser.add_argument('--queries', nargs='+', help='Multiple search queries (run all, deduplicate across)')
    parser.add_argument('--max-results', type=int, default=50,
                        help='Max results per source per query (default: 50)')
    parser.add_argument('--sources', default='semantic_scholar,arxiv',
                        help='Comma-separated list of sources (default: semantic_scholar,arxiv)')
    args = parser.parse_args()

    # Collect all queries from both --query and --queries
    queries = []
    if args.query:
        queries.append(args.query)
    if args.queries:
        queries.extend(args.queries)
    if not queries:
        parser.error('At least one of --query or --queries is required')

    sources = [s.strip() for s in args.sources.split(',')]
    all_papers = []

    for qi, query in enumerate(queries):
        if qi > 0:
            time.sleep(3)  # Rate limiting between queries

        if 'semantic_scholar' in sources:
            print(f"[INFO] [{qi+1}/{len(queries)}] Searching Semantic Scholar for: {query}", file=sys.stderr)
            ss_papers = search_semantic_scholar(query, args.max_results)
            print(f"[INFO] Found {len(ss_papers)} results from Semantic Scholar", file=sys.stderr)
            all_papers.extend(ss_papers)
            time.sleep(3)

        if 'arxiv' in sources:
            print(f"[INFO] [{qi+1}/{len(queries)}] Searching arXiv for: {query}", file=sys.stderr)
            arxiv_papers = search_arxiv(query, args.max_results)
            print(f"[INFO] Found {len(arxiv_papers)} results from arXiv", file=sys.stderr)
            all_papers.extend(arxiv_papers)

    # Deduplicate across all queries and sources
    unique_papers = deduplicate(all_papers)
    print(f"[INFO] {len(all_papers)} total → {len(unique_papers)} unique after deduplication ({len(queries)} queries)", file=sys.stderr)

    # Output JSON to stdout
    json.dump(unique_papers, sys.stdout, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    main()
