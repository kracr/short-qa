from tqdm import tqdm
import wikidata.client
import pickle

from multiprocessing.pool import ThreadPool


client = wikidata.client.Client()


def get_entity_data(line):
    global data
    line = line.strip()
    if not line:
        return
    entity_id = line

    p = client.get(entity_id=entity_id)
    if "aliases" in p.attributes and "en" in p.attributes["aliases"]:
        aliases = [str(p.label)] + [
            str(alias["value"]) for alias in p.attributes["aliases"]["en"]
        ]
    else:
        aliases = [str(p.label)]

    # print(entity_id)
    return {"label": str(p.label), "aliases": set(aliases), "id": entity_id}


if __name__ == "__main__":
    # freeze_support()

    res = []

    with open("./data/doc_entities.txt", "r") as file:
        lines = file.readlines()
        with ThreadPool(32) as pool:
            res = pool.map(get_entity_data, lines)

    data = {}

    for item in res:
        if not item:
            continue
        data[item["id"]] = item

    with open("./data/entity_data.pkl", "wb") as file:
        pickle.dump(data, file)

    with open("./data/entity_data.pkl", "rb") as file:
        print(pickle.load(file))
