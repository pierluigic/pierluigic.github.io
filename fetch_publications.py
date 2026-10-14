import requests
import time
from collections import defaultdict

# ============================================================
# Configuration
# ============================================================

SPARQL_ENDPOINT = "https://sparql.dblp.org/sparql"

AUTHOR_URI = "https://dblp.org/pid/209/2984"
AUTHOR_NAME = "Pierluigi Cassotti"

OUTPUT_FILE = "publications.markdown"

HEADERS = {
    "Accept": "application/sparql-results+json",
    "User-Agent": "AcademicPublicationsUpdater/1.0"
}


# ============================================================
# Execute SPARQL queries
# ============================================================

def execute_sparql(query, max_retries=3):
    """Execute a SPARQL query against DBLP."""

    for attempt in range(max_retries):

        try:
            response = requests.get(
                SPARQL_ENDPOINT,
                params={
                    "query": query,
                    "format": "json"
                },
                headers=HEADERS,
                timeout=120
            )

            response.raise_for_status()

            return response.json()["results"]["bindings"]

        except (
            requests.exceptions.RequestException,
            ValueError,
            KeyError
        ) as e:

            if attempt == max_retries - 1:
                raise RuntimeError(
                    f"SPARQL query failed after {max_retries} attempts"
                ) from e

            wait_time = 2 ** (attempt + 1)

            print(
                f"Request failed: {e}. "
                f"Retrying in {wait_time} seconds..."
            )

            time.sleep(wait_time)


def get_value(row, key, default=""):
    """Extract a value from a SPARQL JSON binding."""
    return row.get(key, {}).get("value", default)


# ============================================================
# Fetch publications
# ============================================================

def fetch_publications():
    """Retrieve publications and their metadata."""

    query = f"""
    PREFIX dblp: <https://dblp.org/rdf/schema#>

    SELECT DISTINCT
        ?publication
        ?title
        ?year
        ?eventYear
        ?type
        ?venue
        ?url
    WHERE {{
        ?publication dblp:authoredBy <{AUTHOR_URI}> ;
                     dblp:title ?title ;
                     a ?type .

        OPTIONAL {{
            ?publication dblp:yearOfPublication ?year .
        }}

        OPTIONAL {{
            ?publication dblp:yearOfEvent ?eventYear .
        }}

        OPTIONAL {{
            ?publication dblp:publishedIn ?venue .
        }}

        OPTIONAL {{
            ?publication dblp:primaryDocumentPage ?url .
        }}
    }}
    ORDER BY DESC(?year)
    """

    return execute_sparql(query)


# ============================================================
# Fetch authors
# ============================================================

def fetch_authors(publication_uris):
    """Retrieve authors in their original publication order."""

    authors = defaultdict(dict)

    batch_size = 20

    for i in range(0, len(publication_uris), batch_size):

        batch = publication_uris[i:i + batch_size]

        values = " ".join(
            f"<{uri}>" for uri in batch
        )

        query = f"""
        PREFIX dblp: <https://dblp.org/rdf/schema#>

        SELECT
            ?publication
            ?author
            ?position
        WHERE {{
            VALUES ?publication {{ {values} }}

            ?signature dblp:signaturePublication ?publication ;
                       dblp:signatureOrdinal ?position ;
                       dblp:signatureDblpName ?author .
        }}
        ORDER BY ?publication ?position
        """

        results = execute_sparql(query)

        for row in results:

            publication = get_value(row, "publication")
            author = get_value(row, "author")
            position = get_value(row, "position")

            if publication and author and position:
                authors[publication][int(position)] = author

        # Avoid excessive requests
        if i + batch_size < len(publication_uris):
            time.sleep(0.5)

    return authors


# ============================================================
# Process publication metadata
# ============================================================

def process_publications(publication_rows):

    publications = {}

    for row in publication_rows:

        publication_id = get_value(row, "publication")

        if not publication_id:
            continue

        if publication_id not in publications:

            publications[publication_id] = {
                "title": get_value(row, "title"),
                "year": get_value(row, "year"),
                "event_year": get_value(row, "eventYear"),
                "types": set(),
                "venue": get_value(row, "venue"),
                "url": get_value(row, "url") or publication_id
            }

        pub = publications[publication_id]

        publication_type = get_value(row, "type")

        if publication_type:
            pub["types"].add(publication_type)

        if not pub["venue"]:
            pub["venue"] = get_value(row, "venue")

        if not pub["url"] or pub["url"] == publication_id:
            pub["url"] = get_value(row, "url") or publication_id

    # --------------------------------------------------------
    # Resolve publication years
    # --------------------------------------------------------

    for publication_id, pub in publications.items():

        publication_year = pub["year"]
        event_year = pub["event_year"]

        is_conference = any(
            t.endswith("#Inproceedings")
            for t in pub["types"]
        )

        # Prefer event year for conference papers
        if is_conference and event_year:
            resolved_year = event_year

        elif publication_year:
            resolved_year = publication_year

        elif event_year:
            resolved_year = event_year

        else:
            resolved_year = "0"

        # Report inconsistencies
        if (
            publication_year
            and event_year
            and publication_year != event_year
        ):
            print("\nWARNING: Year mismatch detected")
            print(f"  Title: {pub['title']}")
            print(f"  Publication year: {publication_year}")
            print(f"  Event year: {event_year}")
            print(f"  Selected year: {resolved_year}")
            print(f"  DBLP: {publication_id}")

        pub["year"] = resolved_year

    return publications


# ============================================================
# Generate Markdown
# ============================================================

def publications_to_markdown(publications, authors):

    markdown = """---
layout: page
title: Publications
permalink: /publications/
---

"""

    sorted_publications = sorted(
        publications.items(),
        key=lambda item: (
            int(item[1]["year"]),
            item[1]["title"]
        ),
        reverse=True
    )

    count = 0

    for publication_id, pub in sorted_publications:

        title = pub["title"]
        year = pub["year"]
        venue = pub["venue"]
        url = pub["url"]
        types = pub["types"]

        # ----------------------------------------------------
        # Exclude Data and Artifacts
        # ----------------------------------------------------

        if any(
            t.endswith("#Data")
            for t in types
        ):
            continue

        if "data and artifacts" in venue.lower():
            continue

        # ----------------------------------------------------
        # Exclude arXiv / CoRR
        # ----------------------------------------------------

        if venue.strip().lower() == "corr":
            continue

        if "/journals/corr/" in publication_id.lower():
            continue

        # ----------------------------------------------------
        # Format authors
        # ----------------------------------------------------

        ordered_authors = authors.get(publication_id, {})

        formatted_authors = []

        for _, author in sorted(ordered_authors.items()):

            if author == AUTHOR_NAME:
                formatted_authors.append(f"**{author}**")
            else:
                formatted_authors.append(author)

        authors_string = ", ".join(formatted_authors)

        if not authors_string:
            print(f"WARNING: No authors found for {title}")

        # ----------------------------------------------------
        # Generate Markdown
        # ----------------------------------------------------

        markdown += f"### [{title}]({url})\n"

        markdown += f"- **Year:** {year}\n"

        markdown += f"- **Authors:** {authors_string}\n"

        if any(
            t.endswith("#Inproceedings")
            for t in types
        ):
            markdown += (
                f"- **Conference/Workshop:** {venue}\n"
            )

        elif any(
            t.endswith("#Article")
            for t in types
        ):
            markdown += (
                f"- **Journal:** {venue}\n"
            )

        markdown += "\n"

        count += 1

    return markdown, count


# ============================================================
# Main
# ============================================================

def main():

    print("Fetching publications from DBLP SPARQL...")

    publication_rows = fetch_publications()

    publication_uris = sorted({
        get_value(row, "publication")
        for row in publication_rows
        if get_value(row, "publication")
    })

    print(
        f"Found {len(publication_uris)} unique publications."
    )

    print("Fetching publication authors...")

    authors = fetch_authors(publication_uris)

    print("Processing publication metadata...")

    publications = process_publications(publication_rows)

    print("Generating Markdown...")

    markdown, count = publications_to_markdown(
        publications,
        authors
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        file.write(markdown)

    print("\n================================")
    print(f"Exported {count} publications.")
    print(f"Saved to {OUTPUT_FILE}")
    print("================================")


if __name__ == "__main__":
    main()