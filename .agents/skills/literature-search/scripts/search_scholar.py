#!/usr/bin/env python3
"""
Search Google Scholar using the 'scholarly' Python library.
Falls back gracefully if scholarly is not installed.

Usage:
    python search_scholar.py --query "approximate nearest neighbor" --max-results 20
"""

import argparse
import json
import sys
import time


def search_google_scholar(query: str, max_results: int = 20) -> list:
    """Search Google Scholar using the scholarly library."""
    try:
        from scholarly import scholarly
    except ImportError:
        print("[WARN] 'scholarly' package not installed. Install with: pip install scholarly",
              file=sys.stderr)
        print("[WARN] Skipping Google Scholar search.", file=sys.stderr)
        return []

    papers = []
    try:
        search_results = scholarly.search_pubs(query)

        for i, result in enumerate(search_results):
            if i >= max_results:
                break

            bib = result.get('bib', {})

            # Extract authors
            authors = bib.get('author', [])
            if isinstance(authors, str):
                authors = [a.strip() for a in authors.split(' and ')]

            # Extract year
            year = bib.get('pub_year')
            if year:
                try:
                    year = int(year)
                except (ValueError, TypeError):
                    year = None

            # PDF url
            pdf_url = None
            if result.get('eprint_url'):
                pdf_url = result['eprint_url']
            elif result.get('pub_url'):
                pdf_url = result['pub_url']

            papers.append({
                'title': bib.get('title', ''),
                'abstract': bib.get('abstract', ''),
                'year': year,
                'authors': authors,
                'venue': bib.get('venue', bib.get('journal', '')),
                'doi': None,  # scholarly doesn't reliably provide DOIs
                'arxiv_id': None,
                'pdf_url': pdf_url,
                'url': result.get('pub_url', ''),
                'source': 'google_scholar'
            })

            # Rate limiting — Google Scholar is aggressive about blocking
            time.sleep(2)

    except Exception as e:
        print(f"[WARN] Google Scholar search failed: {e}", file=sys.stderr)

    return papers


def main():
    parser = argparse.ArgumentParser(description='Search Google Scholar')
    parser.add_argument('--query', required=True, help='Search query string')
    parser.add_argument('--max-results', type=int, default=20,
                        help='Max results (default: 20)')
    args = parser.parse_args()

    print(f"[INFO] Searching Google Scholar for: {args.query}", file=sys.stderr)
    papers = search_google_scholar(args.query, args.max_results)
    print(f"[INFO] Found {len(papers)} results from Google Scholar", file=sys.stderr)

    json.dump(papers, sys.stdout, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    main()
