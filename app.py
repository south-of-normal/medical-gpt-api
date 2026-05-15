from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/pubmed_search', methods=['GET'])
def pubmed_search():

    query = request.args.get('query')

    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": 5
    }

    response = requests.get(url, params=params)

    return jsonify(response.json())

if __name__ == "__main__":
    app.run()
