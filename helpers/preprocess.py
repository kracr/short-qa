import spacy
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from tqdm import tqdm
from helpers.entity_resolution import closest_local_named_entity, closest_local_entity
import pickle
import re
# import spacy_transformers
nltk.download('stopwords')
nlp = spacy.load("en_core_web_md")
# nlp.add_pipe("entityLinker", last=True)
nltk.download('wordnet')
lemmatizer = WordNetLemmatizer()
stopwords = stopwords.words("english")
properties = pickle.load(file=open("data/properties", "rb"))


def replace_w_word(question):
    question = question.lower()
    w_words = {
        "who": "@<PERSON>",
        "where": "@<LOC>",
        "when": "@<DATETIME>",
        "what": "@<THING>",
        "which": "@<THING>",
        "how": "@<THING>",
    }
    f=0
    reformat=re.compile(r"(where)\s(is|was).+(from)$")
    check_format=reformat.fullmatch(question)
    if check_format:
        question = question.replace("where", "which place")
        question = question.replace("where", "which place")
        f=1
    found_w_words = []
    modified = question
    for w_word in w_words:
        if question.count(w_word):
            found_w_words.append(w_word)
            modified = modified.replace(w_word, w_words[w_word])
    if len(found_w_words) == 1:
        return modified,f
    else:
        return None,f


def preprocess_question(question):

    modified,f = replace_w_word(question)
    if not modified:
        return None,f

    doc = nlp(question)
    closest_local = closest_local_entity(question)
    for ent in closest_local:
        if not ent:
            continue

        modified = modified.replace(ent["span"] + "s", "@<" + ent["id"] + ">")
        modified = modified.replace(ent["span"], "@<" + ent["id"] + ">")
    return modified,f


def get_bag_of_words_triple(triple):
    bag_of_words_triple = set([])

    if triple[1] not in properties:
        return []

    for alias in properties[triple[1]]["aliases"]:
        bag_of_words_triple = bag_of_words_triple.union(set(str(alias).split()))

    bag_of_words_triple = map(
        lambda word: lemmatizer.lemmatize(word, "v"),
        bag_of_words_triple,
    )

    bag_of_words_triple = filter(
        lambda word: word not in stopwords, bag_of_words_triple
    )
    bag_of_words_triple = set(bag_of_words_triple)

    return bag_of_words_triple


def get_bag_of_words_query(question):

    bag_of_words_query = question.split()
    bag_of_words_query = map(
        lambda word: lemmatizer.lemmatize(word, "v"), bag_of_words_query
    )
    bag_of_words_query = filter(lambda word: word not in stopwords, bag_of_words_query)
    bag_of_words_query = set(bag_of_words_query)
    return bag_of_words_query


def get_lemmatized_verbs(question):
    question = nlp(question)
    verbs = set([])
    for token in question:
        if token.pos_[0] == "V":
            verbs.add(token.lemma_)
    return verbs
