#!/usr/bin/env python3
"""
Download a PDF from a URL and save it to a local file.
Validates that the downloaded file is actually a PDF.

Usage:
    python download_pdf.py --url "https://arxiv.org/pdf/2301.00001.pdf" --output "./paper.pdf"
"""

import argparse
import os
import sys
import time
import urllib.request


def sanitize_filename(title: str, max_length: int = 100) -> str:
    """Sanitize a paper title for use as a filename."""
    # Replace problematic characters
    replacements = {
        ':': '_', '/': '_', '\\': '_', '?': '_', '*': '_',
        '"': '_', '<': '_', '>': '_', '|': '_', '\n': ' ',
        '\r': '', '\t': ' '
    }
    for old, new in replacements.items():
        title = title.replace(old, new)

    # Remove leading/trailing whitespace and dots
    title = title.strip().strip('.')

    # Collapse multiple underscores/spaces
    import re
    title = re.sub(r'[_\s]+', ' ', title)

    # Truncate
    if len(title) > max_length:
        title = title[:max_length].rstrip()

    return title


def download_pdf(url: str, output_path: str, max_retries: int = 3) -> bool:
    """Download a PDF from a URL with retries."""
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

    for attempt in range(max_retries):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; LiteratureSearch/1.0)',
                'Accept': 'application/pdf,*/*'
            }
            req = urllib.request.Request(url, headers=headers)

            with urllib.request.urlopen(req, timeout=60) as resp:
                content = resp.read()

            # Validate it's actually a PDF (check magic bytes)
            if content[:5] != b'%PDF-':
                # Some servers return HTML error pages — check for that
                if b'<html' in content[:1000].lower() or b'<!doctype' in content[:1000].lower():
                    print(f"[WARN] URL returned HTML instead of PDF: {url}", file=sys.stderr)
                    return False
                # Some PDFs have a BOM or whitespace before the header
                pdf_start = content.find(b'%PDF-')
                if pdf_start == -1 or pdf_start > 1024:
                    print(f"[WARN] Downloaded content does not appear to be a PDF: {url}", file=sys.stderr)
                    return False

            with open(output_path, 'wb') as f:
                f.write(content)

            file_size = os.path.getsize(output_path)
            print(f"[INFO] Downloaded {file_size:,} bytes to {output_path}", file=sys.stderr)
            return True

        except Exception as e:
            print(f"[WARN] Download attempt {attempt + 1}/{max_retries} failed: {e}", file=sys.stderr)
            if attempt < max_retries - 1:
                time.sleep(2 * (attempt + 1))  # Exponential backoff

    return False


def main():
    parser = argparse.ArgumentParser(description='Download a PDF and validate it')
    parser.add_argument('--url', required=True, help='URL of the PDF to download')
    parser.add_argument('--output', required=True, help='Output file path')
    parser.add_argument('--title', default=None,
                        help='Paper title (used to generate filename if --output is a directory)')
    args = parser.parse_args()

    output_path = args.output

    # If output is a directory and title is provided, generate filename
    if os.path.isdir(output_path) and args.title:
        filename = sanitize_filename(args.title) + '.pdf'
        output_path = os.path.join(output_path, filename)

    success = download_pdf(args.url, output_path)

    if success:
        print(json.dumps({"status": "ok", "path": output_path}))
    else:
        print(json.dumps({"status": "failed", "url": args.url}))
        sys.exit(1)


# Need json for output
import json

if __name__ == '__main__':
    main()
