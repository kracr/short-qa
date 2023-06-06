import spacy
from helpers.entity_extractor import EntityExtractor
import pickle
import wikidata.client
import en_core_web_sm
extractor = EntityExtractor()
entities = extractor.load(save_path="./data/relevant_entities.pkl")
entity_data = pickle.load(file=open("data/entity_data.pkl", "rb"))

client = wikidata.client.Client()

def find_edit(str1,str2):
    m=len(str1)
    n=len(str2)
    dp = [[0 for x in range(n + 1)] for x in range(m + 1)]
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0:
                dp[i][j] = j
            elif j == 0:
                dp[i][j] = i
            elif str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i][j - 1],
                                   dp[i - 1][j],
                                   dp[i - 1][j - 1])

    return dp[m][n]
def closest_local_named_entity(name):

    closest_entity = None
    closest_score = -1

    if type(name) != str:
        return None, None, 0

    name = name.strip().lower()
    for id, entity in entity_data.items():
        cleaned_entities = set([label.strip().lower() for label in entity["aliases"]])

        if name in cleaned_entities:
            return {"id": id, "name": entity["label"], "score": 1, "span": name}

        score = max(
            1
            - find_edit(cleaned_entity, name)
            / max(len(name), len(cleaned_entity))
            for cleaned_entity in cleaned_entities
        )

        if score > closest_score:
            closest_entity = id
            closest_score = score

    if closest_score > 0.7:
        return {
            "id": closest_entity,
            "name": entity_data[closest_entity]["label"],
            "score": closest_score,
            "span": name,
        }


nlp = spacy.load("en_core_web_sm")


def closest_local_entity(question, *args, **kwargs):
    doc = nlp(question)
    ents = []
    for chunk in doc.noun_chunks:
        ent = closest_local_named_entity(chunk.text, *args, **kwargs)

        if ent is None:
            continue
        ents.append(ent)
    return ents


"""
    Sample use:

    questions = [
        "Who is a Boddhisattava?",
        "What are the Four noble truths?",
        "who built dharmachakra stupa",
    ]

    for question in questions:
        print(question, closest_local_entity(question))    
"""
