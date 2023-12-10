from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
import json
from langdetect import detect

# traduction ? https://pypi.org/project/deep-translator/
es = Elasticsearch(hosts="http://elastic:changeme@localhost:9200/")

dump_language = "fr" # fr

all_docs = []
docs = scan(es, index="hal-nlp", query={"query": {"match_all": {}}})
for doc in docs:

    if doc["_source"][dump_language + "_title_s"] != "" or doc["_source"][dump_language + "_abstract_s"] != "":

        try:
           # test si le contributeur a correctement renseigné les champs
            if len(doc["_source"][dump_language + "_title_s"]) > 2:
                title_lang = detect(doc["_source"][dump_language + "_title_s"])
            else:
                title_lang = dump_language
            if len(doc["_source"][dump_language + "_abstract_s"]) > 2:
                abstract_lang = detect(doc["_source"][dump_language + "_abstract_s"])
            else:
                abstract_lang = dump_language
        except Exception as e:
              print(e)
              print(doc)
              continue

        # si les champs sont dans la bonne langue, alors on ajoute au fichier .json
        if title_lang == dump_language and abstract_lang == dump_language:
            all_docs.append({"title": doc["_source"][dump_language + "_title_s"].replace("'", " "), "abstract": doc["_source"][dump_language + "_abstract_s"].replace("'", " "),
                             "created": doc["_source"]["date"],
                             "author_and_inst": [], "author_name": [], "category": [], "set" : "",
                             "id": doc["_id"]}) # à changer pour le dump depuis la véritable instance ES

with open("dataset-" + dump_language + "-documents/data/documents.json", "w", encoding="utf-8") as file:
    json.dump(all_docs, file, ensure_ascii=False, indent=4)

