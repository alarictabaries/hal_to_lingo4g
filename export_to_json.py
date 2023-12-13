import json
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan

def process_documents(es, ids, filename):
    all_docs = []

    for doc_id in ids:
        query = {
            "query": {
                "terms": {
                    "_id": [doc_id]
                }
            }
        }

        docs = scan(es, index="hal-nlp", query=query, scroll='10m')
        for doc in docs:
            # Ajoutez ici votre logique de traitement du document
            all_docs.append(doc)  # ou formatage spécifique si nécessaire

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(all_docs, file, ensure_ascii=False, indent=4)

def main():
    es = Elasticsearch(hosts="http://elastic:changeme@localhost:9200/")

    # Récupérer tous les IDs des documents
    docs = scan(es, index="hal-nlp", query={"query": {"match_all": {}}}, scroll='1h')
    all_ids = [doc['_id'] for doc in docs]

    # Diviser les IDs en 4 parties
    num_parts = 4
    part_size = len(all_ids) // num_parts
    for i in range(num_parts):
        start = i * part_size
        end = start + part_size if i < num_parts - 1 else len(all_ids)
        process_documents(es, all_ids[start:end], f'documents_part_{i}.json')

if __name__ == "__main__":
    main()