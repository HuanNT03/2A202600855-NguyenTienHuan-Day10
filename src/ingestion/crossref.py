from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from core.config import Settings


@dataclass(frozen=True)
class PaperRecord:
    paper_id: str
    title: str
    summary: str
    authors: list[str]
    categories: list[str]
    primary_category: str
    published: str
    updated: str
    abs_url: str
    pdf_url: str
    comment: str


import re
import time
import requests
from core.utils import normalize_whitespace, write_json, read_json


def clean_xml_tags(text: str) -> str:
    if not text:
        return ""
    cleaned = re.sub(r"<[^>]+>", "", text)
    cleaned = cleaned.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    return normalize_whitespace(cleaned)


def extract_date(item: dict) -> str:
    for date_field in ["published-print", "published-online", "issued", "created"]:
        date_parts = item.get(date_field, {}).get("date-parts", [])
        if date_parts and date_parts[0]:
            parts = date_parts[0]
            try:
                year = int(parts[0])
                month = int(parts[1]) if len(parts) > 1 else 1
                day = int(parts[2]) if len(parts) > 2 else 1
                return f"{year:04d}-{month:02d}-{day:02d}"
            except (ValueError, TypeError, IndexError):
                continue
    return "2026-01-01"


def parse_crossref_payload(payload: dict) -> list[PaperRecord]:
    """TODO(student): parse Crossref payload thanh list PaperRecord.

    Pseudo-code:
    1. Duyet `payload["message"]["items"]`.
    2. Lay DOI, title, abstract, authors, subject, dates, URLs.
    3. Chuan hoa text va bo record khong hop le.
    4. Tra ve list `PaperRecord`.
    """
    items = payload.get("message", {}).get("items", [])
    records = []
    for item in items:
        paper_id = item.get("DOI", "").strip()
        if not paper_id:
            continue
        
        title_list = item.get("title", [])
        title = normalize_whitespace(title_list[0]) if title_list else ""
        if not title:
            continue
        
        abstract = item.get("abstract", "")
        summary = clean_xml_tags(abstract)
        if not summary:
            continue
            
        author_list = item.get("author", [])
        authors = []
        for a in author_list:
            given = a.get("given", "").strip()
            family = a.get("family", "").strip()
            if given or family:
                name = f"{given} {family}".strip()
                authors.append(name)
        
        categories = item.get("subject", [])
        categories = [normalize_whitespace(c) for c in categories if c]
        primary_category = categories[0] if categories else "Computer Science"
        
        published = extract_date(item)
        updated = published
        created_date = item.get("created", {}).get("date-parts", [])
        if created_date and created_date[0]:
            try:
                parts = created_date[0]
                year = int(parts[0])
                month = int(parts[1]) if len(parts) > 1 else 1
                day = int(parts[2]) if len(parts) > 2 else 1
                updated = f"{year:04d}-{month:02d}-{day:02d}"
            except (ValueError, TypeError, IndexError):
                pass
                
        abs_url = item.get("URL", f"https://doi.org/{paper_id}")
        pdf_url = ""
        for link in item.get("link", []):
            if link.get("content-type") == "application/pdf":
                pdf_url = link.get("URL", "")
                break
        if not pdf_url:
            pdf_url = abs_url
            
        comment = item.get("container-title", [""])[0] or "Crossref"
        
        records.append(
            PaperRecord(
                paper_id=paper_id,
                title=title,
                summary=summary,
                authors=authors,
                categories=categories,
                primary_category=primary_category,
                published=published,
                updated=updated,
                abs_url=abs_url,
                pdf_url=pdf_url,
                comment=comment
            )
        )
    return records


def fetch_source_records(settings: Settings) -> list[PaperRecord]:
    """TODO(student): goi source API, luu raw response, parse thanh records.

    Pseudo-code:
    1. Tao params tu `settings.source_query`, `settings.source_filter`, `settings.max_results`.
    2. Goi API voi retry cho cac status code nhu 429/503.
    3. Luu raw response vao `settings.paths.raw_api_response`.
    4. Parse payload bang `parse_crossref_payload`.
    5. Luu records vao `settings.paths.raw_records_json`.
    """
    url = "https://api.crossref.org/works"
    params = {
        "query": settings.source_query,
        "filter": settings.source_filter,
        "rows": settings.max_results
    }
    headers = {
        "User-Agent": "Day10LabStudent/1.0 (mailto:student@example.com)"
    }
    
    max_retries = 3
    backoff = 2.0
    response_data = {}
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            if response.status_code == 200:
                response_data = response.json()
                break
            elif response.status_code in {429, 503, 504}:
                time.sleep(backoff * (2 ** attempt))
            else:
                response.raise_for_status()
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(backoff * (2 ** attempt))
            
    if not response_data:
        raise RuntimeError("Failed to fetch data from Crossref API after multiple attempts.")
        
    write_json(settings.paths.raw_api_response, response_data)
    records = parse_crossref_payload(response_data)
    records_dict = [r.__dict__ for r in records]
    write_json(settings.paths.raw_records_json, records_dict)
    return records


def load_raw_records(path: Path) -> list[PaperRecord]:
    """TODO(student): doc JSON snapshot va map thanh `PaperRecord`."""
    data = read_json(path)
    records = []
    for item in data:
        records.append(
            PaperRecord(
                paper_id=item["paper_id"],
                title=item["title"],
                summary=item["summary"],
                authors=item["authors"],
                categories=item["categories"],
                primary_category=item["primary_category"],
                published=item["published"],
                updated=item["updated"],
                abs_url=item["abs_url"],
                pdf_url=item["pdf_url"],
                comment=item["comment"]
            )
        )
    return records

