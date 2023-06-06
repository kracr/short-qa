from tqdm import tqdm
import pickle

from multiprocessing.pool import ThreadPool
from tqdm import tqdm
import wikidata.client

client = wikidata.client.Client()

properties_of_ent = {}
properties = set([])

with open("data/subgraph.txt",encoding='utf8') as f:
    for line in tqdm(f.readlines()):
        try:
            triple = eval(line)
            if triple[0] not in properties_of_ent:
                properties_of_ent[triple[0]] = []
            properties_of_ent[triple[0]].append(triple)
            properties.add(triple[1])
        except:
            pass


properties = list(properties)


def get_property_data(property):
    try:
        p = client.get(property)
        if "aliases" in p.attributes and "en" in p.attributes["aliases"]:
            aliases = [str(p.label)] + [
                str(alias["value"]) for alias in p.attributes["aliases"]["en"]
            ]
        else:
            aliases = [str(p.label)]

        return {"label": str(p.label), "aliases": set(aliases), "id": property}
    except:
        return {"label": 'not found', "aliases": 'not found', "id": 'not found'}



with ThreadPool(32) as pool:
    res = pool.map(get_property_data, properties)

property_details = {}

for item in tqdm(res):
    if not item:
        continue
    property_details[item["id"]] = item


pickle.dump(property_details, file=open("data/properties", "wb"))
pickle.dump(properties_of_ent, file=open("data/properties_of_ent", "wb"))


with open("./data/properties", "rb") as file:
    print(pickle.load(file))
