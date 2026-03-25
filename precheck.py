import requests
import json
import os

#PUBMED: Title of article and abstract || Dont have to add PMC; can just input IDs directly into param field
#PMCOA: Full Article, title, results, methods, discussion, etc. || HAVE TO add PMC to PMID param in URL


""" TOMORROW
    Read all text
    seperate metadata and non-main paragraph texts into seperate categories
    Get ALL the text from the PMCIDs
    IF everything works as properly, tokenize and create embeddings for small batches of the text for vector database
    Decide on AI Model to use for RAG
"""

request = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi", params={
    "db":"pmc",
    "term":"diabetes AND book[ptyp]",
    "retmax":100,
    "retmode":"json",
    "datetype": "pdat",
    "mindate": "2020/01/01",
    "maxdate": "2023/12/12",
    "sort": "relevance",
    "api_key": "9d8db6716c70bb95404c39e917f71fc15e08",
})
data = request.json()
PCIDS = data['esearchresult']['idlist']
results = []
for pmid in PCIDS:
    getData = requests.get(f"https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/PMC{pmid}/unicode", params={'api_key': "9d8db6716c70bb95404c39e917f71fc15e08"})
    if getData.ok and getData.text.strip() and not getData.text.startswith('[Error]'):
        results.append(getData.json())

"""with open("results.txt", "a") as f:
    f.write(json.dumps(results[0], indent=2))"""

os.makedirs("Texts", exist_ok=True)
for idx, result in enumerate(results):
    doc_id = results[idx][0]['documents'][0]['id']
    with open(os.path.join("Texts", f"{doc_id}.txt"), "a") as f:
        documents = results[idx][0]['documents']
        for passage in documents[0]['passages']:
            text = passage.get('text', '').strip()
            if passage['infons']['section_type'] == 'TITLE':
                text = 'TITLE: ' + '' + text
            if text:
                f.write(text + "\n\n")
        
"""with open("Text.txt", "a") as f:
    documents = results[0][0]['documents']
    for passage in documents[0]['passages']:
        text = passage.get('text', '').strip()
        if passage['infons']['section_type'] == 'TITLE':
            text = 'TITLE: ' + '' + text
        if text:
            f.write(text + "\n\n")"""

#"https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pubmed.cgi/bioc_json/17299597/ascii"