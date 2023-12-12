from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
import json
from langdetect import detect
import datetime

# Load model directly
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

tokenizer = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-fr-en")
model = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-fr-en")

def translate_fr_en(text):
    input_ids = tokenizer.encode(text, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(input_ids)
    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return decoded

# traduction ? https://pypi.org/project/deep-translator/
es = Elasticsearch(hosts="http://elastic:changeme@localhost:9200/")


all_docs = []
docs = scan(es, index="hal-nlp", query={"query": {"match_all": {}}}, scroll='1h')
for doc in docs:
    if len(all_docs) % 100 == 0:
        # affiche l'heure et le nombre de documents traités
        print(datetime.datetime.now(), len(all_docs))
    title_status = 0
    title = ""
    abstract = "@"
    # title...
    if doc["_source"]["en_title_s"] != "":
        if len(doc["_source"]["en_title_s"]) > 2:
            try:
                title_lang = detect(doc["_source"]["en_title_s"])
                if title_lang == "en":
                    title = doc["_source"]["en_title_s"]
                else:
                    title_status = -1
            except Exception as e:
                print(e)
                print(doc)
                continue
                title_status = -1
    else:
        if doc["_source"]["fr_title_s"] != "":
            if len(doc["_source"]["fr_title_s"]) > 2:
                try:
                    title_lang = detect(doc["_source"]["fr_title_s"])
                    if title_lang == "fr":
                        title = translate_fr_en(doc["_source"]["fr_title_s"])
                    else:
                        print(doc)
                        title_status = -1
                except Exception as e:
                    print(e)
                    print(doc)
                    continue
                    title_status = -1
    # abstract...
    abstract_status = 0
    if doc["_source"]["en_abstract_s"] != "":
        if len(doc["_source"]["en_abstract_s"]) > 2:
            try:
                abstract_lang = detect(doc["_source"]["en_abstract_s"])
                if title_lang == "en":
                    abstract = doc["_source"]["en_abstract_s"]
                else:
                    title_status = -1
            except Exception as e:
                print(e)
                print(doc)
                continue
                abstract_status = -1
    else:
        if doc["_source"]["fr_abstract_s"] != "":
            if len(doc["_source"]["fr_abstract_s"]) > 2:
                try:
                    abstract_lang = detect(doc["_source"]["fr_abstract_s"])
                    if title_lang == "fr":
                        abstract = translate_fr_en(doc["_source"]["fr_abstract_s"])
                    else:
                        print(doc)
                        title_status = -1
                except Exception as e:
                    print(e)
                    print(doc)
                    continue
                    abstract_status = -1
            else:
                abstract = ""
    if title_status == 0 and abstract_status == 0:
        all_docs.append({"title": title, "abstract": abstract,
                         "created": doc["_source"]["date"],
                         "author_and_inst": [], "author_name": [], "category": [], "set" : "",
                         "id": doc["_id"]})

with open("dataset-en-documents/data/documents.json", "w", encoding="utf-8") as file:
    json.dump(all_docs, file, ensure_ascii=False, indent=4)
