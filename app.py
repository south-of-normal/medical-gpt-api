from flask import Flask, request, jsonify
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)

@app.route('/pubmed_search', methods=['GET'])
def pubmed_search():

    query = request.args.get('query')

    # STEP 1: Search PubMed
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

    search_params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": 3
    }

    search_response = requests.get(
        search_url,
        params=search_params,
        timeout=10
    )

    search_data = search_response.json()

    ids = search_data["esearchresult"]["idlist"]

    if not ids:
        return jsonify({"results": []})

    # STEP 2: Fetch article details
    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

    fetch_params = {
        "db": "pubmed",
        "id": ",".join(ids),
        "retmode": "xml"
    }

    fetch_response = requests.get(
        fetch_url,
        params=fetch_params,
        timeout=10
    )

    root = ET.fromstring(fetch_response.text)

    results = []

    for article in root.findall(".//PubmedArticle"):

        title_elem = article.find(".//ArticleTitle")
        abstract_elem = article.find(".//Abstract/AbstractText")
        pmid_elem = article.find(".//PMID")

        title = title_elem.text if title_elem is not None else "No title"
        abstract = abstract_elem.text if abstract_elem is not None else "No abstract available"
        pmid = pmid_elem.text if pmid_elem is not None else "Unknown"

        results.append({
            "pmid": pmid,
            "title": title,
            "abstract": abstract
        })

    return jsonify({"results": results})

if __name__ == "__main__":
    app.run()
