from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
import json
from langdetect import detect

# traduction ? https://pypi.org/project/deep-translator/
es = Elasticsearch(hosts="http://elastic:changeme@localhost:9200/")

dump_language = "fr"
if dump_language == "fr":
    import spacy
    from nltk.corpus import stopwords
    from nltk.stem.snowball import SnowballStemmer
    from unidecode import unidecode

    nlp = spacy.load("fr_core_news_sm")
    stemmer = SnowballStemmer(language='french')
    stopWords = set(stopwords.words('french'))

    def stem(sentence):
        doc = nlp(sentence)
        tokens = [token.text for token in doc if not token.is_punct and not token.is_space]
        tokens = [token.replace("’", "").replace("‘", "").replace("«", "").replace("»", "").replace("-", " ") for token in tokens]
        tokens = [token for token in tokens if token not in stopWords]
        tokens = [unidecode(token) for token in tokens]
        tokens = [stemmer.stem(token) for token in tokens]
        return ' '.join(tokens)

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

            if dump_language == "fr":
                # stemming
                all_docs.append({"title": stem(doc["_source"][dump_language + "_title_s"]), "abstract": stem(doc["_source"][dump_language + "_abstract_s"]),
                                 "created": doc["_source"]["date"],
                                 "author_and_inst": [], "author_name": [], "category": [], "set" : "",
                                 "id": doc["_id"]})
            elif dump_language == "en":
                all_docs.append({"title": doc["_source"][dump_language + "_title_s"], "abstract": doc["_source"][dump_language + "_abstract_s"],
                                 "created": doc["_source"]["date"],
                                 "author_and_inst": [], "author_name": [], "category": [], "set" : "",
                                 "id": doc["_id"]}) # à changer pour le dump depuis la véritable instance ES
            else:
                print("Language not supported")
with open("dataset-" + dump_language + "-documents/data/documents.json", "w", encoding="utf-8") as file:
    json.dump(all_docs, file, ensure_ascii=False, indent=4)

