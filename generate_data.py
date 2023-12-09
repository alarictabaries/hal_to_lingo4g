import requests
from elasticsearch import Elasticsearch, helpers

es = Elasticsearch(hosts="http://elastic:changeme@localhost:9200/")

start = 0

# 45755
while start < 50000:
    url = "http://api.archives-ouvertes.fr/search/?q=domain_s:1.shs.info&fl=fr_title_s,fr_abstract_s,submittedDate_tdate&rows=10000&start=" + str(start) + "&wt=json"
    r = requests.get(url)
    data = r.json()
    docs = data['response']['docs']

    for doc in docs:
        if "fr_title_s" in doc and "fr_abstract_s" in doc:
            doc_short = {}
            doc_short["title"] = doc["fr_title_s"]
            doc_short["abstract"] = doc["fr_abstract_s"]
            doc_short["date"] = doc["submittedDate_tdate"]
            es.index(index='nlp-hal', document=doc_short)
    start += 10000
