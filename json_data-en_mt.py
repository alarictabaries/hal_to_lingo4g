from multiprocessing import Pool
import json
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
import json
import datetime
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import nltk
from nltk.tokenize import sent_tokenize

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

def translate_fr_en(text, max_length=512):
    # Segmenter le texte en phrases
    sentences = sent_tokenize(text)

    # Traduire chaque phrase séparément et les rassembler
    translated_text = ""
    for sentence in sentences:
        input_ids = tokenizer.encode(sentence, return_tensors="pt", max_length=max_length, truncation=True)
        outputs = model.generate(input_ids, max_length=max_length)
        translated_sentence = tokenizer.decode(outputs[0], skip_special_tokens=True)
        translated_text += translated_sentence + " "

    return translated_text


def process_documents(filename):
    # Lire les documents depuis le fichier JSON
    with open(filename, "r", encoding="utf-8") as file:
        docs = json.load(file)
    all_docs = []
    total_docs = len(docs)
    for i, doc in enumerate(docs):
        title_status = 0
        title = ""
        abstract = ""
        # title...
        if doc["_source"]["en_title_s"] != "":
            if len(doc["_source"]["en_title_s"]) > 2:
                try:
                    title_lang = detect_lang(doc["_source"]["en_title_s"])
                    if title_lang == "English":
                        title = doc["_source"]["en_title_s"]
                    elif title_lang == "French":
                        if detect_lang(doc["_source"]["fr_title_s"]) == "English":
                            title = doc["_source"]["fr_title_s"]
                        else:
                            if (doc["_source"]["fr_title_s"] == "") or (len(doc["_source"]["fr_title_s"]) < 2):
                                title = translate_fr_en(doc["_source"]["en_title_s"])
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
                        elif title_lang == "English":
                            title = doc["_source"]["fr_title_s"]
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
                    elif abstract_lang == "French":
                        if detect_lang(doc["_source"]["fr_abstract_s"]) == "English":
                            abstract = doc["_source"]["fr_abstract_s"]
                        else:
                            if (doc["_source"]["fr_abstract_s"] == "") or (len(doc["_source"]["fr_abstract_s"]) < 2):
                                abstract = translate_fr_en(doc["_source"]["en_abstract_s"])
                    else:
                        abstract_status = -1
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
                        elif abstract_lang == "English":
                            abstract = doc["_source"]["fr_abstract_s"]
                        else:
                            print("!fr_abstract", end=" > ")
                            print(doc)
                            abstract_status = -1
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
                             "author_and_inst": [], "author_name": [], "category": [], "set": "",
                             "id": doc["_id"]})
        # pass
    progress = (i + 1) / total_docs * 100
    print(f"Processing {filename}: {progress:.2f}% complete")

    with open("data/" + filename, "w", encoding="utf-8") as file:
        json.dump(all_docs, file, ensure_ascii=False, indent=4)

def main():
    nltk.download('punkt')
    num_processes = 4  # Correspond au nombre de fichiers JSON
    filenames = [f'documents_part_{i}.json' for i in range(num_processes)]

    with Pool(num_processes) as pool:
        pool.map(process_documents, filenames)

if __name__ == "__main__":
    main()
