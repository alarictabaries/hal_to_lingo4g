import spacy
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from unidecode import unidecode


nlp = spacy.load("fr_core_news_sm")
stemmer = SnowballStemmer(language='french')
stopWords = set(stopwords.words('french'))

test = "Avec l’adoption généralisée de la science ouverte par la communauté scientifique, la volumétrie d’information accessible par le chercheur s’accroît de manière exponentielle. Dans ce contexte, l’utilisation d’archives ouvertes regroupant ces données joue un rôle important dans toute entreprise scientifique : elle permet d’archiver, de décrire puis d’indexer pour améliorer la visibilité et la pérennité des productions. Réciproquement celles-ci deviennent plus faciles à identifier pour, entre autres, réaliser des avancées scientifiques sur la base de recherches antérieures. Ce processus de veille scientifique ne peut être réalisé que si les données sont correctement indexées, ce qui permet alors de retrouver l’information de manière instrumentée par les moteurs de recherche. Cependant, cette étape tend à être reportée, voire négligée, par le chercheur, que ce soit par manque de temps ou d’intérêt. Nous proposons donc une métrique pour évaluer la qualité des métadonnées de références déposées sur l’archive HAL."
clean_words = []

doc = nlp(test)

tokens = [token.text for token in doc if not token.is_punct and not token.is_space]
tokens = [token.replace("’", "").replace("‘", "").replace("«", "").replace("»", "").replace("-", " ") for token in tokens]
tokens = [token for token in tokens if token not in stopWords]
tokens = [unidecode(token) for token in tokens]
tokens = [stemmer.stem(token) for token in tokens]

print(' '.join(tokens))
