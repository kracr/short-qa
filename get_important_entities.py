import wikipedia
import spacy
from tqdm import tqdm
from helpers.entity_extractor import EntityExtractor

nlp = spacy.load("en_core_web_sm")
nlp.add_pipe("entityLinker", last=True)

topics = ["emperor humayun", "gautam buddha"]

entities = set([])
urls = []
for topic in topics:
    wiki = wikipedia.page(topic)
    print(wiki.url)
    urls.append(wiki.url)
    # text = wiki.content
    # text = text.split("\n")

    # for para in text:
    #     if len(para) > 5:
    #         try:
    #             doc = nlp(para)
    #             for entity in tqdm(doc._.linkedEntities):
    #                 entities.add("Q" + str(entity.identifier))
    #         except:
    #             pass


extractor = EntityExtractor()
for url in urls:
    extractor(url)

extractor.save_ids("./data/doc_entities.txt")

with open("./data/doc_entities.txt", "r") as file:
    # file.write("\n".join(entities))
    print(f"Saved {len(file.readlines())}!")
