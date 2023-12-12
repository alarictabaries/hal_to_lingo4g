from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
import json
import datetime
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

tokenizer = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-fr-en")
model = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-fr-en")

from transformers import AutoTokenizer, AutoModelForSequenceClassification

tokenizer2 = AutoTokenizer.from_pretrained("DunnBC22/distilbert-base-multilingual-cased-language_detection")
model2 = AutoModelForSequenceClassification.from_pretrained("DunnBC22/distilbert-base-multilingual-cased-language_detection")

def detect_lang(text):
    inputs = tokenizer2(text, return_tensors="pt", max_length=512, truncation=True)

    with torch.no_grad():
        logits = model2(**inputs).logits

    predicted_id = torch.argmax(logits, dim=-1).item()
    return model2.config.id2label[predicted_id]

def translate_fr_en(text):
    input_ids = tokenizer.encode(text, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(input_ids)
    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return decoded

# traduction ? https://pypi.org/project/deep-translator/
es = Elasticsearch(hosts="http://elastic:changeme@localhost:9200/")

query = {
    "query": {
        "terms": {
            "_id": ["1147500"]
        }
    }
}

all_docs = []
debug = False
if debug:
    docs = scan(es, index="hal-nlp", query=query, scroll='1h')
else:
    docs = scan(es, index="hal-nlp", query={"query": {"match_all": {}}}, scroll='1h')
for doc in docs:
    if len(all_docs) % 100 == 0:
        print(datetime.datetime.now(), len(all_docs))
    title_status = 0
    title = ""
    abstract = "@"
    # title...
    if doc["_source"]["en_title_s"] != "":
        if len(doc["_source"]["en_title_s"]) > 2:
            try:
                title_lang = detect_lang(doc["_source"]["en_title_s"])
                if title_lang == "English":
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
                    title_lang = detect_lang(doc["_source"]["fr_title_s"])
                    if title_lang == "French":
                        title = translate_fr_en(doc["_source"]["fr_title_s"])
                    else:
                        print("!fr_title", end=" > ")
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
                abstract_lang = detect_lang(doc["_source"]["en_abstract_s"])
                if abstract_lang == "English":
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
                    abstract_lang = detect_lang(doc["_source"]["fr_abstract_s"])
                    if abstract_lang == "French":
                        abstract = translate_fr_en(doc["_source"]["fr_abstract_s"])
                    else:
                        print("!fr_abstract", end=" > ")
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
