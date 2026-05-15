from flask import Flask, request, jsonify
import requests
import xml.etree.ElementTree as ET
import spacy

app = Flask(__name__)
nlp = spacy.load("en_core_sci_sm")

@app.route('/pubmed_search', methods=['GET'])
def pubmed_search():

    query = request.args.get('query')

    doc = nlp(query)

    keywords = []

    for token in doc:
        if token.is_stop:
            continue

        if token.is_punct:
            continue

        if len(token.text) < 3:
            continue

        keywords.append(token.lemma_.lower())

    query = " ".join(keywords)
    print("Processed query:", query)
    if not query.strip():
        return jsonify({"results": []})
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
        abstract_texts = article.findall(".//Abstract/AbstractText")

        abstract = " ".join([
            elem.text for elem in abstract_texts
            if elem.text
        ])
        if not abstract:
            abstract = "No abstract available"
        
        pmid_elem = article.find(".//PMID")

        title = title_elem.text if title_elem is not None else "No title"
        pmid = pmid_elem.text if pmid_elem is not None else "Unknown"

        results.append({
            "pmid": pmid,
            "title": title,
            "abstract": abstract
        })

    return jsonify({"results": results})

if __name__ == "__main__":
    app.run()
