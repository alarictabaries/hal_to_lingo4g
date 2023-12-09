import requests
from elasticsearch import Elasticsearch, helpers

es = Elasticsearch(hosts="http://elastic:changeme@localhost:9200/")

start = 0
count = 10000000
# 45755


while start < count:
    url = "http://api.archives-ouvertes.fr/search/?q=domain_s:1.shs.info&fl=*_title_s,*_abstract_s,submittedDate_tdate,docid&rows=10000&start=" + str(start) + "&sort=docid%20asc"
    print(url)
    r = requests.get(url)
    data = r.json()
    docs = data['response']['docs']
    print(len(docs))
    for doc in docs:
        doc_short = {}

        if not "en_title_s" in doc:
            doc_short["en_title_s"] = ""
        else:
            doc_short["en_title_s"] = doc["en_title_s"][0]
        if not "fr_title_s" in doc:
            doc_short["fr_title_s"] = ""
        else:
            doc_short["fr_title_s"] = doc["fr_title_s"][0]

        if not "en_abstract_s" in doc:
            doc_short["en_abstract_s"] = ""
        else:
            doc_short["en_abstract_s"] = doc["en_abstract_s"][0]
        if not "fr_abstract_s" in doc:
            doc_short["fr_abstract_s"] = ""
        else:
            doc_short["fr_abstract_s"] = doc["fr_abstract_s"][0]

        doc_short["date"] = doc["submittedDate_tdate"]

        res = es.index(index='hal-nlp', id=doc["docid"], document=doc_short)

    count = data['response']['numFound']
    start += 10000
